"""graver — Git-like version control for LLM prompts.

Save, diff, and roll back prompt versions with a simple Python API.
All data is stored as plain text files under a ``.graver/`` directory.

Example::

    from graver import Prompt

    p = Prompt("system")
    p.save("You are a helpful assistant")
    print(p.get())
"""

from graver.core import Prompt
from graver.exceptions import (
    GraverError,
    PromptNotFoundError,
    StorageError,
    VersionNotFoundError,
)

__version__ = "0.3.0"
__author__ = "Practical Mind"

__all__ = [
    "Prompt",
    "GraverError",
    "PromptNotFoundError",
    "VersionNotFoundError",
    "StorageError",
]
