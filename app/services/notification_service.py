from __future__ import annotations

from typing import Protocol


class NotificationService(Protocol):
    def info(self, message: str) -> None: ...
    def warning(self, message: str) -> None: ...
