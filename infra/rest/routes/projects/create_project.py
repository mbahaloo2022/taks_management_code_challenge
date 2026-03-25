from datetime import datetime

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.usecases.projects.create_project import (
    CreateProjectInput,
    CreateProjectUseCase,
)
from infra.rest.deps import ProjectRepositoryDep
from infra.rest.schemas import ProjectRead

router = APIRouter()


class PostProjectHttpBody(BaseModel):
    """JSON body for POST /projects."""

    title: str = Field(min_length=1, description="Project title.")
    deadline: datetime = Field(
        description="Project deadline (timezone-aware recommended).",
    )


@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a project",
)
def create_project(
    body: PostProjectHttpBody, projects: ProjectRepositoryDep
) -> ProjectRead:
    uc = CreateProjectUseCase(projects)
    project = uc.execute(CreateProjectInput(title=body.title, deadline=body.deadline))
    return ProjectRead.model_validate(project)
