# Game Bug Classification and Analysis System

A small Python tool for sorting game feedback and reviewing the results in a spreadsheet. It suggests categories and picks out a few log keywords. It does not reproduce bugs or identify their root causes.

The project grew out of questions raised during a game testing internship. All examples in this public repository are fictional. No employer files, internal reports or private player data are included.

## Getting started

Use Python 3.11 or later. Open a terminal in this folder, then run:

```bash
python -m venv .venv
```

Activate the environment with `.venv\Scripts\activate` on Windows, or `source .venv/bin/activate` on macOS and Linux.

```bash
python -m pip install -r requirements.txt
python validate_data.py
python -m unittest discover -s tests -v
python workbench.py --input examples/sample_feedback.csv --id-col report_id --log-col log_excerpt --logs-dir examples
```

The worksheet is saved to `private/workbench_results.csv`. Open it in a spreadsheet editor, fill in `reviewed_category`, and save it as UTF-8 CSV. The accepted categories are `Audio`, `Gameplay`, `Network`, `Performance` and `UI`.

```bash
python review_results.py
```

This creates `private/reviewed_results.csv`. Suggestions and your final categories stay separate. Clearing a reviewed category returns the row to `needs_review`, or `unresolved` if its description is empty. The tool never treats a model suggestion as an accepted review.

Existing output files are kept. Choose another `--output` path for a new run, or pass `--overwrite` when you deliberately want to replace a worksheet.

## Using another spreadsheet

```bash
python workbench.py --input incoming/feedback.xlsx --text-col "Feedback" --output private/new_review.csv
```

Only the selected description and review fields are exported. To include a source ID, link or log excerpt, explicitly choose the column:

```bash
python workbench.py --input incoming/feedback.xlsx --text-col "Feedback" --id-col "Record ID" --url-col "Record URL" --log-col "Log excerpt" --output private/linked_review.csv
```

Source links are saved as text; they are not opened. Log excerpts are used to produce signals such as `network` or `memory`; the original excerpts are not copied to the output. Local logs need a `log_file` column and `--logs-dir`. Only `.txt` and `.log` files inside that folder are read, up to 100,000 characters per file. Missing and shortened logs are noted in the worksheet.

`classify_reports.py` uses the same arguments and workflow as `workbench.py`.

## Model evaluation

The original experiment uses 140 fictional reports, with 28 reports in each category. It fits TF-IDF and Logistic Regression in a single pipeline. The holdout split is stratified, with 105 training reports and 35 test reports. Cross-validation uses five stratified folds. Both use seed 42.

The bundled results were rerun on 2 November 2026:

| Measure | Result |
|---|---:|
| Holdout accuracy | 60.0% |
| Holdout macro-F1 | 0.600 |
| Five-fold mean accuracy | 68.6% |
| Most-frequent-class accuracy | 20.0% |

`output/evaluation.txt` contains the class-level results. `output/metrics.json` records the dataset SHA-256, package version, seed and fold scores. Predictions, split IDs and plots are included so the figures can be checked.

To rerun the experiment without replacing the bundled results:

```bash
python main.py
```

New evaluation files go to `private/evaluation`. If that folder already contains results, choose a different `--output` folder. `requirements_tested.txt` records the package versions used for the bundled run; `requirements.txt` allows compatible versions.

### Expanded synthetic experiment

An optional second experiment adds 100 fictional reports to the training pool (240 in total, 48 per category). A separate set of 50 fictional challenge reports (10 per category) is never used for training. These additions were drafted with AI assistance and are labelled as synthetic. They are not player submissions or evidence of performance in a live QA environment.

To repeat the expanded development evaluation, run:

```bash
python main.py --input data/synthetic_bug_reports_expanded.csv --output private/expanded_development
```

To compare a model fitted on the original 140 reports with the same model fitted on all 240, use the fixed 50-report challenge set:

```bash
python evaluate_expanded.py --output private/expanded_challenge
```

Recorded outputs are under `output/expanded_development/` and `output/challenge_evaluation/`. Both models use identical TF-IDF and Logistic Regression settings. On the synthetic challenge set, accuracy was **80.0%** for the original training pool and **82.0%** for the expanded pool. Macro-F1 was **0.805** and **0.822**, respectively. A difference of one correctly classified report out of 50 is not strong evidence of improvement. Similar issue scenarios may appear across the sets, so these numbers must not be described as real-world validation.

The original **60.0% / 0.600 / 68.6%** evaluation is unchanged. It uses a different dataset and split; its numbers must not be directly compared with the new 240-report holdout results. See `docs/ExpandedExperiment.md` for the experimental setup and limitations.

These scores describe a small synthetic dataset. Similar scenarios may occur in both training and test sets, and the scores do not establish accuracy on real player feedback. The model scores are not calibrated probabilities. No accuracy improvement is claimed for the spreadsheet workflow or log checks.

## What is included

- `main.py`, `rules.py`, `validate_data.py`: training, evaluation and data checks.
- `workbench.py`, `review_results.py`, `csv_output.py`, `log_signals.py`: import, review and export.
- `data/`: the original 140 fictional reports, a 240-report expanded training version, a separate 50-report synthetic challenge set, 50 proposed QA cases marked `Not run`, and an empty observation template.
- `examples/`, `tests/`: a small demo and automated tests.
- `output/`: original results plus separate expanded-development and challenge-test outputs.
- `docs/`: usage, upload and academic evidence notes.

This is a standalone command-line project. It does not include the separate team website, Feishu sync or an external AI service.

## Handling private data

Keep real input files in `incoming/` and results in `private/`. Both folders are ignored by Git. Extra spreadsheet columns, such as email addresses, are dropped from the review worksheet. Source IDs and URLs are included only when explicitly selected.

This is not automatic anonymisation: descriptions, selected IDs and links can still contain private information. Review them before sharing. `.gitignore` does not remove files already tracked by Git or erase repository history.

CSV cells that could be interpreted as formulas are prefixed with an apostrophe, including cells beginning with `=`, `+`, `-`, `@`, tab or a line break. The original input file is not changed. A spreadsheet application may display the apostrophe; removing it or resaving in another format can remove that protection.
