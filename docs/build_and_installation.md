# Build and Installation Policy

## Source of Truth

`pyproject.toml` is the canonical source for package metadata, supported Python
versions, runtime dependencies, optional developer dependencies, and console
entry points.

Do not add runtime dependencies only to ad-hoc shell commands or local virtual
environments. Add them to `pyproject.toml` first.

## Supported Python Versions

| Python | Support status | Release gate |
| --- | --- | --- |
| 3.10 | supported | `tox -e py310` |
| 3.11 | supported | `tox -e py311` |
| 3.12 | supported | `tox -e py312` |

The package metadata intentionally restricts installation to `>=3.10,<3.13`.
Expand the upper bound only after the release matrix has passed on newer Python
versions.

## Standard Installation

From the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install --constraint requirements-lock.txt -e ".[dev]"
```

This installs the local package in editable mode and exposes:

```bash
.venv/bin/hitop-codegen --help
.venv/bin/hitop-suffix --help
```

## Lock and Constraints Policy

`requirements-lock.txt` is a pinned constraints snapshot for release
verification. It is not the source of truth for package requirements; it records
the dependency versions used for the current tested release environment.

Use the lock file for release checks:

```bash
.venv/bin/python -m pip install --constraint requirements-lock.txt -e ".[dev]"
```

Refresh the lock file only as an intentional release maintenance task:

```bash
.venv/bin/python -m pip install --upgrade -e ".[dev]"
.venv/bin/python -m pip freeze --exclude-editable > requirements-lock.txt
```

After refreshing, run the full validation suite and review the dependency diff.

## Release Verification

Run the local quality gate:

```bash
scripts/validate_hitop_suffix_tooling.sh
```

Build the release distributions:

```bash
.venv/bin/python -m build
```

Run the supported Python matrix on a runner that has Python 3.10, 3.11, and
3.12 installed:

```bash
.venv/bin/tox -e py310,py311,py312
```

The release is not ready if any matrix environment is missing or failing.
