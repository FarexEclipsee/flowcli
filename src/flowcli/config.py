"""Configuration handling for FlowCLI.

Config lives at ~/.flowcli/config.yaml by default, but both the config
directory and the database path can be overridden with environment
variables, which is primarily useful for testing.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict

import yaml

ENV_HOME = "FLOWCLI_HOME"

DEFAULT_CONFIG: Dict[str, Any] = {
    "db_path": None,  # resolved relative to home dir if not set
    "default_project": None,
    "date_format": "%Y-%m-%d %H:%M",
}


def get_home_dir() -> Path:
    """Return the FlowCLI home directory, creating it if necessary."""
    home = os.environ.get(ENV_HOME)
    path = Path(home).expanduser() if home else Path.home() / ".flowcli"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_config_path() -> Path:
    return get_home_dir() / "config.yaml"


@dataclass
class Config:
    db_path: Path
    default_project: str | None = None
    date_format: str = "%Y-%m-%d %H:%M"
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls) -> "Config":
        config_path = get_config_path()
        data = dict(DEFAULT_CONFIG)
        if config_path.exists():
            with config_path.open("r", encoding="utf-8") as fh:
                loaded = yaml.safe_load(fh) or {}
            data.update(loaded)

        db_path = data.get("db_path") or str(get_home_dir() / "flowcli.db")
        return cls(
            db_path=Path(db_path).expanduser(),
            default_project=data.get("default_project"),
            date_format=data.get("date_format", "%Y-%m-%d %H:%M"),
            raw=data,
        )

    def save(self) -> None:
        data = {
            "db_path": str(self.db_path),
            "default_project": self.default_project,
            "date_format": self.date_format,
        }
        with get_config_path().open("w", encoding="utf-8") as fh:
            yaml.safe_dump(data, fh, default_flow_style=False)
