from __future__ import annotations

from datetime import datetime
from uuid import UUID

from app.domain.task import Task
from infra.repos._codec import datetime_to_iso, iso_to_datetime
from infra.repos.database import SqliteDatabase
from app.repos.page import Page
from app.repos.task_repository import TaskListFilters


class SqliteTaskRepository:
    def __init__(self, db: SqliteDatabase) -> None:
        self._db = db

    @staticmethod
    def _row_to_task(row) -> Task:
        return Task(
            id=UUID(row["id"]),
            project_id=UUID(row["project_id"]) if row["project_id"] else None,
            title=row["title"],
            description=row["description"],
            deadline=iso_to_datetime(row["deadline"]),
            completed=bool(row["completed"]),
            created_at=iso_to_datetime(row["created_at"]),
            updated_at=iso_to_datetime(row["updated_at"]),
        )

    def get_by_id(self, task_id: UUID) -> Task | None:
        with self._db.read() as conn:
            row = conn.execute(
                "SELECT * FROM tasks WHERE id = ?",
                (str(task_id),),
            ).fetchone()
        return self._row_to_task(row) if row else None

    def list_tasks(
        self,
        filters: TaskListFilters | None = None,
        *,
        as_of: datetime | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> Page[Task]:
        filters = filters or TaskListFilters()
        where: list[str] = ["1 = 1"]
        params: list[object] = []

        if filters.completed is not None:
            where.append("completed = ?")
            params.append(1 if filters.completed else 0)

        if filters.project_id is not None:
            where.append("project_id = ?")
            params.append(str(filters.project_id))

        if filters.overdue:
            if as_of is None:
                msg = "as_of is required when filters.overdue is true"
                raise ValueError(msg)
            where.append("completed = 0")
            where.append("deadline < ?")
            params.append(datetime_to_iso(as_of))

        where_sql = " AND ".join(where)
        order_sql = "ORDER BY created_at DESC, id DESC"

        with self._db.read() as conn:
            total = conn.execute(
                f"SELECT COUNT(*) FROM tasks WHERE {where_sql}",
                params,
            ).fetchone()[0]

            sql = f"SELECT * FROM tasks WHERE {where_sql} {order_sql}"
            qparams = list(params)
            if limit is not None:
                sql += " LIMIT ? OFFSET ?"
                qparams.extend([limit, offset])
            elif offset > 0:
                sql += " LIMIT -1 OFFSET ?"
                qparams.append(offset)

            rows = conn.execute(sql, qparams).fetchall()

        return Page(
            items=[self._row_to_task(r) for r in rows],
            total=total,
            limit=limit,
            offset=offset,
        )

    def save(self, task: Task) -> Task:
        with self._db.write() as conn:
            conn.execute(
                """
                INSERT INTO tasks (
                    id, project_id, title, description, deadline,
                    completed, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (id) DO UPDATE SET
                    project_id = excluded.project_id,
                    title = excluded.title,
                    description = excluded.description,
                    deadline = excluded.deadline,
                    completed = excluded.completed,
                    created_at = tasks.created_at,
                    updated_at = excluded.updated_at
                """,
                (
                    str(task.id),
                    str(task.project_id) if task.project_id else None,
                    task.title,
                    task.description,
                    datetime_to_iso(task.deadline),
                    1 if task.completed else 0,
                    datetime_to_iso(task.created_at),
                    datetime_to_iso(task.updated_at),
                ),
            )
        return task

    def delete(self, task_id: UUID) -> None:
        with self._db.write() as conn:
            conn.execute("DELETE FROM tasks WHERE id = ?", (str(task_id),))
