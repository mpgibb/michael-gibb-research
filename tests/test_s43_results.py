"""Population conservation and interval display identities for property research."""
import json,unittest
from pathlib import Path
R=json.loads((Path(__file__).resolve().parents[1]/'studies/S43/results/result.json').read_text());T=R['tables']
class PropertyResultTests(unittest.TestCase):
 def test_validation_only_selection(self):self.assertEqual(T['selected_leaves'],min(T['tuning'],key=lambda x:x['validation_median_ape_pct'])['leaves'])
 def test_source_join_accounting(self):
  a=T['audit'];self.assertEqual(a['source_sales']-a['excluded_publisher_sale_flags']-a['excluded_remaining_duplicate_documents']-a['unmatched_sales'],a['matched_sales_before_scope'])
 def test_aggregate_profiles_obey_suppression(self):
  for x in T['profiles']:self.assertGreaterEqual(x['sales'],30);self.assertGreaterEqual(x['sales'],x['parcels']);self.assertTrue(x['median_lower_USD']<=x['prediction_median_USD']<=x['median_upper_USD'])
 def test_nominal_intervals_nest(self):
  for model in ['local_median','hedonic','spatial_boosting','physical_boosting']:
   rows=sorted([x for x in T['coverage'] if x['model']==model],key=lambda x:x['nominal']);self.assertEqual([x['log_radius'] for x in rows],sorted(x['log_radius'] for x in rows));self.assertEqual([x['coverage'] for x in rows],sorted(x['coverage'] for x in rows))
 def test_county_profile_matches_final_metrics(self):
  x=next(x for x in T['profiles'] if x['township']=='All townships' and x['size_profile']=='All sizes' and x['model']=='spatial_boosting' and x['nominal']==.9);self.assertEqual(x['sales'],R['samples']['test']);c=next(x for x in T['coverage'] if x['model']=='spatial_boosting' and x['nominal']==.9);self.assertEqual(x['coverage'],c['coverage'])
 def test_snapshot_precedes_every_cohort(self):
  for x in T['audit']['cohorts'].values():self.assertGreater(x['start'],'2024-04-10')
