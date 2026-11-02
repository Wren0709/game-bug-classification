import csv
import json
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from csv_output import write_csv
from log_signals import MAX_LOG_CHARS, read_log
from review_results import apply_reviews
from workbench import analyse_feedback
import test_workbench


class ExportTests(unittest.TestCase):
    def test_extra_personal_columns_are_not_exported(self):
        source = pd.DataFrame({
            'description': ['A sound stops'], 'email': ['example@example.invalid'],
            'password': ['fictional secret'], 'source_record_url': ['private link'],
            'log_excerpt': ['memory allocation failed'],
        })
        test_workbench.WorkbenchTests.setUpClass()
        result = analyse_feedback(source, test_workbench.WorkbenchTests.model, 'description', log_column='log_excerpt')
        self.assertNotIn('email', result)
        self.assertNotIn('password', result)
        self.assertNotIn('log_excerpt', result)
        self.assertEqual(result.loc[0, 'source_record_url'], '')
        self.assertEqual(result.loc[0, 'log_signals'], 'memory')

    def test_review_export_drops_added_columns(self):
        frame = pd.DataFrame({'review_status': ['needs_review'], 'reviewed_category': ['UI'],
                              'suggested_category': ['Audio'], 'email': ['example@example.invalid']})
        self.assertNotIn('email', apply_reviews(frame))

    def test_formula_cells_are_text_in_csv(self):
        values = ['=1+1', '  +1', '-1', '@SUM(1)', '\t=1', '\n=1', '\r=1', 'ordinary text']
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'safe.csv'
            write_csv(pd.DataFrame({'description': values}), path)
            with path.open(encoding='utf-8-sig', newline='') as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual([r['description'] for r in rows], ["'" + v for v in values[:-1]] + [values[-1]])

    def test_output_not_replaced_without_explicit_option(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'review.csv'
            path.write_text('keep existing review', encoding='utf-8')
            with self.assertRaises(FileExistsError):
                write_csv(pd.DataFrame({'description': ['new']}), path)
            self.assertEqual(path.read_text(), 'keep existing review')
            write_csv(pd.DataFrame({'description': ['new']}), path, overwrite=True)
            self.assertIn('new', path.read_text(encoding='utf-8-sig'))


class ReviewStateTests(unittest.TestCase):
    def test_clearing_review_reopens_row(self):
        source = pd.DataFrame({'description': ['Menu is missing', ''],
                               'review_status': ['reviewed', 'reviewed'],
                               'reviewed_category': ['', ''], 'suggested_category': ['UI', ''],
                               'final_category': ['UI', 'UI']})
        result = apply_reviews(source)
        self.assertEqual(result.review_status.tolist(), ['needs_review', 'unresolved'])
        self.assertEqual(result.final_category.tolist(), ['', ''])
        self.assertEqual(apply_reviews(result).to_dict(), result.to_dict())

    def test_whitespace_in_review_category_is_normalized(self):
        result = apply_reviews(pd.DataFrame({'description': ['Menu is missing'],
            'review_status': ['needs_review'], 'reviewed_category': [' UI '], 'suggested_category': ['Audio']}))
        self.assertEqual(result.loc[0, 'reviewed_category'], 'UI')
        self.assertEqual(result.loc[0, 'final_category'], 'UI')
        self.assertEqual(result.loc[0, 'review_status'], 'reviewed')


class LogReadTests(unittest.TestCase):
    def test_long_log_is_truncated_with_notice(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'sample.log'
            path.write_text('x' * (MAX_LOG_CHARS + 100), encoding='utf-8')
            content, note = read_log(path.name, directory)
            self.assertEqual(len(content), MAX_LOG_CHARS)
            self.assertEqual(note, 'log_truncated')

    def test_missing_log_directory_is_visible(self):
        from main import build_model, load_reports
        root = Path(__file__).resolve().parents[1]
        data = load_reports(root / 'data/synthetic_bug_reports.csv')
        model = build_model().fit(data.description, data.category)
        result = analyse_feedback(pd.DataFrame({'description': ['A sound stops'],
            'log_file': ['sample.log']}), model, 'description')
        self.assertEqual(result.loc[0, 'log_note'], 'log_file_not_loaded')


class EvaluationFilesTests(unittest.TestCase):
    def test_recorded_results_match_the_bundled_data(self):
        root = Path(__file__).resolve().parents[1]
        metrics = json.loads((root / 'output/metrics.json').read_text())
        self.assertEqual(metrics['dataset_sha256'], hashlib.sha256((root / 'data/synthetic_bug_reports.csv').read_bytes()).hexdigest())
        predictions = pd.read_csv(root / 'output/test_predictions.csv')
        accuracy = (predictions.actual_category == predictions.predicted_category).mean()
        self.assertAlmostEqual(metrics['model']['accuracy'], accuracy)
        split = pd.read_csv(root / 'output/split.csv')
        self.assertEqual(set(predictions.report_id), set(split.loc[split.split == 'test', 'report_id']))
        self.assertEqual(len(split), 140)
        self.assertEqual(len(predictions), 35)
