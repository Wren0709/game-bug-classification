import re
from pathlib import Path

SIGNALS = {
    "exception": re.compile(r"\b(?:exception|traceback|stack\s+trace)\b", re.I),
    "crash": re.compile(r"\b(?:fatal|crash(?:ed)?|segmentation\s+fault)\b", re.I),
    "memory": re.compile(r"\b(?:out\s+of\s+memory|memory\s+allocation\s+failed|oom)\b", re.I),
    "network": re.compile(r"\b(?:disconnect(?:ed)?|connection\s+(?:timed?\s*out|lost|refused)|network\s+timeout)\b", re.I),
    "performance": re.compile(r"\b(?:frame\s+time|low\s+fps|stutter(?:ing)?|long\s+frame)\b", re.I),
}

MAX_LOG_CHARS = 100_000


def detect_signals(text):
    sample = str(text or "")[:MAX_LOG_CHARS]
    return [name for name, pattern in SIGNALS.items() if pattern.search(sample)]


def read_log(log_name, logs_dir):
    if not str(log_name).strip():
        return "", ""
    if logs_dir is None:
        return "", "log_file_not_loaded"
    root = Path(logs_dir).expanduser().resolve()
    target = (root / str(log_name)).resolve()
    if not target.is_relative_to(root) or not target.is_file() or target.suffix.lower() not in {".txt", ".log"}:
        return "", "log_file_unavailable"
    try:
        with target.open(encoding="utf-8", errors="replace") as stream:
            content = stream.read(MAX_LOG_CHARS + 1)
        return content[:MAX_LOG_CHARS], "log_truncated" if len(content) > MAX_LOG_CHARS else ""
    except OSError:
        return "", "log_file_unavailable"
