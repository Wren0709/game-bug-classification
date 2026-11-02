# Expanded synthetic dataset and evaluation

## Question

Does the same text-classification pipeline behave differently when trained on 240 rather than 140 fictional bug reports?

## Data

The original dataset contains 140 fictional reports, evenly divided across Audio, Gameplay, Network, Performance and UI. The expanded version preserves all 140 original records and adds 100 new records (20 per category). Another 50 records (10 per category) form a separate challenge set and are not included in either training pool. All 150 new records were drafted with generative-AI assistance and are labelled synthetic. None comes from company records or observed player feedback.

The reports deliberately include different interfaces, save systems, sessions and multiplayer scenarios. They were checked for schema consistency, category counts and exact duplicate descriptions. Some scenarios still resemble one another, and a manually authored label is not proof that a real bug would have that root cause.

## Method

Both training pools use the same scikit-learn pipeline: TF-IDF with word unigrams and bigrams, followed by balanced Logistic Regression. Each model is trained on its own complete pool and evaluated on the same 50 challenge descriptions. Neither model is trained on those 50 records. Accuracy and macro-F1 are computed from the same labels. The evaluation exports each prediction and its correctness, per-class results, confusion matrices, package versions and source-file hashes.

The expanded 240-report pool is also evaluated separately using a stratified 75/25 holdout split and five-fold cross-validation, following the original `main.py` procedure. Those holdout results do not use the same examples as the original 140-report experiment and are not a like-for-like performance comparison.

## Recorded results

| Evaluation | Original 140 | Expanded 240 |
|---|---:|---:|
| Synthetic challenge, n=50: accuracy | 80.0% | 82.0% |
| Synthetic challenge, n=50: macro-F1 | 0.805 | 0.822 |

For the expanded dataset's separate development split, holdout accuracy was **71.7%**, macro-F1 **0.714**, and five-fold mean accuracy **77.9%**. These results are recorded in `output/expanded_development/`.

The original experiment remains **60.0% holdout accuracy**, **0.600 macro-F1**, and **68.6% five-fold mean accuracy**, using the original 140 records. The new results are not replacements for those figures.

## Interpretation

The expanded model classified one more challenge report correctly (41 rather than 40 out of 50). With such a small, synthetic challenge set, the difference is not meaningful evidence that a larger training dataset improves performance in practice. The models were assessed on fictional reports written for this project, not on independent real player feedback. Some scenarios and vocabulary overlap across the datasets; evaluation could therefore be optimistic.

For a stronger study, the next step would be to obtain permitted, independently sourced public issue reports, establish an annotation guide and a separate test split before training, and inspect per-class errors. Model selection or tuning should not use the final test set. No performance claim is made for production defect triage.

## Reproduction

```bash
python validate_data.py
python -m unittest discover -s tests -v
python main.py --input data/synthetic_bug_reports_expanded.csv --output private/expanded_development
python evaluate_expanded.py --output private/expanded_challenge
```

The checked-in expanded results were generated using Python 3.13.5; package versions are recorded in the result files. Use `requirements.txt` for installation. `requirements_expanded_tested.txt` records the main package versions used for this run.
