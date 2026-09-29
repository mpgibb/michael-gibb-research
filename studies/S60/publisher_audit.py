"""Recompute published repeated-run reliability without invoking model APIs."""
from pathlib import Path
import sys,json,hashlib
from collections import Counter,defaultdict
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from research_program.io import provenance,download,data_dir,write_json
from research_program.evaluation import pass_power,interval
HERE=Path(__file__).resolve().parent
CONFIG=json.loads((HERE/'config.json').read_text())


def analyze_runs(runs):
    groups=defaultdict(list);keys=set();escalations=0;repeat_calls=0;tool_calls=0;user_cost=0.;cost_known=0;reward_disagreements=0
    for row in runs:
        key=(row['task_id'],row['trial'])
        if key in keys:raise ValueError('Duplicate task/trial pair')
        keys.add(key)
        if row['reward'] not in [0,1]:raise ValueError('Nonbinary reward')
        groups[row['task_id']].append(row)
        info=row.get('info',{});reward=info.get('reward_info',{}).get('reward')
        if reward is not None and reward!=row['reward']:reward_disagreements+=1
        seen=set();escalated=False
        for message in row['traj']:
            if message.get('role')!='assistant':continue
            for call in message.get('tool_calls') or []:
                function=call.get('function',{});name=function.get('name');args=function.get('arguments');tool_calls+=1
                signature=(name,json.dumps(args,sort_keys=True) if isinstance(args,dict) else args)
                if signature in seen:repeat_calls+=1
                seen.add(signature);escalated|=name=='transfer_to_human_agents'
        escalations+=int(escalated)
        if info.get('user_cost') is not None:user_cost+=info['user_cost'];cost_known+=1
    if reward_disagreements:raise ValueError('Recorded reward disagreement')
    tasks=sorted(groups);counts=[len(groups[t]) for t in tasks]
    if min(counts)<4:raise ValueError('Insufficient repeats for pass^4')
    values={}
    for variant in ['all_available','first_four']:
        selected={t:sorted(groups[t],key=lambda x:x['trial'])[:4] if variant=='first_four' else groups[t] for t in tasks}
        values[variant]={k:np.array([pass_power(sum(int(x['reward']) for x in selected[t]),len(selected[t]),k) for t in tasks]) for k in [1,2,3,4]}
    return tasks,values,{'runs':len(runs),'tasks':len(tasks),'repeats_min':min(counts),'repeats_max':max(counts),'recorded_successes':sum(int(x['reward']) for x in runs),'tool_calls':tool_calls,'repeated_identical_calls':repeat_calls,'escalated_dialogs':escalations,'recorded_user_cost_USD':user_cost if cost_known==len(runs) else None,'cost_metadata_rows':cost_known,'complete_api_cost_USD':None,'latency_seconds':None,'reward_disagreements':reward_disagreements}


def main():
    version=provenance('S60');output=[];stored={}
    for file,checksum in CONFIG['historical_files'].items():
        url=f'https://raw.githubusercontent.com/sierra-research/tau-bench/{CONFIG["benchmark_commit"]}/historical_trajectories/{file}'
        path=download(url,data_dir('S60')/file,checksum,max_bytes=30_000_000);runs=json.loads(path.read_text());tasks,values,audit=analyze_runs(runs);rng=np.random.default_rng(CONFIG['seed']);indices=rng.integers(0,len(tasks),size=(CONFIG['bootstrap_repetitions'],len(tasks)))
        metrics=[{'repeat_subset':variant,'k':k,'estimate':float(array.mean()),**interval(array[indices].mean(axis=1))} for variant,scores in values.items() for k,array in scores.items()]
        output.append({'file':file,'sha256':checksum,'publisher_model_label':file.rsplit('-',1)[0],'exact_model_snapshot':None,'environment':file.rsplit('-',1)[1].replace('.json',''),'audit':audit,'metrics':metrics});stored[file]=(tasks,values)
    comparisons=[]
    for env in ['retail','airline']:
        left=stored[f'sonnet-35-new-{env}.json'];right=stored[f'gpt-4o-{env}.json']
        if left[0]!=right[0]:raise ValueError('Different task cohorts')
        rng=np.random.default_rng(CONFIG['seed']);indices=rng.integers(0,len(left[0]),size=(CONFIG['bootstrap_repetitions'],len(left[0])))
        for k in [1,2,3,4]:
            delta=left[1]['first_four'][k]-right[1]['first_four'][k]
            comparisons.append({'environment':env,'k':k,'comparison':'publisher sonnet-35-new minus publisher gpt-4o; first four repeats','estimate':float(delta.mean()),**interval(delta[indices].mean(axis=1))})
    final_ids=sorted(range(115),key=lambda i:hashlib.sha256(f'S60-retail-test-{i}'.encode()).hexdigest())[:CONFIG['new_trial_plan']['final_task_count']]
    result={'study_id':'S60','artifact_kind':'publisher_trajectory_baseline_audit','execution_scope':'Reanalysis of recorded publisher trials; no new model calls or intervention outcomes.','run_id':'S60-audit-'+version['code_version'][:8],**version,'benchmark_commit':CONFIG['benchmark_commit'],'files':output,'historical_model_comparisons':comparisons,'planned_final_task_ids':final_ids,'new_trial_results':None,'limitations':['Dated model snapshots, matched user configurations and total cost/latency are unavailable in historical files.','Source rewards are checked for internal agreement, not independently reconstructed from final databases in this audit.','Repeated identical calls are descriptive, not adjudicated unnecessary actions.','Publisher model differences do not identify the effect of the planned validation intervention.']}
    write_json(HERE/'results/publisher-baseline.json',result);print(json.dumps({'run_id':result['run_id'],'files':[{**x['audit'],'file':x['file']} for x in output],'final_task_ids':final_ids}),flush=True)


if __name__=='__main__':main()
