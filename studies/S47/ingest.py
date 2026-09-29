"""Verified telecom rows and profile-grouped development/calibration/test partitions."""
import hashlib
import io
import json
from pathlib import Path
from zipfile import ZipFile
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
from research_program.io import data_dir,download

CONFIG=json.loads(Path(__file__).with_name('config.json').read_text())
NUMERIC=['Call Failure','Subscription Length','Charge Amount','Seconds of Use','Frequency of use','Frequency of SMS','Distinct Called Numbers']
CATEGORICAL=['Complains','Age Group','Tariff Plan']
CORE=NUMERIC+CATEGORICAL
VARIANTS=['core','no_friction','with_status','with_value','with_both']


def feature_columns(variant):
    if variant not in VARIANTS:raise ValueError('Unknown feature variant')
    numeric=[x for x in NUMERIC if variant!='no_friction' or x!='Call Failure'];categorical=[x for x in CATEGORICAL if variant!='no_friction' or x!='Complains']
    if variant in ['with_value','with_both']:numeric.append('Customer Value')
    if variant in ['with_status','with_both']:categorical.append('Status')
    return numeric,categorical


def profile_ids(frame):
    return np.array([hashlib.sha256(('|'.join(format(float(v),'.12g') for v in row)).encode()).hexdigest() for row in frame[CORE].to_numpy()])


def partition(frame):
    groups=profile_ids(frame);labels=frame.Churn.to_numpy(int);assignment=np.full(len(frame),-1)
    for fold,(_,held) in enumerate(StratifiedGroupKFold(5,shuffle=True,random_state=CONFIG['seed']).split(frame,labels,groups)):assignment[held]=fold
    if (assignment<0).any():raise ValueError('Incomplete partition')
    for group in np.unique(groups):
        if len(np.unique(assignment[groups==group]))!=1:raise ValueError('Profile crosses source partition')
    return assignment,groups


def ingest():
    p=download(CONFIG['source_url'],data_dir('S47')/'iranian-churn.zip',CONFIG['archive_sha256'],1_000_000)
    with ZipFile(p) as z:raw=z.read('Customer Churn.csv')
    if hashlib.sha256(raw).hexdigest()!=CONFIG['csv_sha256']:raise ValueError('CSV checksum mismatch')
    f=pd.read_csv(io.BytesIO(raw));f.columns=[' '.join(x.split()) for x in f.columns]
    if f.shape!=(3150,14) or f.isna().any().any() or not set(f.Churn.unique())=={0,1}:raise ValueError('Source shape or labels changed')
    if not np.isfinite(f.to_numpy(float)).all() or (f.to_numpy(float)<0).any():raise ValueError('Invalid numeric source values')
    folds,groups=partition(f);keys=np.array([hashlib.sha256(f'S47-rank:{i}'.encode()).hexdigest() for i in range(len(f))]);counts=pd.Series(groups).value_counts();sizes=pd.Series(groups).map(counts).to_numpy()
    by=f.assign(group=groups).groupby('group').Churn.agg(['size','nunique'])
    audit={'rows':len(f),'profiles':len(by),'churn':int(f.Churn.sum()),'exact_repeated_rows':int(f.duplicated().sum()),'primary_profile_repeated_rows':len(f)-len(by),'conflicting_profile_groups':int((by['nunique']>1).sum()),'conflicting_profile_rows':int(by.loc[by['nunique']>1,'size'].sum()),'largest_profile_size':int(by['size'].max()),'charge_above_dictionary_maximum':int((f['Charge Amount']>9).sum()),'zero_usage_rows':int((f['Seconds of Use']==0).sum()),'representative_age_values':sorted(f.Age.unique().tolist()),'partitions':{name:{'rows':int(mask.sum()),'profiles':int(len(np.unique(groups[mask]))),'churn':int(f.loc[mask,'Churn'].sum())} for name,mask in [('development',folds>=2),('calibration',folds==1),('test',folds==0)]}}
    return f,folds,groups,keys,sizes,audit
