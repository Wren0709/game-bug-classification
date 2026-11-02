import argparse
from pathlib import Path

import pandas as pd

from csv_output import REVIEW_COLUMNS, write_csv

CATEGORIES = {"Audio", "Gameplay", "Network", "Performance", "UI"}


def apply_reviews(frame):
    required = {"review_status", "reviewed_category", "suggested_category"}
    if not required.issubset(frame.columns):
        raise ValueError("Input is not a workbench review worksheet")
    result = frame.loc[:, [column for column in REVIEW_COLUMNS if column in frame]].fillna("").copy()
    selected = result["reviewed_category"].astype(str).str.strip()
    invalid = sorted(set(selected) - CATEGORIES - {""})
    if invalid:
        raise ValueError(f"Unrecognised reviewed category: {', '.join(invalid)}")
    result["final_category"] = selected
    result["reviewed_category"] = selected
    if "description" in result:
        empty = result["description"].astype(str).str.strip().eq("")
    else:
        empty = result["review_status"].eq("unresolved")
        if "review_reason" in result:
            empty |= result["review_reason"].eq("empty_description")
    result["review_status"] = "needs_review"
    result.loc[empty, "review_status"] = "unresolved"
    result.loc[selected.ne(""), "review_status"] = "reviewed"
    return result


def main():
    parser = argparse.ArgumentParser(description="Record manually reviewed bug categories")
    root = Path(__file__).resolve().parent
    parser.add_argument("--input", type=Path, default=root / "private/workbench_results.csv")
    parser.add_argument("--output", type=Path, default=root / "private/reviewed_results.csv")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing output file")
    args = parser.parse_args()
    frame = pd.read_csv(args.input, keep_default_na=False, dtype=str, encoding="utf-8-sig")
    result = apply_reviews(frame)
    write_csv(result, args.output, args.overwrite)
    print(f"Saved {sum(result.review_status == 'reviewed')} reviewed rows to {args.output}")


if __name__ == "__main__":
    main()
