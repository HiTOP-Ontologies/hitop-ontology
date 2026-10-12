# HiTOP Ontology

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10-3.12](https://img.shields.io/badge/python-3.10--3.12-blue.svg)](pyproject.toml)

The HiTOP Ontology is a machine-readable representation of the Hierarchical
Taxonomy of Psychopathology (HiTOP). It provides stable identifiers, RDF/OWL
ontology artifacts, and Python tooling for representing dimensional
psychopathology concepts and their study-, instrument-, or dataset-specific
manifestations.

The repository is designed for research, semantic interoperability, and
auditable ontology development. It is not a diagnostic instrument and does not
provide clinical advice.

## Contents

- [Status](#status)
- [Why this exists](#why-this-exists)
- [Core artifacts](#core-artifacts)
- [Identifier model](#identifier-model)
- [Standards alignment](#standards-alignment)
- [Repository layout](#repository-layout)
- [Quickstart](#quickstart)
- [Using the tools](#using-the-tools)
- [Validation](#validation)
- [Ontology conversion](#ontology-conversion)
- [Documentation](#documentation)
- [Ecosystem and reuse](#ecosystem-and-reuse)
- [Contributing](#contributing)
- [Citation](#citation)
- [License](#license)

## Status

| Item | Current state |
| --- | --- |
| Ontology IRI | `http://purl.org/hitop` |
| Canonical ontology source | [`ontology/hitop.rdf`](ontology/hitop.rdf) |
| Ontology version | `0.1.0` in the ontology declaration |
| Python package | `hitop-ontology-tools`, version `0.1.0` |
| Primary ontology format | RDF/XML |
| Generated formats | Turtle and OWL/RDF XML via conversion scripts |
| Supported Python versions | 3.10, 3.11, 3.12 |
| License | MIT |

The technical tooling is usable for local generation, validation, conversion,
and release checks. Clinical content, ontology metadata, and release-governance
decisions should still be reviewed before treating a public release as stable.

## Why this exists

Mental health datasets often use overlapping concepts with different labels,
instrument items, local codes, and operational definitions. This makes
cross-study comparison and downstream data integration difficult even when the
underlying psychopathology constructs are related.

This repository addresses that problem by separating:

- stable HiTOP concept identity
- local manifestation identity
- provenance and namespace authority
- mapping and harmonization evidence
- reproducible ontology conversion and validation

The intended outcome is shared semantics with local flexibility: studies and
systems can keep their local operational detail while still referencing common
HiTOP concepts.

## Core artifacts

| Artifact | Purpose |
| --- | --- |
| [`ontology/hitop.rdf`](ontology/hitop.rdf) | Canonical RDF/XML ontology source |
| [`src/data/hitop_base_vocabulary.csv`](src/data/hitop_base_vocabulary.csv) | Local lookup table for stable HiTOP base codes |
| [`schema/manifestation-record.schema.json`](schema/manifestation-record.schema.json) | JSON Schema for manifestation record exports |
| [`schema/factorization-manifest.schema.json`](schema/factorization-manifest.schema.json) | JSON Schema for factorization manifests under `factorizations/` |
| [`docs/codesystem.md`](docs/codesystem.md) | HiTOP code-system explanation |
| [`docs/modular-namespaced-suffix-schema.md`](docs/modular-namespaced-suffix-schema.md) | Modular namespaced manifestation suffix specification |
| [`docs/mapping-und-harmonisierung.md`](docs/mapping-und-harmonisierung.md) | Mapping, review, and harmonization specification |
| [`docs/factorizations.md`](docs/factorizations.md) | Factorization manifest structure, versioning, and governance |
| [`docs/reference/tooling-and-cli.md`](docs/reference/tooling-and-cli.md) | Copyable CLI and Python API examples |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Review workflow, validation gates, and contribution expectations |

## Identifier model

The project separates a stable HiTOP base code from optional manifestation
suffixes.

```text
<HITOP_BASE_CODE>.M-<TT>-<NS>-<SLUG>
```

Example:

```text
U0aB2X.M-AF-ROR3J2WQSVQFFIKK-CHRONIC_WORRY
```

| Part | Meaning |
| --- | --- |
| `<HITOP_BASE_CODE>` | Stable HiTOP base concept code |
| `M` | Literal manifestation block |
| `<TT>` | Controlled manifestation type, for example `AF`, `SS`, or `IM` |
| `<NS>` | Fixed-length namespace token for the local authority space |
| `<SLUG>` | Human-readable local manifestation slug |

The code string is intentionally compact. Full semantic meaning belongs in the
ontology, metadata, mappings, definitions, and review evidence, not in the
identifier alone. In data exchange, use the local code together with the HiTOP
system IRI `http://purl.org/hitop`.

## Standards alignment

The README structure and project documentation are aligned with common GitHub
and ontology-publication practice: explain what the project does, why it is
useful, how to get started, where to get help, who maintains it, and how to
cite or reuse it.

| Area | Implementation in this repository |
| --- | --- |
| FAIR findability | Stable ontology IRI, documented repository layout, explicit artifacts |
| FAIR accessibility | Public repository paths, open license, copyable setup and validation commands |
| FAIR interoperability | RDF/XML source, OWL/RDF XML and Turtle conversion, SKOS/Dublin Core usage |
| FAIR reusability | License, provenance-oriented mappings, versioned specifications, validation gates |
| Linked Data | HTTP-based ontology IRI, RDF/OWL representation, reusable vocabularies |
| OBO-style ontology practice | Open license, common formal formats, scope, identifiers, textual definitions, documentation, contribution workflow |

Relevant external guidance includes:

- [GitHub Docs: About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
- [The FAIR Guiding Principles](https://www.nature.com/articles/sdata201618)
- [W3C Best Practices for Publishing Linked Data](https://www.w3.org/TR/ld-bp/)
- [OBO Foundry Principles](https://obofoundry.org/principles/fp-000-summary.html)
- [Citation File Format](https://citation-file-format.github.io/)

## Repository layout

| Path | Purpose |
| --- | --- |
| [`ontology`](ontology) | Canonical RDF source and generated ontology artifacts |
| [`factorizations`](factorizations) | Versioned factorization manifests composing core concepts into specific HiTOP factor structures |
| [`src/hitop/base`](src/hitop/base) | HiTOP base-code checksum and CSV generation tooling |
| [`src/hitop/suffix`](src/hitop/suffix) | Manifestation suffix namespace, slug, code, metadata, and mapping tooling |
| [`scripts`](scripts) | Setup, validation, ontology conversion, and generation entry points |
| [`schema`](schema) | JSON Schema artifacts for manifestation record and factorization manifest exports |
| [`validation`](validation) | Regression tests used by local and release gates |
| [`docs`](docs) | Specifications, examples, release audit material, and operational documentation |

## Quickstart

Use Python 3.10, 3.11, or 3.12. From the repository root:

```bash
scripts/bootstrap_hitop_suffix_tools.sh
```

Manual equivalent:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install --constraint requirements-lock.txt -e ".[dev]"
```

The editable install exposes two command line tools:

```bash
.venv/bin/hitop-codegen --help
.venv/bin/hitop-suffix --help
```

## Using the tools

Generate a namespace token:

```bash
.venv/bin/hitop-suffix namespace ROR https://ror.org/00tkfw097
```

Normalize a manifestation label into a slug:

```bash
.venv/bin/hitop-suffix slug "Chronic worry"
```

Build a full manifestation code:

```bash
.venv/bin/hitop-suffix build-code \
  --hitop U0aB2X \
  --manifestation-type AF \
  --namespace-token ROR3J2WQSVQFFIKK \
  --slug CHRONIC_WORRY
```

Validate a full manifestation code:

```bash
.venv/bin/hitop-suffix validate-code \
  U0aB2X.M-AF-ROR3J2WQSVQFFIKK-CHRONIC_WORRY
```

More CLI and Python API examples are maintained in
[`docs/reference/tooling-and-cli.md`](docs/reference/tooling-and-cli.md).

## Validation

Run the compact local quality gate:

```bash
scripts/validate_hitop_suffix_tooling.sh
```

The validation script compiles Python sources, runs regression tests under
[`validation`](validation), and checks manifestation-code examples embedded in
[`docs`](docs).

For release verification across supported Python versions:

```bash
.venv/bin/tox -e py310,py311,py312
```

The runner must provide all three Python interpreters.

## Ontology conversion

The canonical ontology source is [`ontology/hitop.rdf`](ontology/hitop.rdf).
Generate Turtle and cleaned OWL/RDF XML artifacts with:

```bash
.venv/bin/python scripts/rdf2ttl.py
.venv/bin/python scripts/rdf2owl.py
```

For review and release gates, write generated files to temporary paths first:

```bash
.venv/bin/python scripts/rdf2ttl.py --output /tmp/hitop_release_gate.ttl
.venv/bin/python scripts/rdf2owl.py --output /tmp/hitop_release_gate.owl
```

Only commit generated ontology artifacts after reviewing the generated diff.

## Documentation

Start with these documents:

| Topic | Document |
| --- | --- |
| Installation and dependency policy | [`docs/reference/build-and-installation.md`](docs/reference/build-and-installation.md) |
| Code-system model | [`docs/codesystem.md`](docs/codesystem.md) |
| Base vocabulary | [`docs/concepts/core-vocabulary.md`](docs/concepts/core-vocabulary.md) |
| Manifestation suffixes | [`docs/modular-namespaced-suffix-schema.md`](docs/modular-namespaced-suffix-schema.md) |
| Mapping and harmonization | [`docs/mapping-und-harmonisierung.md`](docs/mapping-und-harmonisierung.md) |
| Tooling examples | [`docs/reference/tooling-and-cli.md`](docs/reference/tooling-and-cli.md) |

## Ecosystem and reuse

HiTOP Ontology is maintained as an independent, domain-focused upstream
project. It is not an official publication of the organizations linked below.
The links document relevant research and implementation contexts without
implying ownership, endorsement, or joint governance.

| Context | Relationship | Reference |
| --- | --- | --- |
| German Center for Mental Health (DZPG) | Mental-health research context; the repository contains a versioned DZPG Minimal Data Set factorization | [DZPG website](https://www.dzpg.org/) · [`factorizations/dzpg-mds`](factorizations/dzpg-mds/) |
| Medical Informatics Initiative (MII) | Interoperability and downstream implementation context | [MII repositories on GitHub](https://github.com/medizininformatik-initiative) |

Downstream specifications should link to a tagged HiTOP Ontology release or
DOI rather than copying an unversioned snapshot. Conversely, concrete public
implementations can be added here once a stable module-specific URL is
available. See
[`docs/project/publication-and-citation.md`](docs/project/publication-and-citation.md)
for the publication and cross-referencing policy.

## Contributing

Contributions should keep clinical content, ontology artifacts, tooling, schema
changes, and documentation changes reviewable as separate concerns. Before
opening or merging changes, read [`CONTRIBUTING.md`](CONTRIBUTING.md) and run
the relevant validation gates.

Use GitHub issues for term requests, bugs, mapping questions, or release-gate
problems:

```text
https://github.com/HiTOP-Ontologies/hitop-ontology/issues
```

## Citation

Until a DOI-backed release and `CITATION.cff` are published, cite the
repository and the version used:

```bibtex
@misc{hitop_ontology_2026,
  title = {HiTOP Ontology},
  author = {{HiTOP Ontologies contributors}},
  year = {2026},
  version = {0.1.0},
  url = {https://github.com/HiTOP-Ontologies/hitop-ontology}
}
```

For a DOI-backed scholarly release, update the root-level [`CITATION.cff`](CITATION.cff)
with the DOI, release date, authorship metadata, and preferred citation.

## License

This repository is licensed under the [MIT License](LICENSE).
