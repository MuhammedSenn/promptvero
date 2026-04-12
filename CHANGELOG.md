# Changelog

## [0.1.0] - 2026-04-05

### Added
- `Prompt` class with `save`, `save_from_file`, `get`, `log`, `diff`, `checkout`, `changes`, `show` methods
- `list_all()` module-level function to display all saved prompts
- `Storage` class for file-based version management using `.txt` files and `history.json`
- Custom exceptions: `PromptVeroError`, `PromptNotFoundError`, `VersionNotFoundError`, `StorageError`
