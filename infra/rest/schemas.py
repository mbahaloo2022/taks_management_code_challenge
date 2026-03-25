"""Shared response models (outputs) for HTTP APIs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TaskRead(BaseModel):
    """Task returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID | None
    title: str
    description: str | None
    deadline: datetime
    completed: bool
    created_at: datetime
    updated_at: datetime


class ProjectRead(BaseModel):
    """Project returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    deadline: datetime
    completed: bool
    created_at: datetime
    updated_at: datetime


class PaginatedTasks(BaseModel):
    """Paginated list of tasks."""

    items: list[TaskRead]
    total: int = Field(ge=0, description="Total number of tasks matching the filters.")
    limit: int = Field(ge=1, description="Maximum number of items in this page.")
    offset: int = Field(
        ge=0, description="Number of matching items skipped before this page."
    )


class PaginatedProjects(BaseModel):
    """Paginated list of projects."""

    items: list[ProjectRead]
    total: int = Field(ge=0, description="Total number of projects.")
    limit: int = Field(ge=1, description="Maximum number of items in this page.")
    offset: int = Field(ge=0, description="Number of items skipped before this page.")
