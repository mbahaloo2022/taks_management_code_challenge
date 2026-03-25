from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.clock import utc_now
from app.domain.events import ProjectDeadlineShortenedEvent
from app.domain.project import Project, ProjectNotFound
from app.repos.project_repository import ProjectRepository
from app.repos.task_repository import TaskListFilters, TaskRepository
from app.services.event_bus import EventBus

type UpdateProjectOutput = Project


@dataclass(slots=True)
class UpdateProjectInput:
    project_id: UUID
    title: str | None = None
    deadline: datetime | None = None
    completed: bool | None = None


class UpdateProjectUseCase:
    def __init__(
        self,
        projects: ProjectRepository,
        tasks: TaskRepository,
        events: EventBus | None = None,
    ) -> None:
        self._projects = projects
        self._tasks = tasks
        self._events = events

    def execute(self, input_: UpdateProjectInput) -> UpdateProjectOutput:
        project = self._projects.get_by_id(input_.project_id)
        if project is None:
            raise ProjectNotFound(input_.project_id)

        now = utc_now()
        updated = project.with_updates(
            now=now,
            title=input_.title,
            deadline=input_.deadline,
            completed=(
                project.completed if input_.completed is None else input_.completed
            ),
        )

        associated = self._tasks.list_tasks(
            TaskListFilters(project_id=input_.project_id),
            limit=None,
            offset=0,
        ).items

        if input_.completed is True:
            incomplete = [t.id for t in associated if not t.completed]
            updated = updated.mark_completed(incomplete_task_ids=incomplete, now=now)
        elif input_.completed is False:
            updated = updated.reopen(now=now)

        saved = self._projects.save(updated)

        if (
            input_.deadline is not None
            and input_.deadline < project.deadline
            and self._events is not None
        ):
            self._events.publish(
                ProjectDeadlineShortenedEvent(
                    occurred_at=now,
                    project_id=input_.project_id,
                    old_deadline=project.deadline,
                    new_deadline=input_.deadline,
                )
            )

        return saved
