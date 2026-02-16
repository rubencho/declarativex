---
title: Local Development
description: Learn how to set up a local development environment, run tests, linters, and verify your changes before submitting a pull request.
---

# Local Development 💻

This guide explains how to set up a local development environment for DeclarativeX and run the full test and linting suite on your machine.

## Prerequisites

- **Python 3.10+** (the project supports 3.10–3.13)
- **[Poetry](https://python-poetry.org/docs/#installation)** for dependency management
- **Make** (optional, but recommended for running predefined commands)

## Setting Up the Environment

Clone the repository (or your fork) and install all dependencies, including optional extras:

```bash
git clone https://github.com/<your-username>/declarativex.git
cd declarativex
poetry install --all-extras
```

`--all-extras` installs the optional groups (`http2`, `graphql`, `brotli`) so every feature can be tested.

## Running the Full Check Suite

The `Makefile` provides a single command that runs **flake8**, **pylint**, **mypy**, and **pytest** in sequence:

```bash
make test
```

This is the same set of checks that CI runs on every pull request. If `make test` passes locally, your PR checks should pass too.

## Running Individual Checks

You can run each tool separately:

### Flake8 (style linting)

```bash
make flake8
# or directly:
poetry run flake8 src/declarativex
```

### Pylint (code analysis)

```bash
make pylint
# or directly:
poetry run pylint src/declarativex
```

### Mypy (type checking)

```bash
make mypy
# or directly:
poetry run mypy src/declarativex
```

### Pytest (unit tests)

```bash
make pytest
# or directly:
poetry run pytest -n 6 tests/
```

The `-n 6` flag runs tests in parallel across 6 workers using `pytest-xdist`.

## Running Specific Tests

To run a single test file:

```bash
poetry run pytest tests/test_sync_clients.py -v
```

To run a specific test function or class:

```bash
poetry run pytest tests/test_sync_clients.py::test_proxies -v
```

To run tests matching a keyword expression:

```bash
poetry run pytest -k "auth" -v
```

## Test Coverage

Generate a coverage report to make sure your changes maintain full coverage:

```bash
poetry run pytest --cov=src/declarativex tests/
```

For an HTML report you can open in your browser:

```bash
poetry run pytest --cov=src/declarativex --cov-report=html tests/
# open htmlcov/index.html
```

## Code Formatting

Format the codebase with **Black**:

```bash
make black
# or directly:
poetry run black .
```

The project enforces a line length of **79 characters** (configured in `pyproject.toml`).

## Project Layout

Understanding where things live helps when writing or debugging tests:

```
declarativex/
├── src/declarativex/   # Library source code
├── tests/              # Test suite
│   ├── fixtures/       # Shared test fixtures (schemas, clients)
│   ├── test_sync_clients.py
│   ├── test_async_clients.py
│   ├── test_authentication.py
│   ├── test_middlewares.py
│   └── ...
├── docs/               # MkDocs documentation
├── Makefile            # Development commands
├── pyproject.toml      # Project & tool configuration
└── mkdocs.yml          # Documentation site config
```

## Testing with Different Pydantic Versions

DeclarativeX supports both Pydantic v1 and v2. CI tests against both. To test locally with a specific version:

=== "Pydantic v1"

    ```bash
    poetry add "pydantic>=1,<2"
    poetry run pytest tests/ -v
    ```

=== "Pydantic v2"

    ```bash
    poetry add "pydantic>=2,<3"
    poetry run pytest tests/ -v
    ```

## Serving the Documentation Locally

To preview documentation changes:

```bash
poetry run mkdocs serve
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

## Troubleshooting

| Problem | Solution |
|---|---|
| `poetry: command not found` | Install Poetry: `pipx install poetry` |
| `make: command not found` | Run the underlying commands directly with `poetry run …` (see sections above) |
| Tests fail with import errors | Ensure you ran `poetry install --all-extras` |
| Mypy reports missing stubs | Run `poetry install` again to pick up `types-setuptools` |
