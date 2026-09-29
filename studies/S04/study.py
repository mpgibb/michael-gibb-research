"""Corrected-release uplift policies scored on independent benchmark outcomes."""
from pathlib import Path
import sys,json,platform
import numpy as np
import pandas as pd
import scipy,sklearn,econml
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import roc_auc_score,brier_score_loss
from econml.dml import CausalForestDML
from threadpoolctl import threadpool_limits
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from research_program.io import provenance,write_json,data_dir
from research_program.evaluation import ranked_selection
from research_program.validate import validate_result
from ingest import ingest,CONFIG,HERE,FEATURES
from effects import outcome_model,propensity_model,nuisance_fit,nuisance_predict,doubly_robust,cluster_mean,cluster_folds


def main():
    version=provenance('S04');train,val,test,audit=ingest();print('Cohorts',len(train),len(val),len(test),flush=True)
    x=train[FEATURES].to_numpy();y=train.conversion.to_numpy();t=train.treatment.to_numpy();folds=cluster_folds(train.fold.to_numpy())
    xv=val[FEATURES].to_numpy();xt=test[FEATURES].to_numpy();yv=val.conversion.to_numpy();tv=val.treatment.to_numpy();yt=test.conversion.to_numpy();tt=test.treatment.to_numpy();profiles=test.profile_hash.to_numpy()
    pseudo=np.empty(len(train));crossfit=[]
    for k,(fit,held) in enumerate(folds):
        nuisance=nuisance_fit(x[fit],y[fit],t[fit],CONFIG['seed']+k);m0,m1,e=nuisance_predict(nuisance,x[held]);pseudo[held]=doubly_robust(y[held],t[held],m0,m1,e)
        crossfit.append({'fold':k,'fit_rows':len(fit),'held_rows':len(held),'held_conversions':int(y[held].sum()),'held_control':int((t[held]==0).sum())});print('Cross-fit fold',k,flush=True)
    final_nuisance=nuisance_fit(x,y,t,CONFIG['seed']);v0,v1,ve=nuisance_predict(final_nuisance,xv);m0,m1,e=nuisance_predict(final_nuisance,xt)
    phi_v=doubly_robust(yv,tv,v0,v1,ve);phi=doubly_robust(yt,tt,m0,m1,e)
    candidates={};scores_v={};specifications={};tuning=[]
    for strength in CONFIG['dr_l2']:
        name=f'dr_l2_{strength}'
        model=HistGradientBoostingRegressor(max_leaf_nodes=7,max_iter=CONFIG['iterations'],learning_rate=.05,l2_regularization=strength,early_stopping=False,random_state=CONFIG['seed']).fit(x,pseudo)
        scores_v[name]=model.predict(xv);candidates[name]=model.predict(xt);specifications[name]={'family':'cross-fitted doubly robust learner','l2':strength,'leaves':7,'iterations':CONFIG['iterations']}
        print('Fitted',name,flush=True)
    for leaf in CONFIG['forest_min_leaf']:
        name=f'honest_forest_{leaf}'
        model=CausalForestDML(model_y=outcome_model(CONFIG['seed']),model_t=propensity_model(),discrete_treatment=True,cv=folds,n_estimators=CONFIG['forest_trees'],max_depth=10,min_samples_leaf=leaf,max_samples=.45,honest=True,inference=False,n_jobs=2,random_state=CONFIG['seed'])
        model.fit(y,t,X=x,inference=None);scores_v[name]=model.effect(xv);candidates[name]=model.effect(xt);specifications[name]={'family':'EconML honest causal forest DML','min_leaf':leaf,'trees':CONFIG['forest_trees'],'depth':10,'max_samples':.45,'honest':True,'inference':'independent profile-cluster policy intervals'}
        print('Fitted',name,flush=True)
    for name,score in scores_v.items():
        chosen=ranked_selection(score,CONFIG['primary_capacity']);tuning.append({'model':name,'validation_contrast_per_10000':float(np.mean(chosen*phi_v)*10000),'selected':int(chosen.sum())})
    selected_model=max(tuning,key=lambda r:r['validation_contrast_per_10000'])['model']
    labels={**{f'dr_l2_{v}':f'Doubly robust learner · L2 {v}' for v in CONFIG['dr_l2']},**{f'honest_forest_{v}':f'Honest causal forest · leaf {v}' for v in CONFIG['forest_min_leaf']},'response':'Response-probability targeting','random':'Expected random allocation'}
    all_scores={**candidates,'response':m1};frontier=[];selections={};metrics=[];calibration=[]
    for name in labels:
        for capacity in CONFIG['capacities']:
            selection=np.full(len(test),capacity) if name=='random' else ranked_selection(all_scores[name],capacity).astype(float)
            inference=cluster_mean(selection*phi,profiles,10000);selected=float(selection.sum())
            row={'model':name,'capacity':capacity,'selected':selected,'selected_fraction':float(selection.mean()),'kind':'analytical expected selection' if name=='random' else 'frozen ranked selection',**inference,'unit':'incremental benchmark conversions per 10000 eligible records','selected_treated':float(np.dot(selection,tt)),'selected_control':float(np.dot(selection,1-tt)),'observed_conversions_in_selection':float(np.dot(selection,yt))}
            frontier.append(row)
            if capacity==CONFIG['primary_capacity']:
                selections[name]=selection;metrics.append({'name':'incremental_benchmark_conversions_per_10000','model':name,'unit':row['unit'],'split':'untouched profile-separated final cohort',**inference})
        if name in candidates:
            score=candidates[name];order=np.argsort(score,kind='stable');groups=np.array_split(order,10)
            for i,indices in enumerate(groups):
                calibration.append({'model':name,'decile':i+1,'n':len(indices),'events':int(yt[indices].sum()),'treated':int(tt[indices].sum()),'predicted_effect_per_10000':float(score[indices].mean()*10000),**cluster_mean(phi[indices],profiles[indices],10000)})
    difference=cluster_mean((selections[selected_model]-selections['response'])*phi,profiles,10000)
    difference.update(comparison=f'{selected_model} minus response targeting',capacity=CONFIG['primary_capacity'])
    prevalence=float(t.mean());constant_phi=doubly_robust(yt,tt,m0,m1,np.full(len(test),prevalence));ipw=tt*yt/e-(1-tt)*yt/(1-e)
    sensitivities=[];unique=~test.profile_hash.duplicated().to_numpy()
    for name in labels:
        sel=selections[name]
        for label,values,mask in [('learned_propensity_DR',phi,np.ones(len(test),bool)),('constant_propensity_DR',constant_phi,np.ones(len(test),bool)),('learned_propensity_IPW',ipw,np.ones(len(test),bool)),('one_record_per_profile',phi,unique)]:
            sensitivities.append({'model':name,'analysis':label,'capacity':CONFIG['primary_capacity'],'n':int(mask.sum()),'selected_fraction':float(sel[mask].mean()),**cluster_mean((sel*values)[mask],profiles[mask],10000)})
    balance=[]
    for j,key in enumerate(FEATURES):
        a=xt[tt==1,j];b=xt[tt==0,j];den=np.sqrt((a.var()+b.var())/2)
        balance.append({'feature':key,'standardized_treatment_difference':float((a.mean()-b.mean())/den) if den else 0})
    propensity={'min':float(e.min()),'p01':float(np.quantile(e,.01)),'median':float(np.median(e)),'p99':float(np.quantile(e,.99)),'max':float(e.max()),'assignment_auroc':float(roc_auc_score(tt,e)),'assignment_brier':float(brier_score_loss(tt,e)),'development_treatment_prevalence':prevalence,'clipped_fraction':float(((e<=.05)|(e>=.95)).mean())}
    data={'source_url':'https://ailab.criteo.com/criteo-uplift-prediction-dataset/','release':'Corrected Criteo v2.1; downloaded 2026-09-29','sha256':CONFIG['sha256'],'license':'CC BY-NC-SA 4.0; https://creativecommons.org/licenses/by-nc-sa/4.0/; aggregate research transformations; no warranty.','citation':'Diemert, Betlei, Renaudin & Amini (2018), A Large Scale Benchmark for Uplift Modeling, AdKDD/TargetAd Workshop.','coverage':'13,979,592 source records; anonymous benchmark with no released dates or campaign IDs.'}
    models=[{'id':name,'label':label,'specification':specifications.get(name,{'family':'expected random allocation' if name=='random' else 'development-fitted treated conditional mean'})} for name,label in labels.items()]
    result={'schema_version':'1.0','study_id':'S04','run_id':'S04-'+version['code_version'][:8]+'-'+CONFIG['sha256'][:8],**version,'evaluated_on':CONFIG['evaluated_on'],'data':data,'target':{'label':'Recorded conversion under assigned advertising eligibility','estimand':'Released-benchmark policy treatment contrast conditional on sampling and exchangeability assumptions','prediction_cutoff':'Anonymized baseline features only; realized exposure and both outcomes excluded','horizon':'Publisher conversion label; exact attribution window and per-record dates unavailable','unit':'Released anonymous record, clustered by matching feature profile'},'cohort':'Outcome-independent profile-hash sample; disjoint development/validation/evaluation profiles; bounded fitting subset.','samples':{'total':audit['bounded_rows'],'train':len(train),'validation':len(val),'test':len(test),'test_profiles':int(test.profile_hash.nunique()),'events':{'train':int(y.sum()),'validation':int(yv.sum()),'test':int(yt.sum())}},'models':models,'metrics':metrics,'uncertainty':'Paired 95% profile-cluster normal intervals from independent held-out score contributions. Conditional on fitted models and rankings; unobserved campaign dependence and privacy-selection bias are not identified.','assumptions':['Consistency, overlap and benchmark-sample exchangeability are needed for causal interpretation.','Non-uniform privacy subsampling prevents recovery of original advertiser effects or economics.','Matching profiles are grouped conservatively; they are not asserted to identify people.','Assumed conversion value and contact cost are scenario inputs only.'],'limitations':['No dates, campaign IDs, demographic meanings or original experimental strata are released.','Rare conversion and control events can make capacity-specific contrasts imprecise.','Cluster intervals omit fitting uncertainty and are not simultaneous frontier guarantees.','Profile-hash sampling and bounded fitting do not establish full-source or current-market performance.','Exposure and visit are excluded as post-assignment variables.','No advertiser ROI, realized profit or fairness conclusion is identified.','Independent technical review is pending.'],'tables':{'audit':audit,'crossfit':crossfit,'tuning':tuning,'selected_model':selected_model,'primary_difference':difference,'capacity_frontier':frontier,'effect_calibration':calibration,'sensitivity':sensitivities,'feature_balance':balance,'propensity':propensity,'all_vs_none':cluster_mean(phi,profiles,10000),'scenario_formula':'Incremental benchmark conversions per 10000 × assumed conversion value − selected fraction × 10000 × assumed contact cost.','economic_ranges':{'conversion_value_USD':[0,1000],'contact_cost_USD':[0,10]}},'software':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__,'scikit-learn':sklearn.__version__,'econml':econml.__version__}}
    validate_result(result);write_json(HERE/'results/result.json',result)
    np.savez_compressed(data_dir('S04')/'verification.npz',y=yt,t=tt,profile=profiles,phi=phi,m0=m0,m1=m1,e=e,**all_scores)
    print(json.dumps({'selected':selected_model,'primary_difference':difference,'run_id':result['run_id']}),flush=True)


if __name__=='__main__':
    with threadpool_limits(limits=2):main()
