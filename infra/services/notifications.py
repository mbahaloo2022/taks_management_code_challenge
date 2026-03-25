from __future__ import annotations

import logging
from dataclasses import dataclass, field


@dataclass(slots=True)
class InMemoryNotificationService:
    logger: logging.Logger = field(
        default_factory=lambda: logging.getLogger("tasks.notifications")
    )
    messages: list[tuple[str, str]] = field(default_factory=list)

    def info(self, message: str) -> None:
        self.messages.append(("info", message))
        self.logger.info(message)

    def warning(self, message: str) -> None:
        self.messages.append(("warning", message))
        self.logger.warning(message)
