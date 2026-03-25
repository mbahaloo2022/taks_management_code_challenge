from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Application settings that affect use-case behavior."""

    auto_complete_project_when_all_tasks_done: bool = True
    approaching_deadline_hours: int = 24
