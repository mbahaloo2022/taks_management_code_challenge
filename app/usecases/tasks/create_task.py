from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.clock import utc_now
from app.domain.project import ProjectNotFound
from app.domain.task import Task
from app.repos.project_repository import ProjectRepository
from app.repos.task_repository import TaskRepository
from app.services.event_bus import EventBus
from app.usecases.event_handlers import maybe_emit_deadline_approaching_event

type CreateTaskOutput = Task


@dataclass(slots=True)
class CreateTaskInput:
    title: str
    description: str | None
    deadline: datetime
    project_id: UUID | None


class CreateTaskUseCase:
    def __init__(
        self,
        tasks: TaskRepository,
        projects: ProjectRepository,
        events: EventBus | None = None,
    ) -> None:
        self._tasks = tasks
        self._projects = projects
        self._events = events

    def execute(self, input_: CreateTaskInput) -> CreateTaskOutput:
        now = utc_now()
        if input_.project_id is not None:
            project = self._projects.get_by_id(input_.project_id)
            if project is None:
                raise ProjectNotFound(input_.project_id)
            Task.assert_deadline_not_after_project_deadline(
                input_.deadline, project.deadline
            )

        task = Task.create(
            project_id=input_.project_id,
            title=input_.title,
            description=input_.description,
            deadline=input_.deadline,
            now=now,
        )
        saved = self._tasks.save(task)
        if self._events is not None:
            maybe_emit_deadline_approaching_event(
                task=saved, now=now, publish_event=self._events.publish
            )
        return saved
