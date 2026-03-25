from uuid import UUID

from fastapi import APIRouter, status
from pydantic import BaseModel, Field
from starlette.responses import Response

from app.usecases.projects.delete_project import (
    DeleteProjectInput,
    DeleteProjectUseCase,
)
from infra.rest.deps import ProjectRepositoryDep, TaskRepositoryDep

router = APIRouter()


class DeleteProjectHttpInput(BaseModel):
    """Path parameters for DELETE /projects/{project_id}."""

    project_id: UUID = Field(description="Project identifier.")


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project",
    response_class=Response,
)
def delete_project(
    project_id: UUID,
    projects: ProjectRepositoryDep,
    tasks: TaskRepositoryDep,
) -> Response:
    http_in = DeleteProjectHttpInput(project_id=project_id)
    uc = DeleteProjectUseCase(projects, tasks)
    uc.execute(DeleteProjectInput(project_id=http_in.project_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
