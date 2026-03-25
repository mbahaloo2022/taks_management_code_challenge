from typing import Protocol
from uuid import UUID

from app.domain.project import Project

from app.repos.page import Page


class ProjectRepository(Protocol):
    def get_by_id(self, project_id: UUID) -> Project | None:
        """Return the project or None if it does not exist."""

    def list_projects(
        self,
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> Page[Project]:
        """Return projects, optionally paginated.

        When ``limit`` is None, all projects are returned; ``Page.limit`` should be None.
        """

    def save(self, project: Project) -> Project:
        """Persist create or update.

        Returns:
            Project: The saved project.
        """

    def delete(self, project_id: UUID) -> None:
        """Remove the project if it exists."""
