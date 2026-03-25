from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.usecases.tasks.complete_task import CompleteTaskInput, CompleteTaskUseCase
from infra.rest.deps import (
    AppConfigDep,
    EventBusDep,
    ProjectRepositoryDep,
    TaskRepositoryDep,
)
from infra.rest.schemas import TaskRead

router = APIRouter()


class PatchTaskCompleteHttpInput(BaseModel):
    task_id: UUID = Field(description="Task identifier.")


@router.patch(
    "/{task_id}/complete", response_model=TaskRead, summary="Mark a task completed"
)
def complete_task(
    task_id: UUID,
    tasks: TaskRepositoryDep,
    projects: ProjectRepositoryDep,
    config: AppConfigDep,
    events: EventBusDep,
) -> TaskRead:
    http_in = PatchTaskCompleteHttpInput(task_id=task_id)
    uc = CompleteTaskUseCase(tasks, projects, config, events)
    task = uc.execute(CompleteTaskInput(task_id=http_in.task_id))
    return TaskRead.model_validate(task)
