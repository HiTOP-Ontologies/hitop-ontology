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
| Factorizations | `factorizations/<id>/v<N>/`, one factorization version per change |
| Documentation | public docs, examples, release notes, and audit updates |

Do not mix clinical content changes with unrelated refactors. That makes review
and release approval harder to audit. Factorization manifests must not modify
`ontology/` — see [`docs/factorizations.md`](docs/factorizations.md).

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

Use `ontology/hitop.rdf` as the canonical RDF/XML input; `ontology/hitop.ttl`
and `ontology/hitop.owl` are generated from it. While drafting a change, write
generated artifacts to `/tmp` first so a work-in-progress `hitop.rdf` edit
never lands as a stale, out-of-sync `.ttl`/`.owl` pair:

```bash
.venv/bin/python scripts/rdf2ttl.py --output /tmp/hitop_review.ttl
.venv/bin/python scripts/rdf2owl.py --output /tmp/hitop_review.owl
```

Once a change to `ontology/hitop.rdf` is ready to commit, regenerate
`ontology/hitop.ttl` and `ontology/hitop.owl` in place (same commands, without
`--output`) and commit all three files together. Both converters produce
byte-deterministic output for the same input (see `TECH-T4-05`), so the
regenerated files are safe to diff and review like any other change.

### ROBOT Quality Gate

Run [ROBOT](http://robot.obolibrary.org/) against the generated OWL artifact
before a release:

```bash
robot report --input ontology/hitop.owl \
  --profile scripts/robot_report_profile.txt \
  --output /tmp/robot_report.tsv
```

The report is not checked into the repository (it is trivially regenerable
from `ontology/hitop.owl`, so keeping a copy in version control would just go
stale and add diff noise). CI runs this same report on every push/PR and
uploads it as the `robot-report` workflow artifact; regenerate it locally
with the command above whenever you need to inspect the current state.

`scripts/robot_report_profile.txt` is ROBOT's default report profile with one
deliberate override: `duplicate_label` is downgraded from `ERROR` to `WARN`.
HiTOP intentionally reuses the same clinical term at two different levels for
some constructs (for example "Anhedonia" as both a state-like Component,
`C00XyI`, and a stable trait, `T01hQc`, each with its own distinct
definition) — that is a modeling decision, not a data error, so it should not
fail the gate. Do not silence any other rule this way without the same kind
of documented, deliberate reasoning.

## Dependency Changes

Add or change dependencies in `pyproject.toml` first. If the change is intended
for release verification, refresh `requirements-lock.txt`, run the full release
gates, and document the reason for the dependency change.

## Versioning and Releases

Tags follow `vMAJOR.MINOR.PATCH` (SemVer) and match the version in
`pyproject.toml` and `owl:versionInfo` in `ontology/hitop.rdf`. Record every
notable change under an `[Unreleased]` section at the top of
[`CHANGELOG.md`](CHANGELOG.md) as part of the same pull request; create that
section with the first change after a release. Before tagging a release,
rename it to the version and release date, and work through
[`docs/reference/release-checklist.md`](docs/reference/release-checklist.md), which also tracks
the current version table across package, ontology, schema, and
specification documents.
