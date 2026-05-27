# Contributing to graver

## Setup

```bash
git clone https://github.com/PracticalMind/graver
cd graver
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Before submitting

```bash
ruff check .       # linting
pytest -q          # tests
```

Both must pass cleanly.

## Code standards

- Type hints on all functions
- No commented-out code
- Docstrings only when the why is non-obvious — method names should be self-explanatory

## Pull requests

- Branch from `main`, name it `type/short-description` (e.g. `feat/export-json`, `fix/version-collision`)
- One logical change per PR
- For significant changes, open an issue first to align on approach

## Reporting issues

Use [GitHub Issues](https://github.com/PracticalMind/graver/issues). Include a minimal reproducible example where possible.
