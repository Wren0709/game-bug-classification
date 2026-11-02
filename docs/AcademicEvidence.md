# Technical evidence for academic review

This document identifies what can be verified in the repository. It does not claim equivalence to undergraduate computer science courses or automatic eligibility for any degree.

| Evidence | Location | Supported claim |
|---|---|---|
| Python data handling and input checks | `main.py`, `validate_data.py` | Reads labelled reports and checks required fields, IDs and duplicate descriptions. |
| Supervised text classification | `main.py` | Fits a TF-IDF + balanced Logistic Regression pipeline without fitting the vectoriser before cross-validation. |
| Original evaluation | `output/evaluation.txt`, `output/metrics.json`, `output/test_predictions.csv` | Original synthetic holdout accuracy 60.0%, macro-F1 0.600 and mean five-fold accuracy 68.6%. |
| Baselines and error analysis | `main.py`, `output/misclassified_reports.csv`, `output/confusion_matrix.png` | Compares against a trivial baseline and exports category-level errors. |
| Expanded synthetic experiment | `evaluate_expanded.py`, `docs/ExpandedExperiment.md`, `output/challenge_evaluation/` | Compares models trained on 140 and 240 synthetic reports using the same 50 held-out synthetic challenge reports. |
| Data provenance | `data/`, `docs/LabelGuidelines.md` | Fictional-only datasets; 150 additions drafted with generative-AI assistance; no employer records. |
| Software workflow and tests | `workbench.py`, `review_results.py`, `log_signals.py`, `tests/` | Batch spreadsheet import, manual review state, basic log indicators and 22 passing local tests. |
| Repeatability | `README.md`, `requirements.txt`, `.github/workflows/tests.yml` | Commands for validation, testing and experiments; CI configuration for new GitHub commits. |

**Scope:** This is a small, single-label text classification project and a separate command-line review workflow. It is not a deep-learning system. Neither synthetic evaluation establishes performance on real player reports. The proposed 50 manual QA cases were not executed. Code-level evidence of formal data structures, advanced algorithms or AI architecture coursework is not provided.

**Original experiment:** 140 synthetic reports; 35-report stratified holdout; Accuracy 60.0%; macro-F1 0.600; five-fold CV mean accuracy 68.6%. The smallest reported per-class F1 is Network (0.43). These figures describe seven test reports per class and are sensitive to the sample.

**Supplement:** 240-report synthetic training pool; 50 separate fictional challenge examples; original-trained and expanded-trained model accuracies 80.0% and 82.0%. The difference is one correct prediction and is not evidence of a meaningful real-world gain.

All results should be checked against the committed code and dataset versions before the report is sent to a university.
