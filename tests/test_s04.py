"""Causal-score identities, independent policy scoring and grouped partitions."""
import unittest,importlib.util
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('s04_effects',ROOT/'studies/S04/effects.py');effects=importlib.util.module_from_spec(spec);spec.loader.exec_module(effects)
from research_program.evaluation import ranked_selection
class UpliftTests(unittest.TestCase):
 def test_dr_recovers_balanced_known_contrast(self):
  t=np.tile([0,1],100);y=t.copy();e=np.full(200,.5)
  score=effects.doubly_robust(y,t,np.full(200,.2),np.full(200,.7),e)
  self.assertAlmostEqual(score.mean(),1)
 def test_dr_exact_outcomes_have_zero_residuals(self):
  t=np.array([0,1,0,1]);m0=np.array([.2,.3,.1,.5]);m1=m0+.1;y=np.where(t,m1,m0)
  np.testing.assert_allclose(effects.doubly_robust(y,t,m0,m1,np.repeat(.8,4)),m1-m0)
 def test_policy_uses_independent_outcomes(self):
  selection=ranked_selection([5,4,3,2],.5)
  self.assertEqual(np.mean(selection*np.array([-1,-1,1,1])),-.5)
 def test_paired_cluster_interval_zero_identical_policies(self):
  out=effects.cluster_mean(np.zeros(6),[1,1,2,2,3,3],10000)
  self.assertEqual(out['estimate'],0);self.assertEqual(out['upper'],0)
 def test_cluster_variance_matches_independent_formula(self):
  x=np.array([0,2,4,6.]);out=effects.cluster_mean(x,np.arange(4))
  self.assertAlmostEqual(out['standard_error'],np.std(x,ddof=1)/2)
 def test_fold_members_never_overlap(self):
  f=np.repeat([0,1,2],3)
  for train,test in effects.cluster_folds(f):
   self.assertFalse(set(train)&set(test));self.assertFalse(set(f[train])&set(f[test]))
 def test_overlap_required(self):
  with self.assertRaises(ValueError):effects.doubly_robust([1],[1],[0],[1],[1])
