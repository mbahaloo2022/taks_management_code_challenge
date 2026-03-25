"""FastAPI dependencies: repositories and services from ``app.state``."""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from app.config import AppConfig
from app.repos.project_repository import ProjectRepository
from app.repos.task_repository import TaskRepository
from app.services.event_bus import EventBus
from app.services.notification_service import NotificationService


def _not_configured(what: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"{what} is not configured. Provide it when creating the application.",
    )


def get_task_repository(request: Request) -> TaskRepository:
    repo = getattr(request.app.state, "task_repository", None)
    if repo is None:
        raise _not_configured("Task repository")
    return repo


def get_project_repository(request: Request) -> ProjectRepository:
    repo = getattr(request.app.state, "project_repository", None)
    if repo is None:
        raise _not_configured("Project repository")
    return repo


def get_app_config(request: Request) -> AppConfig:
    return request.app.state.config


def get_event_bus(request: Request) -> EventBus:
    bus = getattr(request.app.state, "event_bus", None)
    if bus is None:
        raise _not_configured("Event bus")
    return bus


def get_notification_service(request: Request) -> NotificationService:
    service = getattr(request.app.state, "notification_service", None)
    if service is None:
        raise _not_configured("Notification service")
    return service


TaskRepositoryDep = Annotated[TaskRepository, Depends(get_task_repository)]
ProjectRepositoryDep = Annotated[ProjectRepository, Depends(get_project_repository)]
AppConfigDep = Annotated[AppConfig, Depends(get_app_config)]
EventBusDep = Annotated[EventBus, Depends(get_event_bus)]
NotificationServiceDep = Annotated[
    NotificationService, Depends(get_notification_service)
]
