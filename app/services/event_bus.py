from __future__ import annotations

from typing import Protocol

from app.domain.events import DomainEvent


class EventBus(Protocol):
    def publish(self, event: DomainEvent) -> None: ...
