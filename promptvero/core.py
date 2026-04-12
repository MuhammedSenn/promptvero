"""Public-facing API for promptvero."""

from pathlib import Path

from promptvero.exceptions import PromptNotFoundError
from promptvero.storage import Storage


class Prompt:
    """Git-like version control for a single named prompt.

    Args:
        name: Unique identifier for this prompt.
        base_dir: Root directory for all prompt storage. Defaults to ".promptvero".
    """

    def __init__(self, name: str, base_dir: str = ".promptvero") -> None:
        self.name = name
        self._storage = Storage(base_dir=base_dir)

    @staticmethod
    def list_all(base_dir: str = ".promptvero") -> list[str]:
        """Return the names of all saved prompts in the given base directory.

        Args:
            base_dir: Root directory for all prompt storage.

        Returns:
            A sorted list of prompt name strings.
        """
        return Storage(base_dir=base_dir).list_prompts()

    def save(self, content: str) -> str:
        """Save a new version of this prompt.

        Args:
            content: The prompt text to persist.

        Returns:
            The version string for the saved version (e.g. "v1").
        """
        return self._storage.save(self.name, content)

    def save_from_file(self, filepath: str) -> str:
        """Read prompt content from a file and save it as a new version.

        Args:
            filepath: Path to the file whose contents will be saved.

        Returns:
            The version string for the saved version (e.g. "v1").

        Raises:
            PromptNotFoundError: If the specified file does not exist.
        """
        path = Path(filepath)
        if not path.exists():
            raise PromptNotFoundError(
                f"File not found: '{filepath}'. Check the path and try again."
            )
        content = path.read_text(encoding="utf-8")
        return self.save(content)

    def get(self, version: str | None = None) -> str:
        """Retrieve a version of this prompt.

        Args:
            version: Version string to retrieve (e.g. "v2"). If None,
                returns the latest saved version.

        Returns:
            The prompt text for the requested version.
        """
        return self._storage.get(self.name, version)

    def log(self) -> list[dict]:
        """Return the full version history of this prompt.

        Returns:
            A list of dicts ordered from oldest to newest. Each dict
            contains "version" (str), "timestamp" (str), and "is_main" (bool).
        """
        main = self._storage.get_main(self.name)
        history = self._storage.history(self.name)
        for entry in history:
            entry["is_main"] = entry["version"] == main
        return history

    def set_main(self, version: str) -> None:
        """Mark a specific version as the main (canonical) version.

        Args:
            version: Version string to mark as main (e.g. "v2").

        Raises:
            VersionNotFoundError: If the version does not exist.
        """
        self._storage.set_main(self.name, version)

    def get_main(self) -> str:
        """Return the content of the main version.

        Returns:
            The prompt text of the main version.

        Raises:
            PromptNotFoundError: If no main version has been set.
        """
        version = self._storage.get_main(self.name)
        if version is None:
            raise PromptNotFoundError(
                f"No main version set for '{self.name}'. Use set_main() first."
            )
        return self._storage.get(self.name, version)

    def diff(self, v1: str, v2: str) -> dict:
        """Compute a line-by-line diff between two versions.

        Args:
            v1: The base version string (e.g. "v1").
            v2: The target version string (e.g. "v2").

        Returns:
            A dict with keys "added", "removed", and "unchanged", each
            containing a list of strings representing the changed lines.
        """
        return self._storage.diff(self.name, v1, v2)

    def checkout(self, version: str) -> str:
        """Return the content of a specific historical version.

        Args:
            version: Version string to retrieve (e.g. "v1").

        Returns:
            The prompt text for the requested version.
        """
        return self._storage.checkout(self.name, version)

    def changes(self, v1: str | None = None, v2: str | None = None) -> str:
        """Return a formatted change report between two versions.

        If no versions are specified, compares the last two saved versions.

        Args:
            v1: Base version (e.g. "v1"). If None, uses second-to-last.
            v2: Target version (e.g. "v2"). If None, uses latest.

        Returns:
            A formatted string showing added and removed lines.
        """
        history = self._storage.history(self.name)
        if len(history) < 2:
            return "Need at least 2 versions to compare."

        if v1 is None and v2 is None:
            v1 = history[-2]["version"]
            v2 = history[-1]["version"]
        elif v2 is None:
            v2 = history[-1]["version"]

        result = self._storage.diff(self.name, v1, v2)

        added = [line for line in result["added"] if line.strip()]
        removed = [line for line in result["removed"] if line.strip()]

        lines = [
            f"\n{self.name}  |  {v1} -> {v2}",
            "=" * 55,
            f"\n+ ADDED ({len(added)} lines)",
            *[f"    + {line}" for line in added],
            f"\n- REMOVED ({len(removed)} lines)",
            *[f"    - {line}" for line in removed],
        ]
        return "\n".join(lines)

    def show(self, version: str | None = None) -> str:
        """Return a version's full content with a formatted header.

        Args:
            version: Version to display (e.g. "v2"). If None, shows latest.

        Returns:
            A formatted string with header and prompt content.
        """
        history = self._storage.history(self.name)
        content = self._storage.get(self.name, version)

        resolved = version or (history[-1]["version"] if history else "v?")
        entry = next((e for e in history if e["version"] == resolved), {})
        timestamp = entry.get("timestamp", "")
        main_version = self._storage.get_main(self.name)
        main_tag = "  [main]" if resolved == main_version else ""

        lines = [
            f"\n{'=' * 60}",
            f"  {self.name}  |  {resolved}{main_tag}  |  {timestamp}",
            "=" * 60,
            content,
            "=" * 60,
        ]
        return "\n".join(lines)
