from pathlib import Path
import argparse

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
    normalized = reports.description.str.lower().str.replace(r"\s+", " ", regex=True)
    if normalized.duplicated().any():
        raise ValueError("Duplicate descriptions found")
    if reports.category.nunique() < 2 or reports.category.value_counts().min() < 5:
        raise ValueError("At least two categories with five examples each are required")
    return reports


def main():
    parser = argparse.ArgumentParser(description="Evaluate game bug report classification")
    parser.add_argument("--input", type=Path, default=BASE_DIR / "data" / "synthetic_bug_reports.csv")
    parser.add_argument("--output", type=Path, default=BASE_DIR / "output")
    args = parser.parse_args()

    reports = load_reports(args.input)
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
    report = classification_report(test.category, predictions, labels=labels, zero_division=0)

    args.output.mkdir(parents=True, exist_ok=True)
    matrix = confusion_matrix(test.category, predictions, labels=labels)
    fig, ax = plt.subplots(figsize=(9, 7))
    ConfusionMatrixDisplay(confusion_matrix=matrix, display_labels=labels).plot(
        ax=ax, cmap="Blues", xticks_rotation=45, colorbar=False
    )
    ax.set_title("Confusion matrix (synthetic holdout set)")
    fig.tight_layout()
    fig.savefig(args.output / "confusion_matrix.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    lines = [
        "Game bug report classification: synthetic dataset",
        f"Training reports: {len(train)}",
        f"Held-out reports: {len(test)}",
        f"Model accuracy: {accuracy:.3f}",
        f"Model macro F1: {macro_f1:.3f}",
        f"Most frequent baseline accuracy: {baseline_accuracy:.3f}",
        f"Most frequent baseline macro F1: {baseline_f1:.3f}",
        f"Five-fold CV accuracy: {fold_accuracy.mean():.3f} +/- {fold_accuracy.std():.3f}",
        f"Five-fold CV macro F1: {fold_f1.mean():.3f} +/- {fold_f1.std():.3f}",
        "", report,
        "These fictional reports are not an independent real-world benchmark.",
        "Random splitting cannot rule out scenario similarity across the sets.",
    ]
    (args.output / "evaluation.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    results = test[["report_id", "title", "description", "category"]].copy()
    results = results.rename(columns={"category": "actual_category"})
    results["predicted_category"] = predictions
    results["correct"] = results.actual_category == results.predicted_category
    results.sort_values("report_id").to_csv(args.output / "test_predictions.csv", index=False)
    results.loc[~results.correct].sort_values("report_id").to_csv(args.output / "misclassified_reports.csv", index=False)

    reports.category.value_counts().sort_index().plot.bar(title="Synthetic reports by category")
    plt.xlabel("Category")
    plt.ylabel("Reports")
    plt.tight_layout()
    plt.savefig(args.output / "category_counts.png", dpi=160)
    plt.close()

    print("\n".join(lines[:9]))
    print(f"Saved evaluation files to {args.output}")


if __name__ == "__main__":
    main()
