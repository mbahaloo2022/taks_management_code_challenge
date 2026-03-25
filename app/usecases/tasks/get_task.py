from dataclasses import dataclass
from uuid import UUID

from app.domain.task import Task, TaskNotFound
from app.repos.task_repository import TaskRepository

type GetTaskOutput = Task


@dataclass(slots=True)
class GetTaskInput:
    task_id: UUID


class GetTaskUseCase:
    def __init__(self, tasks: TaskRepository) -> None:
        self._tasks = tasks

    def execute(self, input_: GetTaskInput) -> GetTaskOutput:
        task = self._tasks.get_by_id(input_.task_id)
        if task is None:
            raise TaskNotFound(input_.task_id)
        return task
