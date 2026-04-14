"""promptvero — Git-like version control for LLM prompts.

Save, diff, and roll back prompt versions with a simple Python API.
All data is stored as plain text files under a ``.promptvero/`` directory.

Example::

    from promptvero import Prompt

    p = Prompt("system")
    p.save("You are a helpful assistant")
    print(p.get())
"""

from promptvero.core import Prompt
from promptvero.exceptions import (
    PromptNotFoundError,
    PromptVeroError,
    StorageError,
    VersionNotFoundError,
)

__version__ = "0.2.0"
__author__ = "Muhammed Sen"

__all__ = [
    "Prompt",
    "PromptVeroError",
    "PromptNotFoundError",
    "VersionNotFoundError",
    "StorageError",
]
