from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.usecases.projects.get_project import GetProjectInput, GetProjectUseCase
from infra.rest.deps import ProjectRepositoryDep
from infra.rest.schemas import ProjectRead

router = APIRouter()


class GetProjectHttpInput(BaseModel):
    """Path parameters for GET /projects/{project_id}."""

    project_id: UUID = Field(description="Project identifier.")


@router.get(
    "/{project_id}",
    response_model=ProjectRead,
    summary="Get a project",
)
def get_project(project_id: UUID, projects: ProjectRepositoryDep) -> ProjectRead:
    http_in = GetProjectHttpInput(project_id=project_id)
    uc = GetProjectUseCase(projects)
    project = uc.execute(GetProjectInput(project_id=http_in.project_id))
    return ProjectRead.model_validate(project)
