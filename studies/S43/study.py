"""Forward-sale evaluation, spatial transfer and honest local interval coverage."""
from pathlib import Path
import sys,json,hashlib,platform
import numpy as np,pandas as pd,sklearn
from threadpoolctl import threadpool_limits
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from research_program.io import provenance,write_json,data_dir
from research_program.evaluation import interval
from research_program.validate import validate_result
from ingest import ingest,CONFIG,HERE
from models import fit_local,fit_hedonic,fit_boosting,metrics,radius
NAMES={'local_median':'Local training-sale median','hedonic':'Regularized hedonic regression','spatial_boosting':'Spatial gradient boosting','physical_boosting':'Physical attributes only'}

def evaluate():
 version=provenance('S43');cohorts,audit=ingest();train=cohorts['train'];cal=cohorts['calibration'];test=cohorts['test'];y=test.sale_price.to_numpy(float);tuning=[]
 for leaves in CONFIG['candidate_leaves']:
  f=fit_boosting(cohorts['development'],leaves);score=metrics(cohorts['validation'].sale_price.to_numpy(),f(cohorts['validation']))['median_ape_pct'];tuning.append({'leaves':leaves,'validation_median_ape_pct':score});print('Validation',leaves,score,flush=True)
 chosen=min(tuning,key=lambda x:x['validation_median_ape_pct'])['leaves'];fitted={'local_median':fit_local(train),'hedonic':fit_hedonic(train),'spatial_boosting':fit_boosting(train,chosen),'physical_boosting':fit_boosting(train,chosen,True)};predictions={name:f(test) for name,f in fitted.items()};residuals={name:np.abs(np.log(cal.sale_price.to_numpy())-f(cal)) for name,f in fitted.items()};radii={name:{coverage:radius(values,coverage) for coverage in CONFIG['confidence_levels']} for name,values in residuals.items()}
 print('Final comparisons fitted',len(train),len(cal),len(test),flush=True)
 grid=test.grid.to_numpy();groups=[np.flatnonzero(grid==g) for g in sorted(set(grid))];rng=np.random.default_rng(CONFIG['seed']);draws=[np.concatenate([groups[i] for i in rng.integers(0,len(groups),len(groups))]) for _ in range(CONFIG['bootstrap_repetitions'])];measures=[];boot={};unit={'median_ape_pct':'percent','log_rmse':'log USD','median_absolute_error_USD':'USD','median_price_ratio':'ratio'}
 for name,p in predictions.items():
  point=metrics(y,p);boot[name]=np.array([metrics(y[idx],p[idx])['median_ape_pct'] for idx in draws])
  for metric,value in point.items():
   scores=boot[name] if metric=='median_ape_pct' else np.array([metrics(y[idx],p[idx])[metric] for idx in draws]);measures.append({'name':metric,'model':name,'estimate':value,'unit':unit[metric],'split':'April–December2025 sales',**interval(scores)})
 primary={'comparison':'spatial_boosting minus hedonic','estimate':metrics(y,predictions['spatial_boosting'])['median_ape_pct']-metrics(y,predictions['hedonic'])['median_ape_pct'],'unit':'percentage points',**interval(boot['spatial_boosting']-boot['hedonic'])}
 coverage_rows=[];diagnostics=[]
 for name,p in predictions.items():
  for confidence,rad in radii[name].items():
   covered=np.abs(np.log(y)-p)<=rad;lower=np.exp(p-rad);upper=np.exp(p+rad);boot_coverage=np.array([covered[idx].mean() for idx in draws]);coverage_rows.append({'model':name,'nominal':confidence,'coverage':float(covered.mean()),'coverage_interval':interval(boot_coverage),'median_width_USD':float(np.median(upper-lower)),'log_radius':rad,'calibration_parcels':len(cal)})
  for grouping in ['meta_township_name','size_profile','value_tier']:
   for group in sorted(test[grouping].unique()):
    idx=np.flatnonzero(test[grouping].to_numpy()==group)
    if len(idx)<30:continue
    diagnostics.append({'model':name,'grouping':grouping,'group':group,'sales':len(idx),**metrics(y[idx],p[idx]),'coverage_90':float((np.abs(np.log(y[idx])-p[idx])<=radii[name][.9]).mean())})
 # Fixed spatial block stress: remove complete grid cells from both fit and calibration.
 stress_train=train[~train.reserved_cell];stress_cal=cal[~cal.reserved_cell];stress_test=test[test.reserved_cell];stress=[]
 stress_tuning=[];stress_dev=cohorts['development'][~cohorts['development'].reserved_cell];stress_val=cohorts['validation'][~cohorts['validation'].reserved_cell]
 for leaves in CONFIG['candidate_leaves']:
  f=fit_boosting(stress_dev,leaves);stress_tuning.append({'leaves':leaves,'validation_median_ape_pct':metrics(stress_val.sale_price.to_numpy(),f(stress_val))['median_ape_pct']})
 stress_chosen=min(stress_tuning,key=lambda x:x['validation_median_ape_pct'])['leaves']
 for name,fit in [('hedonic',fit_hedonic),('spatial_boosting',lambda f:fit_boosting(f,stress_chosen))]:
  f=fit(stress_train);p=f(stress_test);rad=radius(abs(np.log(stress_cal.sale_price.to_numpy())-f(stress_cal)),.9);actual=stress_test.sale_price.to_numpy();stress.append({'model':name,'analysis':'unseen_spatial_cells','train_sales':len(stress_train),'calibration_parcels':len(stress_cal),'test_sales':len(stress_test),'test_cells':int(stress_test.grid.nunique()),**metrics(actual,p),'coverage_90':float((abs(np.log(actual)-p)<=rad).mean()),'median_width_USD':float(np.median(np.exp(p+rad)-np.exp(p-rad)))})
 known=set(train.pin)|set(cal.pin);idx=np.flatnonzero(~test.pin.isin(known).to_numpy())
 for name,p in predictions.items():stress.append({'model':name,'analysis':'previously_unseen_parcels','test_sales':len(idx),'test_parcels':int(test.iloc[idx].pin.nunique()),**metrics(y[idx],p[idx]),'coverage_90':float((abs(np.log(y[idx])-p[idx])<=radii[name][.9]).mean())})
 prior=test.meta_1yr_pri_board_tot.to_numpy(float)*10;eligible=np.isfinite(prior)&(prior>0);assessment={'basis':'prior-year board assessment in April2024 snapshot ×10; separate available-case cohort','test_sales':int(eligible.sum()),'missing_or_nonpositive':int((~eligible).sum()),**metrics(y[eligible],np.log(prior[eligible]))}
 # Saved distribution views have no individual addresses, prices or predictions.
 profiles=[];towns=['All townships',*sorted(test.meta_township_name.unique())]
 for town in towns:
  for size in ['All sizes',*sorted(test.size_profile.unique())]:
   mask=np.ones(len(test),bool)
   if town!='All townships':mask&=test.meta_township_name.to_numpy()==town
   if size!='All sizes':mask&=test.size_profile.to_numpy()==size
   idx=np.flatnonzero(mask)
   if len(idx)<30:continue
   local_train=train
   if town!='All townships':local_train=local_train[local_train.meta_township_name==town]
   if size!='All sizes':local_train=local_train[local_train.size_profile==size]
   sub=test.iloc[idx];base={'township':town,'size_profile':size,'sales':len(idx),'parcels':int(sub.pin.nunique()),'training_comparable_sales':len(local_train),'latitude':round(float(sub.loc_latitude.mean()),3),'longitude':round(float(sub.loc_longitude.mean()),3),'observed_price_q10_USD':float(np.quantile(y[idx],.1)),'observed_price_median_USD':float(np.median(y[idx])),'observed_price_q90_USD':float(np.quantile(y[idx],.9))}
   for name,p in predictions.items():
    score=metrics(y[idx],p[idx])
    for confidence,rad in radii[name].items():profiles.append({**base,'model':name,'nominal':confidence,'prediction_median_USD':float(np.median(np.exp(p[idx]))),'median_lower_USD':float(np.median(np.exp(p[idx]-rad))),'median_upper_USD':float(np.median(np.exp(p[idx]+rad))),'coverage':float((abs(np.log(y[idx])-p[idx])<=rad).mean()),'median_ape_pct':score['median_ape_pct']})
 print('Spatial and interval diagnostics complete',primary,flush=True)
 composite=hashlib.sha256((CONFIG['snapshot_sha256']+''.join(x['sha256'] for x in CONFIG['monthly_sales'])).encode()).hexdigest()
 result={'schema_version':'1.0','study_id':'S43','run_id':'S43-'+version['code_version'][:8]+'-'+composite[:8],**version,'evaluated_on':CONFIG['evaluated_on'],'data':{'source_url':'https://datacatalog.cookcountyil.gov/stories/s/Assessor-2025-Open-Data-Refresh/gzdr-q7c4/','release':'April10,2024 characteristic snapshot plus September29,2026 extracts of May2024–December2025 sales','sha256':composite,'license':'Cook County public-data terms; no accuracy/completeness warranty or endorsement. No separate Creative Commons license specified.','citation':"Cook County Assessor’s Office, 2024 final residential model input and Parcel Sales wvhk-k5uv; retrieved September29,2026.",'coverage':'Single-family, single-card, single-parcel scope; fixed pre-sale features and later recorded sales.'},'target':{'label':'Historical single-family sale price','estimand':'Conditional log-price prediction for eligible recorded sales; primary median percentage error','prediction_cutoff':'Frozen characteristics object last modified April10,2024, preceding every sale; no closing-date predictors','horizon':'Final sales April–December2025, with intervening January–March calibration','unit':'Recorded sale; parcel repeats stay in spatial uncertainty clusters'},'cohort':'Eligible Cook County single-family sale records April–December2025 joined to the earlier fixed property snapshot.','samples':{'total':audit['source_sales'],'train':len(train),'validation':len(cohorts['validation']),'calibration':len(cal),'test':len(test),'test_parcels':int(test.pin.nunique()),'test_spatial_cells':len(groups)},'models':[{'id':name,'label':label,'specification':{'target':'log sale price','max_leaves':chosen if 'boosting' in name else None,'fixed_hyperparameters':'See frozen protocol and models.py'}} for name,label in NAMES.items()],'metrics':measures,'uncertainty':'500 paired .03-degree spatial-grid cluster bootstrap draws retain parcel repeats. Split-calibration log-residual bands use finite-sample order statistics; temporal/spatial dependence means empirical coverage is reported, not guaranteed.','assumptions':['Snapshot features predate every included sale; later feature corrections are excluded.','Recorded sales and legacy flags do not prove every transaction is arm’s length.','Dollar intervals exponentiate log-residual bands and are not appraisals.'],'limitations':['A retrospective sale-date split cannot reconstruct historical sale-ingestion availability.','Properties with multiple cards, land lines, parcel bundles or prorations are excluded; stated price/area bounds restrict generalization.','The snapshot becomes stale as properties and markets change; later renovations are not observed.','Calibration guarantees require exchangeability that geographic dependence and market drift can violate.','Group median interval endpoints are summaries of individual bands, not confidence intervals for group market value.','No causal effect, current address-level appraisal, tax appeal recommendation or realized commercial saving is claimed.','Independent technical review is pending.'],'tables':{'audit':audit,'tuning':tuning,'selected_leaves':chosen,'primary_difference':primary,'coverage':coverage_rows,'diagnostics':diagnostics,'stress_tests':stress,'spatial_stress_tuning':stress_tuning,'spatial_stress_selected_leaves':stress_chosen,'assessment_baseline':assessment,'profiles':profiles,'source_checksums':{'snapshot':CONFIG['snapshot_sha256'],**{x['file']:x['sha256'] for x in CONFIG['monthly_sales']}}},'software':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'scikit-learn':sklearn.__version__}}
 validate_result(result);write_json(HERE/'results/result.json',result);np.savez_compressed(data_dir('S43')/'verification.npz',truth=y,pin=test.pin.to_numpy(),grid=grid,**predictions);print(json.dumps({'run_id':result['run_id'],'primary':primary,'coverage':coverage_rows}),flush=True)
if __name__=='__main__':
 with threadpool_limits(limits=2):evaluate()
