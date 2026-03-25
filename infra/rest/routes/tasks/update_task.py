from datetime import datetime
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.usecases.tasks.update_task import UpdateTaskInput, UpdateTaskUseCase
from infra.rest.deps import EventBusDep, ProjectRepositoryDep, TaskRepositoryDep
from infra.rest.schemas import TaskRead

router = APIRouter()


class PutTaskHttpBody(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    description: str | None = None
    deadline: datetime | None = None
    completed: bool | None = None
    project_id: UUID | None = None


@router.put("/{task_id}", response_model=TaskRead, summary="Update a task")
def update_task(
    task_id: UUID,
    body: PutTaskHttpBody,
    tasks: TaskRepositoryDep,
    projects: ProjectRepositoryDep,
    events: EventBusDep,
) -> TaskRead:
    uc = UpdateTaskUseCase(tasks, projects, events)
    task = uc.execute(
        UpdateTaskInput(
            task_id=task_id,
            title=body.title,
            description=body.description,
            deadline=body.deadline,
            completed=body.completed,
            project_id=body.project_id,
        )
    )
    return TaskRead.model_validate(task)
