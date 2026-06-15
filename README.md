# HiTOP Ontology Tools

This repository contains ontology conversion scripts, HiTOP base-code checksum
tools, and tooling for modular namespaced manifestation suffixes.

## Repository Layout

| Path | Purpose |
| --- | --- |
| `src/hitop/base` | HiTOP base-code checksum and CSV generation tooling |
| `src/hitop/suffix` | Manifestation suffix namespace, slug, code, metadata, and mapping tooling |
| `scripts` | Repository-local setup, validation, ontology conversion, and CSV generation entry points |
| `schema` | JSON Schema artifacts for manifestation record exports |
| `ontology` | Canonical RDF source and generated ontology artifacts |
| `validation` | Regression tests used by local and release gates |
| `docs` | Specifications, release audit material, and operational documentation |

## Local Setup

Use Python 3.10, 3.11, or 3.12. The canonical dependency and package metadata
source is `pyproject.toml`.

Recommended setup from the repository root:

```bash
scripts/bootstrap_hitop_suffix_tools.sh
```

Manual equivalent:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install --constraint requirements-lock.txt -e ".[dev]"
```

The editable install exposes these command line entry points:

```bash
.venv/bin/hitop-codegen --help
.venv/bin/hitop-suffix --help
```

## CLI and API Examples

Copyable examples for `hitop-codegen`, `hitop-suffix`, and the Python API are
maintained in `docs/tooling_examples.md`.

## Validation

Run the repository checks from the repository root:

```bash
scripts/validate_hitop_suffix_tooling.sh
```

The validation script compiles the Python sources, runs the regression tests in
`validation`, and checks manifestation-code examples embedded in `docs`.

For release verification across supported Python versions, use:

```bash
.venv/bin/tox -e py310,py311,py312
```

The runner must provide all three Python interpreters for a release gate.

## Release Gate Commands

Run these commands from the repository root before creating a release commit or
tag. A release is not ready while any command fails or while `git status` shows
unintentional generated, deleted, or untracked files.

```bash
git status --short
scripts/bootstrap_hitop_suffix_tools.sh
scripts/validate_hitop_suffix_tooling.sh
.venv/bin/tox -e py310,py311,py312
```

Validate that the JSON Schema parses as JSON:

```bash
.venv/bin/python -m json.tool \
  schema/manifestation-record.schema.json \
  /tmp/manifestation-record.schema.json
```

Run ontology conversion gates against temporary output paths so review builds
do not modify repository artifacts:

```bash
.venv/bin/python scripts/rdf2ttl.py --output /tmp/hitop_release_gate.ttl
.venv/bin/python scripts/rdf2owl.py --output /tmp/hitop_release_gate.owl
```

Build release distributions:

```bash
.venv/bin/python -m build
.venv/bin/pip check
```

Expected build artifacts are written to `dist/`. The `dist/`, `.tox/`, and
`.venv/` directories are local build outputs and must not be committed.

## Ontology Conversion

The RDF conversion scripts require the package dependencies installed by the
setup command above:

```bash
.venv/bin/python scripts/rdf2ttl.py
.venv/bin/python scripts/rdf2owl.py
```

The scripts read `ontology/hitop.rdf` and write generated ontology artifacts
under `ontology/`.

For release checks, prefer writing to `/tmp` as shown above. Only update
repository ontology artifacts intentionally, after reviewing the generated diff.

## Dependency Policy

`pyproject.toml` is the source of truth. `requirements-lock.txt` is a tested
constraints snapshot for reproducible release checks. See
`docs/build_and_installation.md` for the complete policy.

## Contribution Policy

Use `CONTRIBUTING.md` for the minimum workflow, validation gates, and review
expectations before opening or merging changes.
