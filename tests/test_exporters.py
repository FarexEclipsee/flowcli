from __future__ import annotations

import json

import pytest

from flowcli.exporters import available_formats, get_exporter

SAMPLE_SESSIONS = [
    {
        "task_id": 1,
        "description": "Write tests",
        "project": "flowcli",
        "tag": "chore",
        "branch": "main",
        "started_at": "2026-07-01 09:00:00",
        "ended_at": "2026-07-01 09:30:00",
        "duration_seconds": 1800.0,
        "duration_human": "30m 0s",
    }
]


def test_available_formats_include_builtins():
    formats = available_formats()
    assert {"csv", "json", "markdown"}.issubset(set(formats))


def test_csv_exporter_includes_header_and_row():
    exporter = get_exporter("csv")
    output = exporter.export(SAMPLE_SESSIONS)
    assert "task_id" in output.splitlines()[0]
    assert "Write tests" in output


def test_json_exporter_round_trips():
    exporter = get_exporter("json")
    output = exporter.export(SAMPLE_SESSIONS)
    parsed = json.loads(output)
    assert parsed[0]["description"] == "Write tests"


def test_markdown_exporter_renders_table():
    exporter = get_exporter("markdown")
    output = exporter.export(SAMPLE_SESSIONS)
    assert "| Task | Project | Branch | Started | Duration |" in output
    assert "Write tests" in output
    assert "Total tracked time" in output


def test_markdown_exporter_handles_empty():
    exporter = get_exporter("markdown")
    output = exporter.export([])
    assert "No sessions found" in output


def test_unknown_format_raises():
    with pytest.raises(ValueError):
        get_exporter("xml")
