"""Execute grouped telecom risk comparisons and prospective experiment scenarios."""
import json
import platform
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import sklearn
from sklearn.metrics import log_loss,brier_score_loss,average_precision_score,roc_auc_score
from threadpoolctl import threadpool_limits
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from research_program.io import provenance,write_json,data_dir
from research_program.validate import validate_result
from studies.S47.ingest import CONFIG,NUMERIC,VARIANTS,ingest
from studies.S47.models import make_model,select,nested,CalibrationMap,ComplaintUsageRule,capacity,sample_size,contrasts

HERE=Path(__file__).resolve().parent
LABELS={'prevalence':'Development prevalence','service_rule':'Complaint / low-usage rule','linear':'Ridge logistic','additive':'Additive logistic','boosting':'Histogram boosting'}


def scores(y,p,weights=None):
    p=np.clip(p,1e-8,1-1e-8)
    return {'log_loss':log_loss(y,p,sample_weight=weights),'brier':brier_score_loss(y,p,sample_weight=weights),'average_precision':average_precision_score(y,p,sample_weight=weights),'roc_auc':roc_auc_score(y,p,sample_weight=weights),'predicted_observed_churn_ratio':np.average(p,weights=weights)/np.average(y,weights=weights)}


def group_draws(groups,repetitions,seed):
    unique=np.unique(groups);indices=[np.flatnonzero(groups==g) for g in unique];rng=np.random.default_rng(seed)
    for _ in range(repetitions):yield np.concatenate([indices[i] for i in rng.integers(len(unique),size=len(unique))])


def evaluate(y,groups,keys,predictions):
    rows=[];curves=[];samples={};recalls={}
    for model,p in predictions.items():
        samples[model]={k:[] for k in scores(y,p)};recalls[model]=[]
    for ix in group_draws(groups,CONFIG['bootstrap_repetitions'],CONFIG['seed']+30):
        for model,p in predictions.items():
            for name,value in scores(y[ix],p[ix]).items():samples[model][name].append(value)
            order=np.lexsort((keys[ix],-p[ix]));cumulative=np.r_[0,np.cumsum(y[ix][order])];k=np.floor(len(ix)*np.array(CONFIG['capacities'])).astype(int);recalls[model].append(cumulative[k]/y[ix].sum())
    for model,p in predictions.items():
        for name,estimate in scores(y,p).items():
            low,high=np.quantile(samples[model][name],[.025,.975]);rows.append({'model':model,'name':name,'estimate':estimate,'lower':low,'upper':high,'confidence':.95,'unit':'natural-log units' if name=='log_loss' else 'ratio' if name.endswith('ratio') else 'proportion','split':'final'})
        lo,hi=np.quantile(recalls[model],[.025,.975],axis=0)
        for j,c in enumerate(CONFIG['capacities']):curves.append({'model':model,**capacity(y,p,keys,c),'recall_lower':lo[j],'recall_upper':hi[j]})
    a=np.array(samples['core/boosting']['log_loss']);b=np.array(samples['core/additive']['log_loss']);low,high=np.quantile(a-b,[.025,.975]);delta={'comparison':'core boosting minus core additive','metric':'log_loss','estimate':scores(y,predictions['core/boosting'])['log_loss']-scores(y,predictions['core/additive'])['log_loss'],'lower':low,'upper':high,'draws':CONFIG['bootstrap_repetitions']}
    variants=[]
    for v in VARIANTS[1:]:
        difference=np.array(samples[v+'/boosting']['log_loss'])-a;low,high=np.quantile(difference,[.025,.975]);variants.append({'variant':v,'comparison':'variant boosting minus core boosting','estimate':scores(y,predictions[v+'/boosting'])['log_loss']-scores(y,predictions['core/boosting'])['log_loss'],'lower':low,'upper':high})
    return rows,curves,delta,variants


def calibration_tables(y,groups,predictions):
    rows=[]
    for model,p in predictions.items():
        for j,ix in enumerate(np.array_split(np.argsort(p,kind='stable'),10),1):
            rates=[np.mean(y[ix][draw]) for draw in group_draws(groups[ix],CONFIG['bootstrap_repetitions'],CONFIG['seed']+40+j)];low,high=np.quantile(rates,[.025,.975]);rows.append({'model':model,'bin':j,'rows':len(ix),'profiles':len(np.unique(groups[ix])),'events':int(y[ix].sum()),'predicted':p[ix].mean(),'observed':y[ix].mean(),'observed_lower':low,'observed_upper':high})
    return rows


def effects(frame,y,groups,setting,model,calibrator):
    references=[('Complains',0.,1.)]+[(c,float(frame[c].quantile(.25)),float(frame[c].quantile(.75))) for c in NUMERIC]
    point=contrasts(model,calibrator,frame,references);draws=[]
    for iteration,ix in enumerate(group_draws(groups,CONFIG['effect_bootstraps'],CONFIG['seed']+50)):
        m=make_model('additive',setting,'core').fit(frame.iloc[ix],y[ix]);draws.append(contrasts(m,calibrator,frame,references))
        if (iteration+1)%25==0:print('effect bootstrap',iteration+1,flush=True)
    draws=np.array(draws);low,high=np.quantile(draws,[.025,.975],axis=0)
    return [{'feature':f,'low_value':lo,'high_value':hi,'risk_difference':point[j],'lower':low[j],'upper':high[j],'positive_fraction':np.mean(draws[:,j]>0),'replicates':len(draws),'reference_rows':len(frame)} for j,(f,lo,hi) in enumerate(references)]


def main():
    prov=provenance('S47');f,folds,groups,keys,sizes,audit=ingest();dev=folds>=2;cal=folds==1;test=folds==0;train=f.loc[dev].reset_index(drop=True);c=f.loc[cal].reset_index(drop=True);final=f.loc[test].reset_index(drop=True);y=train.Churn.to_numpy(int);yc=c.Churn.to_numpy(int);yt=final.Churn.to_numpy(int);gd=groups[dev];gt=groups[test];predictions={};raw=[];fits=[];core_models={};core_calibrators={};nested_results={}
    with threadpool_limits(limits=2):
        for family in ['additive','boosting']:
            nested_results[family]=nested(train,y,gd,family);print('nested',family,nested_results[family],flush=True)
        for variant in VARIANTS:
            for family in ['additive','boosting']+(['linear'] if variant=='core' else []):
                setting,tuning=select(train,y,gd,family,variant,CONFIG['seed']+20);model=make_model(family,setting,variant).fit(train,y);calibrator=CalibrationMap().fit(model.predict_proba(c)[:,1],yc);p=model.predict_proba(final)[:,1];name=variant+'/'+family;predictions[name]=calibrator.predict(p);raw.append({'model':name,**scores(yt,p)});fits.append({'variant':variant,'family':family,'setting':setting,'tuning':tuning,'calibration_intercept':float(calibrator.model.intercept_[0]),'calibration_slope':float(calibrator.model.coef_[0,0])});print('fit',name,'setting',setting,flush=True)
                if variant=='core':core_models[family]=model;core_calibrators[family]=calibrator
        predictions['core/prevalence']=np.full(len(yt),y.mean());rule=ComplaintUsageRule().fit(train,y);predictions['core/service_rule']=rule.predict(final)
        metrics,curves,difference,variant_comparisons=evaluate(yt,gt,keys[test],predictions)
        calibration=calibration_tables(yt,gt,predictions)
        setting=next(x['setting'] for x in fits if x['variant']=='core' and x['family']=='additive');effect_rows=effects(train,y,gd,setting,core_models['additive'],core_calibrators['additive'])
    segments=[];suppressed=[]
    for feature in ['Age Group','Tariff Plan']:
        for value in sorted(final[feature].unique()):
            mask=(final[feature]==value).to_numpy();events=int(yt[mask].sum())
            if mask.sum()<CONFIG['minimum_segment_rows'] or min(events,mask.sum()-events)<CONFIG['minimum_segment_events']:suppressed.append({'feature':feature,'value':int(value),'reason':'Fewer than 30 rows or five events in either class'});continue
            for name,p in predictions.items():
                if not name.startswith('core/'):continue
                segments.append({'feature':feature,'value':int(value),'model':name,'rows':int(mask.sum()),'profiles':len(np.unique(gt[mask])),'events':events,'observed':yt[mask].mean(),'predicted':p[mask].mean(),**scores(yt[mask],p[mask])})
    reweighted=[{'model':name,**scores(yt,p,1/sizes[test])} for name,p in predictions.items() if name.startswith('core/')]
    samples={'total':len(f),'test':len(final),'test_profiles':audit['partitions']['test']['profiles'],'test_churn':int(yt.sum()),'development':len(train),'development_churn':int(y.sum()),'calibration':len(c),'calibration_churn':int(yc.sum())}
    result={'schema_version':'1.0','study_id':'S47','run_id':f"S47-{prov['code_version'][:8]}-{CONFIG['archive_sha256'][:8]}",**prov,'evaluated_on':CONFIG['evaluated_on'],'data':{'source_url':'https://archive.ics.uci.edu/dataset/563/iranian+churn+dataset','release':'Official UCI Iranian Churn CSV retrieved September 29, 2026','sha256':CONFIG['archive_sha256'],'csv_sha256':CONFIG['csv_sha256'],'license':'CC BY 4.0','citation':'Iranian Churn (2020). UCI Machine Learning Repository. doi:10.24432/C5JW3Z.'},'target':{'label':'Churn at the end of month twelve','estimand':'Historical row-level risk among the sampled telecom profiles','prediction_cutoff':'Publisher-described first-nine-month aggregate features; source timestamps unavailable','horizon':'Three-month documented planning gap','unit':'Source row, with identical primary-feature profiles grouped across every split'},'cohort':'Fixed grouped stratified final partition; no out-of-time or verified individual-customer validation','samples':samples,'models':[{'id':name,'label':LABELS[name.split('/')[1]]+' · '+name.split('/')[0],'specification':'Frozen group-separated model, variant-specific selection and reserved probability calibration; see PROTOCOL.md.'} for name in predictions],'metrics':metrics,'uncertainty':'1,000 paired primary-profile bootstrap draws; 95% percentile intervals condition on the fitted model. Capacity ranking is recomputed per draw. Additive effect stability refits 100 profile-bootstrap development samples using a fixed calibration map.','assumptions':['Publisher timing places predictors before the three-month planning gap; no timestamps independently establish this.','Identical primary profiles are kept together as a conservative dependence proxy; actual identities are absent.','Prospective sample-size controls are assumptions for an unrun randomized trial, not estimated campaign effects.'],'limitations':['Small single-company sample with unspecified collection year and no temporal replication.','No actual customer ID; repetitions and conflicting identical profiles prevent verified customer independence.','Status and calculated customer value have insufficiently documented semantics; their sensitivity gains do not prove operational availability.','Age is a category representative, and charge amount includes seven values beyond the dictionary range.','Associations and model-risk contrasts do not identify benefits from resolving complaints or changing usage.','Sparse contractual churn and correlated features limit subgroup and effect interpretation.','Independent technical review is pending.'],'tables':{'audit':audit,'nested_development':nested_results,'fits':fits,'raw_probability_metrics':raw,'primary_difference':difference,'variant_comparisons':variant_comparisons,'capacity':curves,'calibration':calibration,'effects':effect_rows,'segments':segments,'suppressed_segments':suppressed,'equal_profile_weight_sensitivity':reweighted,'rule':{'low_usage_training_median_seconds':rule.median,'prior':rule.prior,'pseudo_observations':20},'experiment_default':sample_size(.15,.03),'experiment_grid':[sample_size(p,d) for p in [.05,.1,.15,.2,.3,.4] for d in [.01,.02,.03,.05,.1] if d<p]},'software':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'sklearn':sklearn.__version__,'seed':CONFIG['seed']}}
    validate_result(result);write_json(HERE/'results/result.json',result)
    private={'y':yt,'group':gt,'key':keys[test],'profile_size':sizes[test],'age_group':final['Age Group'].to_numpy(),'tariff':final['Tariff Plan'].to_numpy()};private.update({name.replace('/','_'):p for name,p in predictions.items()});np.savez_compressed(data_dir('S47')/'verification.npz',**private)
    print(json.dumps({'run':result['run_id'],'samples':samples,'primary':difference},indent=2),flush=True)


if __name__=='__main__':main()
