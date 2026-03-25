from datetime import UTC, datetime, timedelta


def iso(dt: datetime) -> str:
    return dt.astimezone(UTC).isoformat()


def test_task_and_project_crud_and_filters(client):
    project_deadline = datetime.now(UTC) + timedelta(days=3)
    project = client.post(
        "/projects", json={"title": "P1", "deadline": iso(project_deadline)}
    ).json()
    assert project["title"] == "P1"

    task_deadline = datetime.now(UTC) + timedelta(days=1)
    task = client.post(
        "/tasks",
        json={
            "title": "T1",
            "description": "desc",
            "deadline": iso(task_deadline),
            "project_id": project["id"],
        },
    ).json()
    assert task["project_id"] == project["id"]

    listed = client.get("/tasks", params={"project_id": project["id"]}).json()
    assert listed["total"] == 1

    get_task = client.get(f"/tasks/{task['id']}")
    assert get_task.status_code == 200

    complete = client.patch(f"/tasks/{task['id']}/complete")
    assert complete.status_code == 200
    assert complete.json()["completed"] is True

    project_tasks = client.get(f"/projects/{project['id']}/tasks")
    assert project_tasks.status_code == 200
    assert len(project_tasks.json()) == 1

    update_project = client.put(
        f"/projects/{project['id']}", json={"title": "Updated", "completed": True}
    )
    assert update_project.status_code == 200
    assert update_project.json()["completed"] is True

    delete_task = client.delete(f"/tasks/{task['id']}")
    assert delete_task.status_code == 204

    delete_project = client.delete(f"/projects/{project['id']}")
    assert delete_project.status_code == 204


def test_deadline_validation_and_event_adjustment(client):
    project_deadline = datetime.now(UTC) + timedelta(days=5)
    project = client.post(
        "/projects", json={"title": "P1", "deadline": iso(project_deadline)}
    ).json()
    bad_task = client.post(
        "/tasks",
        json={
            "title": "Late",
            "deadline": iso(project_deadline + timedelta(days=1)),
            "project_id": project["id"],
        },
    )
    assert bad_task.status_code == 400

    task = client.post(
        "/tasks",
        json={
            "title": "T1",
            "deadline": iso(project_deadline - timedelta(hours=1)),
            "project_id": project["id"],
        },
    ).json()
    shortened = datetime.now(UTC) + timedelta(days=1)
    resp = client.put(f"/projects/{project['id']}", json={"deadline": iso(shortened)})
    assert resp.status_code == 200
    task_after = client.get(f"/tasks/{task['id']}").json()
    assert task_after["deadline"].replace("Z", "+00:00") == iso(shortened)


def test_link_and_unlink_task(client):
    project_deadline = datetime.now(UTC) + timedelta(days=3)
    project = client.post(
        "/projects", json={"title": "P1", "deadline": iso(project_deadline)}
    ).json()
    task = client.post(
        "/tasks",
        json={"title": "Free", "deadline": iso(datetime.now(UTC) + timedelta(days=1))},
    ).json()
    linked = client.post(f"/projects/{project['id']}/tasks/{task['id']}/link")
    assert linked.status_code == 200
    assert linked.json()["project_id"] == project["id"]
    unlinked = client.delete(f"/projects/{project['id']}/tasks/{task['id']}/unlink")
    assert unlinked.status_code == 200
    assert unlinked.json()["project_id"] is None


def test_reopening_task_reopens_project_and_docs_exist(client):
    project = client.post(
        "/projects",
        json={"title": "P1", "deadline": iso(datetime.now(UTC) + timedelta(days=3))},
    ).json()
    task = client.post(
        "/tasks",
        json={
            "title": "T1",
            "deadline": iso(datetime.now(UTC) + timedelta(hours=12)),
            "project_id": project["id"],
        },
    ).json()
    client.patch(f"/tasks/{task['id']}/complete")
    project_after_completion = client.get(f"/projects/{project['id']}").json()
    assert project_after_completion["completed"] is True
    reopened = client.put(f"/tasks/{task['id']}", json={"completed": False})
    assert reopened.status_code == 200
    project_after_reopen = client.get(f"/projects/{project['id']}").json()
    assert project_after_reopen["completed"] is False
    assert client.get("/docs").status_code == 200
