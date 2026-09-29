"""Application-separated remaining-time evaluation and explicit capacity arithmetic."""
from pathlib import Path
import sys,json,platform
from collections import defaultdict
import numpy as np,pandas as pd,scipy,sklearn
from threadpoolctl import threadpool_limits
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from research_program.io import provenance,write_json,data_dir
from research_program.evaluation import interval,ranked_selection
from research_program.validate import validate_result
from ingest import ingest,CONFIG,HERE
from survival import baseline_survival,fit_hazard,summarize_survival
NAMES={'pooled_km':'Pooled survival baseline','stage_age_km':'Current stage and age baseline','hazard_boosting':'Workflow hazard boosting','reduced_hazard':'Age and current stage only'}


def weighted(values,weight):return float(np.average(values,weights=weight))


def metric_arrays(truth,summary):
    return {'restricted_mae_days':np.abs(summary['mean']-truth),'brier_14':(summary['late_14']-(truth>14))**2,'coverage_80':((truth>=summary['lower'])&(truth<=summary['upper'])).astype(float)}


def main():
    version=provenance('S58');cohorts,audit=ingest();train=cohorts['development'];val=cohorts['validation'];final_train=cohorts['final_training'];test=cohorts['test'];print('Cohorts', {k:len(v) for k,v in cohorts.items()},flush=True)
    tuning=[]
    for leaves in CONFIG['candidate_leaves']:
        s,info=fit_hazard(train,val,leaves,CONFIG['seed']);summary=summarize_survival(s);mae=weighted(np.abs(summary['mean']-val.restricted_days.to_numpy()),val.weight.to_numpy());tuning.append({'leaves':leaves,'validation_mae_days':mae,'risk_rows':info['risk_rows']});print('Tuning',leaves,mae,flush=True)
    chosen=min(tuning,key=lambda row:row['validation_mae_days'])['leaves']
    curves={'pooled_km':baseline_survival(final_train,test),'stage_age_km':baseline_survival(final_train,test,stage=True)};specs={name:{'family':'discrete Kaplan–Meier','stage_and_age':name=='stage_age_km','horizon_days':30} for name in curves}
    for name,reduced in [('hazard_boosting',False),('reduced_hazard',True)]:
        curves[name],specs[name]=fit_hazard(final_train,test,chosen,CONFIG['seed'],reduced);print('Fitted',name,flush=True)
    summaries={name:summarize_survival(s) for name,s in curves.items()};truth=test.restricted_days.to_numpy();weight=test.weight.to_numpy();arrays={name:metric_arrays(truth,s) for name,s in summaries.items()}
    applications=test.application.unique();groups=[np.flatnonzero(test.application.to_numpy()==a) for a in applications];rng=np.random.default_rng(CONFIG['seed']);draws=[np.concatenate([groups[i] for i in rng.integers(0,len(groups),len(groups))]) for _ in range(CONFIG['bootstrap_repetitions'])]
    metrics=[];bootstrap={}
    for name in NAMES:
        bootstrap[name]={}
        for metric,values in arrays[name].items():
            scores=[weighted(values[idx],weight[idx]) for idx in draws];bootstrap[name][metric]=scores
            metrics.append({'name':metric,'model':name,'estimate':weighted(values,weight),'unit':'days' if metric=='restricted_mae_days' else 'fraction','split':'December applications, prefixes before January 1',**interval(scores)})
    difference={'comparison':'hazard_boosting minus stage_age_km','estimate':weighted(arrays['hazard_boosting']['restricted_mae_days']-arrays['stage_age_km']['restricted_mae_days'],weight),**interval(np.asarray(bootstrap['hazard_boosting']['restricted_mae_days'])-np.asarray(bootstrap['stage_age_km']['restricted_mae_days']))}
    diagnostics=[];calibration=[];frontier=[]
    for name,summary in summaries.items():
        for prefix in [0,*CONFIG['prefix_lengths']]:
            for stage in ['all',*sorted(test.stage.unique())]:
                mask=((test.prefix==prefix) if prefix else np.ones(len(test),bool))&((test.stage==stage) if stage!='all' else np.ones(len(test),bool));idx=np.flatnonzero(mask)
                if len(idx)<30:continue
                diagnostics.append({'model':name,'prefix':prefix,'stage':stage,'prefixes':len(idx),'applications':int(test.iloc[idx].application.nunique()),'mean_observed_restricted_days':weighted(truth[idx],weight[idx]),'mean_predicted_restricted_days':weighted(summary['mean'][idx],weight[idx]),'mean_lower_days':weighted(summary['lower'][idx],weight[idx]),'mean_upper_days':weighted(summary['upper'][idx],weight[idx]),'mae_days':weighted(arrays[name]['restricted_mae_days'][idx],weight[idx]),'brier_14':weighted(arrays[name]['brier_14'][idx],weight[idx]),'late_rate':weighted((truth[idx]>14),weight[idx]),'coverage_80':weighted(arrays[name]['coverage_80'][idx],weight[idx])})
        bins=np.minimum((summary['late_14']*10).astype(int),9)
        for b in np.unique(bins):
            idx=np.flatnonzero(bins==b);calibration.append({'model':name,'bin':int(b),'prefixes':len(idx),'prediction':weighted(summary['late_14'][idx],weight[idx]),'observed':weighted(truth[idx]>14,weight[idx])})
        for prefix in CONFIG['prefix_lengths']:
            idx=np.flatnonzero(test.prefix.to_numpy()==prefix);actual=truth[idx]>14;score=summary['late_14'][idx];boot_rng=np.random.default_rng(CONFIG['seed']+prefix)
            # One prefix of this length per application makes rows distinct application units.
            resamples=boot_rng.integers(0,len(idx),size=(CONFIG['bootstrap_repetitions'],len(idx)))
            for capacity in CONFIG['capacities']:
                selection=ranked_selection(score,capacity);hits=selection&actual
                denominator=actual[resamples].sum(axis=1);valid=denominator>0;captures=hits[resamples].sum(axis=1)[valid]/denominator[valid]
                frontier.append({'model':name,'prefix':prefix,'capacity':capacity,'applications':len(idx),'selected':int(selection.sum()),'late_applications':int(actual.sum()),'late_selected':int(hits.sum()),'capture':float(hits.sum()/actual.sum()) if actual.any() else None,'capture_interval':interval(captures) if len(captures) else None})
    edges=defaultdict(list)
    for row in test.sort_values('prefix').drop_duplicates('application',keep='last').itertuples():
        for edge in row.transitions:edges[edge['from'],edge['to']].append(edge['elapsed_days'])
    transitions=[{'from':a,'to':b,'observations':len(values),'median_elapsed_days':float(np.median(values)),'p90_elapsed_days':float(np.quantile(values,.9))} for (a,b),values in edges.items() if len(values)>=30]
    transitions.sort(key=lambda row:row['observations'],reverse=True)
    data={'source_url':'https://figshare.com/articles/dataset/BPI_Challenge_2017/12696884','release':'Original BPI Challenge 2017 XES; events through 2017-02-01T14:11:03.499Z','sha256':CONFIG['sha256'],'license':'4TU General Terms of Use (2016): noncommercial reuse, source citation and bibliographic publication notification.','citation':'van Dongen, B. (2017): BPI Challenge 2017. Eindhoven University of Technology / 4TU.ResearchData. https://doi.org/10.4121/uuid:5f3067df-f10b-45da-b98b-86ae4c7a310b','coverage':'31,509 applications opened in 2016; 1,202,267 events through February 1, 2017.'}
    result={'schema_version':'1.0','study_id':'S58','run_id':'S58-'+version['code_version'][:8]+'-'+CONFIG['sha256'][:8],**version,'evaluated_on':CONFIG['evaluated_on'],'data':data,'target':{'label':'Restricted remaining time to first recorded Pending/Denied/Cancelled application status','estimand':'Expected remaining discrete days capped at 30, among applications still active at the selected event prefix','prediction_cutoff':'Only first 5,10 or20 application events; all related offers remain in the application split','horizon':'30 days with daily intervals; complete final-horizon ascertainment','unit':'Application; multiple event prefixes remain clustered'},'cohort':'December2016 application arrivals; eligible prefixes observed before January1,2017. Later source events are outcomes only.','samples':{'total':CONFIG['applications'],'train':int(final_train.application.nunique()),'test':int(test.application.nunique()),'test_prefixes':len(test),'validation':int(val.application.nunique()),'events':{'test_late_prefixes':int((truth>14).sum()),'test_observed_status_prefixes':int(test.event_observed.sum())}},'models':[{'id':name,'label':label,'specification':specs[name]} for name,label in NAMES.items()],'metrics':metrics,'uncertainty':'500 paired application-cluster bootstrap draws retain all evaluated prefixes of each application. Conditional on fitted models and one institutional/time cohort; no retraining uncertainty.','assumptions':['The first Pending/Denied/Cancelled status is a defined workflow endpoint, not confirmed disbursement.','All final prefixes have at least30-day outcome ascertainment; longer times remain capped.','Lifecycle events are retained and elapsed gaps are not active service measurements.','Capacity changes are explicit proportional scenarios, not identified staffing effects.'],'limitations':['One institution and one final arrival month; temporal generalization is not established.','Early prefixes may omit later loops; unavailable prefixes and already-dispositioned cases are excluded with counts.','All predictions and bands refer to a30-day restricted endpoint, not unrestricted remaining duration.','Repeated prefixes are dependent and treated as application clusters.','No resource-efficiency, causal automation, financial-saving or lending-decision claim is made.','Independent technical review is pending.'],'tables':{'audit':audit,'tuning':tuning,'selected_leaves':chosen,'primary_difference':difference,'diagnostics':diagnostics,'calibration':calibration,'late_frontier':frontier,'workflow_transitions':transitions,'transition_scope':'Consecutive application-stage events within the longest eligible final prefix per application; edges with fewer than30 occurrences omitted.','capacity_scenario':{'formula':'restricted_days * ((1 - addressable_share) + addressable_share / capacity_multiplier)','addressable_share_range':[0,1],'capacity_multiplier_range':[.5,2],'unit':'hypothetical remaining days under proportional-time assumptions','interpretation':'Scenario arithmetic, not a causal queueing/staffing estimate.'}},'software':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__,'scikit-learn':sklearn.__version__}}
    validate_result(result);write_json(HERE/'results/result.json',result)
    np.savez_compressed(data_dir('S58')/'verification.npz',truth=truth,weight=weight,application=test.application.to_numpy(),prefix=test.prefix.to_numpy(),**{name:curve for name,curve in curves.items()})
    print(json.dumps({'run_id':result['run_id'],'primary_difference':difference}),flush=True)


if __name__=='__main__':
    with threadpool_limits(limits=2):main()
