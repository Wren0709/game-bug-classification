from pathlib import Path
import argparse

import pandas as pd
from main import build_model, load_reports

BASE_DIR = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description="Suggest categories for independently written bug reports")
    parser.add_argument("--training", type=Path, default=BASE_DIR / "data" / "synthetic_bug_reports.csv")
    parser.add_argument("--observations", type=Path, default=BASE_DIR / "data" / "bug_observations.csv")
    parser.add_argument("--output", type=Path, default=BASE_DIR / "output" / "game_predictions.csv")
    args = parser.parse_args()

    reports = load_reports(args.training)
    observations = pd.read_csv(args.observations, keep_default_na=False)
    if "description" not in observations.columns:
        raise ValueError("Observation file must have a description column")
    observations = observations.loc[observations.description.astype(str).str.strip().ne("")].copy()
    if observations.empty:
        print("No independent observations found. Fill in data/bug_observations.csv first.")
        return

    model = build_model()
    model.fit(reports.description, reports.category)
    observations["suggested_category"] = model.predict(observations.description.astype(str))
    observations["model_score"] = model.predict_proba(observations.description.astype(str)).max(axis=1).round(3)
    observations["reviewed_category"] = ""
    args.output.parent.mkdir(parents=True, exist_ok=True)
    observations.to_csv(args.output, index=False)
    print(f"Saved {len(observations)} category suggestions to {args.output}")
    print("Scores are not calibrated confidence estimates. Review each suggestion manually.")


if __name__ == "__main__":
    main()
