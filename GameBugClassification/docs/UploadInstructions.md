# Uploading the project

Target: https://github.com/Wren0709/game-bug-classification

This package contains the complete classification experiment and review workflow. It can be used on its own; it no longer depends on files left in an older repository.

## Before uploading

1. Unzip the package. The Python scripts and folders are at the top level of the extracted package.
2. Follow the README to install dependencies, validate the data and run the tests.
3. Check the files you are about to upload. Only the supplied fictional data and its evaluation results belong in the public repository.

The internship background and academic evidence notes are intentionally retained. Upload a technical report as a separate admissions attachment if needed; it does not need to be published here.

## GitHub website

Use **Add file → Upload files** in the repository. Upload the extracted source files and their folders, not the ZIP itself or an extra wrapper folder. GitHub does not extract ZIP files into source files.

Replace files with matching names, including README, requirements and the Python scripts. Keep the supplied `data/` and `output/` folders together: the reported evaluation refers to this exact dataset. Uploading these files does not remove unrelated files already in the repository; review those separately.

## Git command line

Copy the package contents into a local clone, preserving relative paths. Then run:

```bash
git status --short
git add README.md .gitignore .gitattributes requirements.txt requirements_tested.txt requirements_expanded_tested.txt main.py evaluate_expanded.py rules.py validate_data.py classify_reports.py workbench.py log_signals.py review_results.py csv_output.py data examples tests docs output
git diff --cached --stat
git diff --cached
git commit -m "Add synthetic expansion and a separate challenge evaluation"
git push
```

Do not add real feedback, credentials, local environments or files from `private/` and `incoming/`. Ignore rules do not protect files already tracked by Git. Check the staged diff before committing.

## What changed in this version

- `data/synthetic_bug_reports.csv` and the original `output/` result files are unchanged.
- `data/synthetic_bug_reports_expanded.csv` includes 100 additional AI-assisted fictional reports.
- `data/synthetic_challenge_reports.csv` contains 50 additional fictional reports reserved for evaluation.
- `evaluate_expanded.py` compares both training pools on the same challenge set.
- New results and experiment notes are stored separately under `output/` and `docs/`.

If your repository already contains files with these names, compare them before replacing anything. After uploading, open `README.md`, verify the two `output/` subdirectories and confirm that no private files were added.
