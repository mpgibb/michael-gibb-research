"""Protect sensor cutoffs, split boundaries and inspection accounting."""
import importlib.util,sys,unittest
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def load(name,file):
 spec=importlib.util.spec_from_file_location(name,ROOT/'studies/S13'/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
I=load('s13_ingest','ingest.py');prior=sys.modules.get('ingest');sys.modules['ingest']=I;M=load('s13_models','models.py')
if prior is None:sys.modules.pop('ingest')
else:sys.modules['ingest']=prior
class SensorTests(unittest.TestCase):
 def test_calendar_boundaries(self):
  masks=I.split_masks(pd.Series(pd.to_datetime(['2008-08-31','2008-09-01','2008-09-30','2008-10-01'])));self.assertEqual([np.flatnonzero(m).tolist() for m in masks],[[0],[1,2],[3]])
 def test_future_extreme_does_not_change_training_transform(self):
  a=np.column_stack([np.arange(50),np.sin(np.arange(50)),np.ones(50)]);p=M.SensorProcessor().fit(a);before=p.transform(a).copy();p.transform(np.full((3,3),1e12));np.testing.assert_array_equal(before,p.transform(a));self.assertNotIn(2,p.columns_)
 def test_high_missing_and_duplicate_columns_removed(self):
  a=np.arange(100,dtype=float);b=a.copy();b[:75]=np.nan;p=M.SensorProcessor().fit(np.column_stack([a,a,b]));self.assertEqual(p.columns_.tolist(),[0])
 def test_missing_indicator_is_training_based(self):
  a=np.column_stack([np.arange(100,dtype=float),np.sin(np.arange(100))]);a[:10,0]=np.nan;p=M.SensorProcessor().fit(a);self.assertEqual(len(p.names_),3);q=M.SensorProcessor(False).fit(a);self.assertEqual(len(q.names_),2)
 def test_capacity_endpoints_and_tie_break(self):
  y=np.array([0,1,1,0]);p=np.ones(4);z=M.capacity_row(y,p,0);self.assertIsNone(z['precision']);self.assertEqual(z['missed_failures'],2);r=M.capacity_row(y,p,.5);self.assertEqual(r['detected_failures'],1);self.assertEqual(M.capacity_row(y,p,1)['missed_failures'],0)
 def test_day_clusters_kept_intact(self):
  days=np.array(['a','a','b','b','b']);
  for ix in M.cluster_draws(days,10,19):self.assertEqual(np.sum(ix==0),np.sum(ix==1));self.assertEqual(np.sum(ix==2),np.sum(ix==4))
 def test_pca_only_learns_pass_subspace(self):
  rng=np.random.default_rng(4);x=rng.normal(size=(80,8));y=np.r_[np.zeros(60),np.ones(20)];m=M.PCAMonitor(3).fit(x,y);self.assertEqual(m.pca.n_samples_,60);self.assertEqual(m.predict_proba(x).shape,(80,2))
