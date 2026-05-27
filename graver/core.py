from pathlib import Path

from graver.exceptions import PromptNotFoundError
from graver.storage import Storage


class Prompt:
    """Git-like version control for a single named prompt."""

    def __init__(self, name: str, base_dir: str = ".graver") -> None:
        self.name = name
        self._storage = Storage(base_dir=base_dir)

    @staticmethod
    def list_all(base_dir: str = ".graver") -> list[str]:
        """Return the names of all saved prompts in the given base directory."""
        return Storage(base_dir=base_dir).list_prompts()

    def save(self, content: str) -> str:
        """Save a new version and return its version string (e.g. "v1")."""
        return self._storage.save(self.name, content)

    def save_from_file(self, filepath: str) -> str:
        """Read content from a file and save it as a new version."""
        path = Path(filepath)
        if not path.exists():
            raise PromptNotFoundError(
                f"File not found: '{filepath}'. Check the path and try again."
            )
        content = path.read_text(encoding="utf-8")
        return self.save(content)

    def get(self, version: str | None = None) -> str:
        """Return the prompt text for the given version, or the latest if None."""
        return self._storage.get(self.name, version)

    def log(self) -> list[dict]:
        """Return the full version history, oldest to newest, with is_main flag."""
        main = self._storage.get_main(self.name)
        history = self._storage.history(self.name)
        for entry in history:
            entry["is_main"] = entry["version"] == main
        return history

    def set_main(self, version: str) -> None:
        """Pin a version as the canonical main."""
        self._storage.set_main(self.name, version)

    def get_main(self) -> str:
        """Return the content of the pinned main version."""
        version = self._storage.get_main(self.name)
        if version is None:
            raise PromptNotFoundError(
                f"No main version set for '{self.name}'. Use set_main() first."
            )
        return self._storage.get(self.name, version)

    def delete_prompt(self) -> None:
        """Delete this prompt and all its versions."""
        self._storage.delete_prompt(self.name)

    def delete_version(self, version: str) -> None:
        """Delete a specific version; clears the main pointer if it was main."""
        self._storage.delete_version(self.name, version)

    def diff(self, v1: str, v2: str) -> dict:
        """Return raw line-by-line diff between two versions."""
        return self._storage.diff(self.name, v1, v2)

    def changes(self, v1: str | None = None, v2: str | None = None) -> str:
        """Return a formatted change report; defaults to the last two versions."""
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

        if not added and not removed:
            return f"No changes between {v1} and {v2}."

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
        """Return a version's content with a formatted header."""
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
