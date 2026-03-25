from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.usecases.projects.link_task_to_project import (
    LinkTaskToProjectInput,
    LinkTaskToProjectUseCase,
)
from infra.rest.deps import ProjectRepositoryDep, TaskRepositoryDep
from infra.rest.schemas import TaskRead

router = APIRouter()


class PostProjectTaskLinkHttpInput(BaseModel):
    """Path parameters for POST .../link."""

    project_id: UUID = Field(description="Project identifier.")
    task_id: UUID = Field(description="Task identifier.")


@router.post(
    "/{project_id}/tasks/{task_id}/link",
    response_model=TaskRead,
    summary="Link a task to a project",
)
def link_task_to_project(
    project_id: UUID,
    task_id: UUID,
    tasks: TaskRepositoryDep,
    projects: ProjectRepositoryDep,
) -> TaskRead:
    http_in = PostProjectTaskLinkHttpInput(project_id=project_id, task_id=task_id)
    uc = LinkTaskToProjectUseCase(tasks, projects)
    task = uc.execute(
        LinkTaskToProjectInput(project_id=http_in.project_id, task_id=http_in.task_id),
    )
    return TaskRead.model_validate(task)
