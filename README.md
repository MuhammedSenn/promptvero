# Graver

[![CI](https://github.com/PracticalMind/graver/actions/workflows/ci.yml/badge.svg)](https://github.com/PracticalMind/graver/actions/workflows/ci.yml)
[![Python](https://img.shields.io/pypi/pyversions/graver)](https://pypi.org/project/graver/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Version control for LLM prompts. Zero dependencies, works offline, embeds in any project.

---

## Why graver?

### vs. cloud-based prompt management platforms

Most prompt management tools are cloud services: they require a signup, an API key, and your prompts leave your machine. They're built around dashboards, collaboration features, and A/B testing infrastructure, useful at scale, but heavy when you just want to track how a prompt evolves.

Graver is the opposite: install it, import it, start versioning. No server, no account, no data leaving your codebase. It's fast to set up, fast to use, and stays out of your way.

### vs. just using git

Git tracks files. Graver tracks **prompt content** - independently of your code.

- Save a new version from inside your code without creating a commit
- Pin one version as your stable "main" while others keep evolving
- Compare prompt changes in isolation, not buried in a diff full of source code
- Works inside notebooks, scripts, and pipelines without touching your repo

If your prompts live in `.txt` files committed alongside code, you'll feel the friction immediately: every prompt tweak becomes a commit, rollback means `git checkout`, and `git diff` mixes logic changes with wording changes.

### vs. building it yourself

Prompt versioning looks simple until you handle edge cases: version numbering after deletions, pinning a canonical version independently of the latest, history that survives partial deletions. Graver handles all of this. One `pip install`, zero boilerplate.

---

## Installation

```bash
pip install graver
```

## Quick Start

```python
from graver import Prompt

p = Prompt("system")

p.save("You are a helpful assistant.")
p.save("You are an expert analyst. Be concise and data-driven.")

# See what changed
print(p.changes())

# Pin a stable version
p.set_main("v1")

# Always retrieve the pinned version, regardless of newer saves
content = p.get_main()
```

---

## CLI

```bash
gr save system prompt.txt        # save a file as a new version
gr log system                    # show version history
gr show system v2                # show a specific version
gr changes system                # diff the last two versions
gr set-main system v1            # pin a version as main
gr get-main system               # print the pinned version
gr list                          # list all saved prompts
gr delete system v2              # delete a version
gr delete-prompt system          # delete a prompt entirely
```

Use `--base-dir` to point to a custom storage directory:

```bash
gr --base-dir ./prompts log system
```

---

## How It Works

Every `Prompt` writes to a `.graver/` folder in your working directory. No database, no server, no configuration.

```
.graver/
  system/
    v1.txt
    v2.txt
    history.json   ← version index with timestamps
    main.json      ← pointer to the pinned version
```

Versions are never overwritten, only explicitly deleted. Version numbers never collide even if you delete intermediate versions.

---

## API Reference

### `Prompt(name, base_dir=".graver")`

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Unique identifier for this prompt. |
| `base_dir` | `str` | Storage root. Defaults to `.graver` in the working directory. |

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `save(content)` | `str` | Save a new version. Returns the version string (e.g. `"v3"`). |
| `save_from_file(filepath)` | `str` | Read from a file and save as a new version. |
| `get(version=None)` | `str` | Get a version's content. Defaults to latest. |
| `log()` | `list[dict]` | Full version history with `version`, `timestamp`, `is_main`. |
| `set_main(version)` | `None` | Pin a version as the canonical main. |
| `get_main()` | `str` | Get the content of the pinned main version. |
| `changes(v1=None, v2=None)` | `str` | Formatted diff. Defaults to last two versions. |
| `diff(v1, v2)` | `dict` | Raw diff with `added`, `removed`, `unchanged` line lists. |
| `show(version=None)` | `str` | Content with formatted header. Defaults to latest. |
| `delete_version(version)` | `None` | Delete a specific version. Clears main pointer if it was main. |
| `delete_prompt()` | `None` | Delete this prompt and all its versions. |
| `Prompt.list_all(base_dir)` | `list[str]` | List all prompt names in the given directory. |

### Exceptions

| Exception | Raised when |
|-----------|-------------|
| `GraverError` | Base class for all graver errors. |
| `PromptNotFoundError` | Prompt name or file does not exist. |
| `VersionNotFoundError` | Version string does not exist. |
| `StorageError` | A file system operation fails. |

---

## Examples

See [`examples/`](examples/) for usage with OpenAI, Anthropic, and LangChain.

---

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions, code standards, and the PR process.

To report a bug or request a feature, open an [issue](https://github.com/PracticalMind/graver/issues).

---

## License

Released under the [MIT License](LICENSE).
