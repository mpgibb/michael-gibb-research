"""Run prespecified rolling customer-base comparisons and aggregate evidence."""
import json
import platform
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import scipy
import sklearn
from scipy.special import xlogy
from scipy.stats import pearsonr,spearmanr
from sklearn.metrics import mean_poisson_deviance
from threadpoolctl import threadpool_limits

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from research_program.io import data_dir,provenance,write_json
from research_program.validate import validate_result
from studies.S03.ingest import CONFIG,ingest,snapshots,history,validation_selection,permitted_training
from studies.S03.models import BGNBD,GammaGamma,HurdleBoosting,RFMRule,recent_rule,predictive_distribution,interval_quantile,empirical_bands

HERE=Path(__file__).resolve().parent
LABELS={'recent_rule':'Recent 90-day purchasing','rfm_rule':'Historical RFM cohorts','bgnbd':'BG/NBD + Gamma-Gamma','boosting':'Hurdle count–spend boosting'}


def parts(frame,p):
    count=frame.future_count.to_numpy(float);spend=frame.future_spend.to_numpy(float);event=count>0;mu=np.maximum(p['count'],1e-8);prob=np.clip(p['purchase'],1e-8,1-1e-8);one=np.ones(len(frame))
    output={'count_poisson_deviance':(2*(xlogy(count,count/mu)-count+mu),one),
            'count_mae':(np.abs(count-p['count']),one),'purchase_brier':((event-prob)**2,one),
            'purchase_log_loss':(np.where(event,-np.log(prob),-np.log1p(-prob)),one),
            'count_ratio':(p['count'],count),'spend_mae':(np.abs(spend-p['spend']),one),
            'spend_ratio':(p['spend'],spend)}
    if 'count_lower' in p:
        for target,actual in [('count',count),('spend',spend)]:
            output[target+'_coverage_90']=(((actual>=p[target+'_lower'])&(actual<=p[target+'_upper'])).astype(float),one)
            output[target+'_interval_width']=(p[target+'_upper']-p[target+'_lower'],one)
    return output


def score(frame,p):
    return {name:float(a.sum()/b.sum()) for name,(a,b) in parts(frame,p).items()}


def evaluate(frame,predictions,seed):
    names=[];numerators=[];denominators=[]
    for model,p in predictions.items():
        for metric,(a,b) in parts(frame,p).items():
            names.append((model,metric));numerators.append(a);denominators.append(b)
    customers,inverse=np.unique(frame.customer.to_numpy(),return_inverse=True)
    num=np.zeros((len(customers),len(names)));den=num.copy()
    np.add.at(num,inverse,np.column_stack(numerators));np.add.at(den,inverse,np.column_stack(denominators))
    estimates=num.sum(axis=0)/den.sum(axis=0);rng=np.random.default_rng(seed);draws=[]
    for _ in range(CONFIG['bootstrap_repetitions']):
        ix=rng.integers(len(customers),size=len(customers));draws.append(num[ix].sum(axis=0)/den[ix].sum(axis=0))
    draws=np.array(draws);low,high=np.quantile(draws,[.025,.975],axis=0);metrics=[]
    for j,(model,metric) in enumerate(names):
        unit='GBP per customer-cutoff' if metric in ['spend_mae','spend_interval_width'] else 'purchase days per customer-cutoff' if metric in ['count_mae','count_interval_width'] else 'ratio' if metric.endswith('ratio') else 'proportion' if ('coverage' in metric or metric=='purchase_brier') else 'natural-log units' if metric=='purchase_log_loss' else 'Poisson deviance'
        metrics.append({'model':model,'name':metric,'estimate':estimates[j],'lower':low[j],'upper':high[j],'confidence':.95,'unit':unit,'split':'final_90_days'})
    a=names.index(('boosting','count_poisson_deviance'));b=names.index(('bgnbd','count_poisson_deviance'));delta=draws[:,a]-draws[:,b];lo,hi=np.quantile(delta,[.025,.975])
    return metrics,{'comparison':'boosting minus bgnbd','metric':'count_poisson_deviance','estimate':estimates[a]-estimates[b],'lower':lo,'upper':hi,'draws':len(draws),'unique_customers':len(customers)}


def subset_predictions(predictions,mask):
    return {name:{k:v[mask] for k,v in pred.items()} for name,pred in predictions.items()}


def cohort_profiles(frame,predictions):
    output=[]
    for horizon in CONFIG['horizons_days']:
        for inactivity in ['All inactivity bands','0–30 days','31–90 days','Over 90 days']:
            for frequency in ['All purchase histories','One purchase day','2–5 purchase days','6+ purchase days']:
                mask=(frame.horizon==horizon).to_numpy()
                if inactivity!='All inactivity bands':mask&=(frame.inactivity_band==inactivity).to_numpy()
                if frequency!='All purchase histories':mask&=(frame.frequency_band==frequency).to_numpy()
                if mask.sum()<CONFIG['cohort_minimum']:continue
                f=frame.loc[mask];actual=f.future_count.to_numpy(float)
                for name,p in subset_predictions(predictions,mask).items():
                    row={'model':name,'horizon_days':horizon,'inactivity':inactivity,'frequency':frequency,'observations':len(f),'unique_customers':f.customer.nunique(),'observed_count':actual.mean(),'predicted_count':p['count'].mean(),'observed_purchase_probability':(actual>0).mean(),'predicted_purchase_probability':p['purchase'].mean(),'latent_alive_probability':p['alive'].mean() if 'alive' in p else None,'observed_spend_gbp':f.future_spend.mean(),'predicted_spend_gbp':p['spend'].mean(),'predicted_spend_per_purchase':p['spend'].sum()/p['count'].sum() if p['count'].sum()>0 else None,'predicted_count_distribution':p['count_distribution'].mean(axis=0) if 'count_distribution' in p else None,'observed_count_distribution':[np.mean(actual==k) if k<5 else np.mean(actual>=5) for k in range(6)]}
                    for target in ['count','spend']:
                        if target+'_lower' in p:
                            y=f['future_'+target].to_numpy(float);row[target+'_coverage_90']=np.mean((y>=p[target+'_lower'])&(y<=p[target+'_upper']));row[target+'_interval_width']=np.mean(p[target+'_upper']-p[target+'_lower'])
                        else:row[target+'_coverage_90']=None;row[target+'_interval_width']=None
                    output.append(row)
    return output


def run_accounting(events,net,fixed_setting=None):
    cutoffs=CONFIG['development_cutoffs']+[CONFIG['validation_cutoff']]+CONFIG['final_cutoffs']
    all_snapshots={c:snapshots(events,net,c) for c in cutoffs}
    development=pd.concat([all_snapshots[c] for c in CONFIG['development_cutoffs']],ignore_index=True)
    validation=all_snapshots[CONFIG['validation_cutoff']]
    selection=validation_selection(validation.customer)&(validation.horizon==90).to_numpy()
    calibration=~validation_selection(validation.customer)
    tuning=[]
    if fixed_setting is None:
        for leaves in CONFIG['boosting_leaves']:
            candidate=HurdleBoosting(leaves).fit(development);p=candidate.predict(validation.loc[selection]);value=mean_poisson_deviance(validation.loc[selection,'future_count'],np.maximum(p['count'],1e-8));tuning.append({'leaves':leaves,'validation_90_day_deviance':value});print('validation',leaves,value,flush=True)
        setting=min(tuning,key=lambda x:(x['validation_90_day_deviance'],x['leaves']))['leaves']
    else:setting=fixed_setting
    calibrated_model=HurdleBoosting(setting).fit(development);cal=validation.loc[calibration].reset_index(drop=True);calp=calibrated_model.predict(cal);quantiles={}
    for horizon in CONFIG['horizons_days']:
        mask=(cal.horizon==horizon).to_numpy();quantiles[horizon]={}
        for target in ['count','spend']:
            center=calp[target][mask];scale=np.sqrt(center+1) if target=='count' else np.maximum(center,1)
            residual=np.abs(cal.loc[mask,'future_'+target].to_numpy(float)-center)/scale;quantiles[horizon][target]=interval_quantile(residual)
    finals=[];chunks={name:[] for name in LABELS};fit_info=[]
    for index,cutoff in enumerate(CONFIG['final_cutoffs']):
        train=permitted_training(all_snapshots,cutoff)
        test=all_snapshots[cutoff].reset_index(drop=True);past=history(events,cutoff)
        bg=BGNBD().fit(past);gg=GammaGamma().fit(past);bp=bg.predict(test,CONFIG['quadrature_nodes']);bp['spend_per_purchase']=gg.predict(test);bp['spend']=bp['count']*bp['spend_per_purchase']
        fine=bg.predict(test,128)['count']
        if not np.allclose(bp['count'],fine,rtol=1e-6,atol=1e-8):raise ValueError('Predictive quadrature failed convergence')
        bp.update(predictive_distribution(bg,gg,test,bp,CONFIG['seed']+index,CONFIG['predictive_draws']))
        boost=HurdleBoosting(setting).fit(train).predict(test);boost.update(empirical_bands(boost,test.horizon,quantiles))
        predictions={'recent_rule':recent_rule(test),'rfm_rule':RFMRule().fit(train).predict(test),'bgnbd':bp,'boosting':boost}
        repeat=past[past.frequency>0];pearson=pearsonr(repeat.frequency,repeat.repeat_mean_spend);spearman=spearmanr(repeat.frequency,repeat.repeat_mean_spend)
        fit_info.append({'cutoff':cutoff,'history_customers':len(past),'supervised_training_rows':len(train),'latest_label_end':str(train.label_end.max()),'bgnbd_parameters':dict(zip(['r','alpha_weeks','a','b'],bg.params)),'bgnbd_fit':bg.fit_info,'gamma_gamma_parameters':{'p':gg.params[0],'q':1+gg.params[1],'gamma_in_hundreds_gbp':gg.params[2]},'gamma_gamma_fit':gg.fit_info,'repeat_spend_customers':len(repeat),'frequency_spend_pearson':pearson.statistic,'frequency_spend_spearman':spearman.statistic,'quadrature_max_absolute_difference':np.max(np.abs(bp['count']-fine))})
        finals.append(test)
        for name,p in predictions.items():chunks[name].append(p)
        print('finished rolling cutoff',cutoff,'customers',len(past),flush=True)
    final=pd.concat(finals,ignore_index=True);predictions={name:{key:np.concatenate([p[key] for p in values]) for key in values[0]} for name,values in chunks.items()}
    primary=(final.horizon==90).to_numpy();metrics,delta=evaluate(final.loc[primary],subset_predictions(predictions,primary),CONFIG['seed'])
    windows=[]
    for cutoff in CONFIG['final_cutoffs']:
        for h in CONFIG['horizons_days']:
            mask=((final.cutoff==pd.Timestamp(cutoff))&(final.horizon==h)).to_numpy()
            for name,p in subset_predictions(predictions,mask).items():windows.append({'cutoff':cutoff,'horizon_days':h,'model':name,'observations':int(mask.sum()),'purchasers':int((final.loc[mask,'future_count']>0).sum()),'actual_purchase_days':int(final.loc[mask,'future_count'].sum()),'observed_gross_spend_gbp':final.loc[mask,'future_spend'].sum(),**score(final.loc[mask],p)})
    calibration_rows=[]
    for name,p in subset_predictions(predictions,primary).items():
        f=final.loc[primary].reset_index(drop=True)
        for j,ix in enumerate(np.array_split(np.argsort(p['count'],kind='stable'),10),1):calibration_rows.append({'model':name,'bin':j,'observations':len(ix),'observed_count':f.iloc[ix].future_count.mean(),'predicted_count':p['count'][ix].mean(),'observed_purchase_probability':(f.iloc[ix].future_count>0).mean(),'predicted_purchase_probability':p['purchase'][ix].mean(),'observed_spend_gbp':f.iloc[ix].future_spend.mean(),'predicted_spend_gbp':p['spend'][ix].mean()})
    net_rows=[]
    for name,p in subset_predictions(predictions,primary).items():
        signed=final.loc[primary,'future_net'].to_numpy(float);net_rows.append({'model':name,'target':'signed net spend; same gross-spend forecast, no net-target refit','observed_net_spend_gbp':signed.sum(),'predicted_gross_spend_gbp':p['spend'].sum(),'predicted_gross_to_observed_net_ratio':p['spend'].sum()/signed.sum(),'net_spend_mae_gbp':np.mean(np.abs(p['spend']-signed))})
    aggregate={'selected_leaves':setting,'tuning':tuning,'interval_calibration_quantiles':quantiles,'calibration_observations':int(calibration.sum()),'fit_information':fit_info,'metrics':metrics,'primary_difference':delta,'windows':windows,'cohort_profiles':cohort_profiles(final,predictions),'calibration':calibration_rows,'net_spend_sensitivity':net_rows,'gross_spend_tail':{'largest_customer_window_gbp':float(final.loc[primary,'future_spend'].max()),'top_one_percent_share':float(final.loc[primary,'future_spend'].nlargest(max(1,int(np.ceil(primary.sum()*.01)))).sum()/final.loc[primary,'future_spend'].sum())}}
    return final,predictions,aggregate


def main():
    prov=provenance('S03');primary,repeated,audit=ingest()
    with threadpool_limits(limits=2):
        final,predictions,tables=run_accounting(*primary)
        repeated_final,repeated_predictions,repeated_tables=run_accounting(*repeated,fixed_setting=tables['selected_leaves'])
    mask=(final.horizon==90).to_numpy();f=final.loc[mask]
    samples={'total':audit['positive_customers'],'source_rows':audit['raw_rows'],'source_purchase_days':audit['positive_purchase_days'],'test':len(f),'test_unique_customers':f.customer.nunique(),'test_purchase_days':int(f.future_count.sum()),'test_customer_windows_with_purchase':int((f.future_count>0).sum()),'final_windows':3,'all_horizon_observations':len(final)}
    result={'schema_version':'1.0','study_id':'S03','run_id':f"S03-{prov['code_version'][:8]}-{CONFIG['archive_sha256'][:8]}",**prov,'evaluated_on':CONFIG['evaluated_on'],
            'data':{'source_url':'https://archive.ics.uci.edu/dataset/502/online+retail+ii','release':'Online Retail II, official workbook retrieved September 29, 2026','sha256':CONFIG['archive_sha256'],'license':'CC BY 4.0','citation':'Chen, D. (2012). Online Retail II [Dataset]. UCI Machine Learning Repository. doi:10.24432/C5CG6D.','workbook_sha256':CONFIG['xlsx_sha256']},
            'target':{'label':'Positive purchase-day counts, probability of any future purchase and gross positive spend','estimand':'Future observed purchasing among identified customers with at least 30 days of prior history','prediction_cutoff':'History strictly before each March/June/September 2011 cutoff; supervised labels complete before each fit','horizon':'30, 60 and 90 days; primary 90 days','unit':'Customer-cutoff; repeated windows clustered by customer'},
            'cohort':'Three nonoverlapping final 90-day windows, beginning March 1, June 1 and September 1, 2011; first observed purchase need not be acquisition',
            'samples':samples,'models':[{'id':name,'label':label,'specification':f'Frozen {name}; purchase-day grain, completed-label rolling fits, no current-window outcome features. Hurdle leaves {tables["selected_leaves"]}. See protocol.'} for name,label in LABELS.items()],
            'metrics':tables['metrics'],'uncertainty':'1,000 paired customer-cluster bootstrap draws with all final windows retained per sampled customer; 95% percentile intervals condition on fitted models. BG/NBD predictive distributions use 2,000 draws/customer; 90% challenger residual bands use separate December calibration customers.',
            'assumptions':['First observed purchase approximates the start of the customer relationship; actual acquisition is unavailable.','BG/NBD latent activity is not observed churn; zero-repeat histories have model alive probability one.','Gamma-Gamma assumes stable customer spend and independence from purchasing frequency.','Contact cost and contribution margin are hypothetical; break-even assumes one incremental purchase occasion and does not measure campaign lift.'],
            'limitations':['Older single-retailer giftware and wholesale behavior may not transfer to a current consumer business.','Missing IDs, overlapping sheets, repeated line ambiguity and cancellations materially affect accounting.','Positive-purchase spend excludes returns and is not profit or net realized revenue.','Seasonality, refitting and customer dependence undermine guaranteed predictive interval coverage.','Only three primary final windows are observed; unseen future shocks and parameter uncertainty remain unresolved.','No randomized win-back intervention or observed permanent churn label is available.','Independent technical review is pending.'],
            'tables':{'audit':audit,**tables,'duplicate_accounting_sensitivity':{'definition':'Multiset union of source sheets, retaining maximum within-sheet row multiplicity; same selected model complexity, no retuning','source_purchase_days':len(repeated[0]),'source_positive_spend_gbp':repeated[0].spend.sum(),'metrics':repeated_tables['metrics'],'primary_difference':repeated_tables['primary_difference'],'fit_information':repeated_tables['fit_information']},'scenario_ranges':{'contact_cost_gbp':[0,5],'contribution_margin':[.1,.5],'default_contact_cost_gbp':1,'default_contribution_margin':.3}},
            'software':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__,'sklearn':sklearn.__version__,'seed':CONFIG['seed']}}
    validate_result(result);write_json(HERE/'results/result.json',result)
    private={col:final[col].to_numpy(dtype=str if col in ['customer','cutoff','inactivity_band','frequency_band'] else float) for col in ['customer','cutoff','inactivity_band','frequency_band','horizon','future_count','future_spend','future_net']}
    for name,p in predictions.items():
        for key,value in p.items():private[name+'_'+key]=value
    np.savez_compressed(data_dir('S03')/'verification.npz',**private)
    print(json.dumps({'run':result['run_id'],'samples':samples,'primary':tables['primary_difference'],'duplicate_sensitivity':repeated_tables['primary_difference']},indent=2),flush=True)


if __name__=='__main__':main()
