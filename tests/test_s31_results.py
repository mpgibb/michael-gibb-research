"""Check exported actuarial totals and the public uncertainty contract."""
import json
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/'studies/S31/results/result.json'
@unittest.skipUnless(PATH.exists(),'S31 has not yet been evaluated')
class InsuranceResultChecks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=json.loads(PATH.read_text())
 def test_split_and_claim_conservation(self):
  s=self.r['samples'];self.assertEqual(s['development']+s['validation']+s['test'],s['total']);self.assertEqual(s['final_fit_claims']+s['test_claims'],s['total_claims'])
 def test_premium_decomposition_and_shared_cohorts(self):
  for scenario in self.r['tables']['scenarios'].values():
   for x in scenario['segments']:
    self.assertGreaterEqual(x['policies'],500)
    self.assertAlmostEqual(x['predicted_pure_premium']*x['exposure_years'],x['predicted_loss_eur'],delta=.01)
    if x['predicted_frequency'] is not None:self.assertAlmostEqual(x['predicted_frequency']*x['predicted_severity'],x['predicted_pure_premium'],delta=.001)
    else:self.assertEqual(x['model'],'tweedie');self.assertIsNone(x['predicted_severity'])
    self.assertLessEqual(x['ratio_lower'],x['ratio_upper'])
 def test_calibration_conserves_final_policy_and_claim_counts(self):
  for scenario in self.r['tables']['scenarios'].values():
   for model in self.r['models']:
    rows=[x for x in scenario['calibration'] if x['model']==model['id']]
    self.assertEqual(len(rows),10);self.assertEqual(sum(x['policies'] for x in rows),self.r['samples']['test']);self.assertEqual(sum(x['claims'] for x in rows),self.r['samples']['test_claims'])
 def test_tail_target_and_geographic_separation(self):
  t=self.r['tables'];u=t['scenarios']['uncapped'];c=t['scenarios']['capped'];self.assertIsNone(u['claim_cap_eur']);self.assertEqual(c['claim_cap_eur'],50000)
  for a,b in zip(u['segments'],c['segments']):
   self.assertEqual((a['grouping'],a['group'],a['model'],a['claims']),(b['grouping'],b['group'],b['model'],b['claims']));self.assertGreaterEqual(a['observed_loss_eur'],b['observed_loss_eur'])
  self.assertTrue(t['geographic_stress']['region_feature_excluded']);self.assertEqual(t['geographic_stress']['region'],'Ile-de-France')
 def test_primary_difference_is_actual_model_difference(self):
  for s in [*self.r['tables']['scenarios'].values(),self.r['tables']['geographic_stress']]:
   values={x['model']:x['estimate'] for x in s['metrics'] if x['name']=='tweedie_deviance'}
   self.assertAlmostEqual(values['boosting']-values['glm'],s['primary_difference']['estimate'],places=7);self.assertEqual(s['primary_difference']['draws'],500)
