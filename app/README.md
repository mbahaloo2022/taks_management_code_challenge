# Application layer

This folder contains the application's core business logic and interfaces.

Contents
- `domain/`: domain entities, value objects, domain events, and domain errors
- `usecases/`: application services (use-cases) that orchestrate domain operations
- `services/` and `repos/`: outbound port protocols used by adapters in `infra/`

Guidelines
- Keep business rules and domain invariants inside domain entities and use-cases.
- Avoid importing infrastructure modules (database, HTTP frameworks) into this layer.

Author: Mohsen Bahaloo <mbahaloo1398@gmail.com>