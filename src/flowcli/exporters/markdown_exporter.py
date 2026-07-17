from __future__ import annotations

from typing import Any, Dict, List

from flowcli.exporters.base import Exporter


class MarkdownExporter(Exporter):
    name = "markdown"

    def export(self, sessions: List[Dict[str, Any]]) -> str:
        if not sessions:
            return "_No sessions found for the given filters._\n"

        lines = [
            "| Task | Project | Branch | Started | Duration |",
            "|------|---------|--------|---------|----------|",
        ]
        total_seconds = 0.0
        for s in sessions:
            total_seconds += s.get("duration_seconds") or 0.0
            lines.append(
                f"| {s.get('description', '')} "
                f"| {s.get('project') or '-'} "
                f"| {s.get('branch') or '-'} "
                f"| {s.get('started_at', '')} "
                f"| {s.get('duration_human') or '-'} |"
            )
        from flowcli.models import format_duration

        lines.append("")
        lines.append(f"**Total tracked time:** {format_duration(total_seconds)}")
        return "\n".join(lines) + "\n"
