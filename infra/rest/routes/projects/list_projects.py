from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.usecases.projects.list_projects import ListProjectsInput, ListProjectsUseCase
from infra.rest.deps import ProjectRepositoryDep
from infra.rest.schemas import PaginatedProjects, ProjectRead

router = APIRouter()


class ListProjectsHttpInput(BaseModel):
    """Query parameters for GET /projects."""

    limit: int = Field(default=20, ge=1, le=100, description="Page size.")
    offset: int = Field(default=0, ge=0, description="Number of items to skip.")


def _list_projects_query(
    limit: int = Query(20, ge=1, le=100, description="Page size."),
    offset: int = Query(0, ge=0, description="Number of items to skip."),
) -> ListProjectsHttpInput:
    return ListProjectsHttpInput(limit=limit, offset=offset)


@router.get(
    "",
    response_model=PaginatedProjects,
    summary="List projects",
    description="Returns projects with pagination via limit and offset.",
)
def list_projects(
    http_in: Annotated[ListProjectsHttpInput, Depends(_list_projects_query)],
    projects: ProjectRepositoryDep,
) -> PaginatedProjects:
    uc = ListProjectsUseCase(projects)
    page = uc.execute(ListProjectsInput(limit=http_in.limit, offset=http_in.offset))
    return PaginatedProjects(
        items=[ProjectRead.model_validate(p) for p in page.items],
        total=page.total,
        limit=http_in.limit,
        offset=http_in.offset,
    )
