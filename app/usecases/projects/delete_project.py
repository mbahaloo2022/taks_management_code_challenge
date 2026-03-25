from dataclasses import dataclass
from uuid import UUID

from app.domain.clock import utc_now
from app.domain.project import ProjectNotFound
from app.repos.project_repository import ProjectRepository
from app.repos.task_repository import TaskListFilters, TaskRepository


@dataclass(slots=True)
class DeleteProjectInput:
    project_id: UUID


class DeleteProjectUseCase:
    def __init__(self, projects: ProjectRepository, tasks: TaskRepository) -> None:
        self._projects = projects
        self._tasks = tasks

    def execute(self, input_: DeleteProjectInput) -> None:
        if self._projects.get_by_id(input_.project_id) is None:
            raise ProjectNotFound(input_.project_id)

        now = utc_now()
        associated = self._tasks.list_tasks(
            TaskListFilters(project_id=input_.project_id),
            limit=None,
            offset=0,
        ).items
        for task in associated:
            self._tasks.save(
                task.remove_from_project(expected_project_id=input_.project_id, now=now)
            )

        self._projects.delete(input_.project_id)
