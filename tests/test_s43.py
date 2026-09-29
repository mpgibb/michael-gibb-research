"""Interval order statistics, geographic units and training-only mappings."""
import unittest,sys,importlib.util
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'studies/S43'))
def load(name,file):
 spec=importlib.util.spec_from_file_location(name,ROOT/'studies/S43'/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
# Import within an isolated module name; models imports its adjacent ingest module.
prior=sys.modules.pop('ingest',None);I=load('ingest','ingest.py');sys.modules['ingest']=I;M=load('s43_models','models.py')
if prior is not None:sys.modules['ingest']=prior
else:sys.modules.pop('ingest',None)
sys.path.pop(0)
class ValuationTests(unittest.TestCase):
 def test_finite_sample_order_statistic(self):self.assertEqual(M.radius(np.arange(1,10),.8),8)
 def test_too_small_calibration_fails(self):
  with self.assertRaises(ValueError):M.radius([1,2],.95)
 def test_interval_nesting(self):
  widths=[M.radius(np.arange(1,100),c) for c in [.8,.9,.95]];self.assertEqual(widths,sorted(widths))
 def test_metrics_known_prices(self):
  x=M.metrics(np.array([100,200]),np.log([110,180]));self.assertAlmostEqual(x['median_ape_pct'],10);self.assertAlmostEqual(x['median_absolute_error_USD'],15)
 def test_same_parcel_coordinates_share_block(self):
  ids=I.grid_ids([41.88,41.88],[-87.63,-87.63]);self.assertEqual(ids[0],ids[1]);self.assertEqual(I.reserved(ids[0]),I.reserved(ids[1]))
 def test_local_median_never_reads_prediction_outcomes(self):
  train=pd.DataFrame({'sale_price':np.full(35,100.),'meta_nbhd_code':['A']*35,'meta_township_name':['T']*35});pred=M.fit_local(train);future=train.copy();future.sale_price=999999;np.testing.assert_allclose(pred(future),np.log(100))
 def test_local_fallback_for_unknown_neighborhood(self):
  train=pd.DataFrame({'sale_price':np.full(35,100.),'meta_nbhd_code':['A']*35,'meta_township_name':['T']*35});future=pd.DataFrame({'meta_nbhd_code':['New'],'meta_township_name':['T']});self.assertAlmostEqual(M.fit_local(train)(future)[0],np.log(100))
