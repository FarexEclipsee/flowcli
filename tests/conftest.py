from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from flowcli.db import Database


@pytest.fixture
def tmp_db(tmp_path: Path) -> Database:
    db_path = tmp_path / "test.db"
    db = Database(db_path)
    yield db
    db.close()


@pytest.fixture
def cli_env(tmp_path, monkeypatch):
    """Isolate FlowCLI's config/db directory for CLI-level tests."""
    home = tmp_path / "flowcli_home"
    home.mkdir()
    monkeypatch.setenv("FLOWCLI_HOME", str(home))
    return home


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()
