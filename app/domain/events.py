from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class DomainEvent:
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class TaskCompletedEvent(DomainEvent):
    task_id: UUID
    project_id: UUID | None


@dataclass(frozen=True, slots=True)
class TaskReopenedEvent(DomainEvent):
    task_id: UUID
    project_id: UUID | None


@dataclass(frozen=True, slots=True)
class ProjectDeadlineShortenedEvent(DomainEvent):
    project_id: UUID
    old_deadline: datetime
    new_deadline: datetime


@dataclass(frozen=True, slots=True)
class TaskDeadlineApproachingEvent(DomainEvent):
    task_id: UUID
    deadline: datetime


@dataclass(frozen=True, slots=True)
class ProjectAutoCompletedEvent(DomainEvent):
    project_id: UUID
