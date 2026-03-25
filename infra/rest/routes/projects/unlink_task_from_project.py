from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.usecases.projects.unlink_task_from_project import (
    UnlinkTaskFromProjectInput,
    UnlinkTaskFromProjectUseCase,
)
from infra.rest.deps import ProjectRepositoryDep, TaskRepositoryDep
from infra.rest.schemas import TaskRead

router = APIRouter()


class DeleteProjectTaskUnlinkHttpInput(BaseModel):
    """Path parameters for DELETE .../unlink."""

    project_id: UUID = Field(description="Project identifier.")
    task_id: UUID = Field(description="Task identifier.")


@router.delete(
    "/{project_id}/tasks/{task_id}/unlink",
    response_model=TaskRead,
    summary="Unlink a task from a project",
)
def unlink_task_from_project(
    project_id: UUID,
    task_id: UUID,
    tasks: TaskRepositoryDep,
    projects: ProjectRepositoryDep,
) -> TaskRead:
    http_in = DeleteProjectTaskUnlinkHttpInput(project_id=project_id, task_id=task_id)
    uc = UnlinkTaskFromProjectUseCase(tasks, projects)
    task = uc.execute(
        UnlinkTaskFromProjectInput(
            project_id=http_in.project_id, task_id=http_in.task_id
        ),
    )
    return TaskRead.model_validate(task)
