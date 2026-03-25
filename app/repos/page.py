from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Page(Generic[T]):
    """A slice of a larger result set."""

    items: list[T]
    total: int
    limit: int | None = None
    offset: int = 0
