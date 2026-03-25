from dataclasses import dataclass
from uuid import UUID

from app.domain.project import ProjectNotFound
from app.domain.task import Task
from app.repos.project_repository import ProjectRepository
from app.repos.task_repository import TaskListFilters, TaskRepository

type ListProjectTasksOutput = list[Task]


@dataclass(slots=True)
class ListProjectTasksInput:
    project_id: UUID


class ListProjectTasksUseCase:
    def __init__(self, tasks: TaskRepository, projects: ProjectRepository) -> None:
        self._tasks = tasks
        self._projects = projects

    def execute(self, input_: ListProjectTasksInput) -> ListProjectTasksOutput:
        if self._projects.get_by_id(input_.project_id) is None:
            raise ProjectNotFound(input_.project_id)
        return self._tasks.list_tasks(
            TaskListFilters(project_id=input_.project_id),
            limit=None,
            offset=0,
        ).items
