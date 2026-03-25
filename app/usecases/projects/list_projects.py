from dataclasses import dataclass

from app.domain.project import Project
from app.repos.page import Page
from app.repos.project_repository import ProjectRepository

type ListProjectsOutput = Page[Project]


@dataclass(slots=True)
class ListProjectsInput:
    limit: int = 20
    offset: int = 0


class ListProjectsUseCase:
    def __init__(self, projects: ProjectRepository) -> None:
        self._projects = projects

    def execute(self, input_: ListProjectsInput) -> ListProjectsOutput:
        return self._projects.list_projects(limit=input_.limit, offset=input_.offset)
