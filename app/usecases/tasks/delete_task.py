from dataclasses import dataclass
from uuid import UUID

from app.domain.task import TaskNotFound
from app.repos.task_repository import TaskRepository


@dataclass(slots=True)
class DeleteTaskInput:
    task_id: UUID


class DeleteTaskUseCase:
    def __init__(self, tasks: TaskRepository) -> None:
        self._tasks = tasks

    def execute(self, input_: DeleteTaskInput) -> None:
        if self._tasks.get_by_id(input_.task_id) is None:
            raise TaskNotFound(input_.task_id)
        self._tasks.delete(input_.task_id)
        return None
