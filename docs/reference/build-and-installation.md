# Build & installation

<div class="hitop-page-intro">
  <p>One command sets up a working local environment; the rest of this page covers what that command does, the dependency lock policy around it, and the checks a release must pass.</p>
  <span class="hitop-source">Source · <a href="https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/pyproject.toml">pyproject.toml</a> · <a href="https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/scripts/bootstrap_hitop_suffix_tools.sh">scripts/bootstrap_hitop_suffix_tools.sh</a> · <a href="https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/requirements-lock.txt">requirements-lock.txt</a></span>
</div>

## Source of truth

`pyproject.toml` is the canonical source for package metadata, supported Python
versions, runtime dependencies, optional developer dependencies, and console
entry points.

Do not add runtime dependencies only to ad-hoc shell commands or local virtual
environments. Add them to `pyproject.toml` first.

## Supported Python versions

| Python | Support status | Release gate |
| --- | --- | --- |
| 3.10 | supported | `tox -e py310` |
| 3.11 | supported | `tox -e py311` |
| 3.12 | supported | `tox -e py312` |

The package metadata intentionally restricts installation to `>=3.10,<3.13`.
Expand the upper bound only after the release matrix has passed on newer Python
versions.

## Quick start

From the repository root, `scripts/bootstrap_hitop_suffix_tools.sh` creates
`.venv`, installs the pinned dependency set from `requirements-lock.txt`, and
installs the package itself in editable mode with the `dev` extra:

**Command**

```bash
scripts/bootstrap_hitop_suffix_tools.sh
```

**Output**

```text
HiTOP suffix tooling installed.

Use:
  .venv/bin/hitop-suffix --help
```

This puts both console entry points on the venv; each prints its own
`--help` text once installed. See [Tooling & CLI](tooling-and-cli.md) for
the full command reference and copyable examples:

```bash
.venv/bin/hitop-codegen --help
.venv/bin/hitop-suffix --help
```

## What the script does

The bootstrap script is a thin, fixed wrapper around three commands. Run
them directly instead of the script in CI systems, containers, or any shell
the script doesn't target:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install --constraint requirements-lock.txt -e ".[dev]"
```

The install step resolves both the runtime dependencies (`lxml`, `PyYAML`,
`rdflib`) and the `dev` extra (`build`, `pytest`, `jsonschema`, `ruff`,
`tox`), pinned to the versions recorded in `requirements-lock.txt`, and ends
with `Successfully installed hitop-ontology-tools-{{ hitop_ontology_version }}` plus its resolved
dependency set.

## Lock and constraints policy

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

Expected result: `requirements-lock.txt` is rewritten with exact pins for the
newly resolved dependency set. Review the diff, then run the full validation
suite below against the refreshed lock file before committing.

## Release verification

Run the local quality gate — it compiles `src`, `scripts`, and `validation`,
runs the complete regression suite under `validation/`, and validates every
code example in `docs/`. A fully clean run reports every stage as `PASS` and
ends with the success confirmation shown below:

**Command**

```bash
scripts/validate_hitop_suffix_tooling.sh
```

**Output**

```text
Checking Python syntax and imports... PASS
Checking regression tests... PASS
Checking documentation code examples... PASS
Validation completed successfully.
```

Convert the ontology to Turtle and OWL without modifying repository artifacts:

```bash
.venv/bin/python scripts/rdf2ttl.py --output /tmp/hitop_release_gate.ttl
.venv/bin/python scripts/rdf2owl.py --output /tmp/hitop_release_gate.owl
```

Expected success signals include `Validated 892 Turtle triples` for the
Turtle gate and `Wrote /tmp/hitop_release_gate.owl` for the OWL/RDF XML gate.

Build the release distributions:

**Command**

```bash
.venv/bin/python -m build
```

**Output**

```text
Successfully built hitop_ontology_tools-{{ hitop_ontology_version }}.tar.gz and hitop_ontology_tools-{{ hitop_ontology_version }}-py3-none-any.whl
```

Run the supported Python matrix on a machine that has Python 3.10, 3.11, and
3.12 installed:

```bash
.venv/bin/tox -e py310,py311,py312
```

The release is not ready if any matrix environment is missing or failing —
see the [release checklist](release-checklist.md) for the authoritative
go/no-go status.
