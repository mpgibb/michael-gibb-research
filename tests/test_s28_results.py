"""Independent checks of saved counts, scores and policy accounting."""
import json
import unittest
import numpy as np
from research_program.io import ROOT


class SavedResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads((ROOT/'studies/S28/results/result.json').read_text())

    def test_disjoint_partition_conserves_source_population(self):
        s = self.result['samples']
        self.assertEqual(s['train'] + s['calibration'] + s['test'], s['total'])
        self.assertEqual(sum(s['events'].values()), 4640)
        self.assertEqual(s['test'], 8238)

    def test_frontiers_conserve_counts_and_capture(self):
        s = self.result['samples']
        for row in self.result['tables']['capacity_frontier']:
            self.assertEqual(row['selected'], int(s['test'] * row['capacity']))
            self.assertAlmostEqual(row['precision'] * row['selected'], row['responses'], delta=0.0001)
            self.assertAlmostEqual(row['capture'] * s['events']['test'], row['responses'], delta=0.0001)
            if row['capacity'] == 1:
                self.assertEqual(row['responses'], s['events']['test'])
            if row['model'] == 'random':
                self.assertAlmostEqual(row['precision'], s['events']['test']/s['test'], places=7)

    def test_constant_forecast_score_from_closed_form(self):
        s=self.result['samples']; prevalence=s['events']['test']/s['test']; p=s['events']['calibration']/s['calibration']
        expected=-prevalence*np.log(p)-(1-prevalence)*np.log(1-p)
        actual=next(m['estimate'] for m in self.result['metrics'] if m['model']=='random' and m['name']=='log_loss')
        self.assertAlmostEqual(actual, expected, places=7)

    def test_calibration_and_periods_preserve_holdout(self):
        s=self.result['samples']
        for model in self.result['models']:
            bins=[b for b in self.result['tables']['calibration'] if b['model']==model['id']]
            periods=[b for b in self.result['tables']['periods'] if b['model']==model['id']]
            self.assertEqual(sum(b['n'] for b in bins),s['test'])
            self.assertAlmostEqual(sum(b['n']*b['observed'] for b in bins),s['events']['test'],delta=.001)
            self.assertEqual(sum(b['events'] for b in periods),s['events']['test'])

    def test_principal_family_selected_without_final_metrics(self):
        tuning=self.result['tables']['tuning']
        winner=min(tuning,key=lambda row:row['mean_log_loss'])['model']
        self.assertEqual(self.result['tables']['selected_model'],winner)
        m={(r['model'],r['name']):r['estimate'] for r in self.result['metrics']}
        for row in self.result['tables']['block_sensitivity']:
            self.assertAlmostEqual(row['estimate'],m[(winner,'log_loss')]-m[('business_rule','log_loss')],places=7)


if __name__ == '__main__': unittest.main()
