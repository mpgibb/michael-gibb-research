"""Join a fixed pre-sale characteristics snapshot at unambiguous parcel grain."""
from pathlib import Path
import sys,json,hashlib,io
import numpy as np,pandas as pd,pyarrow.parquet as pq,requests
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from research_program.io import download,data_dir,sha256,write_json
HERE=Path(__file__).resolve().parent;CONFIG=json.loads((HERE/'config.json').read_text())
NUMERIC=['char_bldg_sf','char_land_sf','age','char_beds','char_rooms','char_fbath','char_hbath','char_frpl']
PHYSICAL=['char_type_resd','char_cnst_qlty','char_roof_cnst','char_bsmt','char_air','char_gar1_size']
CATEGORIES=PHYSICAL+['meta_township_name'];SPATIAL=['loc_latitude','loc_longitude']

def grid_ids(lat,lon):return pd.Series([f'{int(np.floor(a/.03))}:{int(np.floor(b/.03))}' for a,b in zip(lat,lon)])
def reserved(cell):return int(hashlib.sha256(('S43-'+cell).encode()).hexdigest(),16)%5==0

def ingest():
 root=data_dir('S43');path=download(CONFIG['snapshot_url'],root/'assessment-2024.parquet',CONFIG['snapshot_sha256'],max_bytes=400_000_000)
 cols=['meta_pin','meta_year','meta_class','meta_modeling_group','meta_card_num','ind_pin_is_multicard','ind_pin_is_multiland','ind_pin_is_prorated','meta_1yr_pri_board_tot','meta_nbhd_code','char_yrblt',*filter(lambda x:x!='age',NUMERIC),*CATEGORIES,*SPATIAL]
 f=pq.read_table(path,columns=cols).to_pandas();audit={'snapshot_rows':len(f),'snapshot_unique_pins':int(f.meta_pin.nunique()),'snapshot_year_counts':f.meta_year.value_counts().to_dict()}
 f=f[(f.meta_modeling_group=='SF')&(f.meta_card_num=='1')&(f.ind_pin_is_multicard==False)&(f.ind_pin_is_multiland==False)&(f.ind_pin_is_prorated==False)].copy()
 f['meta_pin']=f.meta_pin.str.zfill(14)
 if f.meta_pin.duplicated().any():raise ValueError('Snapshot grain is not unique parcel')
 audit['eligible_snapshot_parcels']=len(f);frames=[]
 for source in CONFIG['monthly_sales']:
  file=root/source['file']
  if not file.exists():
   r=requests.get(source['url'],params=source['params'],timeout=(15,45));r.raise_for_status();file.write_bytes(r.content)
  if sha256(file)!=source['sha256']:raise ValueError('Mutable sale extract differs from frozen checksum')
  frame=pd.read_csv(file,dtype={'pin':str,'doc_no':str,'row_id':str,'class':str})
  if len(frame)!=source['rows']:raise ValueError('Sale row count mismatch')
  frames.append(frame)
 s=pd.concat(frames,ignore_index=True);audit['source_sales']=len(s);audit['source_missing']=s.isna().sum().to_dict()
 if s.row_id.duplicated().any() or s.duplicated(['pin','doc_no']).any():raise ValueError('Duplicate source sale grain')
 audit['source_repeated_document_rows']=int(s.doc_no.duplicated().sum());s['pin']=s.pin.str.zfill(14)
 keep=(s.is_multisale==False)&(s.sale_filter_same_sale_within_365==False)&(s.sale_filter_less_than_10k==False)&(s.sale_filter_deed_type==False)
 audit['excluded_publisher_sale_flags']=int((~keep).sum());s=s[keep].copy();dup=s.doc_no.duplicated(keep=False);audit['excluded_remaining_duplicate_documents']=int(dup.sum());s=s[~dup];audit['unmatched_sales']=int((~s.pin.isin(f.meta_pin)).sum());m=s.merge(f,left_on='pin',right_on='meta_pin',validate='many_to_one');audit['matched_sales_before_scope']=len(m)
 for field,bounds in [('sale_price',CONFIG['price_bounds']),('char_bldg_sf',CONFIG['building_sf_bounds']),('char_land_sf',CONFIG['land_sf_bounds']),('loc_latitude',[41,43]),('loc_longitude',[-89,-87])]:
  keep=m[field].between(*bounds)&np.isfinite(m[field]);audit['excluded_'+field]=int((~keep).sum());m=m[keep].copy()
 m=m.sort_values(['sale_date','row_id']).reset_index(drop=True);m['date']=pd.to_datetime(m.sale_date);m['age']=2024-m.char_yrblt;m.loc[~m.age.between(0,250),'age']=np.nan
 for c in CATEGORIES+['meta_nbhd_code']:m[c]=m[c].astype(object).where(m[c].notna(),'Unknown').astype(str)
 m['grid']=grid_ids(m.loc_latitude,m.loc_longitude);m['reserved_cell']=m.grid.map(reserved);m['size_profile']=pd.cut(m.char_bldg_sf,[0,1500,2500,np.inf],labels=['Under 1,500 sq ft','1,500–2,500 sq ft','Over 2,500 sq ft'],right=False).astype(str);m['value_tier']=pd.cut(m.sale_price,[0,250000,500000,1000000,np.inf],labels=['Under $250k','$250k–$500k','$500k–$1m','$1m+'],right=False).astype(str)
 if not (m.date>pd.Timestamp(CONFIG['snapshot_last_modified']).tz_localize(None)).all():raise ValueError('Characteristic snapshot follows a sale')
 cohorts={'development':m[m.date<CONFIG['development_end']].copy(),'validation':m[(m.date>=CONFIG['development_end'])&(m.date<CONFIG['validation_end'])].copy(),'train':m[m.date<CONFIG['validation_end']].copy(),'calibration':m[(m.date>=CONFIG['validation_end'])&(m.date<CONFIG['calibration_end'])].copy(),'test':m[(m.date>=CONFIG['calibration_end'])&(m.date<CONFIG['test_end'])].copy()}
 before=len(cohorts['calibration']);cohorts['calibration']=cohorts['calibration'].drop_duplicates('pin',keep='last');audit['calibration_repeat_sales_removed']=before-len(cohorts['calibration'])
 audit['cohorts']={k:{'sales':len(v),'parcels':int(v.pin.nunique()),'cells':int(v.grid.nunique()),'reserved_cell_sales':int(v.reserved_cell.sum()),'start':str(v.date.min().date()),'end':str(v.date.max().date())} for k,v in cohorts.items()};audit['predictor_missing']=m[NUMERIC+SPATIAL].isna().sum().to_dict();audit['final_repeated_fitting_parcels']=int(cohorts['test'].pin.isin(cohorts['train'].pin).sum());audit['eligible_sales']=len(m)
 write_json(root/'ingestion-audit.json',audit);return cohorts,audit
if __name__=='__main__':
 c,a=ingest();print(json.dumps(a,default=str))
