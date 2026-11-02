import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from log_signals import detect_signals, read_log
from review_results import apply_reviews
from workbench import analyse_feedback, load_feedback


class WorkbenchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data = []
        for label, keyword in [("Audio", "sound"), ("Gameplay", "quest"), ("Network", "disconnect"),
                              ("Performance", "stutter"), ("UI", "button")]:
            data.extend([(f"{keyword} bug scenario {i}", label) for i in range(5)])
        model = make_pipeline(TfidfVectorizer(), LogisticRegression(max_iter=500))
        model.fit([x[0] for x in data], [x[1] for x in data])
        cls.model = model

    def test_blank_description_remains_unresolved(self):
        frame = pd.DataFrame({"id": ["1", "2"], "description": ["", "The lobby disconnects"],
                              "log_excerpt": ["Fatal exception", "connection timed out"]})
        result = analyse_feedback(frame, self.model, "description", "id", log_column="log_excerpt")
        self.assertEqual(result.loc[0, "review_status"], "unresolved")
        self.assertEqual(result.loc[0, "review_reason"], "empty_description")
        self.assertEqual(result.loc[1, "review_status"], "needs_review")
        self.assertIn("network", result.loc[1, "log_signals"])
        self.assertIn("exception", result.loc[0, "log_signals"])

    def test_unchecked_labels_are_not_final(self):
        frame = pd.DataFrame({"review_status": ["needs_review", "unresolved"],
                              "reviewed_category": ["", ""], "suggested_category": ["Audio", ""]})
        result = apply_reviews(frame)
        self.assertTrue(result.final_category.eq("").all())

    def test_manual_review_sets_final_label(self):
        frame = pd.DataFrame({"review_status": ["needs_review"], "reviewed_category": ["UI"],
                              "suggested_category": ["Audio"]})
        result = apply_reviews(frame)
        self.assertEqual(result.loc[0, "final_category"], "UI")
        self.assertEqual(result.loc[0, "review_status"], "reviewed")

    def test_invalid_review_label_is_rejected(self):
        frame = pd.DataFrame({"review_status": ["needs_review"], "reviewed_category": ["Security"],
                              "suggested_category": ["Audio"]})
        with self.assertRaises(ValueError):
            apply_reviews(frame)

    def test_mismatched_headers_fail(self):
        with self.assertRaises(ValueError):
            analyse_feedback(pd.DataFrame({"wrong": ["foo"]}), self.model, "description")

    def test_csv_and_xlsx_import(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            frame = pd.DataFrame({"id": ["1"], "description": ["sample"]})
            frame.to_csv(folder / "test.csv", index=False)
            frame.to_excel(folder / "test.xlsx", index=False)
            self.assertEqual(len(load_feedback(folder / "test.csv")), 1)
            self.assertEqual(len(load_feedback(folder / "test.xlsx")), 1)

    def test_log_path_cannot_escape_directory(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "x.log").write_text("[WARN] disconnected", encoding="utf-8")
            self.assertIn("disconnected", read_log("x.log", root)[0])
            content, reason = read_log("../secret.log", root)
            self.assertEqual(content, "")
            self.assertEqual(reason, "log_file_unavailable")

    def test_log_patterns_not_root_cause_claim(self):
        self.assertEqual(detect_signals("no known issue"), [])
        self.assertIn("memory", detect_signals("out of memory"))


if __name__ == "__main__":
    unittest.main()
