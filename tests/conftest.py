from collections.abc import Iterator
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from infra.repos.database import SqliteDatabase
from infra.repos.project_repository_sqlite import SqliteProjectRepository
from infra.repos.task_repository_sqlite import SqliteTaskRepository
from infra.rest.app import create_app


@pytest.fixture()
def app(tmp_path: Path):
    db = SqliteDatabase(tmp_path / "test.db")
    task_repo = SqliteTaskRepository(db)
    project_repo = SqliteProjectRepository(db)
    app = create_app(task_repository=task_repo, project_repository=project_repo)
    try:
        yield app
    finally:
        db.close()


@pytest.fixture()
def client(app) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client
