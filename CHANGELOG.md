# Changelog

## [0.2.0] - 2026-04-14

### Added
- `set_main(version)` to pin a specific version as the canonical prompt
- `get_main()` to retrieve the content of the pinned main version
- `delete_version(version)` to permanently remove a version; clears the main pointer if the deleted version was main
- `delete_prompt()` to permanently remove a prompt and all its versions
- `list_all()` static method to return all saved prompt names as a list
- `log()` entries now include an `is_main` boolean flag
- `show()` displays a `[main]` tag when viewing the pinned version
- `pv` CLI with commands: `list`, `save`, `log`, `show`, `changes`, `set-main`, `get-main`, `delete`, `delete-prompt`
- CLI test suite covering all commands

### Changed
- `changes()` now returns a formatted string instead of printing to stdout
- `show()` now returns a formatted string instead of printing to stdout
- `history.json` no longer stores prompt content — only `version` and `timestamp` metadata
- `base_dir` is now resolved to an absolute path, preventing unexpected storage locations when the working directory differs
- `_next_version` now uses `max()` instead of `len()` to prevent version number collisions if version files are deleted

### Removed
- `checkout()` — redundant alias for `get()`; use `get(version)` directly

### Fixed
- Version numbering collision: deleting a version file no longer causes the next save to reuse an existing version number

## [0.1.0] - 2026-04-05

### Added
- `Prompt` class with `save`, `save_from_file`, `get`, `log`, `diff`, `checkout`, `changes`, `show` methods
- `list_all()` module-level function to display all saved prompts
- `Storage` class for file-based version management using `.txt` files and `history.json`
- Custom exceptions: `PromptVeroError`, `PromptNotFoundError`, `VersionNotFoundError`, `StorageError`
