from uuid import UUID


class DomainError(Exception):
    """Base class for domain and use-case errors (no HTTP mapping)."""


class ResourceNotFound(DomainError):
    """Resource not found error."""

    def __init__(self, resource: str, resource_id: UUID) -> None:
        self.resource = resource
        self.resource_id = resource_id
        super().__init__(f"{resource} not found: {resource_id}")
