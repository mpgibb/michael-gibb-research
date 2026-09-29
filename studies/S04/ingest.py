"""Corrected publisher release with outcome-independent profile partitions."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from research_program.io import download,data_dir,sha256,write_json
HERE=Path(__file__).resolve().parent
CONFIG=json.loads((HERE/'config.json').read_text())
FEATURES=[f'f{i}' for i in range(12)]

def profile_partition(h):
    h=np.asarray(h,dtype=np.uint64)
    return h%70<10,(h//70)%100,(h//7000)%2==0,(h//14000)%3

def ingest():
    folder=data_dir('S04');source=download(CONFIG['source_url'],folder/'criteo-uplift-v2.1.csv.gz',CONFIG['sha256'],max_bytes=350_000_000)
    if source.stat().st_size!=CONFIG['bytes']:raise ValueError('Publisher size changed')
    frames=[];rows=0;counts={};missing={}
    for block in pd.read_csv(source,chunksize=250000):
        if list(block)!=FEATURES+['treatment','conversion','visit','exposure']:raise ValueError('Unexpected corrected schema')
        rows+=len(block)
        for key in block:
            missing[key]=missing.get(key,0)+int(block[key].isna().sum())
        if not np.isfinite(block.to_numpy()).all():raise ValueError('Invalid source numeric fields')
        for key in ['treatment','conversion','visit','exposure']:
            if not block[key].isin([0,1]).all():raise ValueError('Nonbinary label')
            counts[key]=counts.get(key,0)+int(block[key].sum())
        h=pd.util.hash_pandas_object(block[FEATURES],index=False).to_numpy();take,bucket,fit,fold=profile_partition(h)
        selected=block.loc[take].copy();selected['profile_hash']=h[take];selected['split_bucket']=bucket[take];selected['fit_eligible']=fit[take];selected['fold']=fold[take];frames.append(selected)
    cohort=pd.concat(frames,ignore_index=True)
    if rows!=CONFIG['source_rows'] or len(cohort)!=CONFIG['expected_sample_rows']:raise ValueError('Cohort changed')
    train=cohort[(cohort.split_bucket<60)&cohort.fit_eligible].copy();validation=cohort[cohort.split_bucket.between(60,79)].copy();test=cohort[cohort.split_bucket>=80].copy()
    parts={'development':train,'validation':validation,'test':test}
    for i,a in enumerate(parts.values()):
        for b in list(parts.values())[i+1:]:
            if np.intersect1d(a.profile_hash.unique(),b.profile_hash.unique()).size:raise ValueError('Profile leakage')
    audit={'source_rows':rows,'source_label_counts':counts,'missing':missing,'bounded_rows':len(cohort),'bounded_unique_profiles':int(cohort.profile_hash.nunique()),'repeated_profile_rows':int(cohort.profile_hash.duplicated().sum()),'partitions':{name:{'rows':len(frame),'profiles':int(frame.profile_hash.nunique()),'cells':frame.groupby(['treatment','conversion']).size().reset_index(name='n').to_dict('records'),'exposure_cells':frame.groupby(['treatment','exposure']).size().reset_index(name='n').to_dict('records')} for name,frame in parts.items()}}
    write_json(folder/'ingestion-audit.json',audit)
    return train,validation,test,audit
