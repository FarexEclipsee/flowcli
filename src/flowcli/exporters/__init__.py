"""Exporter registry.

Built-in exporters are always available. Additional exporters can be
contributed by third-party packages via the `flowcli.exporters` entry
point group, so `flow report --format <name>` grows without touching
this codebase.
"""
from __future__ import annotations

import sys
from typing import Dict, Type

from flowcli.exporters.base import Exporter
from flowcli.exporters.csv_exporter import CsvExporter
from flowcli.exporters.json_exporter import JsonExporter
from flowcli.exporters.markdown_exporter import MarkdownExporter

_BUILTIN: Dict[str, Type[Exporter]] = {
    "csv": CsvExporter,
    "json": JsonExporter,
    "markdown": MarkdownExporter,
}


def _discover_plugins() -> Dict[str, Type[Exporter]]:
    registry = dict(_BUILTIN)
    try:
        if sys.version_info >= (3, 10):
            from importlib.metadata import entry_points

            eps = entry_points(group="flowcli.exporters")
        else:
            from importlib.metadata import entry_points

            eps = entry_points().get("flowcli.exporters", [])
    except Exception:
        return registry

    for ep in eps:
        try:
            registry[ep.name] = ep.load()
        except Exception:
            # A broken third-party plugin shouldn't break the whole CLI.
            continue
    return registry


def get_exporter(name: str) -> Exporter:
    registry = _discover_plugins()
    try:
        exporter_cls = registry[name]
    except KeyError as exc:
        available = ", ".join(sorted(registry))
        raise ValueError(f"Unknown export format '{name}'. Available: {available}") from exc
    return exporter_cls()


def available_formats() -> list[str]:
    return sorted(_discover_plugins())
