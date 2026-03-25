from __future__ import annotations

import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path

_SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    deadline TEXT NOT NULL,
    completed INTEGER NOT NULL CHECK (completed IN (0, 1)),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    project_id TEXT REFERENCES projects (id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT,
    deadline TEXT NOT NULL,
    completed INTEGER NOT NULL CHECK (completed IN (0, 1)),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON tasks (project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks (completed);
CREATE INDEX IF NOT EXISTS idx_tasks_deadline ON tasks (deadline);
"""


class SqliteDatabase:
    """Thread-safe SQLite access for sync FastAPI route handlers."""

    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self._path = path
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(str(path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        with self._lock:
            self._conn.executescript(_SCHEMA)
            self._conn.commit()

    @contextmanager
    def write(self):
        with self._lock:
            try:
                yield self._conn
                self._conn.commit()
            except Exception:
                self._conn.rollback()
                raise

    @contextmanager
    def read(self):
        with self._lock:
            yield self._conn

    def close(self) -> None:
        with self._lock:
            self._conn.close()
