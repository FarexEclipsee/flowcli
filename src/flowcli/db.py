"""SQLite persistence layer for FlowCLI.

A thin wrapper around sqlite3 that owns schema creation/migration and
exposes simple CRUD-style helpers used by the command layer. Keeping all
SQL in one place makes the rest of the codebase storage-agnostic and easy
to test with a temporary database file.
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Optional

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    project     TEXT,
    tag         TEXT,
    branch      TEXT,
    status      TEXT NOT NULL DEFAULT 'open',
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    done_at     TEXT
);

CREATE TABLE IF NOT EXISTS sessions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id     INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    started_at  TEXT NOT NULL DEFAULT (datetime('now')),
    ended_at    TEXT,
    note        TEXT
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_sessions_task ON sessions(task_id);
"""


class Database:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON;")
        self._init_schema()

    def _init_schema(self) -> None:
        with self._conn:
            self._conn.executescript(SCHEMA)

    @contextmanager
    def cursor(self) -> Iterator[sqlite3.Cursor]:
        cur = self._conn.cursor()
        try:
            yield cur
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise
        finally:
            cur.close()

    def close(self) -> None:
        self._conn.close()

    # -- Tasks ---------------------------------------------------------

    def add_task(
        self,
        description: str,
        project: Optional[str] = None,
        tag: Optional[str] = None,
        branch: Optional[str] = None,
    ) -> int:
        with self.cursor() as cur:
            cur.execute(
                "INSERT INTO tasks (description, project, tag, branch) "
                "VALUES (?, ?, ?, ?)",
                (description, project, tag, branch),
            )
            return cur.lastrowid

    def get_task(self, task_id: int) -> Optional[sqlite3.Row]:
        with self.cursor() as cur:
            cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            return cur.fetchone()

    def list_tasks(
        self,
        status: Optional[str] = None,
        project: Optional[str] = None,
    ) -> list[sqlite3.Row]:
        query = "SELECT * FROM tasks WHERE 1=1"
        params: list[Any] = []
        if status:
            query += " AND status = ?"
            params.append(status)
        if project:
            query += " AND project = ?"
            params.append(project)
        query += " ORDER BY created_at DESC"
        with self.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()

    def mark_done(self, task_id: int) -> bool:
        with self.cursor() as cur:
            cur.execute(
                "UPDATE tasks SET status = 'done', done_at = datetime('now') "
                "WHERE id = ? AND status != 'done'",
                (task_id,),
            )
            return cur.rowcount > 0

    def delete_task(self, task_id: int) -> bool:
        with self.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            return cur.rowcount > 0

    # -- Sessions (time tracking) ---------------------------------------

    def start_session(self, task_id: int) -> int:
        with self.cursor() as cur:
            cur.execute(
                "INSERT INTO sessions (task_id) VALUES (?)", (task_id,)
            )
            return cur.lastrowid

    def open_session(self) -> Optional[sqlite3.Row]:
        with self.cursor() as cur:
            cur.execute(
                "SELECT * FROM sessions WHERE ended_at IS NULL "
                "ORDER BY started_at DESC LIMIT 1"
            )
            return cur.fetchone()

    def stop_session(self, session_id: int, note: Optional[str] = None) -> bool:
        with self.cursor() as cur:
            cur.execute(
                "UPDATE sessions SET ended_at = datetime('now'), note = ? "
                "WHERE id = ? AND ended_at IS NULL",
                (note, session_id),
            )
            return cur.rowcount > 0

    def sessions_for_report(
        self,
        project: Optional[str] = None,
        since: Optional[str] = None,
    ) -> list[sqlite3.Row]:
        query = """
            SELECT s.id, s.started_at, s.ended_at, s.note,
                   t.id as task_id, t.description, t.project, t.tag, t.branch
            FROM sessions s
            JOIN tasks t ON t.id = s.task_id
            WHERE s.ended_at IS NOT NULL
        """
        params: list[Any] = []
        if project:
            query += " AND t.project = ?"
            params.append(project)
        if since:
            query += " AND s.started_at >= ?"
            params.append(since)
        query += " ORDER BY s.started_at ASC"
        with self.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()
