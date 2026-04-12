"""Custom exceptions for the promptvero library."""


class PromptVeroError(Exception):
    """Base class for all promptvero errors."""


class PromptNotFoundError(PromptVeroError):
    """Raised when a prompt name does not exist in storage."""


class VersionNotFoundError(PromptVeroError):
    """Raised when a requested version string does not exist."""


class StorageError(PromptVeroError):
    """Raised when a file system operation fails."""
