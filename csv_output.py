from pathlib import Path


REVIEW_COLUMNS = (
    "analysis_id", "description", "source_record_id", "source_record_url",
    "log_signals", "log_note", "suggested_category", "model_score",
    "review_status", "review_reason", "reviewed_category", "final_category",
)


def safe_cell(value):
    if not isinstance(value, str) or not value:
        return value
    if value.startswith(("\t", "\r", "\n")) or value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def write_csv(frame, path, overwrite=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    safe = frame.copy()
    for column in safe.columns:
        safe[column] = safe[column].map(safe_cell)
    safe = safe.rename(columns=safe_cell)
    with path.open("w" if overwrite else "x", encoding="utf-8-sig", newline="") as stream:
        safe.to_csv(stream, index=False)
