from __future__ import annotations

import csv
import io
from typing import Any, Dict, List

from flowcli.exporters.base import Exporter

FIELDS = [
    "task_id",
    "description",
    "project",
    "tag",
    "branch",
    "started_at",
    "ended_at",
    "duration_human",
]


class CsvExporter(Exporter):
    name = "csv"

    def export(self, sessions: List[Dict[str, Any]]) -> str:
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        for session in sessions:
            writer.writerow(session)
        return buf.getvalue()
