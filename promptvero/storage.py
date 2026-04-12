"""File-system storage backend for promptvero."""

import difflib
import json
from datetime import datetime
from pathlib import Path

from promptvero.exceptions import (
    PromptNotFoundError,
    StorageError,
    VersionNotFoundError,
)


class Storage:
    """Handles all file system operations for promptvero.

    Args:
        base_dir: Root directory for all prompt storage.
    """

    def __init__(self, base_dir: str = ".promptvero") -> None:
        self._base = Path(base_dir)
        self._base.mkdir(parents=True, exist_ok=True)

    def _prompt_dir(self, name: str) -> Path:
        return self._base / name

    def _version_file(self, name: str, version: str) -> Path:
        return self._prompt_dir(name) / f"{version}.txt"

    def _history_file(self, name: str) -> Path:
        return self._prompt_dir(name) / "history.json"

    def _main_file(self, name: str) -> Path:
        return self._prompt_dir(name) / "main.json"

    def _next_version(self, prompt_dir: Path) -> int:
        files = list(prompt_dir.glob("v*.txt"))
        if not files:
            return 1
        return max(int(f.stem[1:]) for f in files) + 1

    def _latest_version_num(self, prompt_dir: Path) -> int:
        files = list(prompt_dir.glob("v*.txt"))
        if not files:
            raise PromptNotFoundError(
                f"No versions found in '{prompt_dir}'. Save a prompt first."
            )
        return max(int(f.stem[1:]) for f in files)

    def save(self, name: str, content: str) -> str:
        """Save a new version of a prompt.

        Args:
            name: Prompt identifier.
            content: The prompt text to persist.

        Returns:
            The version string for the saved version (e.g. "v1").

        Raises:
            StorageError: If any file write operation fails.
        """
        prompt_dir = self._prompt_dir(name)
        prompt_dir.mkdir(parents=True, exist_ok=True)

        version = f"v{self._next_version(prompt_dir)}"
        version_path = prompt_dir / f"{version}.txt"

        try:
            version_path.write_text(content, encoding="utf-8")
        except OSError as exc:
            raise StorageError(f"Failed to write '{version_path}': {exc}") from exc

        history_path = self._history_file(name)
        try:
            history: list[dict] = (
                json.loads(history_path.read_text(encoding="utf-8"))
                if history_path.exists()
                else []
            )
            history.append(
                {
                    "version": version,
                    "timestamp": datetime.now().isoformat(timespec="seconds"),
                }
            )
            history_path.write_text(
                json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except OSError as exc:
            raise StorageError(f"Failed to write history for '{name}': {exc}") from exc

        return version

    def get(self, name: str, version: str | None = None) -> str:
        """Retrieve the content of a prompt version.

        Args:
            name: Prompt identifier.
            version: Version string to retrieve. If None, returns the latest.

        Returns:
            The prompt text for the requested version.

        Raises:
            PromptNotFoundError: If the prompt directory does not exist.
            VersionNotFoundError: If the requested version file does not exist.
        """
        prompt_dir = self._prompt_dir(name)
        if not prompt_dir.exists():
            raise PromptNotFoundError(
                f"Prompt '{name}' not found. Save a version first."
            )

        if version is None:
            target = prompt_dir / f"v{self._latest_version_num(prompt_dir)}.txt"
        else:
            target = self._version_file(name, version)
            if not target.exists():
                raise VersionNotFoundError(
                    f"Version '{version}' not found for prompt '{name}'."
                )

        return target.read_text(encoding="utf-8")

    def history(self, name: str) -> list[dict]:
        """Return the version history for a prompt.

        Args:
            name: Prompt identifier.

        Returns:
            A list of dicts with keys "version", "timestamp", and "content".

        Raises:
            PromptNotFoundError: If the prompt directory does not exist.
        """
        prompt_dir = self._prompt_dir(name)
        if not prompt_dir.exists():
            raise PromptNotFoundError(
                f"Prompt '{name}' not found. Save a version first."
            )

        history_path = self._history_file(name)
        if not history_path.exists():
            return []

        return json.loads(history_path.read_text(encoding="utf-8"))

    def diff(self, name: str, v1: str, v2: str) -> dict:
        """Compute a line-by-line diff between two versions.

        Args:
            name: Prompt identifier.
            v1: The base version string (e.g. "v1").
            v2: The target version string (e.g. "v2").

        Returns:
            A dict with keys "added", "removed", and "unchanged".

        Raises:
            VersionNotFoundError: If either version does not exist.
        """
        lines1 = self.get(name, v1).splitlines(keepends=True)
        lines2 = self.get(name, v2).splitlines(keepends=True)

        added, removed, unchanged = [], [], []

        for line in difflib.ndiff(lines1, lines2):
            if line.startswith("+ "):
                added.append(line[2:].rstrip("\n"))
            elif line.startswith("- "):
                removed.append(line[2:].rstrip("\n"))
            elif line.startswith("  "):
                unchanged.append(line[2:].rstrip("\n"))

        return {"added": added, "removed": removed, "unchanged": unchanged}

    def checkout(self, name: str, version: str) -> str:
        """Return the content of a specific prompt version.

        Args:
            name: Prompt identifier.
            version: Version string to check out (e.g. "v1").

        Returns:
            The prompt text for the requested version.

        Raises:
            VersionNotFoundError: If the version does not exist.
        """
        return self.get(name, version)

    def set_main(self, name: str, version: str) -> None:
        """Mark a specific version as the main (canonical) version.

        Args:
            name: Prompt identifier.
            version: Version string to mark as main (e.g. "v2").

        Raises:
            VersionNotFoundError: If the version does not exist.
            StorageError: If the file write fails.
        """
        if not self._version_file(name, version).exists():
            raise VersionNotFoundError(
                f"Version '{version}' not found for prompt '{name}'."
            )
        main_path = self._main_file(name)
        try:
            main_path.write_text(
                json.dumps({"version": version}, ensure_ascii=False), encoding="utf-8"
            )
        except OSError as exc:
            raise StorageError(f"Failed to write main for '{name}': {exc}") from exc

    def list_prompts(self) -> list[str]:
        """Return the names of all saved prompts.

        Returns:
            A sorted list of prompt name strings.
        """
        return sorted(d.name for d in self._base.iterdir() if d.is_dir())

    def get_main(self, name: str) -> str | None:
        """Return the version string marked as main, or None if not set.

        Args:
            name: Prompt identifier.

        Returns:
            The main version string (e.g. "v2"), or None if not set.
        """
        main_path = self._main_file(name)
        if not main_path.exists():
            return None
        data = json.loads(main_path.read_text(encoding="utf-8"))
        return data.get("version")
