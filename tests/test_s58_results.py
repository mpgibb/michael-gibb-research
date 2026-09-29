"""Saved workflow results preserve cohort and capacity identities."""
from pathlib import Path
import json,unittest
R=json.loads((Path(__file__).resolve().parents[1]/'studies/S58/results/result.json').read_text());T=R['tables']
class WorkflowResultTests(unittest.TestCase):
 def test_validation_selected_model(self):
  self.assertEqual(T['selected_leaves'],min(T['tuning'],key=lambda x:x['validation_mae_days'])['leaves'])
 def test_full_capacity_captures_all_late_cases(self):
  for x in T['late_frontier']:
   self.assertLessEqual(x['late_selected'],x['selected']);self.assertLessEqual(x['late_selected'],x['late_applications'])
   self.assertAlmostEqual(x['capture'],x['late_selected']/x['late_applications'],places=7)
   if x['capacity']==1:self.assertEqual(x['late_selected'],x['late_applications']);self.assertEqual(x['capture'],1)
 def test_every_model_has_identical_capacity_cohorts(self):
  base={(x['prefix'],x['capacity']):(x['applications'],x['late_applications'],x['selected']) for x in T['late_frontier'] if x['model']=='pooled_km'}
  for x in T['late_frontier']:self.assertEqual(base[x['prefix'],x['capacity']],(x['applications'],x['late_applications'],x['selected']))
 def test_diagnostic_coverage_and_restricted_means(self):
  for x in T['diagnostics']:
   self.assertGreaterEqual(x['prefixes'],30);self.assertTrue(0<=x['coverage_80']<=1)
   for k in ['mean_observed_restricted_days','mean_predicted_restricted_days']:self.assertTrue(1<=x[k]<=30)
 def test_primary_difference_matches_marginal_errors(self):
  means={x['model']:x['estimate'] for x in R['metrics'] if x['name']=='restricted_mae_days'}
  self.assertAlmostEqual(T['primary_difference']['estimate'],means['hazard_boosting']-means['stage_age_km'],places=7)
