class GraverError(Exception):
    """Base class for all graver errors."""


class PromptNotFoundError(GraverError):
    """Raised when a prompt name does not exist in storage."""


class VersionNotFoundError(GraverError):
    """Raised when a requested version string does not exist."""


class StorageError(GraverError):
    """Raised when a file system operation fails."""
