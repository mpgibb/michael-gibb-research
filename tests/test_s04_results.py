"""Conservation and selection provenance for independent policy evidence."""
from pathlib import Path
import json,unittest
R=json.loads((Path(__file__).resolve().parents[1]/'studies/S04/results/result.json').read_text());T=R['tables']
class SavedUpliftTests(unittest.TestCase):
 def test_all_policies_share_endpoints(self):
  for name in [x['id'] for x in R['models']]:
   rows={x['capacity']:x for x in T['capacity_frontier'] if x['model']==name}
   self.assertEqual(rows[0]['estimate'],0)
   self.assertAlmostEqual(rows[1]['estimate'],T['all_vs_none']['estimate'],places=6)
 def test_selection_accounts_for_every_arm(self):
  for x in T['capacity_frontier']:
   self.assertAlmostEqual(x['selected'],x['selected_control']+x['selected_treated'],places=5)
   self.assertAlmostEqual(x['selected'],x['selected_fraction']*R['samples']['test'],delta=.003)
 def test_validation_alone_identifies_principal(self):
  self.assertEqual(T['selected_model'],max(T['tuning'],key=lambda x:x['validation_contrast_per_10000'])['model'])
 def test_event_cells_conserve_final_cohort(self):
  cells=T['audit']['partitions']['test']['cells'];self.assertEqual(sum(x['n'] for x in cells),R['samples']['test'])
  self.assertEqual(sum(x['n'] for x in cells if x['conversion']),R['samples']['events']['test'])
 def test_decile_counts_conserve_cohort(self):
  for name in [x['model'] for x in T['tuning']]:
   rows=[x for x in T['effect_calibration'] if x['model']==name]
   self.assertEqual(sum(x['n'] for x in rows),R['samples']['test'])
   self.assertEqual(sum(x['events'] for x in rows),R['samples']['events']['test'])
