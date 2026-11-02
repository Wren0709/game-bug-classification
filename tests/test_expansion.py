import hashlib
import json
import sys
import unittest
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, f1_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evaluate_expanded import verify_datasets
from main import load_reports

ROOT = Path(__file__).resolve().parents[1]


class ExpandedExperimentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = load_reports(ROOT / 'data/synthetic_bug_reports.csv')
        cls.expanded = load_reports(ROOT / 'data/synthetic_bug_reports_expanded.csv')
        cls.challenge = load_reports(ROOT / 'data/synthetic_challenge_reports.csv')

    def test_data_is_separated_and_original_records_are_untouched(self):
        verify_datasets(self.original, self.expanded, self.challenge)
        self.assertEqual(len(self.original), 140)
        self.assertEqual(len(self.expanded), 240)
        self.assertEqual(len(self.challenge), 50)

    def test_supplemental_records_are_marked_as_synthetic(self):
        extra = self.expanded[~self.expanded.report_id.isin(self.original.report_id)]
        self.assertEqual(len(extra), 100)
        self.assertTrue(extra.data_source.str.contains('Synthetic').all())
        self.assertTrue(self.challenge.data_source.str.contains('Synthetic').all())

    def test_challenge_metrics_match_saved_predictions(self):
        output = ROOT / 'output/challenge_evaluation'
        saved = json.loads((output / 'challenge_metrics.json').read_text(encoding='utf-8'))
        preds = pd.read_csv(output / 'challenge_predictions.csv')
        self.assertEqual(len(preds), 50)
        for name in ('original_140','expanded_240'):
            self.assertAlmostEqual(saved['results'][name]['accuracy'],
                                   accuracy_score(preds.actual_category, preds[name + '_prediction']))
            self.assertAlmostEqual(saved['results'][name]['macro_f1'],
                                   f1_score(preds.actual_category, preds[name + '_prediction'], average='macro'))

    def test_saved_data_hashes_are_current(self):
        saved = json.loads((ROOT / 'output/challenge_evaluation/challenge_metrics.json').read_text(encoding='utf-8'))
        for filename, recorded_hash in saved['dataset_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT / 'data' / filename).read_bytes()).hexdigest(), recorded_hash)

    def test_original_evaluation_is_preserved(self):
        m = json.loads((ROOT / 'output/metrics.json').read_text(encoding='utf-8'))
        self.assertEqual(m['dataset_sha256'], hashlib.sha256((ROOT / 'data/synthetic_bug_reports.csv').read_bytes()).hexdigest())
        self.assertAlmostEqual(m['model']['accuracy'], .6)
        self.assertAlmostEqual(m['model']['macro_f1'], .6)
        self.assertAlmostEqual(sum(m['cross_validation']['accuracy']) / 5, .6857142857142857)


if __name__ == '__main__':
    unittest.main()
