from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from uuid import UUID, uuid4

from app.domain.errors import DomainError, ResourceNotFound


class TaskNotFound(ResourceNotFound):
    """Task not found error."""

    def __init__(self, task_id: UUID) -> None:
        super().__init__("Task", task_id)


class DeadlineAfterProjectDeadline(DomainError):
    """Task deadline is later than its project's deadline error."""

    def __init__(self, task_deadline: datetime, project_deadline: datetime) -> None:
        self.task_deadline = task_deadline
        self.project_deadline = project_deadline
        super().__init__(
            "Task deadline must not be later than the associated project's deadline."
        )


class TaskProjectMismatch(DomainError):
    """Task is not linked to the specified project error."""

    def __init__(self, task_id: UUID, project_id: UUID) -> None:
        self.task_id = task_id
        self.project_id = project_id
        super().__init__(f"Task {task_id} is not linked to project {project_id}.")


@dataclass(frozen=True, slots=True)
class Task:
    """Task aggregate root.

    The domain model is intentionally framework-free to keep the core portable and
    easy to test.
    """

    title: str
    deadline: datetime
    created_at: datetime
    updated_at: datetime
    project_id: UUID | None = None
    id: UUID = field(default_factory=uuid4)
    description: str | None = None
    completed: bool = False

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise DomainError("Task title must not be empty.")

    @classmethod
    def create(
        cls,
        *,
        title: str,
        description: str | None,
        deadline: datetime,
        now: datetime,
        project_id: UUID | None = None,
    ) -> "Task":
        return cls(
            id=uuid4(),
            project_id=project_id,
            title=title,
            description=description,
            deadline=deadline,
            completed=False,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def assert_deadline_not_after_project_deadline(
        task_deadline: datetime,
        project_deadline: datetime,
    ) -> None:
        if task_deadline > project_deadline:
            raise DeadlineAfterProjectDeadline(task_deadline, project_deadline)

    def with_updates(
        self,
        *,
        now: datetime,
        title: str | None = None,
        description: str | None = None,
        deadline: datetime | None = None,
        completed: bool | None = None,
        project_id: UUID | None = None,
        project_id_explicitly_set: bool = False,
    ) -> "Task":
        next_title = title if title is not None else self.title
        next_description = description if description is not None else self.description
        next_deadline = deadline if deadline is not None else self.deadline
        next_completed = completed if completed is not None else self.completed
        next_project_id = project_id if project_id_explicitly_set else self.project_id
        return replace(
            self,
            title=next_title,
            description=next_description,
            deadline=next_deadline,
            completed=next_completed,
            project_id=next_project_id,
            updated_at=now,
        )

    def mark_completed(self, *, now: datetime) -> "Task":
        if self.completed:
            return self
        return replace(self, completed=True, updated_at=now)

    def reopen(self, *, now: datetime) -> "Task":
        if not self.completed:
            return self
        return replace(self, completed=False, updated_at=now)

    def assign_to_project(
        self, *, project_id: UUID, project_deadline: datetime, now: datetime
    ) -> "Task":
        self.assert_deadline_not_after_project_deadline(self.deadline, project_deadline)
        return replace(self, project_id=project_id, updated_at=now)

    def remove_from_project(
        self, *, expected_project_id: UUID, now: datetime
    ) -> "Task":
        if self.project_id != expected_project_id:
            raise TaskProjectMismatch(self.id, expected_project_id)
        return replace(self, project_id=None, updated_at=now)

    def shorten_deadline_if_needed(
        self, *, max_deadline: datetime, now: datetime
    ) -> "Task":
        if self.deadline <= max_deadline:
            return self
        return replace(self, deadline=max_deadline, updated_at=now)
