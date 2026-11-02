from pathlib import Path
import argparse
import hashlib
import json
import platform

import sklearn
from rules import rule_prediction
from csv_output import write_csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import make_pipeline

BASE_DIR = Path(__file__).resolve().parent


def build_model():
    return make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=1),
        LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42),
    )


def load_reports(path):
    reports = pd.read_csv(path, keep_default_na=False)
    required = {"report_id", "title", "description", "category"}
    if not required.issubset(reports.columns):
        raise ValueError(f"Required dataset columns: {', '.join(sorted(required))}")
    for field in required:
        reports[field] = reports[field].astype(str).str.strip()
        if reports[field].eq("").any():
            raise ValueError(f"Empty values found in {field}")
    allowed_categories = {"Audio", "Gameplay", "Network", "Performance", "UI"}
    if set(reports.category) - allowed_categories:
        raise ValueError("Unexpected report category")
    if reports.report_id.duplicated().any():
        raise ValueError("Duplicate report IDs found")
    normalized = reports.description.str.normalize("NFKC").str.casefold().str.replace(r"[\W_]+", "", regex=True)
    if normalized.duplicated().any():
        raise ValueError("Duplicate descriptions found")
    if reports.category.nunique() < 2 or reports.category.value_counts().min() < 5:
        raise ValueError("At least two categories with five examples each are required")
    return reports


def main():
    parser = argparse.ArgumentParser(description="Evaluate game bug report classification")
    parser.add_argument("--input", type=Path, default=BASE_DIR / "data" / "synthetic_bug_reports.csv")
    parser.add_argument("--output", type=Path, default=BASE_DIR / "private" / "evaluation")
    args = parser.parse_args()
    if args.output.exists() and any(args.output.iterdir()):
        parser.error("Output folder is not empty. Choose another --output to keep previous results.")

    reports = load_reports(args.input)
    synthetic = "data_source" in reports and reports.data_source.str.contains("synthetic", case=False).all()
    dataset_kind = "synthetic dataset" if synthetic else "user supplied dataset"
    train, test = train_test_split(reports, test_size=0.25, stratify=reports.category, random_state=42)
    model = build_model()
    model.fit(train.description, train.category)
    predictions = model.predict(test.description)

    baseline = DummyClassifier(strategy="most_frequent")
    baseline.fit(train[["description"]], train.category)
    baseline_predictions = baseline.predict(test[["description"]])

    accuracy = accuracy_score(test.category, predictions)
    macro_f1 = f1_score(test.category, predictions, average="macro", zero_division=0)
    baseline_accuracy = accuracy_score(test.category, baseline_predictions)
    rule_predictions = [rule_prediction(text)[0] or "Unanalysable" for text in test.description]
    rule_accuracy = accuracy_score(test.category, rule_predictions)
    rule_f1 = f1_score(test.category, rule_predictions, labels=sorted(reports.category.unique()), average="macro", zero_division=0)
    baseline_f1 = f1_score(test.category, baseline_predictions, average="macro", zero_division=0)
    labels = sorted(reports.category.unique())
    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_validate(
        build_model(),
        reports.description,
        reports.category,
        cv=folds,
        scoring={"accuracy": "accuracy", "macro_f1": "f1_macro"},
    )
    fold_accuracy = scores["test_accuracy"]
    fold_f1 = scores["test_macro_f1"]
    report = classification_report(test.category, predictions, labels=labels, zero_division=0).replace("f1-score", "f1 score")

    args.output.mkdir(parents=True, exist_ok=True)
    matrix = confusion_matrix(test.category, predictions, labels=labels)
    fig, ax = plt.subplots(figsize=(9, 7))
    ConfusionMatrixDisplay(confusion_matrix=matrix, display_labels=labels).plot(
        ax=ax, cmap="Blues", xticks_rotation=45, colorbar=False
    )
    ax.set_title(f"Confusion matrix ({dataset_kind} holdout)")
    fig.tight_layout()
    fig.savefig(args.output / "confusion_matrix.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    lines = [
        f"Game bug report classification: {dataset_kind}",
        f"Training reports: {len(train)}",
        f"Holdout reports: {len(test)}",
        f"Model accuracy: {accuracy:.3f}",
        f"Model macro F1: {macro_f1:.3f}",
        f"Most frequent baseline accuracy: {baseline_accuracy:.3f}",
        f"Most frequent baseline macro F1: {baseline_f1:.3f}",
        f"Five fold CV accuracy: {fold_accuracy.mean():.3f} ± {fold_accuracy.std():.3f}",
        f"Five fold CV macro F1: {fold_f1.mean():.3f} ± {fold_f1.std():.3f}",
        f"Keyword baseline accuracy: {rule_accuracy:.3f}",
        f"Keyword baseline macro F1: {rule_f1:.3f}",
        "Keyword ties/no matches abstain and count as incorrect.",
        "", report,
        "This development evaluation does not establish independent real world performance.",
        "Random splitting cannot rule out scenario similarity across the sets.",
    ]
    (args.output / "evaluation.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    results = test[["report_id", "title", "description", "category"]].copy()
    results = results.rename(columns={"category": "actual_category"})
    results["predicted_category"] = predictions
    results["rule_category"] = rule_predictions
    results["model_score"] = model.predict_proba(test.description).max(axis=1)
    results["correct"] = results.actual_category == results.predicted_category
    write_csv(results.sort_values("report_id"), args.output / "test_predictions.csv")
    write_csv(results.loc[~results.correct].sort_values("report_id"), args.output / "misclassified_reports.csv")

    reports.category.value_counts().sort_index().plot.bar(title=f"Reports by category ({dataset_kind})")
    plt.xlabel("Category")
    plt.ylabel("Reports")
    plt.tight_layout()
    plt.savefig(args.output / "category_counts.png", dpi=160)
    plt.close()

    metrics = {
        "dataset_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
        "python": platform.python_version(), "scikit_learn": sklearn.__version__,
        "seed": 42, "train_count": len(train), "test_count": len(test),
        "model": {"accuracy": accuracy, "macro_f1": macro_f1},
        "majority_baseline": {"accuracy": baseline_accuracy, "macro_f1": baseline_f1},
        "keyword_baseline": {"accuracy": rule_accuracy, "macro_f1": rule_f1},
        "cross_validation": {"accuracy": fold_accuracy.tolist(), "macro_f1": fold_f1.tolist()},
        "dataset_kind": dataset_kind,
        "scope": "Development benchmark, not independent real world validation",
    }
    (args.output / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    split = reports[["report_id"]].copy()
    split["split"] = split.report_id.isin(test.report_id).map({True: "test", False: "train"})
    write_csv(split, args.output / "split.csv")
    print("\n".join(lines[:12]))
    print(f"Saved evaluation files to {args.output}")


if __name__ == "__main__":
    main()
