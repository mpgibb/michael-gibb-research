"""Pinned workbook ingestion, overlapping-sheet accounting and as-of snapshots."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pandas as pd

from research_program.io import data_dir, download, sha256

CONFIG=json.loads(Path(__file__).with_name('config.json').read_text())
COLUMNS=['Invoice','StockCode','Description','Quantity','InvoiceDate','Price','Customer ID','Country']
FEATURES=['frequency','tx','age','inactivity','past30_count','past90_count','past30_spend','past90_spend','purchase_days','total_spend','mean_spend','horizon','month_sin','month_cos']


def combine_sheets(frames, preserve_repeated=False):
    pieces=[]
    for frame in frames:
        f=frame[COLUMNS].copy()
        if preserve_repeated:
            f['occurrence']=f.groupby(COLUMNS,dropna=False).cumcount()
        pieces.append(f)
    result=pd.concat(pieces,ignore_index=True).drop_duplicates()
    return result.drop(columns=['occurrence'],errors='ignore').reset_index(drop=True)


def prepare_events(frame):
    frame=frame.copy()
    if not frame.loc[frame['Customer ID'].notna(),'Customer ID'].mod(1).eq(0).all():
        raise ValueError('Customer IDs changed grain')
    known=frame['Customer ID'].notna()&(frame.Price>0)
    signed=frame.loc[known].copy()
    signed['customer']=signed['Customer ID'].astype('int64').astype(str)
    signed['date']=signed.InvoiceDate.dt.normalize()
    signed['spend']=signed.Quantity*signed.Price
    cancelled=signed.Invoice.astype(str).str.upper().str.startswith('C')
    positive=signed[(signed.Quantity>0)&~cancelled]
    events=positive.groupby(['customer','date'],sort=True).agg(spend=('spend','sum')).reset_index()
    net=signed.groupby(['customer','date'],sort=True).agg(net_spend=('spend','sum')).reset_index()
    if (events.spend<=0).any():raise ValueError('Positive-purchase accounting failed')
    return events,net


def ingest():
    folder=data_dir('S03')
    archive=download(CONFIG['source_url'],folder/'online-retail-ii.zip',CONFIG['archive_sha256'],60_000_000)
    with ZipFile(archive) as z:
        raw=z.read('online_retail_II.xlsx')
    if hashlib.sha256(raw).hexdigest()!=CONFIG['xlsx_sha256']:raise ValueError('Workbook hash mismatch')
    path=folder/'online_retail_II.xlsx';path.write_bytes(raw)
    frames=list(pd.read_excel(path,sheet_name=None,dtype={'Invoice':'string','StockCode':'string','Description':'string','Country':'string'},engine='openpyxl').values())
    if len(frames)!=2 or [len(x) for x in frames]!=[525461,541910]:raise ValueError('Publisher sheets changed')
    primary=combine_sheets(frames);sensitivity=combine_sheets(frames,True)
    events,net=prepare_events(primary);repeat_events,repeat_net=prepare_events(sensitivity)
    audit={'raw_rows':sum(len(x) for x in frames),'primary_rows':len(primary),'multiset_rows':len(sensitivity),'within_sheet_duplicates':[int(x.duplicated().sum()) for x in frames],'overlapping_distinct_rows':sum(len(x.drop_duplicates()) for x in frames)-len(primary),'missing_customer_rows':int(primary['Customer ID'].isna().sum()),'missing_descriptions':int(primary.Description.isna().sum()),'positive_purchase_days':len(events),'positive_customers':events.customer.nunique(),'positive_spend_gbp':events.spend.sum(),'signed_net_spend_gbp':net.net_spend.sum(),'source_first_date':str(primary.InvoiceDate.min()),'source_last_date':str(primary.InvoiceDate.max())}
    return (events,net),(repeat_events,repeat_net),audit


def history(events, cutoff):
    cutoff=pd.Timestamp(cutoff)
    past=events[events.date<cutoff].sort_values(['customer','date'])
    grouped=past.groupby('customer',sort=True)
    h=grouped.agg(first=('date','min'),last=('date','max'),purchase_days=('date','size'),total_spend=('spend','sum'),first_spend=('spend','first'))
    h=h[(cutoff-h['first']).dt.days>=CONFIG['minimum_history_days']].copy()
    h['frequency']=h.purchase_days-1;h['tx']=(h['last']-h['first']).dt.days/7;h['age']=(cutoff-h['first']).dt.days/7;h['inactivity']=(cutoff-h['last']).dt.days
    h['mean_spend']=h.total_spend/h.purchase_days
    h['repeat_mean_spend']=((h.total_spend-h.first_spend)/h.frequency.replace(0,np.nan)).fillna(0)
    for days in [30,90]:
        recent=past[past.date>=cutoff-pd.Timedelta(days=days)].groupby('customer').agg(count=('date','size'),spend=('spend','sum'))
        h[f'past{days}_count']=recent['count'].reindex(h.index,fill_value=0)
        h[f'past{days}_spend']=recent.spend.reindex(h.index,fill_value=0)
    h['inactivity_band']=np.where(h.inactivity<=30,'0–30 days',np.where(h.inactivity<=90,'31–90 days','Over 90 days'))
    h['frequency_band']=np.where(h.purchase_days==1,'One purchase day',np.where(h.purchase_days<=5,'2–5 purchase days','6+ purchase days'))
    h['rfm']=h.inactivity_band+' / '+h.frequency_band
    h['month_sin']=np.sin(2*np.pi*cutoff.month/12);h['month_cos']=np.cos(2*np.pi*cutoff.month/12)
    h['cutoff']=cutoff
    return h.reset_index()


def snapshots(events,net,cutoff):
    base=history(events,cutoff);cutoff=pd.Timestamp(cutoff);rows=[]
    for horizon in CONFIG['horizons_days']:
        end=cutoff+pd.Timedelta(days=horizon)
        future=events[(events.date>=cutoff)&(events.date<end)].groupby('customer').agg(count=('date','size'),spend=('spend','sum'))
        signed=net[(net.date>=cutoff)&(net.date<end)].groupby('customer').net_spend.sum()
        f=base.copy();f['horizon']=horizon
        f['future_count']=f.customer.map(future['count']).fillna(0).astype(int)
        f['future_spend']=f.customer.map(future.spend).fillna(0)
        f['future_net']=f.customer.map(signed).fillna(0);f['label_end']=end;rows.append(f)
    return pd.concat(rows,ignore_index=True)


def validation_selection(ids):
    return np.array([hashlib.sha256(('S03-validation:'+str(x)).encode()).digest()[0]<128 for x in ids])


def feature_matrix(frame):
    x=frame[FEATURES].to_numpy(float)
    if not np.isfinite(x).all():raise ValueError('Non-finite as-of feature')
    return x


def permitted_training(all_snapshots,cutoff):
    cutoff=pd.Timestamp(cutoff);permitted=[]
    for earlier,snapshot in all_snapshots.items():
        if pd.Timestamp(earlier)>=cutoff:continue
        use=snapshot.label_end<=cutoff
        if earlier==CONFIG['validation_cutoff']:use&=validation_selection(snapshot.customer)
        permitted.append(snapshot.loc[use])
    train=pd.concat(permitted,ignore_index=True)
    if not (train.label_end<=cutoff).all():raise ValueError('Supervised labels cross prediction cutoff')
    return train
