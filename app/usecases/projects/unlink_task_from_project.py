from dataclasses import dataclass
from uuid import UUID

from app.domain.clock import utc_now
from app.domain.project import ProjectNotFound
from app.domain.task import Task, TaskNotFound
from app.repos.project_repository import ProjectRepository
from app.repos.task_repository import TaskRepository

type UnlinkTaskFromProjectOutput = Task


@dataclass(slots=True)
class UnlinkTaskFromProjectInput:
    project_id: UUID
    task_id: UUID


class UnlinkTaskFromProjectUseCase:
    def __init__(self, tasks: TaskRepository, projects: ProjectRepository) -> None:
        self._tasks = tasks
        self._projects = projects

    def execute(
        self, input_: UnlinkTaskFromProjectInput
    ) -> UnlinkTaskFromProjectOutput:
        if self._projects.get_by_id(input_.project_id) is None:
            raise ProjectNotFound(input_.project_id)
        task = self._tasks.get_by_id(input_.task_id)
        if task is None:
            raise TaskNotFound(input_.task_id)

        now = utc_now()
        unlinked = task.remove_from_project(
            expected_project_id=input_.project_id, now=now
        )
        return self._tasks.save(unlinked)
