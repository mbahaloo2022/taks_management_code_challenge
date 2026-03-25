from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel, Field, RootModel

from app.usecases.projects.list_project_tasks import (
    ListProjectTasksInput,
    ListProjectTasksUseCase,
)
from infra.rest.deps import ProjectRepositoryDep, TaskRepositoryDep
from infra.rest.schemas import TaskRead

router = APIRouter()


class GetProjectTasksHttpInput(BaseModel):
    """Path parameters for GET /projects/{project_id}/tasks."""

    project_id: UUID = Field(description="Project identifier.")


class ListProjectTasksHttpOutput(RootModel[list[TaskRead]]):
    """Response body for GET /projects/{project_id}/tasks (JSON array of tasks)."""


@router.get(
    "/{project_id}/tasks",
    response_model=ListProjectTasksHttpOutput,
    summary="List tasks for a project",
)
def list_project_tasks(
    project_id: UUID,
    tasks: TaskRepositoryDep,
    projects: ProjectRepositoryDep,
) -> ListProjectTasksHttpOutput:
    http_in = GetProjectTasksHttpInput(project_id=project_id)
    uc = ListProjectTasksUseCase(tasks, projects)
    task_list = uc.execute(ListProjectTasksInput(project_id=http_in.project_id))
    return ListProjectTasksHttpOutput([TaskRead.model_validate(t) for t in task_list])
