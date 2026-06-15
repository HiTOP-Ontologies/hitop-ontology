# Contributing

This repository contains both technical tooling and clinically relevant ontology
content. Treat release changes as auditable scientific software changes: keep
the scope clear, preserve reproducibility, and document review decisions.

## Supported Environment

Use Python 3.10, 3.11, or 3.12 from the repository root:

```bash
scripts/bootstrap_hitop_suffix_tools.sh
```

The canonical package and dependency metadata lives in `pyproject.toml`.
`requirements-lock.txt` is the tested constraints snapshot for release checks;
refresh it only as an intentional maintenance change.

## Change Scope

Keep pull requests focused on one concern:

| Change type | Expected scope |
| --- | --- |
| Tooling | `src/`, `scripts/`, `validation/`, and related docs |
| Ontology artifacts | `ontology/` plus conversion evidence |
| Schema/model | `schema/`, validators, generators, fixtures, and docs |
| Clinical content | concept labels, definitions, hierarchy, mappings, and review evidence |
| Documentation | public docs, examples, release notes, and audit updates |

Do not mix clinical content changes with unrelated refactors. That makes review
and release approval harder to audit.

## Local Validation

Run the compact quality gate before submitting changes:

```bash
scripts/validate_hitop_suffix_tooling.sh
```

For release-relevant changes, also run:

```bash
.venv/bin/tox -e py310,py311,py312
.venv/bin/python scripts/rdf2ttl.py --output /tmp/hitop_release_gate.ttl
.venv/bin/python scripts/rdf2owl.py --output /tmp/hitop_release_gate.owl
.venv/bin/python -m build
.venv/bin/pip check
```

The Python matrix requires all supported interpreters to be available on the
runner.

## Code and Documentation Standards

Production code must have clear English module, class, and function docstrings.
Use inline comments only for non-obvious invariants, release contracts,
validation rules, or source-data assumptions.

Public examples must be copyable and include expected output when practical.
When documenting code examples under `docs/`, run the documentation validation
gate because manifestation-code examples are parsed automatically.

## Ontology Artifacts

Use `ontology/hitop.rdf` as the canonical RDF/XML input unless a release task
explicitly changes that policy. During review, write generated artifacts to
`/tmp` first:

```bash
.venv/bin/python scripts/rdf2ttl.py --output /tmp/hitop_review.ttl
.venv/bin/python scripts/rdf2owl.py --output /tmp/hitop_review.owl
```

Commit generated ontology artifacts only when the release plan explicitly calls
for updated artifacts and the generated diff has been reviewed.

## Dependency Changes

Add or change dependencies in `pyproject.toml` first. If the change is intended
for release verification, refresh `requirements-lock.txt`, run the full release
gates, and document the reason for the dependency change.
