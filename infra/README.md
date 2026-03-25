# Infrastructure layer

Adapters and infrastructure for the application live here.

Contents
- `repos/`: database adapters (SQLite implementations) and repository wiring
- `rest/`: FastAPI inbound adapter, routes, and dependency wiring
- `services/`: infrastructure services such as event bus and notifications

Guidelines
- Implement adapters that satisfy port interfaces declared in `app/`.
- Keep transport, persistence, and I/O logic here; do not place business rules in this layer.

Author: Mohsen Bahaloo <mbahaloo1398@gmail.com>