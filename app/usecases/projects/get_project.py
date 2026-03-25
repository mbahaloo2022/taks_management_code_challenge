from dataclasses import dataclass
from uuid import UUID

from app.domain.project import Project, ProjectNotFound
from app.repos.project_repository import ProjectRepository

type GetProjectOutput = Project


@dataclass(slots=True)
class GetProjectInput:
    project_id: UUID


class GetProjectUseCase:
    def __init__(self, projects: ProjectRepository) -> None:
        self._projects = projects

    def execute(self, input_: GetProjectInput) -> GetProjectOutput:
        project = self._projects.get_by_id(input_.project_id)
        if project is None:
            raise ProjectNotFound(input_.project_id)
        return project
