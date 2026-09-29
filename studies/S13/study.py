"""Run the frozen rare-failure screening comparison and aggregate exports."""
import json,platform,sys
from pathlib import Path
import numpy as np,pandas as pd,sklearn,scipy
from sklearn.metrics import average_precision_score,roc_auc_score,log_loss,brier_score_loss
from threadpoolctl import threadpool_limits
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from research_program.io import ROOT,data_dir,provenance,write_json
from research_program.validate import validate_result
from ingest import CONFIG,ingest,split_masks
from models import make_model,selected_sensors,cluster_draws,capacity_row
HERE=Path(__file__).resolve().parent
LABELS={'pca_monitor':'PCA process monitor','elastic_net':'Sparse elastic-net logistic','boosting':'Gradient boosting','boosting_no_missing':'Boosting without missingness indicators','prevalence':'Training failure prevalence'}
def measures(y,p):
 p=np.clip(p,1e-8,1-1e-8)
 return {'average_precision':average_precision_score(y,p),'roc_auc':roc_auc_score(y,p),'log_loss':log_loss(y,p,labels=[0,1]),'brier':brier_score_loss(y,p)}
def main():
 prov=provenance('S13');x,y,time=ingest();dev,val,test=split_masks(time);fit=dev|val
 if not (dev.sum(),val.sum(),test.sum(),y[dev].sum(),y[val].sum(),y[test].sum())==(618,590,359,65,17,22):raise ValueError('Calendar cohort changed')
 tune=[];settings={};models={};predictions={};fit_info={}
 with threadpool_limits(limits=2):
  for family,choices in CONFIG['candidates'].items():
   for setting in choices:
    model=make_model(family,setting).fit(x[dev],y[dev]);p=model.predict_proba(x[val])[:,1];m=measures(y[val],p);tune.append({'model':family,'setting':setting,**m});print('validation',family,setting,m,flush=True)
   settings[family]=min((r for r in tune if r['model']==family),key=lambda r:(r['log_loss'],r['setting']))['setting']
   models[family]=make_model(family,settings[family]).fit(x[fit],y[fit])
  models['boosting_no_missing']=make_model('boosting',settings['boosting'],False).fit(x[fit],y[fit])
  for name,model in models.items():
   predictions[name]=model.predict_proba(x[test])[:,1]
   pre=model.pre if name=='pca_monitor' else model.named_steps['pre']
   fit_info[name]={'retained_sensor_columns':len(pre.columns_),'transformed_features':len(pre.names_)}
   if name=='elastic_net':fit_info[name].update(nonzero_coefficients=int((np.abs(model.named_steps['model'].coef_[0])>1e-6).sum()),selected_sensors=len(selected_sensors(model)),iterations=int(model.named_steps['model'].n_iter_.max()))
  predictions['prevalence']=np.full(test.sum(),y[fit].mean())
  days=time[test].dt.strftime('%Y-%m-%d').to_numpy();yt=y[test];scores={name:measures(yt,p) for name,p in predictions.items()};boot={name:{m:[] for m in scores[name]} for name in scores};paired=[];skipped=0
  for ix in cluster_draws(days,CONFIG['bootstrap_repetitions'],CONFIG['seed']):
   if len(np.unique(yt[ix]))<2:skipped+=1;continue
   for name,p in predictions.items():
    for m,v in measures(yt[ix],p[ix]).items():boot[name][m].append(v)
   paired.append(boot['boosting']['average_precision'][-1]-boot['elastic_net']['average_precision'][-1])
  sensitivity=[]
  for ix in cluster_draws(days,CONFIG['bootstrap_repetitions'],CONFIG['seed']+1,2):
   if len(np.unique(yt[ix]))<2:continue
   sensitivity.append(average_precision_score(yt[ix],predictions['boosting'][ix])-average_precision_score(yt[ix],predictions['elastic_net'][ix]))
  metrics=[]
  for name,ms in scores.items():
   for metric,value in ms.items():
    low,high=np.quantile(boot[name][metric],[.025,.975]);metrics.append({'model':name,'name':metric,'estimate':value,'unit':'natural-log units' if metric=='log_loss' else 'proportion','split':'final','lower':low,'upper':high,'confidence':.95})
  frontier=[{'model':name,**capacity_row(yt,p,c)} for name,p in predictions.items() if name!='prevalence' for c in CONFIG['capacities']]
  cal=[];diagnostics=[]
  for name,p in predictions.items():
   for j,ix in enumerate(np.array_split(np.argsort(p,kind='stable'),5)):
    cal.append({'model':name,'bin':j+1,'entities':len(ix),'failures':int(yt[ix].sum()),'mean_probability':p[ix].mean(),'observed_failure_rate':yt[ix].mean()})
   for day in np.unique(days):
    mask=days==day;diagnostics.append({'model':name,'grouping':'test_day','group':day,'entities':int(mask.sum()),'failures':int(yt[mask].sum()),'mean_probability':p[mask].mean(),'brier':np.mean((p[mask]-yt[mask])**2)})
   for label,mask in [('At most 5% sensors missing',np.isnan(x[test]).mean(axis=1)<=.05),('More than 5% sensors missing',np.isnan(x[test]).mean(axis=1)>.05)]:
    if mask.any():diagnostics.append({'model':name,'grouping':'missingness','group':label,'entities':int(mask.sum()),'failures':int(yt[mask].sum()),'mean_probability':p[mask].mean(),'brier':np.mean((p[mask]-yt[mask])**2)})
  baseline_set=selected_sensors(models['elastic_net']);selected_counts={};available_counts={};stability_runs=[]
  fitdays=time[fit].dt.strftime('%Y-%m-%d').to_numpy()
  for run,ix in enumerate(cluster_draws(fitdays,CONFIG['stability_repetitions'],CONFIG['seed']+2)):
   model=make_model('elastic_net',settings['elastic_net']).fit(x[fit][ix],y[fit][ix]);chosen=selected_sensors(model);available={n[:10] for n in model.named_steps['pre'].names_}
   for n in chosen:selected_counts[n]=selected_counts.get(n,0)+1
   for n in available:available_counts[n]=available_counts.get(n,0)+1
   union=chosen|baseline_set;stability_runs.append({'replicate':run+1,'selected_sensors':len(chosen),'available_sensors':len(available),'jaccard_to_final':len(chosen&baseline_set)/len(union) if union else 1.,'iterations':int(model.named_steps['model'].n_iter_.max())})
   print('stability',run+1,'selected',len(chosen),flush=True)
  names=models['elastic_net'].named_steps['pre'].names_;coefs=models['elastic_net'].named_steps['model'].coef_[0]
  stability=[]
  for sensor in sorted(available_counts):
   values={n:float(c) for n,c in zip(names,coefs) if n[:10]==sensor}
   stability.append({'sensor':sensor,'selection_frequency':selected_counts.get(sensor,0)/CONFIG['stability_repetitions'],'availability_frequency':available_counts[sensor]/CONFIG['stability_repetitions'],'selected_in_final':sensor in baseline_set,'standardized_measurement_coefficient':values.get(sensor,0.),'standardized_missingness_coefficient':values.get(sensor+'_missing',0.)})
  stability.sort(key=lambda r:(-r['selection_frequency'],r['sensor']))
 months=[{'month':str(m),'entities':int((time.dt.to_period('M')==m).sum()),'failures':int(y[time.dt.to_period('M')==m].sum())} for m in time.dt.to_period('M').unique()]
 low,high=np.quantile(paired,[.025,.975]);sl,sh=np.quantile(sensitivity,[.025,.975])
 audit={'actual_sensor_columns':x.shape[1],'documented_sensor_columns':591,'missing_cells':int(np.isnan(x).sum()),'constant_columns':int((pd.DataFrame(x).nunique()<=1).sum()),'duplicate_columns':int(pd.DataFrame(x).T.duplicated().sum()),'duplicate_sensor_rows':int(pd.DataFrame(x).duplicated().sum()),'duplicate_timestamps':int(time.duplicated().sum()),'columns_over_half_missing':int((np.isnan(x).mean(axis=0)>.5).sum()),'months':months,'source_timestamp_min':str(time.min()),'source_timestamp_max':str(time.max())}
 result={'schema_version':'1.0','study_id':'S13','run_id':f"S13-{prov['code_version'][:8]}-{CONFIG['archive_sha256'][:8]}",**prov,'evaluated_on':CONFIG['evaluated_on'],
 'data':{'source_url':'https://archive.ics.uci.edu/dataset/179/secom','release':'SECOM original files; retrieved September 29, 2026','sha256':CONFIG['archive_sha256'],'license':'CC BY 4.0','citation':'McCann, M. & Johnston, A. (2008). SECOM [Dataset]. UCI Machine Learning Repository. doi:10.24432/C54305.','file_sha256':CONFIG['files']},
 'target':{'label':'Publisher +1 failure versus −1 pass','estimand':'Retrospective failure screening, conditional on availability of recorded sensor measurements','prediction_cutoff':'At an assumed screening point with recorded sensor measurements; pre-test acquisition times are not independently documented','horizon':'Associated in-house quality test; no verified advance-warning horizon','unit':'One production entity/source row'},
 'cohort':'October 1–17, 2008 final entities, following July–August development and September validation; original calendar retained',
 'samples':{'total':len(y),'total_failures':int(y.sum()),'development':int(dev.sum()),'development_failures':int(y[dev].sum()),'validation':int(val.sum()),'validation_failures':int(y[val].sum()),'final_fit':int(fit.sum()),'final_fit_failures':int(y[fit].sum()),'test':int(test.sum()),'test_failures':int(yt.sum()),'test_days':len(np.unique(days))},
 'models':[{'id':name,'label':LABELS[name],'specification':('Constant final-training prevalence' if name=='prevalence' else f"Frozen {name}; selected setting {settings.get(name,settings['boosting'])}; training-only preprocessing. See protocol." )} for name in predictions],
 'metrics':metrics,'uncertainty':'1,000 paired calendar-day cluster bootstrap draws; 95% percentile intervals condition on the fitted models and 17 observed test days. Two-day circular-block sensitivity is supplementary. Sensor stability uses 30 training-day bootstrap refits.',
 'assumptions':['Recorded sensors are hypothetically available at screening; the source cannot verify their exact pre-test acquisition timing.','Capacity selects the top-scored entities across the complete final batch, not a daily production schedule.','Calendar days proxy dependence; unobserved wafer/lot groups cannot be reconstructed.'],
 'limitations':['Only 22 final failures and 17 final days support limited precision.','Anonymous sensors and missing acquisition times prevent root-cause and validated early-warning claims.','A short historical sample with changing prevalence does not validate a modern production line.','Intervals condition on fitted models and cannot account for unrecorded batch dependence.','Selection stability is descriptive and does not establish causal or physical sensor importance.','Inspection counts are historical ranking outcomes, not measured savings or avoided failures.','Independent technical review is pending.'],
 'tables':{'audit':audit,'tuning':tune,'selected_settings':settings,'fit_information':fit_info,'primary_difference':{'metric':'average_precision','comparison':'boosting minus elastic_net','estimate':scores['boosting']['average_precision']-scores['elastic_net']['average_precision'],'lower':low,'upper':high,'valid_draws':len(paired),'skipped_draws':skipped},'block_sensitivity':{'block_days':2,'lower':sl,'upper':sh,'valid_draws':len(sensitivity)},'capacity':frontier,'calibration':cal,'diagnostics':diagnostics,'sensor_stability':stability,'stability_runs':stability_runs},
 'software':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__,'sklearn':sklearn.__version__,'seed':CONFIG['seed']}}
 validate_result(result);write_json(HERE/'results/result.json',result)
 np.savez_compressed(data_dir('S13')/'verification.npz',y=yt,days=days,**predictions)
 print(json.dumps({'run':result['run_id'],'scores':scores,'primary':result['tables']['primary_difference'],'selected_settings':settings,'fit':fit_info},indent=2),flush=True)
if __name__=='__main__':main()
