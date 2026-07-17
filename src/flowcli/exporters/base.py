"""Base interface for report exporters.

New exporters can be added either directly in this package or by any
third-party package that registers a `flowcli.exporters` entry point (see
pyproject.toml). This is what makes the report format list "pluggable"
without FlowCLI's core needing to know about every format up front.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class Exporter(ABC):
    """Base class every report exporter must implement."""

    #: short identifier used on the --format flag, e.g. "csv"
    name: str = "base"

    @abstractmethod
    def export(self, sessions: List[Dict[str, Any]]) -> str:
        """Return a string representation of the given session records."""
        raise NotImplementedError
