from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.usecases.tasks.create_task import CreateTaskInput, CreateTaskUseCase
from infra.rest.deps import EventBusDep, ProjectRepositoryDep, TaskRepositoryDep
from infra.rest.schemas import TaskRead

router = APIRouter()


class PostTaskHttpBody(BaseModel):
    title: str = Field(min_length=1, description="Task title.")
    description: str | None = Field(default=None, description="Optional description.")
    deadline: datetime = Field(
        description="Task deadline (timezone-aware recommended)."
    )
    project_id: UUID | None = Field(
        default=None, description="Optional project to associate the task with."
    )


@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a task",
)
def create_task(
    body: PostTaskHttpBody,
    tasks: TaskRepositoryDep,
    projects: ProjectRepositoryDep,
    events: EventBusDep,
) -> TaskRead:
    uc = CreateTaskUseCase(tasks, projects, events)
    task = uc.execute(
        CreateTaskInput(
            title=body.title,
            description=body.description,
            deadline=body.deadline,
            project_id=body.project_id,
        )
    )
    return TaskRead.model_validate(task)
