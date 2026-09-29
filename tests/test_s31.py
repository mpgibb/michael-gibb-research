"""Consequential actuarial grain, target, leakage and arithmetic checks."""
import importlib.util
from pathlib import Path
import sys
import unittest
import numpy as np
import pandas as pd
from sklearn.metrics import mean_tweedie_deviance

ROOT = Path(__file__).resolve().parents[1]
def module(name):
    spec = importlib.util.spec_from_file_location('s31_' + name, ROOT / 'studies/S31' / (name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
ingest, models = module('ingest'), module('models')


class ActuarialChecks(unittest.TestCase):
    def test_equal_claim_amounts_are_not_deleted(self):
        f = pd.DataFrame({'IDpol': ['a', 'b'], 'ClaimNb': [2, 0], 'Exposure': [2.01, .4]})
        s = pd.DataFrame({'IDpol': ['a', 'a'], 'ClaimAmount': [60000., 60000.]})
        joined = ingest.join_claims(f, s)
        self.assertEqual(joined.Loss.tolist(), [120000, 0])
        self.assertEqual(joined.CappedLoss.tolist(), [100000, 0])
        self.assertEqual(joined.Exposure.iloc[0], 2.01)

    def test_claim_count_mismatch_fails(self):
        f = pd.DataFrame({'IDpol': ['a'], 'ClaimNb': [2], 'Exposure': [1]})
        s = pd.DataFrame({'IDpol': ['a'], 'ClaimAmount': [10]})
        with self.assertRaises(ValueError):
            ingest.join_claims(f, s)

    def test_text_factor_ids_not_factor_codes(self):
        f = pd.DataFrame({'IDpol': pd.Categorical(['a', 'b'], categories=['a', 'b']), 'ClaimNb': [1, 0], 'Exposure': [1, 1]})
        s = pd.DataFrame({'IDpol': pd.Categorical(['a'], categories=['b', 'a']), 'ClaimAmount': [10]})
        self.assertEqual(ingest.join_claims(f, s).Loss.tolist(), [10, 0])

    def test_split_is_policy_stable_and_exhaustive(self):
        ids = ['1', '2', '1', '999']
        masks = ingest.split_masks(ids)
        self.assertTrue(np.all(np.sum(masks, axis=0) == 1))
        for mask in masks:
            self.assertEqual(mask[0], mask[2])
        reverse = ingest.split_masks(ids[::-1])
        for a, b in zip(masks, reverse):
            np.testing.assert_equal(a, b[::-1])

    def test_deviance_matches_library_with_zero_outcomes(self):
        y, p, w = np.array([0., 4., 80.]), np.array([5., 3., 20.]), np.array([.1, 2., 1.])
        self.assertAlmostEqual(np.average(models.deviance_rows(y, p), weights=w), mean_tweedie_deviance(y, p, power=1.5, sample_weight=w))

    def test_frequency_exposure_identity(self):
        counts, exposure = np.array([0., 2., 5.]), np.array([.2, 2., .5])
        rates = np.array([.3, 1.1, 4.])
        rate_objective = np.sum(exposure * (rates - (counts / exposure) * np.log(rates)))
        count_objective = np.sum(exposure * rates - counts * np.log(exposure * rates))
        self.assertAlmostEqual(rate_objective - count_objective, np.sum(counts * np.log(exposure)))

    def test_severity_aggregate_gamma_score_identity(self):
        amounts = np.array([2., 8., 5.])
        predictions = np.array([4., 4., 6.])
        claim_score = np.sum(amounts / predictions + np.log(predictions))
        policy_score = 2 * (5 / 4 + np.log(4)) + 5 / 6 + np.log(6)
        self.assertAlmostEqual(claim_score, policy_score)

    def test_feature_cutoff_and_geographic_ablation(self):
        frame = pd.DataFrame({'DrivAge': [30], 'VehAge': [4], 'BonusMalus': [50], 'Density': [10], 'Area': ['A'], 'VehPower': [4], 'VehBrand': ['B1'], 'VehGas': ['Diesel'], 'Region': ['Test'], 'IDpol': ['abc'], 'ClaimNb': [1], 'Loss': [100], 'Exposure': [.4]})
        self.assertFalse(set(['IDpol', 'ClaimNb', 'Loss', 'Exposure']) & set(models.features(frame)))
        self.assertNotIn('Region', models.features(frame, geography=False))
        frame.columns = pd.Index([np.str_(name) for name in frame.columns], dtype=object)
        self.assertTrue(all(type(name) is str for name in models.features(frame).columns))

    def test_expense_assumption_boundaries(self):
        self.assertEqual(models.expense_premium(100, 0), 100)
        self.assertEqual(models.expense_premium(100, .5), 200)
        with self.assertRaises(ValueError):
            models.expense_premium(100, 1)


if __name__ == '__main__':
    unittest.main()
