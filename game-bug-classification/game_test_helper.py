from pathlib import Path
import argparse

import pandas as pd
from main import build_model

BASE_DIR = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description="Organize game bug reports across different games")
    parser.add_argument("--training", type=Path, default=BASE_DIR / "data" / "demo_bug_reports.csv")
    parser.add_argument("--observations", type=Path, default=BASE_DIR / "data" / "game_observations.csv")
    parser.add_argument("--output", type=Path, default=BASE_DIR / "output" / "game_predictions.csv")
    args = parser.parse_args()

    training_data = pd.read_csv(args.training).dropna(subset=["description", "category"])
    category_counts = training_data["category"].value_counts()
    if len(training_data) < 20 or len(category_counts) < 2 or category_counts.min() < 2:
        raise ValueError("Training data needs at least 20 reports and two categories with two reports each.")

    if not args.observations.exists():
        args.observations.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(columns=["game", "description"]).to_csv(
            args.observations, index=False, encoding="utf-8-sig"
        )
        print(f"Created blank observation template: {args.observations}")
        print("Add your own game bug reports, then run this script again.")
        return

    observations = pd.read_csv(args.observations, keep_default_na=False)
    if "description" not in observations.columns:
        raise ValueError("The observation file needs a 'description' column.")
    observations = observations[observations["description"].astype(str).str.strip() != ""].copy()
    if observations.empty:
        print("No bug observations recorded yet. Add your own findings to data/game_observations.csv.")
        return

    model = build_model()
    model.fit(training_data["description"].astype(str), training_data["category"])
    observations["suggested_category"] = model.predict(observations["description"].astype(str))
    observations["model_score"] = model.predict_proba(observations["description"].astype(str)).max(axis=1).round(3)
    observations["reviewed_category"] = ""

    args.output.parent.mkdir(parents=True, exist_ok=True)
    observations.to_csv(args.output, index=False, encoding="utf-8-sig")
    print(f"Saved {len(observations)} reports to {args.output}")
    print("Review each suggestion manually. Model scores are not calibrated probabilities.")


if __name__ == "__main__":
    main()
