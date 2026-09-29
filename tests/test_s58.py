"""Event-prefix cutoff, censoring and discrete survival identities."""
import unittest,importlib.util,sys
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def module(name,file):
 spec=importlib.util.spec_from_file_location(name,ROOT/'studies/S58'/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
S=module('s58_survival','survival.py');I=module('s58_ingest','ingest.py')
class WorkflowTests(unittest.TestCase):
 def test_future_events_do_not_change_prefix(self):
  e=[{'activity':'A_Create Application','lifecycle':'complete','timestamp':0},{'activity':'A_Accepted','lifecycle':'complete','timestamp':3600}]
  self.assertEqual(I.prefix_features(e,2,0),I.prefix_features(e+[{'activity':'A_Pending','lifecycle':'complete','timestamp':999999}],2,0))
 def test_censoring_discards_partial_unobserved_interval(self):
  self.assertEqual(I.discretize(np.nan,False,3.8),(3,0));self.assertEqual(I.discretize(3.8,True,4),(4,1));self.assertEqual(I.discretize(40,True,45),(30,0))
 def test_survival_monotone_and_zero_day_identity(self):
  s=S.survival_from_hazard(np.full((2,30),.2));self.assertTrue(np.all(np.diff(s,axis=1)<=0));np.testing.assert_equal(s[:,0],1);self.assertAlmostEqual(s[0,3],.8**3)
 def test_rmst_degenerate_endpoints(self):
  a=S.summarize_survival(S.survival_from_hazard(np.ones((1,30))));b=S.summarize_survival(S.survival_from_hazard(np.zeros((1,30))))
  self.assertEqual(a['mean'][0],1);self.assertEqual(b['mean'][0],30);self.assertEqual(b['upper'][0],30)
 def test_censored_km_risk_set(self):
  f=pd.DataFrame({'risk_days':[1,2,2],'event_day':[1,2,0],'weight':[1,1,1]});s=S.kaplan_meier(f)
  self.assertAlmostEqual(s[1],2/3);self.assertAlmostEqual(s[2],1/3)
 def test_training_categories_do_not_expand_for_new_stage(self):
  f=pd.DataFrame({'stage':['A','B'],'age_days':[0.,1.]});m=S.FeatureMap(f,True);x=m.transform(pd.DataFrame({'stage':['New'],'age_days':[3.]}));self.assertEqual(x[0,-1],-1);self.assertNotIn('New',m.levels['stage'])
 def test_risk_expansion_preserves_event_count(self):
  f=pd.DataFrame({'risk_days':[1,3,2],'event_day':[1,3,0],'weight':[.5,.5,1]});x,y,w=S.expand_risk(f,np.arange(3)[:,None]);self.assertEqual(len(y),6);self.assertEqual(y.sum(),2);np.testing.assert_array_equal(x[:,1],[1,1,2,3,1,2])
