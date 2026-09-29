"""Verified external M5 files; no raw data is written into this repository."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
from research_program.io import data_dir,sha256

HERE=Path(__file__).resolve().parent
CONFIG=json.loads((HERE/'config.json').read_text())
KEYS=['item_id','dept_id','cat_id','store_id','state_id']


def ingest():
    folder=data_dir('S02')
    for name,info in CONFIG['files'].items():
        path=folder/name
        if not path.exists():raise FileNotFoundError(f'Download {name} from {info["url"]} into the external S02 data directory.')
        if path.stat().st_size!=info['bytes'] or sha256(path)!=info['sha256']:raise ValueError(f'Changed publisher file: {name}')
    frames=[]
    for name,end in [('sales_train_evaluation.csv',1941),('sales_test_evaluation.csv',1969)]:
        parts=[block[block.item_id.isin(CONFIG['items'])] for block in pd.read_csv(folder/name,chunksize=5000)]
        frame=pd.concat(parts).sort_values(['item_id','store_id']).reset_index(drop=True)
        if frame.duplicated(['item_id','store_id']).any() or len(frame)!=210:raise ValueError('Invalid item/store grain')
        if frame.columns[-1]!=f'd_{end}':raise ValueError('Unexpected sales horizon')
        frames.append(frame)
    if not frames[0][KEYS].equals(frames[1][KEYS]):raise ValueError('Training/final source key mismatch')
    meta=frames[0][KEYS].copy();y=np.concatenate([frame.drop(columns=KEYS).to_numpy(dtype=float) for frame in frames],axis=1)
    if y.shape!=(210,1969) or not np.isfinite(y).all() or (y<0).any() or not np.equal(y,np.floor(y)).all():raise ValueError('Invalid unit sales')
    cal=pd.read_csv(folder/'calendar.csv');dates=pd.to_datetime(cal.date)
    if len(cal)!=1969 or dates.iloc[0]!=pd.Timestamp('2011-01-29') or dates.iloc[-1]!=pd.Timestamp('2016-06-19') or not dates.diff().iloc[1:].eq(pd.Timedelta(days=1)).all():raise ValueError('Calendar continuity violated')
    chunks=[];source_count=0
    for block in pd.read_csv(folder/'sell_prices.csv',chunksize=500000):
        source_count+=len(block);chunks.append(block[block.item_id.isin(CONFIG['items'])])
    prices=pd.concat(chunks)
    if prices.duplicated(['item_id','store_id','wm_yr_wk']).any() or (prices.sell_price<=0).any():raise ValueError('Price grain or units invalid')
    # Each weekly observation becomes eligible only after that complete week ends.
    week_ends=cal.groupby('wm_yr_wk',sort=False).apply(lambda group:int(group.index.max())+1,include_groups=False).to_dict()
    price=np.full_like(y,np.nan)
    pairs={(row.item_id,row.store_id):i for i,row in meta.iterrows()}
    for row in prices.itertuples(index=False):
        end=week_ends.get(row.wm_yr_wk)
        if end is not None:price[pairs[row.item_id,row.store_id],end-1]=row.sell_price
    price=pd.DataFrame(price).ffill(axis=1).to_numpy()
    # Origin includes that day's close: the preceding complete week is conservative even on week-ending days.
    price=np.concatenate([np.full((210,1),np.nan),price[:,:-1]],axis=1)
    audit={'source_series':30490,'source_price_rows':source_count,'selected_items':len(CONFIG['items']),'selected_series':len(meta),'selected_departments':int(meta.dept_id.nunique()),'stores':int(meta.store_id.nunique()),'categories':int(meta.cat_id.nunique()),'calendar_start':str(dates.iloc[0].date()),'calendar_end':str(dates.iloc[-1].date()),'zero_fraction_before_final':float((y[:,:CONFIG['final_origins'][0]]==0).mean()),'missing_price_at_final_origins':{str(o):int(np.isnan(price[:,o-1]).sum()) for o in CONFIG['final_origins']},'join_keys':['item_id','store_id'],'price_cutoff':'Weekly price eligible only after its complete source-calendar week ends.'}
    return meta,y,cal,price,audit
