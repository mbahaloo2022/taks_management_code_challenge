from __future__ import annotations

from uuid import UUID

from app.domain.project import Project
from infra.repos._codec import datetime_to_iso, iso_to_datetime
from infra.repos.database import SqliteDatabase
from app.repos.page import Page


class SqliteProjectRepository:
    def __init__(self, db: SqliteDatabase) -> None:
        self._db = db

    @staticmethod
    def _row_to_project(row) -> Project:
        return Project(
            id=UUID(row["id"]),
            title=row["title"],
            deadline=iso_to_datetime(row["deadline"]),
            completed=bool(row["completed"]),
            created_at=iso_to_datetime(row["created_at"]),
            updated_at=iso_to_datetime(row["updated_at"]),
        )

    def get_by_id(self, project_id: UUID) -> Project | None:
        with self._db.read() as conn:
            row = conn.execute(
                "SELECT * FROM projects WHERE id = ?",
                (str(project_id),),
            ).fetchone()
        return self._row_to_project(row) if row else None

    def list_projects(
        self,
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> Page[Project]:
        order_sql = "ORDER BY created_at DESC, id DESC"
        with self._db.read() as conn:
            total = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
            sql = f"SELECT * FROM projects {order_sql}"
            params: list[object] = []
            if limit is not None:
                sql += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])
            elif offset > 0:
                sql += " LIMIT -1 OFFSET ?"
                params.append(offset)
            rows = conn.execute(sql, params).fetchall()

        return Page(
            items=[self._row_to_project(r) for r in rows],
            total=total,
            limit=limit,
            offset=offset,
        )

    def save(self, project: Project) -> Project:
        with self._db.write() as conn:
            conn.execute(
                """
                INSERT INTO projects (
                    id, title, deadline, completed, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT (id) DO UPDATE SET
                    title = excluded.title,
                    deadline = excluded.deadline,
                    completed = excluded.completed,
                    created_at = projects.created_at,
                    updated_at = excluded.updated_at
                """,
                (
                    str(project.id),
                    project.title,
                    datetime_to_iso(project.deadline),
                    1 if project.completed else 0,
                    datetime_to_iso(project.created_at),
                    datetime_to_iso(project.updated_at),
                ),
            )
        return project

    def delete(self, project_id: UUID) -> None:
        with self._db.write() as conn:
            conn.execute("DELETE FROM projects WHERE id = ?", (str(project_id),))
