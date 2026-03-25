from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.config import AppConfig
from app.domain.project import ProjectCompletionDenied
from app.domain.task import (
    DeadlineAfterProjectDeadline,
    DomainError,
    ResourceNotFound,
    TaskProjectMismatch,
)
from app.repos.project_repository import ProjectRepository
from app.repos.task_repository import TaskRepository
from app.usecases.event_handlers import (
    make_project_deadline_shortened_handler,
    make_task_completed_handler,
    make_task_deadline_approaching_handler,
    make_task_reopened_handler,
)
from infra.rest.routes.mount import mount_api_routes
from infra.services.event_bus import InMemoryEventBus
from infra.services.notifications import InMemoryNotificationService
from app.domain.events import (
    ProjectDeadlineShortenedEvent,
    TaskCompletedEvent,
    TaskDeadlineApproachingEvent,
    TaskReopenedEvent,
)


def create_app(
    *,
    task_repository: TaskRepository | None = None,
    project_repository: ProjectRepository | None = None,
    config: AppConfig | None = None,
) -> FastAPI:
    """Build the FastAPI application with optional repository wiring."""

    app = FastAPI(
        title="Tasks API",
        description=(
            "HTTP API for managing tasks and projects: CRUD, completion, "
            "linking tasks to projects, and listing tasks by project."
        ),
        version="0.2.0",
    )
    app.state.task_repository = task_repository
    app.state.project_repository = project_repository
    app.state.config = config or AppConfig()
    app.state.event_bus = InMemoryEventBus()
    app.state.notification_service = InMemoryNotificationService()

    if task_repository is not None and project_repository is not None:
        bus = app.state.event_bus
        notifications = app.state.notification_service
        bus.subscribe(
            ProjectDeadlineShortenedEvent,
            make_project_deadline_shortened_handler(task_repository),
        )
        bus.subscribe(
            TaskCompletedEvent,
            make_task_completed_handler(
                task_repository,
                project_repository,
                app.state.config,
                notifications,
                bus.publish,
            ),
        )
        bus.subscribe(TaskReopenedEvent, make_task_reopened_handler(project_repository))
        bus.subscribe(
            TaskDeadlineApproachingEvent,
            make_task_deadline_approaching_handler(
                notifications,
                within_hours=app.state.config.approaching_deadline_hours,
            ),
        )

    @app.exception_handler(ResourceNotFound)
    async def handle_not_found(_: Request, exc: ResourceNotFound) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(DeadlineAfterProjectDeadline)
    async def handle_deadline_violation(
        _: Request,
        exc: DeadlineAfterProjectDeadline,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ProjectCompletionDenied)
    async def handle_project_completion_denied(
        _: Request,
        exc: ProjectCompletionDenied,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "detail": str(exc),
                "incomplete_task_ids": [str(x) for x in exc.incomplete_task_ids],
            },
        )

    @app.exception_handler(TaskProjectMismatch)
    async def handle_task_project_mismatch(
        _: Request,
        exc: TaskProjectMismatch,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(DomainError)
    async def handle_domain_error(_: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    mount_api_routes(app)

    return app
