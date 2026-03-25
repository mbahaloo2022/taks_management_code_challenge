from uuid import UUID

from fastapi import APIRouter, status
from pydantic import BaseModel, Field
from starlette.responses import Response

from app.usecases.tasks.delete_task import DeleteTaskInput, DeleteTaskUseCase
from infra.rest.deps import TaskRepositoryDep

router = APIRouter()


class DeleteTaskHttpInput(BaseModel):
    """Path parameters for DELETE /tasks/{task_id}."""

    task_id: UUID = Field(description="Task identifier.")


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    response_class=Response,
)
def delete_task(task_id: UUID, tasks: TaskRepositoryDep) -> Response:
    http_in = DeleteTaskHttpInput(task_id=task_id)
    uc = DeleteTaskUseCase(tasks)
    uc.execute(DeleteTaskInput(task_id=http_in.task_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
