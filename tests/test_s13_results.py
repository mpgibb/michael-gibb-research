"""Assert completed screening evidence and publication-safe aggregation."""
import json,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'studies/S13/results/result.json'
@unittest.skipUnless(P.exists(),'S13 not evaluated')
class ScreeningResults(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=json.loads(P.read_text())
 def test_partition_identity(self):
  s=self.r['samples'];self.assertEqual(s['development']+s['validation'],s['final_fit']);self.assertEqual(s['final_fit']+s['test'],s['total']);self.assertEqual(s['test_failures'],22)
 def test_capacity_conservation_and_monotonicity(self):
  r=self.r
  for model in ['elastic_net','pca_monitor','boosting','boosting_no_missing']:
   rows=[x for x in r['tables']['capacity'] if x['model']==model];self.assertEqual([x['detected_failures'] for x in rows],sorted(x['detected_failures'] for x in rows))
   for x in rows:self.assertEqual(x['detected_failures']+x['missed_failures'],22);self.assertEqual(x['detected_failures']+x['unnecessary_inspections'],x['inspections'])
 def test_calibration_accounts_for_entire_cohort(self):
  for model in self.r['models']:
   rows=[x for x in self.r['tables']['calibration'] if x['model']==model['id']];self.assertEqual(sum(x['entities'] for x in rows),359);self.assertEqual(sum(x['failures'] for x in rows),22)
 def test_primary_uncertainty_not_selective(self):
  p=self.r['tables']['primary_difference'];self.assertLess(p['lower'],0);self.assertGreater(p['upper'],0);self.assertEqual(p['valid_draws'],1000)
 def test_stability_and_convergence(self):
  rows=self.r['tables']['stability_runs'];self.assertEqual(len(rows),30);self.assertTrue(all(x['iterations']<20000 for x in rows));self.assertTrue(all(0<=x['selection_frequency']<=x['availability_frequency']<=1 for x in self.r['tables']['sensor_stability']))
