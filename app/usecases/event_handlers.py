from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta

from app.config import AppConfig
from app.domain.events import (
    ProjectAutoCompletedEvent,
    ProjectDeadlineShortenedEvent,
    TaskCompletedEvent,
    TaskDeadlineApproachingEvent,
    TaskReopenedEvent,
)
from app.domain.project import Project
from app.domain.task import Task
from app.repos.project_repository import ProjectRepository
from app.repos.task_repository import TaskListFilters, TaskRepository
from app.services.notification_service import NotificationService

PublishEvent = Callable[[object], None]


def make_project_deadline_shortened_handler(
    tasks: TaskRepository,
) -> Callable[[ProjectDeadlineShortenedEvent], None]:
    def handle(event: ProjectDeadlineShortenedEvent) -> None:
        associated = tasks.list_tasks(
            TaskListFilters(project_id=event.project_id),
            limit=None,
            offset=0,
        ).items
        for task in associated:
            adjusted = task.shorten_deadline_if_needed(
                max_deadline=event.new_deadline,
                now=event.occurred_at,
            )
            if adjusted != task:
                tasks.save(adjusted)

    return handle


def make_task_completed_handler(
    tasks: TaskRepository,
    projects: ProjectRepository,
    config: AppConfig,
    notifications: NotificationService,
    publish_event: PublishEvent,
) -> Callable[[TaskCompletedEvent], None]:
    def handle(event: TaskCompletedEvent) -> None:
        notifications.info(f"Task {event.task_id} marked as completed")
        if event.project_id is None:
            return
        project = projects.get_by_id(event.project_id)
        if project is None:
            return

        associated = tasks.list_tasks(
            TaskListFilters(project_id=event.project_id),
            limit=None,
            offset=0,
        ).items
        if (
            config.auto_complete_project_when_all_tasks_done
            and associated
            and all(t.completed for t in associated)
        ):
            completed = project.mark_completed(
                incomplete_task_ids=[], now=event.occurred_at
            )
            projects.save(completed)
            publish_event(
                ProjectAutoCompletedEvent(
                    occurred_at=event.occurred_at, project_id=project.id
                )
            )

    return handle


def make_task_reopened_handler(
    projects: ProjectRepository,
) -> Callable[[TaskReopenedEvent], None]:
    def handle(event: TaskReopenedEvent) -> None:
        if event.project_id is None:
            return
        project = projects.get_by_id(event.project_id)
        if project is None:
            return
        if project.completed:
            projects.save(project.reopen(now=event.occurred_at))

    return handle


def make_task_deadline_approaching_handler(
    notifications: NotificationService,
    *,
    within_hours: int = 24,
) -> Callable[[TaskDeadlineApproachingEvent], None]:
    def handle(event: TaskDeadlineApproachingEvent) -> None:
        delta = event.deadline - event.occurred_at
        if timedelta(0) <= delta <= timedelta(hours=within_hours):
            notifications.warning(
                f"Task {event.task_id} deadline is approaching at {event.deadline.isoformat()}"
            )

    return handle


def maybe_emit_deadline_approaching_event(
    *,
    task: Task,
    now: datetime,
    publish_event: PublishEvent,
) -> None:
    if task.completed:
        return
    publish_event(
        TaskDeadlineApproachingEvent(
            occurred_at=now,
            task_id=task.id,
            deadline=task.deadline,
        )
    )
