"""Executed cycle-total forecasting and explicitly hypothetical inventory replay."""
from pathlib import Path
import sys,json,hashlib,platform,itertools
import numpy as np
import pandas as pd
import scipy,sklearn
from threadpoolctl import threadpool_limits

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from research_program.io import provenance,write_json,data_dir
from research_program.evaluation import interval
from research_program.validate import validate_result
from ingest import ingest,CONFIG,HERE
from forecast import fit_quantiles,baseline,joint_quantile_scenarios,aggregation,scales,pinball,training,features
from inventory import replay,hindsight

MODELS={'seasonal_7':'Repeat the last week','seasonal_28':'Repeat the last cycle','quantile_boosting':'Global quantile boosting'}


def weighting(meta,y,price,origin):
    known_price=np.where(np.isfinite(price[:,origin-1]),price[:,origin-1],1.)
    weight=y[:,origin-28:origin].sum(axis=1)*known_price
    return weight if weight.sum()>0 else np.ones(len(meta))


def model_scenarios(name,point,quantiles,residuals,origin):
    if name=='quantile_boosting':return joint_quantile_scenarios(quantiles,residuals,CONFIG['scenario_draws'],CONFIG['seed']+origin)
    rng=np.random.default_rng(CONFIG['seed']+origin);indices=rng.integers(0,len(residuals),CONFIG['scenario_draws'])
    return np.maximum(point[None,:]+residuals[indices],0)


def inventory_sweep(meta,y,origin,scenarios):
    demand=y[:,origin:origin+28];historical=y[:,origin-28:origin].sum(axis=1)
    rows=[];item_values=[]
    for lead,holding,penalty,multiplier in itertools.product(CONFIG['lead_times'],CONFIG['holding_costs'],CONFIG['lost_sale_costs'],CONFIG['storage_multipliers']):
        capacity=np.maximum(np.ceil(historical*multiplier),1).astype(int)
        initial=np.minimum(np.ceil(historical/28*lead),capacity).astype(int);limit=capacity-initial
        oracle_order,oracle=hindsight(demand,initial,limit,lead,holding,penalty)
        critical=penalty/(penalty+28*holding)
        scenario_id=f'L{lead}-H{holding}-P{penalty}-K{multiplier}'
        for name in [*MODELS,'conventional_mean']:
            target=historical if name=='conventional_mean' else np.quantile(scenarios[name],critical,axis=0)
            order=np.minimum(np.maximum(np.ceil(target)-initial,0),limit).astype(int)
            out=replay(demand,initial,order,lead,holding,penalty)
            if (out['cost']+1e-7<oracle['cost']).any():raise ValueError('Negative regret violates common feasible set')
            row={'origin':origin,'scenario_id':scenario_id,'model':name,'lead_days':lead,'holding_per_unit_day':holding,'lost_sale_penalty':penalty,'storage_multiplier':multiplier,'quantile':critical,'assumed_cost':float(out['cost'].sum()),'lost_units':float(out['lost_units'].sum()),'unit_fill_rate':float(1-out['lost_units'].sum()/max(demand.sum(),1)),'holding_unit_days':float(out['holding_unit_days'].sum()),'hindsight_cost':float(oracle['cost'].sum()),'regret':float((out['cost']-oracle['cost']).sum()),'order_units':int(order.sum())}
            rows.append(row)
            item_values.append({'scenario_id':scenario_id,'model':name,'origin':origin,'cost':out['cost'],'lost':out['lost_units']})
    return rows,item_values


def bootstrap_summary(records,meta,models):
    items=sorted(meta.item_id.unique());groups=[np.flatnonzero(meta.item_id.to_numpy()==item) for item in items]
    rng=np.random.default_rng(CONFIG['seed']);draws=[np.concatenate([groups[i] for i in rng.integers(0,len(groups),len(groups))]) for _ in range(CONFIG['bootstrap_repetitions'])]
    values={name:{'weighted_scaled_error_28d':[],'scaled_pinball':[],'coverage_80':[]} for name in models}
    for indices in draws:
        for name in models:
            for metric in values[name]:
                per_origin=[]
                for row in records[name]:
                    if metric=='coverage_80':score=row['coverage'][indices].mean()
                    else:
                        weights=row['weight'][indices];weights=weights/weights.sum();key='scaled_error' if metric=='weighted_scaled_error_28d' else 'scaled_pinball'
                        score=np.dot(weights,row[key][indices])
                    per_origin.append(score)
                values[name][metric].append(float(np.mean(per_origin)))
    return values,draws


def main():
    version=provenance('S02');meta,y,calendar,price,audit=ingest();groups,A=aggregation(meta)
    source_hash=hashlib.sha256(json.dumps(CONFIG['files'],sort_keys=True).encode()).hexdigest()
    tune=CONFIG['tuning_origin'];truth=y[:,tune:tune+28].sum(axis=1);scale=scales(y[:,:tune])[1]
    tuning=[]
    for leaves in CONFIG['candidate_leaves']:
        q,cross,ntrain=fit_quantiles(y,price,meta,calendar,tune,leaves,CONFIG)
        loss=float(np.mean(np.column_stack([pinball(truth,q[:,j],p)/scale for j,p in enumerate(CONFIG['quantiles'])])))
        tuning.append({'leaves':leaves,'normalized_pinball':loss,'training_examples':ntrain,'crossing_rows_before_rearrangement':cross})
        print('Tuning',leaves,loss,flush=True)
    chosen=min(tuning,key=lambda row:row['normalized_pinball'])['leaves']
    residuals={name:[] for name in MODELS};calibration=[]
    for origin in CONFIG['calibration_origins']:
        q,cross,ntrain=fit_quantiles(y,price,meta,calendar,origin,chosen,CONFIG);actual=y[:,origin:origin+28].sum(axis=1)
        points={name:baseline(y,origin,name) for name in ['seasonal_7','seasonal_28']};points['quantile_boosting']=q[:,1]
        for name in MODELS:residuals[name].append(actual-points[name])
        calibration.append({'origin':origin,'last_target_day':origin+28,'training_examples':ntrain,'crossing_rows':cross})
        print('Calibration origin',origin,flush=True)
    residuals={name:np.stack(rows) for name,rows in residuals.items()}
    level_metrics=[];aggregate_tables=[];case_rows=[];inventory=[];item_inventory=[];ablation=[]
    records={name:[] for name in MODELS}; verification={}
    for origin in CONFIG['final_origins']:
        quantiles,cross,ntrain=fit_quantiles(y,price,meta,calendar,origin,chosen,CONFIG)
        points={name:baseline(y,origin,name) for name in ['seasonal_7','seasonal_28']};points['quantile_boosting']=quantiles[:,1]
        actual=y[:,origin:origin+28].sum(axis=1);aggregate_actual=A@actual
        scale,absolute_scale=scales(A@y[:,:origin]);bottom_weight=weighting(meta,y,price,origin);group_weight=A@bottom_weight
        scenarios={name:model_scenarios(name,points[name],quantiles,residuals[name],origin) for name in MODELS}
        for name in MODELS:
            draws=scenarios[name];aggregate_draws=draws@A.T;aggregate_point=A@points[name]
            if not np.allclose(aggregate_draws[:,-1],draws.sum(axis=1)):raise ValueError('Scenario aggregation incoherent')
            qs=np.quantile(aggregate_draws,CONFIG['quantiles'],axis=0).T
            error=np.abs(aggregate_actual-aggregate_point)/scale
            qloss=np.mean(np.column_stack([2*pinball(aggregate_actual,qs[:,j],q)/absolute_scale for j,q in enumerate(CONFIG['quantiles'])]),axis=1)
            covered=(aggregate_actual>=qs[:,0])&(aggregate_actual<=qs[:,2]);width=qs[:,2]-qs[:,0]
            verification[f'{origin}_{name}_point']=points[name]
            verification[f'{origin}_{name}_bounds']=qs[:len(meta)]
            verification[f'{origin}_{name}_scenarios']=draws
            verification[f'{origin}_actual']=actual
            verification[f'{origin}_scale']=scale[:len(meta)]
            verification[f'{origin}_absolute_scale']=absolute_scale[:len(meta)]
            verification[f'{origin}_weight']=bottom_weight
            records[name].append({'scaled_error':error[:len(meta)],'scaled_pinball':qloss[:len(meta)],'coverage':covered[:len(meta)],'weight':bottom_weight})
            for level in ['bottom','store','category','total']:
                idx=np.array([i for i,g in enumerate(groups) if g[0]==level]);weights=group_weight[idx]/group_weight[idx].sum()
                level_metrics.append({'origin':origin,'model':name,'level':level,'series':len(idx),'weighted_scaled_error_28d':float(weights@error[idx]),'scaled_pinball':float(weights@qloss[idx]),'coverage_80':float(covered[idx].mean()),'mean_width_units':float(width[idx].mean())})
            for i,(level,label,_) in enumerate(groups):
                if level!='bottom':aggregate_tables.append({'origin':origin,'forecast_date':str(calendar.iloc[origin-1].date),'model':name,'level':level,'group':label,'observed_sales_units':float(aggregate_actual[i]),'point_units':float(aggregate_point[i]),'lower_units':float(qs[i,0]),'upper_units':float(qs[i,2]),'covered':bool(covered[i])})
            for key in ['store_id','dept_id','cat_id']:
                for value in sorted(meta[key].unique()):
                    idx=np.flatnonzero(meta[key].to_numpy()==value);w=bottom_weight[idx]
                    score=float(np.average(error[idx],weights=w)) if w.sum() else float(error[idx].mean())
                    case_rows.append({'origin':origin,'model':name,'grouping':key,'group':str(value),'series':len(idx),'weighted_scaled_error_28d':score,'coverage_80':float(covered[idx].mean())})
        independent=joint_quantile_scenarios(quantiles,residuals['quantile_boosting'],CONFIG['scenario_draws'],CONFIG['seed']+origin,independent=True)@A.T
        dependent=scenarios['quantile_boosting']@A.T
        for level in ['store','category','total']:
            idx=np.array([i for i,g in enumerate(groups) if g[0]==level])
            for label,draws in [('shared_historical_ranks',dependent),('independent_ranks',independent)]:
                bounds=np.quantile(draws[:,idx],[.1,.9],axis=0);covered=(aggregate_actual[idx]>=bounds[0])&(aggregate_actual[idx]<=bounds[1])
                ablation.append({'origin':origin,'level':level,'dependence':label,'coverage_80':float(covered.mean()),'mean_width_units':float(np.diff(bounds,axis=0).mean())})
        inv,per_item=inventory_sweep(meta,y,origin,scenarios);inventory+=inv;item_inventory+=per_item
        print('Final origin',origin,'training examples',ntrain,'crossing',cross,flush=True)
    bootstrap,draws=bootstrap_summary(records,meta,MODELS)
    metrics=[]
    for name in MODELS:
        for metric,unit in [('weighted_scaled_error_28d','scaled cycle-total error'),('scaled_pinball','scaled pinball loss'),('coverage_80','fraction')]:
            estimate=float(np.mean([row[metric] for row in level_metrics if row['model']==name and row['level']=='bottom']))
            metrics.append({'name':metric,'model':name,'estimate':estimate,'unit':unit,'split':'four final rolling origins',**interval(bootstrap[name][metric])})
    delta=np.array(bootstrap['quantile_boosting']['weighted_scaled_error_28d'])-np.array(bootstrap['seasonal_28']['weighted_scaled_error_28d'])
    estimates={(m['model'],m['name']):m['estimate'] for m in metrics};difference={'comparison':'quantile_boosting minus seasonal_28','estimate':estimates['quantile_boosting','weighted_scaled_error_28d']-estimates['seasonal_28','weighted_scaled_error_28d'],**interval(delta)}
    scenario_summary=[]
    for sid in sorted(set(row['scenario_id'] for row in inventory)):
        for name in [*MODELS,'conventional_mean']:
            rows=[row for row in inventory if row['scenario_id']==sid and row['model']==name]
            values=sum((row['cost'] for row in item_inventory if row['scenario_id']==sid and row['model']==name),np.zeros(len(meta)))
            comparison=sum((row['cost'] for row in item_inventory if row['scenario_id']==sid and row['model']=='conventional_mean'),np.zeros(len(meta)))
            differences=[float((values[idx]-comparison[idx]).sum()) for idx in draws]
            scenario_summary.append({'scenario_id':sid,'model':name,'lead_days':rows[0]['lead_days'],'holding_per_unit_day':rows[0]['holding_per_unit_day'],'lost_sale_penalty':rows[0]['lost_sale_penalty'],'storage_multiplier':rows[0]['storage_multiplier'],'assumed_cost':sum(row['assumed_cost'] for row in rows),'lost_units':sum(row['lost_units'] for row in rows),'hindsight_cost':sum(row['hindsight_cost'] for row in rows),'regret':sum(row['regret'] for row in rows),'cost_difference_vs_conventional':float((values-comparison).sum()),'cost_difference_interval':interval(differences)})
    data={'source_url':'https://github.com/Mcompetitions/M5-methods','release':'Organizer evaluation release; files inspected 2026-09-29; sales through d_1969','sha256':source_hash,'file_hashes':CONFIG['files'],'license':'Publisher competition distribution; raw data not redistributed; no additional rights asserted.','citation':'Makridakis, Spiliotis & Assimakopoulos (2022), M5 accuracy competition; official M5-methods repository and competitors guide.','coverage':'2011-01-29–2016-06-19; 210 selected product/store series'}
    result={'schema_version':'1.0','study_id':'S02','run_id':'S02-'+version['code_version'][:8]+'-'+source_hash[:8],**version,'evaluated_on':CONFIG['evaluated_on'],'data':data,'target':{'label':'Next 28-day recorded unit-sales total','estimand':'Sales forecast for a fixed historically available assortment, not latent demand','prediction_cutoff':'Origin-day close; only already completed weekly prices','horizon':'28 days','unit':'product/store replenishment cycle'},'cohort':'21 deterministically selected items across all ten stores; four non-overlapping final 28-day target windows ending June 19, 2016.','samples':{'total':210*1969,'test':210*4,'series':210,'items':21,'stores':10,'origins':4,'days_per_horizon':28,'tuning_examples':tuning[0]['training_examples']},'models':[{'id':name,'label':label,'specification':{'horizon':28,'chosen_leaves':chosen if name=='quantile_boosting' else None,'quantiles':CONFIG['quantiles'],'scenario_draws':CONFIG['scenario_draws']}} for name,label in MODELS.items()],'metrics':metrics,'uncertainty':'500 paired item-cluster bootstrap draws retain all ten stores and four origins per item. Conditional on these locations, historical dates and fitted models. Scenario dependence uses 17 overlapping calibration windows, not 256 independent histories.','assumptions':['Recorded sales are used as scenario demand only; actual inventory availability is unknown.','Price features and forecast weights use only completed source-calendar weeks.','All economic costs and storage/lead-time settings are explicitly assumed.','Aggregate scenarios sum bottom-level units exactly; marginal quantiles are not additive.'],'limitations':['Bounded deterministic 21-item assortment; not a random sample of the full retail market.','Cycle-total scaled error is not the official daily M5 leaderboard score.','Only four final historical windows; item-bootstrap intervals do not quantify future time-regime uncertainty.','Seventeen overlapping calibration windows limit tail and dependence estimation; forecast bands have no exact-coverage guarantee.','No actual stock availability, retailer margin, purchase cost, spoilage or realized savings is observed.','Independent technical review is pending.'],'tables':{'audit':audit,'tuning':tuning,'selected_leaves':chosen,'calibration_origins':calibration,'primary_difference':difference,'metrics_by_origin_level':level_metrics,'aggregate_forecasts':aggregate_tables,'failure_groups':case_rows,'dependence_ablation':ablation,'inventory_by_origin':inventory,'inventory_scenarios':scenario_summary,'scenario_units':'Assumed USD; holding per unit/day, lost-sale penalty per unmet unit.','scenario_formula':'End-of-day inventory × holding cost + lost scenario units × penalty; one constrained order.'},'software':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__,'scikit-learn':sklearn.__version__}}
    np.savez_compressed(data_dir('S02')/'verification.npz',**verification)
    validate_result(result);write_json(HERE/'results/result.json',result)
    print(json.dumps({'primary_difference':difference,'run_id':result['run_id']}),flush=True)


if __name__=='__main__':
    with threadpool_limits(limits=2):main()
