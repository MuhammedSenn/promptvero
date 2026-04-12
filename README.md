# promptvero

Git-like version control for your LLM prompts.

Save prompt versions, view history, compare diffs, and roll back — all from Python, with zero external dependencies.

## Why promptvero?

LLM prompts change constantly. Tracking what changed, when, and which version performed better quickly becomes a mess.

promptvero solves this:
- Every change is automatically versioned — v1, v2, v3...
- Roll back to any version instantly
- See exactly what changed between two versions
- Test different prompt versions inside your application
- Zero dependencies, zero configuration

## Installation

```bash
pip install promptvero
```

## Quick Start

```python
import promptvero as prv

p = prv.Prompt("system")
v1 = p.save("You are a helpful assistant")
v2 = p.save("You are an expert analyst. Be concise and data-driven.")

for entry in p.log():
    print(entry["version"], entry["timestamp"])

content = p.checkout("v1")
p.changes()
prv.list_all()
```

## API Reference

### `Prompt(name, base_dir=".promptvero")`

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Unique identifier for this prompt. |
| `base_dir` | `str` | Root directory for storage. Defaults to `.promptvero`. |

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
| `filepath` | `str` | Path to a `.md` or `.txt` file. |

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

**Returns:** List of dicts with keys `version`, `timestamp`, `content`.

---

### `diff(v1, v2) -> dict`

Returns the raw difference between two versions as a dict. Use this when you want to process the result programmatically.

| Parameter | Type | Description |
|-----------|------|-------------|
| `v1` | `str` | Base version (e.g. `"v1"`). |
| `v2` | `str` | Target version (e.g. `"v2"`). |

**Returns:** Dict with keys `added`, `removed`, `unchanged` — each a list of strings.

---

### `checkout(version) -> str`

Retrieves a specific historical version. Semantically equivalent to `get(version)` but communicates intent — use this when rolling back to an older version rather than simply reading content.

| Parameter | Type | Description |
|-----------|------|-------------|
| `version` | `str` | Version to roll back to (e.g. `"v1"`). |

**Returns:** Prompt text.

---

### `changes(v1=None, v2=None) -> None`

Prints a human-readable change report between two versions. Internally uses `diff()` and formats the result. Use this when you want to quickly inspect what changed without processing the data yourself. If no arguments are given, compares the last two versions.

| Parameter | Type | Description |
|-----------|------|-------------|
| `v1` | `str \| None` | Base version. If `None`, uses second-to-last. |
| `v2` | `str \| None` | Target version. If `None`, uses latest. |

---

### `show(version=None) -> None`

Prints the full content of a version with a header.

| Parameter | Type | Description |
|-----------|------|-------------|
| `version` | `str \| None` | Version to display. If `None`, shows latest. |

---

### `prv.list_all(base_dir=".promptvero") -> None`

Prints all saved prompts and their version history.

---

## How It Works

Every `Prompt` writes to a `.promptvero/` folder in your working directory.

```
.promptvero/
  system/
    v1.txt
    v2.txt
    history.json
```

**history.json format:**

```json
[
  {
    "version": "v1",
    "timestamp": "2024-01-01T10:00:00",
    "content": "You are a helpful assistant"
  },
  {
    "version": "v2",
    "timestamp": "2024-01-01T11:00:00",
    "content": "You are an expert analyst"
  }
]
```

Version numbering is automatic: each `save()` call increments the counter. Versions are never deleted or overwritten.

## License

MIT
