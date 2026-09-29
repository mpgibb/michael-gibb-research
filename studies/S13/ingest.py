"""Inspect the row-aligned SECOM sensor and test-point files."""
import hashlib,io,json,zipfile
from pathlib import Path
import numpy as np,pandas as pd
from research_program.io import data_dir,download
HERE=Path(__file__).resolve().parent
CONFIG=json.loads((HERE/'config.json').read_text())
def ingest():
 p=download(CONFIG['archive_url'],data_dir('S13')/'secom.zip',CONFIG['archive_sha256'],10_000_000)
 with zipfile.ZipFile(p) as z:
  contents={n:z.read(n) for n in CONFIG['files']}
 for n,raw in contents.items():
  if hashlib.sha256(raw).hexdigest()!=CONFIG['files'][n]:raise ValueError('Changed SECOM source')
 x=pd.read_csv(io.BytesIO(contents['secom.data']),sep=r'\s+',header=None).to_numpy(float)
 labs=pd.read_csv(io.BytesIO(contents['secom_labels.data']),sep=r'\s+',header=None)
 time=pd.to_datetime(labs[1],format='%d/%m/%Y %H:%M:%S')
 if x.shape!=(1567,590) or labs.shape!=(1567,2) or set(labs[0])!={-1,1}:raise ValueError('Unexpected source grain')
 if not time.is_monotonic_increasing or time.isna().any() or np.isinf(x).any():raise ValueError('Invalid values or calendar')
 return x,(labs[0].to_numpy()==1).astype(int),time

def split_masks(time):
 a=pd.Timestamp(CONFIG['development_end']); b=pd.Timestamp(CONFIG['validation_end'])
 return (time<a).to_numpy(),((time>=a)&(time<b)).to_numpy(),(time>=b).to_numpy()
