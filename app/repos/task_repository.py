from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.domain.task import Task

from app.repos.page import Page


@dataclass(slots=True)
class TaskListFilters:
    completed: bool | None = None
    project_id: UUID | None = None
    overdue: bool | None = None
    """When True, only tasks that are not completed and have deadline before ``as_of``."""


class TaskRepository(Protocol):
    def get_by_id(self, task_id: UUID) -> Task | None:
        """Return the task or None if it does not exist."""

    def list_tasks(
        self,
        filters: TaskListFilters | None = None,
        *,
        as_of: datetime | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> Page[Task]:
        """Return tasks matching filters, optionally paginated.

        When ``filters.overdue`` is true, ``as_of`` must be provided by the caller.

        When ``limit`` is None, all matching rows are returned (for internal use);
        ``Page.limit`` should be None in that case.
        """

    def save(self, task: Task) -> Task:
        """Persist create or update."""

    def delete(self, task_id: UUID) -> None:
        """Remove the task if it exists."""
