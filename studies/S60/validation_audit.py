"""Measure historical schema mismatches; no intervention outcomes are inferred."""
from pathlib import Path
from collections import Counter
import json,sys,subprocess
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from research_program.io import data_dir,write_json,provenance,sha256
from tool_validation import read_tool_schemas,validate_call
HERE=Path(__file__).resolve().parent

def main():
    config=json.loads((HERE/'config.json').read_text());root=data_dir('S60')/'tau-bench'
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    if revision!=config['benchmark_commit']:raise ValueError('Benchmark revision differs')
    if subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True).strip():raise ValueError('Benchmark checkout has modifications')
    version=provenance('S60');output=[];schema_hashes={}
    for env in ['retail','airline']:
        folder=root/'tau_bench/envs'/env/'tools';schemas=read_tool_schemas(folder)
        schema_hashes[env]={p.name:sha256(p) for p in sorted(folder.glob('*.py'))}
        for file,checksum in config['historical_files'].items():
            if not file.endswith(env+'.json'):continue
            path=data_dir('S60')/file
            if sha256(path)!=checksum:raise ValueError('Trajectory checksum mismatch')
            counts=Counter();affected=0
            for row in json.loads(path.read_text()):
                failed=False
                for message in row['traj']:
                    if message.get('role')!='assistant':continue
                    for call in message.get('tool_calls') or []:
                        function=call.get('function') or {};verdict=validate_call(function.get('name'),function.get('arguments'),schemas);counts[verdict['reason'] or 'valid']+=1;failed|=not verdict['valid']
                affected+=int(failed)
            output.append({'file':file,'tool_schemas':len(schemas),'calls':sum(counts.values()),'outcomes':dict(counts),'dialogs_with_invalid_calls':affected})
    result={'study_id':'S60','artifact_kind':'historical_tool_schema_audit','run_id':'S60-schema-'+version['code_version'][:8],**version,'benchmark_commit':revision,'tool_source_sha256':schema_hashes,'files':output,'new_trial_outcomes':None,'interpretation':'Historical syntax/schema checks only. No tool is invoked, no conversation is rerun, and no causal benefit or semantic policy compliance is established.'}
    write_json(HERE/'results/schema-audit.json',result);print(json.dumps({'run_id':result['run_id'],'files':output}))
if __name__=='__main__':main()
