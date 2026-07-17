from __future__ import annotations

import json
from typing import Any, Dict, List

from flowcli.exporters.base import Exporter


class JsonExporter(Exporter):
    name = "json"

    def export(self, sessions: List[Dict[str, Any]]) -> str:
        return json.dumps(sessions, indent=2, default=str)
