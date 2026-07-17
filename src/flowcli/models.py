"""Small data-shaping helpers shared across commands and exporters."""
from __future__ import annotations

from datetime import datetime

DB_DATETIME_FMT = "%Y-%m-%d %H:%M:%S"


def parse_dt(value: str) -> datetime:
    return datetime.strptime(value, DB_DATETIME_FMT)


def duration_seconds(started_at: str, ended_at: str) -> float:
    start = parse_dt(started_at)
    end = parse_dt(ended_at)
    return max((end - start).total_seconds(), 0.0)


def format_duration(seconds: float) -> str:
    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def session_to_dict(row) -> dict:
    """Convert a sqlite3.Row from sessions_for_report into a plain dict."""
    data = dict(row)
    if data.get("ended_at"):
        data["duration_seconds"] = duration_seconds(data["started_at"], data["ended_at"])
        data["duration_human"] = format_duration(data["duration_seconds"])
    else:
        data["duration_seconds"] = None
        data["duration_human"] = None
    return data
