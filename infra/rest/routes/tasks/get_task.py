from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.usecases.tasks.get_task import GetTaskInput, GetTaskUseCase
from infra.rest.deps import TaskRepositoryDep
from infra.rest.schemas import TaskRead

router = APIRouter()


class GetTaskHttpInput(BaseModel):
    """Path parameters for GET /tasks/{task_id}."""

    task_id: UUID = Field(description="Task identifier.")


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    summary="Get a task",
)
def get_task(task_id: UUID, tasks: TaskRepositoryDep) -> TaskRead:
    http_in = GetTaskHttpInput(task_id=task_id)
    uc = GetTaskUseCase(tasks)
    task = uc.execute(GetTaskInput(task_id=http_in.task_id))
    return TaskRead.model_validate(task)
