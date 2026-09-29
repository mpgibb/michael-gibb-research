"""Checks of profile separation, permitted predictors, ranking and trial assumptions."""
import unittest
import numpy as np
import pandas as pd
from scipy.special import xlogy
from sklearn.metrics import log_loss
from studies.S47 import ingest,models,study


def example():
 n=90;rng=np.random.default_rng(47);f=pd.DataFrame({x:rng.integers(0,100,n) for x in ingest.NUMERIC});f['Complains']=np.arange(n)%2;f['Age Group']=1+np.arange(n)%5;f['Tariff Plan']=1+np.arange(n)%2;f['Status']=1+np.arange(n)%2;f['Customer Value']=rng.random(n)*100;f['Age']=30;f['Churn']=np.arange(n)%3==0
 return f


class TelecomChecks(unittest.TestCase):
 def test_profile_identity_omits_label_and_derived_fields(self):
  f=example();other=f.copy();other.Churn=1-other.Churn.astype(int);other.Status=2;other['Customer Value']=0;other.Age=99;np.testing.assert_array_equal(ingest.profile_ids(f),ingest.profile_ids(other))
 def test_repeated_and_contradictory_profiles_stay_in_partition(self):
  f=example();copy=f.iloc[:20].copy();copy.Churn=~copy.Churn;f=pd.concat([f,copy],ignore_index=True);folds,groups=ingest.partition(f)
  for group in np.unique(groups):self.assertEqual(len(np.unique(folds[groups==group])),1)
  np.testing.assert_array_equal(folds[:20],folds[-20:]);self.assertEqual(set(folds),set(range(5)))
 def test_feature_variants_remove_friction_and_control_derived_inputs(self):
  a,b=ingest.feature_columns('core');self.assertNotIn('Status',a+b);self.assertNotIn('Customer Value',a+b);self.assertNotIn('Age',a+b);self.assertNotIn('Churn',a+b)
  a,b=ingest.feature_columns('no_friction');self.assertNotIn('Complains',a+b);self.assertNotIn('Call Failure',a+b)
  a,b=ingest.feature_columns('with_both');self.assertIn('Status',b);self.assertIn('Customer Value',a)
 def test_transform_ignores_unpermitted_outcomes(self):
  f=example();changed=f.copy();changed.Churn=1-changed.Churn.astype(int);changed.Status=2;changed['Customer Value']=9999;changed.Age=99
  for family,setting in [('linear',1),('additive',1),('boosting',7)]:
   model=models.make_model(family,setting,'core').fit(f,f.Churn);np.testing.assert_allclose(model.predict_proba(f),model.predict_proba(changed))
 def test_rank_capacity_ties_and_zero_and_full_endpoints(self):
  y=np.array([1,0,1,0]);p=np.array([.4,.4,.3,.2]);k=np.array(['b','a','c','d']);zero=models.capacity(y,p,k,0);half=models.capacity(y,p,k,.5);full=models.capacity(y,p,k,1)
  self.assertEqual(zero['contacts'],0);self.assertIsNone(zero['precision']);self.assertEqual(half['churn_found'],1);self.assertEqual(half['churn_missed'],1);self.assertEqual(full['recall'],1);self.assertEqual(full['contacts'],4)
 def test_metric_reweighting_and_losses(self):
  y=np.array([0,1,1,0]);p=np.array([.1,.7,.6,.2]);weights=np.array([1,.5,.5,1]);s=study.scores(y,p,weights)
  expected=np.average(-xlogy(y,p)-xlogy(1-y,1-p),weights=weights);self.assertAlmostEqual(s['log_loss'],expected);self.assertAlmostEqual(s['log_loss'],log_loss(y,p,sample_weight=weights));self.assertAlmostEqual(s['predicted_observed_churn_ratio'],np.dot(weights,p)/np.dot(weights,y))
 def test_cluster_resampling_preserves_multiplicity(self):
  groups=np.array(['a','a','b','c','c','c'])
  for ix in study.group_draws(groups,20,123):
   counts=np.bincount(ix,minlength=6);self.assertEqual(counts[0],counts[1]);self.assertEqual(counts[3],counts[4]);self.assertEqual(counts[4],counts[5])
 def test_experiment_size_is_even_monotone_and_feasible(self):
  small=models.sample_size(.15,.02);large=models.sample_size(.15,.04);self.assertGreater(small['total'],large['total']);self.assertEqual(small['total'],2*small['per_arm']);self.assertAlmostEqual(small['intervention_churn'],.13)
  with self.assertRaises(ValueError):models.sample_size(.05,.1)
  with self.assertRaises(ValueError):models.sample_size(.45,.01)
 def test_rule_requires_only_documented_complaint_and_usage(self):
  f=example();rule=models.ComplaintUsageRule().fit(f,f.Churn.to_numpy());a=rule.predict(f);f.Churn=False;f.Status=2;np.testing.assert_array_equal(a,rule.predict(f));self.assertTrue(np.all((a>0)&(a<1)))


if __name__=='__main__':unittest.main()
