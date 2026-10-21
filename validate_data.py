from pathlib import Path
import pandas as pd
from main import load_reports

ROOT = Path(__file__).resolve().parent


def main():
    reports = load_reports(ROOT / "data" / "synthetic_bug_reports.csv")
    cases = pd.read_csv(ROOT / "data" / "game_test_cases.csv", keep_default_na=False)
    required = {"case_id", "test_title", "test_steps", "expected_result", "status"}
    if not required.issubset(cases.columns):
        raise ValueError("The test case file is missing required columns")
    if cases.case_id.duplicated().any():
        raise ValueError("Duplicate test case IDs found")
    for column in ("case_id", "feature_area", "test_title", "priority", "test_type", "preconditions", "test_steps", "expected_result", "status"):
        if cases[column].astype(str).str.strip().eq("").any():
            raise ValueError(f"Empty values in test cases: {column}")
    if not cases.status.eq("Not run").all():
        raise ValueError("Proposed tests must remain Not run until actually executed")
    if len(cases) != 50:
        raise ValueError("The project expects 50 proposed test cases")
    print(f"Validated {len(reports)} fictional reports and {len(cases)} proposed test cases")
    print(reports.category.value_counts().sort_index().to_string())


if __name__ == "__main__":
    main()
