import os
from pathlib import Path

from infra.repos.database import SqliteDatabase
from infra.repos.project_repository_sqlite import SqliteProjectRepository
from infra.repos.task_repository_sqlite import SqliteTaskRepository
from infra.rest.app import create_app

_db_path = Path(os.environ.get("TASKS_SQLITE_PATH", "tasks.db"))
_db = SqliteDatabase(_db_path)
_task_repo = SqliteTaskRepository(_db)
_project_repo = SqliteProjectRepository(_db)

app = create_app(
    task_repository=_task_repo,
    project_repository=_project_repo,
)
