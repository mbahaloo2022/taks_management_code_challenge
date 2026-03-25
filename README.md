# Tasks challenge submission

This version is refactored toward a stricter hexagonal architecture.

## Architecture

- `app/domain`: framework-free domain entities, errors, and domain events
- `app/usecases`: application services orchestrating ports
- `app/repos` and `app/services`: outbound ports (protocols)
- `infra/repos`: SQLite adapters
- `infra/rest`: FastAPI inbound adapter
- `infra/services`: in-memory adapter implementations
- `frontend`: simple Next.js frontend

## Improvements from prior version

- domain entities are plain frozen dataclasses instead of Pydantic models
- richer domain behavior moved into entities (`mark_completed`, `reopen`, `assign_to_project`, etc.)
- use cases orchestrate ports instead of carrying low-level mutation logic
- event handlers are explicitly typed and focused on side effects
- backend and frontend tests included

## Run locally

### Backend
```bash
uv sync
uv run pytest
# Tasks challenge submission

**Author:** Mohsen Bahaloo <mbahaloo1398@gmail.com>

This repository implements a task management service following a strict hexagonal architecture.

Key components
- `app/`: domain, use-cases, and application ports
- `infra/`: adapters (SQLite repos, REST API)
- `frontend/`: Next.js UI that proxies to backend API routes

Run the backend locally

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt  # or install from pyproject.toml
.venv/bin/python main.py
```

Run tests

```bash
.venv/bin/python -m pip install pytest
.venv/bin/python -m pytest -q
```

Docker

```bash
docker compose up --build
```

Notes
- The frontend proxies browser `/api/*` calls to the backend. In Docker the backend host is `backend:8000`; in local frontend development use `http://localhost:8000`.
