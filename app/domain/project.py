from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from uuid import UUID, uuid4

from app.domain.errors import DomainError, ResourceNotFound


class ProjectNotFound(ResourceNotFound):
    """Project not found error."""

    def __init__(self, project_id: UUID) -> None:
        super().__init__("Project", project_id)


class ProjectCompletionDenied(DomainError):
    """Project cannot be marked completed because some tasks are still open."""

    def __init__(self, incomplete_task_ids: list[UUID]) -> None:
        self.incomplete_task_ids = incomplete_task_ids
        super().__init__(
            "All tasks in the project must be completed before the project can be completed."
        )


@dataclass(frozen=True, slots=True)
class Project:
    """Project aggregate root."""

    title: str
    deadline: datetime
    created_at: datetime
    updated_at: datetime
    id: UUID = field(default_factory=uuid4)
    completed: bool = False

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise DomainError("Project title must not be empty.")

    @classmethod
    def create(cls, *, title: str, deadline: datetime, now: datetime) -> "Project":
        return cls(
            id=uuid4(),
            title=title,
            deadline=deadline,
            completed=False,
            created_at=now,
            updated_at=now,
        )

    def with_updates(
        self,
        *,
        now: datetime,
        title: str | None = None,
        deadline: datetime | None = None,
        completed: bool | None = None,
    ) -> "Project":
        return replace(
            self,
            title=title if title is not None else self.title,
            deadline=deadline if deadline is not None else self.deadline,
            completed=completed if completed is not None else self.completed,
            updated_at=now,
        )

    def mark_completed(
        self, *, incomplete_task_ids: list[UUID], now: datetime
    ) -> "Project":
        if incomplete_task_ids:
            raise ProjectCompletionDenied(incomplete_task_ids)
        if self.completed:
            return self
        return replace(self, completed=True, updated_at=now)

    def reopen(self, *, now: datetime) -> "Project":
        if not self.completed:
            return self
        return replace(self, completed=False, updated_at=now)
