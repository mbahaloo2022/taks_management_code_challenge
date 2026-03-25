from datetime import UTC, datetime, timedelta

from app.config import AppConfig
from app.domain.project import Project, ProjectCompletionDenied
from app.domain.task import DeadlineAfterProjectDeadline, Task
from app.usecases.projects.create_project import (
    CreateProjectInput,
    CreateProjectUseCase,
)
from app.usecases.projects.link_task_to_project import (
    LinkTaskToProjectInput,
    LinkTaskToProjectUseCase,
)
from app.usecases.projects.update_project import (
    UpdateProjectInput,
    UpdateProjectUseCase,
)
from app.usecases.tasks.complete_task import CompleteTaskInput, CompleteTaskUseCase
from app.usecases.tasks.create_task import CreateTaskInput, CreateTaskUseCase
from app.usecases.tasks.list_tasks import ListTasksInput, ListTasksUseCase
from app.usecases.tasks.update_task import UpdateTaskInput, UpdateTaskUseCase
from infra.repos.database import SqliteDatabase
from infra.repos.project_repository_sqlite import SqliteProjectRepository
from infra.repos.task_repository_sqlite import SqliteTaskRepository
from infra.services.event_bus import InMemoryEventBus
from infra.services.notifications import InMemoryNotificationService
from app.usecases.event_handlers import (
    make_project_deadline_shortened_handler,
    make_task_completed_handler,
    make_task_deadline_approaching_handler,
    make_task_reopened_handler,
)
from app.domain.events import (
    ProjectDeadlineShortenedEvent,
    TaskCompletedEvent,
    TaskDeadlineApproachingEvent,
    TaskReopenedEvent,
)


def setup_stack(tmp_path):
    db = SqliteDatabase(tmp_path / "domain.db")
    tasks = SqliteTaskRepository(db)
    projects = SqliteProjectRepository(db)
    bus = InMemoryEventBus()
    notifications = InMemoryNotificationService()
    config = AppConfig(auto_complete_project_when_all_tasks_done=True)
    bus.subscribe(
        ProjectDeadlineShortenedEvent, make_project_deadline_shortened_handler(tasks)
    )
    bus.subscribe(TaskReopenedEvent, make_task_reopened_handler(projects))
    bus.subscribe(
        TaskDeadlineApproachingEvent,
        make_task_deadline_approaching_handler(notifications),
    )
    bus.subscribe(
        TaskCompletedEvent,
        make_task_completed_handler(
            tasks, projects, config, notifications, bus.publish
        ),
    )
    return db, tasks, projects, bus, notifications, config


def test_task_deadline_must_not_exceed_project_deadline(tmp_path):
    db, tasks, projects, bus, _, _ = setup_stack(tmp_path)
    project = CreateProjectUseCase(projects).execute(
        CreateProjectInput("Proj", datetime.now(UTC) + timedelta(days=2))
    )
    try:
        try:
            CreateTaskUseCase(tasks, projects, bus).execute(
                CreateTaskInput(
                    "Late", None, datetime.now(UTC) + timedelta(days=3), project.id
                )
            )
            assert False, "expected exception"
        except DeadlineAfterProjectDeadline:
            assert True
    finally:
        db.close()


def test_project_deadline_shortening_adjusts_task_deadlines(tmp_path):
    db, tasks, projects, bus, _, _ = setup_stack(tmp_path)
    project = CreateProjectUseCase(projects).execute(
        CreateProjectInput("Proj", datetime.now(UTC) + timedelta(days=5))
    )
    task = CreateTaskUseCase(tasks, projects, bus).execute(
        CreateTaskInput("T1", None, datetime.now(UTC) + timedelta(days=4), project.id)
    )
    updated = UpdateProjectUseCase(projects, tasks, bus).execute(
        UpdateProjectInput(project.id, deadline=datetime.now(UTC) + timedelta(days=2))
    )
    adjusted = tasks.get_by_id(task.id)
    try:
        assert adjusted is not None
        assert adjusted.deadline == updated.deadline
    finally:
        db.close()


def test_project_cannot_be_completed_with_open_tasks(tmp_path):
    db, tasks, projects, bus, _, _ = setup_stack(tmp_path)
    project = CreateProjectUseCase(projects).execute(
        CreateProjectInput("Proj", datetime.now(UTC) + timedelta(days=5))
    )
    CreateTaskUseCase(tasks, projects, bus).execute(
        CreateTaskInput("T1", None, datetime.now(UTC) + timedelta(days=2), project.id)
    )
    try:
        try:
            UpdateProjectUseCase(projects, tasks, bus).execute(
                UpdateProjectInput(project.id, completed=True)
            )
            assert False, "expected conflict"
        except ProjectCompletionDenied:
            assert True
    finally:
        db.close()


def test_completing_last_task_auto_completes_project(tmp_path):
    db, tasks, projects, bus, notifications, config = setup_stack(tmp_path)
    project = CreateProjectUseCase(projects).execute(
        CreateProjectInput("Proj", datetime.now(UTC) + timedelta(days=5))
    )
    task = CreateTaskUseCase(tasks, projects, bus).execute(
        CreateTaskInput("T1", None, datetime.now(UTC) + timedelta(days=2), project.id)
    )
    completed = CompleteTaskUseCase(tasks, projects, config, bus).execute(
        CompleteTaskInput(task.id)
    )
    refreshed_project = projects.get_by_id(project.id)
    try:
        assert completed.completed is True
        assert refreshed_project is not None and refreshed_project.completed is True
        assert any(
            "marked as completed" in msg
            for level, msg in notifications.messages
            if level == "info"
        )
    finally:
        db.close()


def test_reopening_task_reopens_completed_project(tmp_path):
    db, tasks, projects, bus, _, config = setup_stack(tmp_path)
    project = CreateProjectUseCase(projects).execute(
        CreateProjectInput("Proj", datetime.now(UTC) + timedelta(days=5))
    )
    task = CreateTaskUseCase(tasks, projects, bus).execute(
        CreateTaskInput("T1", None, datetime.now(UTC) + timedelta(days=2), project.id)
    )
    CompleteTaskUseCase(tasks, projects, config, bus).execute(
        CompleteTaskInput(task.id)
    )
    reopened = UpdateTaskUseCase(tasks, projects, bus).execute(
        UpdateTaskInput(task.id, completed=False)
    )
    refreshed_project = projects.get_by_id(project.id)
    try:
        assert reopened.completed is False
        assert refreshed_project is not None and refreshed_project.completed is False
    finally:
        db.close()


def test_approaching_deadline_notification_is_emitted(tmp_path):
    db, tasks, projects, bus, notifications, _ = setup_stack(tmp_path)
    task = CreateTaskUseCase(tasks, projects, bus).execute(
        CreateTaskInput("Soon", None, datetime.now(UTC) + timedelta(hours=4), None)
    )
    try:
        assert task.title == "Soon"
        assert any(level == "warning" for level, _ in notifications.messages)
    finally:
        db.close()


def test_overdue_filter_only_returns_open_past_deadline_tasks(tmp_path):
    db, tasks, projects, bus, _, _ = setup_stack(tmp_path)
    now = datetime.now(UTC)
    late = CreateTaskUseCase(tasks, projects, bus).execute(
        CreateTaskInput("Late", None, now - timedelta(hours=2), None)
    )
    done = CreateTaskUseCase(tasks, projects, bus).execute(
        CreateTaskInput("Done", None, now - timedelta(hours=1), None)
    )
    UpdateTaskUseCase(tasks, projects, bus).execute(
        UpdateTaskInput(done.id, completed=True)
    )
    CreateTaskUseCase(tasks, projects, bus).execute(
        CreateTaskInput("Future", None, now + timedelta(days=1), None)
    )
    page = ListTasksUseCase(tasks).execute(
        ListTasksInput(overdue=True, limit=20, offset=0), now=now
    )
    try:
        assert [item.id for item in page.items] == [late.id]
    finally:
        db.close()


def test_linking_task_to_project_enforces_deadline_rule(tmp_path):
    db, tasks, projects, bus, _, _ = setup_stack(tmp_path)
    project = CreateProjectUseCase(projects).execute(
        CreateProjectInput("Proj", datetime.now(UTC) + timedelta(days=1))
    )
    task = CreateTaskUseCase(tasks, projects, bus).execute(
        CreateTaskInput("Late", None, datetime.now(UTC) + timedelta(days=2), None)
    )
    try:
        try:
            LinkTaskToProjectUseCase(tasks, projects).execute(
                LinkTaskToProjectInput(project.id, task.id)
            )
            assert False, "expected violation"
        except DeadlineAfterProjectDeadline:
            assert True
    finally:
        db.close()
