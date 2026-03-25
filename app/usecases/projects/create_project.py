from dataclasses import dataclass
from datetime import datetime

from app.domain.clock import utc_now
from app.domain.project import Project
from app.repos.project_repository import ProjectRepository

type CreateProjectOutput = Project


@dataclass(slots=True)
class CreateProjectInput:
    title: str
    deadline: datetime


class CreateProjectUseCase:
    def __init__(self, projects: ProjectRepository) -> None:
        self._projects = projects

    def execute(self, input_: CreateProjectInput) -> CreateProjectOutput:
        now = utc_now()
        project = Project.create(title=input_.title, deadline=input_.deadline, now=now)
        return self._projects.save(project)
