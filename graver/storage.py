import difflib
import json
from datetime import datetime
from pathlib import Path

from graver.exceptions import (
    PromptNotFoundError,
    StorageError,
    VersionNotFoundError,
)


class Storage:
    """File-system backend; stores each prompt version as a plain-text file."""

    def __init__(self, base_dir: str = ".graver") -> None:
        self._base = Path(base_dir).resolve()
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

    def set_main(self, name: str, version: str) -> None:
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

    def delete_version(self, name: str, version: str) -> None:
        version_path = self._version_file(name, version)
        if not version_path.exists():
            raise VersionNotFoundError(
                f"Version '{version}' not found for prompt '{name}'."
            )

        try:
            version_path.unlink()
        except OSError as exc:
            raise StorageError(f"Failed to delete '{version_path}': {exc}") from exc

        history_path = self._history_file(name)
        if history_path.exists():
            try:
                history = json.loads(history_path.read_text(encoding="utf-8"))
                history = [e for e in history if e["version"] != version]
                history_path.write_text(
                    json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8"
                )
            except OSError as exc:
                raise StorageError(
                    f"Failed to update history for '{name}': {exc}"
                ) from exc

        if self.get_main(name) == version:
            self._main_file(name).unlink(missing_ok=True)

    def delete_prompt(self, name: str) -> None:
        prompt_dir = self._prompt_dir(name)
        if not prompt_dir.exists():
            raise PromptNotFoundError(f"Prompt '{name}' not found.")
        try:
            for file in prompt_dir.iterdir():
                file.unlink()
            prompt_dir.rmdir()
        except OSError as exc:
            raise StorageError(f"Failed to delete prompt '{name}': {exc}") from exc

    def list_prompts(self) -> list[str]:
        return sorted(d.name for d in self._base.iterdir() if d.is_dir())

    def get_main(self, name: str) -> str | None:
        main_path = self._main_file(name)
        if not main_path.exists():
            return None
        data = json.loads(main_path.read_text(encoding="utf-8"))
        return data.get("version")
