"""promptvero — Git-like version control for LLM prompts.

Save, diff, and roll back prompt versions with a simple Python API.
All data is stored as plain text files under a ``.promptvero/`` directory.

Example::

    import promptvero as prv

    p = prv.Prompt("system")
    p.save("You are a helpful assistant")
    print(p.get())
"""

from pathlib import Path

from promptvero.core import Prompt
from promptvero.exceptions import (
    PromptNotFoundError,
    PromptVeroError,
    StorageError,
    VersionNotFoundError,
)

__version__ = "0.1.0"
__author__ = "Muhammed Sen"

__all__ = [
    "Prompt",
    "list_all",
    "PromptVeroError",
    "PromptNotFoundError",
    "VersionNotFoundError",
    "StorageError",
]


def list_all(base_dir: str = ".promptvero") -> None:
    """Print all saved prompts and their version history.

    Args:
        base_dir: Root storage directory. Defaults to ".promptvero".
    """
    base = Path(base_dir)
    if not base.exists() or not any(base.iterdir()):
        print("No prompts saved yet.")
        return

    for directory in sorted(base.iterdir()):
        if not directory.is_dir():
            continue
        p = Prompt(directory.name, base_dir=base_dir)
        history = p.log()
        print(f"\n{'=' * 60}")
        print(f"  {directory.name}  ({len(history)} versions)")
        print(f"{'=' * 60}")
        for entry in history:
            preview = entry["content"][:70].replace("\n", " ")
            print(f"  {entry['version']}  |  {entry['timestamp']}")
            print(f"         {preview}...")
        print()
