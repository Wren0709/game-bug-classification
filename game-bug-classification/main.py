from pathlib import Path
import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, classification_report, f1_score,
    confusion_matrix, ConfusionMatrixDisplay,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline

BASE_DIR = Path(__file__).resolve().parent


def build_model():
    return make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True),
        LogisticRegression(max_iter=2000, random_state=42),
    )


def main():
    parser = argparse.ArgumentParser(description="Classify game bug reports")
    parser.add_argument("--input", type=Path, default=BASE_DIR / "data" / "demo_bug_reports.csv")
    parser.add_argument("--output", type=Path, default=BASE_DIR / "output")
    args = parser.parse_args()

    reports = pd.read_csv(args.input).dropna(subset=["description", "category"]).copy()
    if not {"report_id", "title", "description", "category"}.issubset(reports.columns):
        raise ValueError("Input needs report_id, title, description and category columns.")
    reports = reports.drop_duplicates(subset=["description"])
    if reports["report_id"].duplicated().any():
        raise ValueError("Report identifiers must be unique.")
    if len(reports) < 20 or reports["category"].nunique() < 2:
        raise ValueError("At least 20 labeled reports across two categories are needed.")
    if reports["category"].value_counts().min() < 2:
        raise ValueError("Each category needs at least two reports.")

    train_text, test_text, train_labels, test_labels = train_test_split(
        reports["description"].astype(str),
        reports["category"],
        test_size=0.25,
        random_state=42,
        stratify=reports["category"],
    )

    model = build_model()
    model.fit(train_text, train_labels)
    predicted_labels = model.predict(test_text)

    accuracy = accuracy_score(test_labels, predicted_labels)
    macro_f1 = f1_score(test_labels, predicted_labels, average="macro", zero_division=0)
    report = classification_report(test_labels, predicted_labels, zero_division=0)
    print(f"Hold-out accuracy (synthetic examples; n={len(test_labels)}): {accuracy:.3f}")
    print(f"Macro F1-score (sample data): {macro_f1:.3f}")
    print(report)

    args.output.mkdir(parents=True, exist_ok=True)
    labels = sorted(reports["category"].unique())
    matrix = confusion_matrix(test_labels, predicted_labels, labels=labels)
    fig, ax = plt.subplots(figsize=(9, 7))
    ConfusionMatrixDisplay(confusion_matrix=matrix, display_labels=labels).plot(
        ax=ax, cmap="Blues", xticks_rotation=45, colorbar=False
    )
    ax.set_title("Game Bug Classification - Confusion Matrix (Synthetic Data)")
    fig.tight_layout()
    fig.savefig(args.output / "confusion_matrix.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    (args.output / "evaluation.txt").write_text(
        f"Evaluation on fictional examples (n_train={len(train_labels)}, n_test={len(test_labels)})\nAccuracy: {accuracy:.3f}\n"
        f"Macro F1-score: {macro_f1:.3f}\n\n{report}\n"
        "Note: Illustrative score on a small fictional dataset. Not a real-world benchmark.\n",
        encoding="utf-8",
    )
    test_results = pd.DataFrame({
        "description": test_text.to_numpy(),
        "true_category": test_labels.to_numpy(),
        "predicted_category": predicted_labels,
    })
    test_results["needs_review"] = test_results["true_category"] != test_results["predicted_category"]
    test_results.to_csv(args.output / "test_predictions.csv", index=False, encoding="utf-8-sig")

    # This queue is an in-sample demonstration, not an independent evaluation.
    review_queue = reports[["report_id", "title", "description"]].copy()
    review_queue["suggested_category"] = model.predict(reports["description"].astype(str))
    review_queue["model_score"] = model.predict_proba(reports["description"].astype(str)).max(axis=1).round(3)
    review_queue["manual_review"] = ""
    review_queue.to_csv(args.output / "review_queue.csv", index=False, encoding="utf-8-sig")

    reports["category"].value_counts().sort_index().plot.bar(title="Bug categories (sample reports)")
    plt.xlabel("Category")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(args.output / "category_counts.png", dpi=160)
    plt.close()
    print(f"Results saved to {args.output}")
    print("Metrics use fictional examples, not independently verified game defects.")


if __name__ == "__main__":
    main()
