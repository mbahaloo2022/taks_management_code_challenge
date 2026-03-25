from datetime import datetime
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.usecases.projects.update_project import (
    UpdateProjectInput,
    UpdateProjectUseCase,
)
from infra.rest.deps import EventBusDep, ProjectRepositoryDep, TaskRepositoryDep
from infra.rest.schemas import ProjectRead

router = APIRouter()


class PutProjectHttpBody(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    deadline: datetime | None = None
    completed: bool | None = None


@router.put("/{project_id}", response_model=ProjectRead, summary="Update a project")
def update_project(
    project_id: UUID,
    body: PutProjectHttpBody,
    projects: ProjectRepositoryDep,
    tasks: TaskRepositoryDep,
    events: EventBusDep,
) -> ProjectRead:
    uc = UpdateProjectUseCase(projects, tasks, events)
    project = uc.execute(
        UpdateProjectInput(
            project_id=project_id,
            title=body.title,
            deadline=body.deadline,
            completed=body.completed,
        )
    )
    return ProjectRead.model_validate(project)
