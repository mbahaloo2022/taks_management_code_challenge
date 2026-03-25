from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.task import Task
from app.repos.page import Page
from app.repos.task_repository import TaskListFilters, TaskRepository

from app.domain.clock import utc_now

type ListTasksOutput = Page[Task]


@dataclass(slots=True)
class ListTasksInput:
    completed: bool | None = None
    overdue: bool | None = None
    project_id: UUID | None = None
    limit: int = 20
    offset: int = 0


class ListTasksUseCase:
    def __init__(self, tasks: TaskRepository) -> None:
        self._tasks = tasks

    def execute(
        self, input_: ListTasksInput, *, now: datetime | None = None
    ) -> ListTasksOutput:
        now = now or utc_now()
        repo_filters = TaskListFilters(
            completed=input_.completed,
            project_id=input_.project_id,
            overdue=True if input_.overdue is True else None,
        )
        as_of = now if input_.overdue is True else None
        return self._tasks.list_tasks(
            repo_filters,
            as_of=as_of,
            limit=input_.limit,
            offset=input_.offset,
        )
