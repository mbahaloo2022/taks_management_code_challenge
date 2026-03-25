from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.clock import utc_now
from app.domain.events import TaskCompletedEvent, TaskReopenedEvent
from app.domain.project import ProjectNotFound
from app.domain.task import Task, TaskNotFound
from app.repos.project_repository import ProjectRepository
from app.repos.task_repository import TaskRepository
from app.services.event_bus import EventBus
from app.usecases.event_handlers import maybe_emit_deadline_approaching_event

type UpdateTaskOutput = Task


@dataclass(slots=True)
class UpdateTaskInput:
    task_id: UUID
    title: str | None = None
    description: str | None = None
    deadline: datetime | None = None
    completed: bool | None = None
    project_id: UUID | None = None
    clear_project_id: bool = False


class UpdateTaskUseCase:
    def __init__(
        self,
        tasks: TaskRepository,
        projects: ProjectRepository,
        events: EventBus | None = None,
    ) -> None:
        self._tasks = tasks
        self._projects = projects
        self._events = events

    def execute(self, input_: UpdateTaskInput) -> UpdateTaskOutput:
        task = self._tasks.get_by_id(input_.task_id)
        if task is None:
            raise TaskNotFound(input_.task_id)

        now = utc_now()
        explicit_project_change = (
            input_.clear_project_id or input_.project_id is not None
        )
        project_id = (
            None
            if input_.clear_project_id
            else (
                input_.project_id if input_.project_id is not None else task.project_id
            )
        )
        effective_deadline = (
            input_.deadline if input_.deadline is not None else task.deadline
        )

        if project_id is not None:
            project = self._projects.get_by_id(project_id)
            if project is None:
                raise ProjectNotFound(project_id)
            Task.assert_deadline_not_after_project_deadline(
                effective_deadline, project.deadline
            )

        updated = task.with_updates(
            now=now,
            title=input_.title,
            description=input_.description,
            deadline=input_.deadline,
            completed=input_.completed,
            project_id=project_id,
            project_id_explicitly_set=explicit_project_change,
        )
        saved = self._tasks.save(updated)

        if self._events is not None:
            if not task.completed and saved.completed:
                self._events.publish(
                    TaskCompletedEvent(
                        occurred_at=now, task_id=saved.id, project_id=saved.project_id
                    )
                )
            if task.completed and not saved.completed:
                self._events.publish(
                    TaskReopenedEvent(
                        occurred_at=now, task_id=saved.id, project_id=saved.project_id
                    )
                )
            maybe_emit_deadline_approaching_event(
                task=saved, now=now, publish_event=self._events.publish
            )

        return saved
