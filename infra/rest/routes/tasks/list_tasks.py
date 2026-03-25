from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.usecases.tasks.list_tasks import ListTasksInput, ListTasksUseCase
from infra.rest.deps import TaskRepositoryDep
from infra.rest.schemas import PaginatedTasks, TaskRead

router = APIRouter()


class ListTasksHttpInput(BaseModel):
    """Query parameters for GET /tasks."""

    completed: bool | None = None
    overdue: bool | None = None
    project_id: UUID | None = None
    limit: int = Field(default=20, ge=1, le=100, description="Page size.")
    offset: int = Field(default=0, ge=0, description="Number of items to skip.")


def _list_tasks_query(
    completed: bool | None = Query(None, description="Filter by completion status."),
    overdue: bool | None = Query(
        None,
        description="When true, only tasks past deadline and not completed.",
    ),
    project_id: UUID | None = Query(None, description="Filter by project."),
    limit: int = Query(20, ge=1, le=100, description="Page size."),
    offset: int = Query(0, ge=0, description="Number of items to skip."),
) -> ListTasksHttpInput:
    return ListTasksHttpInput(
        completed=completed,
        overdue=overdue,
        project_id=project_id,
        limit=limit,
        offset=offset,
    )


@router.get(
    "",
    response_model=PaginatedTasks,
    summary="List tasks",
    description=(
        "Returns tasks matching optional filters, with pagination. "
        "Use limit and offset to page through results."
    ),
)
def list_tasks(
    http_in: Annotated[ListTasksHttpInput, Depends(_list_tasks_query)],
    tasks: TaskRepositoryDep,
) -> PaginatedTasks:
    uc = ListTasksUseCase(tasks)
    page = uc.execute(
        ListTasksInput(
            completed=http_in.completed,
            overdue=http_in.overdue,
            project_id=http_in.project_id,
            limit=http_in.limit,
            offset=http_in.offset,
        ),
    )
    return PaginatedTasks(
        items=[TaskRead.model_validate(t) for t in page.items],
        total=page.total,
        limit=http_in.limit,
        offset=http_in.offset,
    )
