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
            contains "version" (str), "timestamp" (str), and "content" (str).
        """
        return self._storage.history(self.name)

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

    def changes(self, v1: str | None = None, v2: str | None = None) -> None:
        """Print a formatted change report between two versions.

        If no versions are specified, compares the last two saved versions.

        Args:
            v1: Base version (e.g. "v1"). If None, uses second-to-last.
            v2: Target version (e.g. "v2"). If None, uses latest.
        """
        history = self._storage.history(self.name)
        if len(history) < 2:
            print("Need at least 2 versions to compare.")
            return

        if v1 is None and v2 is None:
            v1 = history[-2]["version"]
            v2 = history[-1]["version"]
        elif v2 is None:
            v2 = history[-1]["version"]

        result = self._storage.diff(self.name, v1, v2)

        added = [line for line in result["added"] if line.strip()]
        removed = [line for line in result["removed"] if line.strip()]
        unchanged = [line for line in result["unchanged"] if line.strip()]

        print(f"\n{self.name}  |  {v1} -> {v2}")
        print("=" * 55)
        print(f"\n+ ADDED ({len(added)} lines)")
        for line in added:
            print(f"    + {line}")
        print(f"\n- REMOVED ({len(removed)} lines)")
        for line in removed:
            print(f"    - {line}")
        print(f"\n= UNCHANGED ({len(unchanged)} lines)\n")

    def show(self, version: str | None = None) -> None:
        """Print a version's full content to stdout with a header.

        Args:
            version: Version to display (e.g. "v2"). If None, shows latest.
        """
        history = self._storage.history(self.name)
        content = self._storage.get(self.name, version)

        resolved = version or (history[-1]["version"] if history else "v?")
        entry = next((e for e in history if e["version"] == resolved), {})
        timestamp = entry.get("timestamp", "")

        print(f"\n{'=' * 60}")
        print(f"  {self.name}  |  {resolved}  |  {timestamp}")
        print(f"{'=' * 60}")
        print(content)
        print(f"{'=' * 60}\n")
