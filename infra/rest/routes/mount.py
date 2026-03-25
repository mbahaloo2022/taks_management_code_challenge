"""Register all HTTP route modules on the application."""

from fastapi import FastAPI

from infra.rest.routes.projects import (
    create_project,
    delete_project,
    get_project,
    link_task_to_project,
    list_project_tasks,
    list_projects,
    unlink_task_from_project,
    update_project,
)
from infra.rest.routes.tasks import (
    complete_task,
    create_task,
    delete_task,
    get_task,
    list_tasks,
    update_task,
)


def mount_api_routes(app: FastAPI) -> None:
    task_tag = ["tasks"]
    project_tag = ["projects"]
    tp = "/tasks"
    pp = "/projects"

    app.include_router(list_tasks.router, prefix=tp, tags=task_tag)
    app.include_router(create_task.router, prefix=tp, tags=task_tag)
    app.include_router(get_task.router, prefix=tp, tags=task_tag)
    app.include_router(update_task.router, prefix=tp, tags=task_tag)
    app.include_router(delete_task.router, prefix=tp, tags=task_tag)
    app.include_router(complete_task.router, prefix=tp, tags=task_tag)

    app.include_router(list_projects.router, prefix=pp, tags=project_tag)
    app.include_router(create_project.router, prefix=pp, tags=project_tag)
    app.include_router(get_project.router, prefix=pp, tags=project_tag)
    app.include_router(update_project.router, prefix=pp, tags=project_tag)
    app.include_router(delete_project.router, prefix=pp, tags=project_tag)
    app.include_router(link_task_to_project.router, prefix=pp, tags=project_tag)
    app.include_router(unlink_task_from_project.router, prefix=pp, tags=project_tag)
    app.include_router(list_project_tasks.router, prefix=pp, tags=project_tag)
