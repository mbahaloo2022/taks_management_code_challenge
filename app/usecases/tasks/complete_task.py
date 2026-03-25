from dataclasses import dataclass
from uuid import UUID

from app.domain.clock import utc_now
from app.domain.events import TaskCompletedEvent
from app.domain.task import Task, TaskNotFound
from app.repos.project_repository import ProjectRepository
from app.repos.task_repository import TaskRepository
from app.services.event_bus import EventBus

type CompleteTaskOutput = Task


@dataclass(slots=True)
class CompleteTaskInput:
    task_id: UUID


class CompleteTaskUseCase:
    def __init__(
        self,
        tasks: TaskRepository,
        projects: ProjectRepository,
        config,
        events: EventBus | None = None,
    ) -> None:
        self._tasks = tasks
        self._projects = projects
        self._config = config
        self._events = events

    def execute(self, input_: CompleteTaskInput) -> CompleteTaskOutput:
        task = self._tasks.get_by_id(input_.task_id)
        if task is None:
            raise TaskNotFound(input_.task_id)
        if task.completed:
            return task

        now = utc_now()
        saved = self._tasks.save(task.mark_completed(now=now))
        if self._events is not None:
            self._events.publish(
                TaskCompletedEvent(
                    occurred_at=now, task_id=saved.id, project_id=saved.project_id
                )
            )
        return saved
