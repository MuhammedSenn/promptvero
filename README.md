# Graver

Git-like version control for your LLM prompts.

Save prompt versions, view history, compare diffs, and roll back — all from Python, with zero external dependencies.

## Why graver?

LLM prompts change constantly. Tracking what changed, when, and which version performed better quickly becomes a mess.

graver solves this:
- Every change is automatically versioned — v1, v2, v3...
- Roll back to any version instantly
- Pin a specific version as your main (canonical) prompt
- See exactly what changed between two versions
- Zero dependencies, zero configuration

## Installation

```bash
pip install graver
```

## Quick Start

```python
from graver import Prompt

p = Prompt("system")
p.save("You are a helpful assistant")
p.save("You are an expert analyst. Be concise and data-driven.")

for entry in p.log():
    print(entry["version"], entry["timestamp"], entry["is_main"])

# Pin the first version as your stable main prompt
p.set_main("v1")

# Always get the pinned version, regardless of how many new versions exist
content = p.get_main()

# See what changed between two versions
print(p.changes("v1", "v2"))
```

## CLI

The `gr` command lets you use graver directly from the terminal — no Python script needed. Useful for quickly saving files, inspecting version history, or integrating into shell scripts and CI/CD pipelines.

```bash
gr list                          # list all saved prompts
gr save <name> <file>            # save a file as a new version
gr log <name>                    # show version history
gr show <name> [version]         # show prompt content
gr changes <name> [v1] [v2]      # show what changed between versions
gr set-main <name> <version>     # mark a version as main
gr get-main <name>               # print the main version content
gr delete <name> <version>       # delete a specific version
gr delete-prompt <name>          # delete a prompt and all its versions
```

Use `--base-dir` to specify a custom storage directory:

```bash
gr --base-dir ./prompts log my-prompt
```

## API Reference

### `Prompt(name, base_dir=".graver")`

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Unique identifier for this prompt. |
| `base_dir` | `str` | Root directory for storage. Defaults to `.graver`. |

---

### `save(content) -> str`

| Parameter | Type | Description |
|-----------|------|-------------|
| `content` | `str` | The prompt text to persist. |

**Returns:** Version string (e.g. `"v1"`).

---

### `save_from_file(filepath) -> str`

| Parameter | Type | Description |
|-----------|------|-------------|
| `filepath` | `str` | Path to the file to read. Any plain text file is accepted. |

**Returns:** Version string.  
**Raises:** `PromptNotFoundError` if the file does not exist.

---

### `get(version=None) -> str`

| Parameter | Type | Description |
|-----------|------|-------------|
| `version` | `str \| None` | Version to retrieve (e.g. `"v2"`). If `None`, returns the latest. |

**Returns:** Prompt text.

---

### `log() -> list[dict]`

Returns the full version history of this prompt, ordered from oldest to newest.

**Returns:** List of dicts with keys `version` (str), `timestamp` (str), and `is_main` (bool).

---

### `set_main(version) -> None`

Marks a specific version as the main (canonical) version. The main version does not change automatically when new versions are saved — only when `set_main()` is called again.

| Parameter | Type | Description |
|-----------|------|-------------|
| `version` | `str` | Version to mark as main (e.g. `"v2"`). |

**Raises:** `VersionNotFoundError` if the version does not exist.

---

### `get_main() -> str`

Returns the full content of the version marked as main. Use this to always retrieve your stable, pinned prompt regardless of how many new versions have been saved since.

**Returns:** Prompt text of the main version.  
**Raises:** `PromptNotFoundError` if no main version has been set.

---

### `delete_prompt() -> None`

Permanently deletes this prompt and all its versions. Removes all version files, history, and the main pointer.

**Raises:** `PromptNotFoundError` if the prompt does not exist.

---

### `delete_version(version) -> None`

Permanently deletes a specific version. Removes the version file and its history entry. If the deleted version was marked as main, the main pointer is also cleared.

| Parameter | Type | Description |
|-----------|------|-------------|
| `version` | `str` | Version string to delete (e.g. `"v2"`). |

**Raises:** `VersionNotFoundError` if the version does not exist.

---

### `diff(v1, v2) -> dict`

Returns the raw line-by-line difference between two versions as a dict. Use this when you want to process the result programmatically. For a human-readable report, use `changes()` instead.

| Parameter | Type | Description |
|-----------|------|-------------|
| `v1` | `str` | Base version (e.g. `"v1"`). |
| `v2` | `str` | Target version (e.g. `"v2"`). |

**Returns:** Dict with keys `added`, `removed`, `unchanged` — each a list of strings.

---

### `changes(v1=None, v2=None) -> str`

Returns a human-readable change report between two versions, showing which lines were added and which were removed. If no arguments are given, compares the last two saved versions. For raw diff data, use `diff()` instead.

| Parameter | Type | Description |
|-----------|------|-------------|
| `v1` | `str \| None` | Base version. If `None`, uses second-to-last. |
| `v2` | `str \| None` | Target version. If `None`, uses latest. |

**Returns:** Formatted string showing added and removed lines.

---

### `show(version=None) -> str`

Returns the full content of a version with a formatted header. Displays a `[main]` tag if the version is the pinned main.

| Parameter | Type | Description |
|-----------|------|-------------|
| `version` | `str \| None` | Version to display. If `None`, shows latest. |

**Returns:** Formatted string with header and prompt content.

---

### `Prompt.list_all(base_dir=".graver") -> list[str]`

Returns the names of all saved prompts in the given base directory.

**Returns:** Sorted list of prompt name strings.

---

## How It Works

Every `Prompt` writes to a `.graver/` folder in your working directory.

```
.graver/
  system/
    v1.txt
    v2.txt
    history.json
    main.json
```

**history.json format:**

```json
[
  {
    "version": "v1",
    "timestamp": "2024-01-01T10:00:00"
  },
  {
    "version": "v2",
    "timestamp": "2024-01-01T11:00:00"
  }
]
```

**main.json format:**

```json
{
  "version": "v1"
}
```

Version numbering is automatic: each `save()` call increments the counter. Versions are never overwritten — only explicitly deleted via `delete_version()`.

## License

MIT
