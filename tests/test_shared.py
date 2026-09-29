import copy
import json
import unittest
import numpy as np
from research_program.evaluation import ranked_selection, circular_block_indices, calibration_bins, pass_power
from research_program.io import ROOT, normalized
from research_program.validate import validate_catalog


class SharedTests(unittest.TestCase):
    def test_capacity_edges_and_stable_ties(self):
        score = [1, 1, 1, 0]
        self.assertEqual(ranked_selection(score, .5).tolist(), [True, True, False, False])
        self.assertEqual(ranked_selection(score, 0).sum(), 0)
        self.assertEqual(ranked_selection(score, 1).sum(), 4)
        with self.assertRaises(ValueError): ranked_selection(score, 1.1)

    def test_block_resamples_preserve_adjacency(self):
        for indices in circular_block_indices(12, 3, 5, 4):
            self.assertEqual(len(indices), 12)
            np.testing.assert_array_equal(np.diff(indices.reshape(-1, 3), axis=1) % 12, np.ones((4, 2)))

    def test_calibration_conserves_count_and_events(self):
        bins = calibration_bins([0, 1, 1, 0], [0, .4, 1, .2])
        self.assertEqual(sum(b['n'] for b in bins), 4)
        self.assertEqual(sum(b['n'] * b['observed'] for b in bins), 2)

    def test_pass_power_requires_repeated_success(self):
        self.assertEqual(pass_power(2, 4, 2), 1/6)
        self.assertEqual(pass_power(1, 4, 2), 0)
        self.assertEqual(pass_power(4, 4, 3), 1)

    def test_catalog_cannot_publish_planned_or_duplicate_ids(self):
        catalog = json.loads((ROOT/'catalog/studies.json').read_text())
        validate_catalog(catalog)
        broken = copy.deepcopy(catalog); broken[0]['publication_status'] = 'published'
        with self.assertRaises(ValueError): validate_catalog(broken)
        broken = copy.deepcopy(catalog); broken[1]['id'] = broken[0]['id']
        with self.assertRaises(ValueError): validate_catalog(broken)

    def test_results_reject_nonfinite_and_preserve_boolean(self):
        self.assertIs(normalized(np.bool_(True)), True)
        with self.assertRaises(ValueError): normalized(float('nan'))


if __name__ == '__main__': unittest.main()
