"""Arithmetic and feasibility invariants of the published inventory evidence."""
import json,unittest
from pathlib import Path
R=json.loads((Path(__file__).resolve().parents[1]/'studies/S02/results/result.json').read_text());T=R['tables']
class SavedInventoryTests(unittest.TestCase):
 def test_final_windows_and_counts(self):
  self.assertEqual(R['samples']['test'],R['samples']['series']*R['samples']['origins'])
  self.assertEqual(sorted({x['origin'] for x in T['aggregate_forecasts']}),[1857,1885,1913,1941])
  self.assertLessEqual(max(x['last_target_day'] for x in T['calibration_origins']),1857)
 def test_aggregate_point_and_truth_are_additive(self):
  for origin in [1857,1885,1913,1941]:
   for model in [x['id'] for x in R['models']]:
    rows=[x for x in T['aggregate_forecasts'] if x['model']==model and x['origin']==origin]
    total=next(x for x in rows if x['level']=='total')
    for level in ['store','category']:
     for key in ['point_units','observed_sales_units']:
      self.assertAlmostEqual(sum(x[key] for x in rows if x['level']==level),total[key],places=5)
 def test_inventory_cost_and_hindsight_feasibility(self):
  for x in T['inventory_by_origin']:
   self.assertAlmostEqual(x['assumed_cost'],x['holding_unit_days']*x['holding_per_unit_day']+x['lost_units']*x['lost_sale_penalty'],places=5)
   self.assertGreaterEqual(x['regret'],-1e-7)
   self.assertAlmostEqual(x['regret'],x['assumed_cost']-x['hindsight_cost'],places=5)
 def test_complete_sensitivity_grid(self):
  self.assertEqual(len(T['inventory_scenarios']),36*4)
  self.assertEqual(len(T['inventory_by_origin']),36*4*4)
  for row in T['inventory_scenarios']:
   parts=[x for x in T['inventory_by_origin'] if x['scenario_id']==row['scenario_id'] and x['model']==row['model']]
   self.assertAlmostEqual(row['assumed_cost'],sum(x['assumed_cost'] for x in parts),places=5)
