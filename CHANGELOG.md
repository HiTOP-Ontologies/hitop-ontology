# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).
Tags follow the `vMAJOR.MINOR.PATCH` convention and match the version in
`pyproject.toml` and `owl:versionInfo` in `ontology/hitop.rdf`.

## [Unreleased]

## [0.1.0] - Not yet tagged

Blocked on Clinical Lab Go/No-Go (`CLIN-C5-02`) before this version is
tagged and released — see [`docs/release_checklist.md`](docs/release_checklist.md).

### Added

- HiTOP RDF/OWL ontology (`ontology/hitop.rdf`) with concept classes across
  the HiTOP hierarchy (Factor, Superspectrum, Spectrum, Subfactor, Component,
  Trait), plus generated Turtle and OWL/RDF XML artifacts.
- HiTOP base vocabulary (`src/data/hitop_base_vocabulary.csv`) and code
  generation tooling (`hitop-codegen`).
- Modular namespaced manifestation suffix schema
  (`docs/modular-namespaced-suffix-schema.md`) and `hitop-suffix` CLI/Python
  tooling for generation and validation.
- Manifestation-record JSON Schema (`schema/manifestation-record.schema.json`).
- Mapping and harmonization specification for manifestation suffixes
  (`docs/mapping-und-harmonisierung.md`).
- Versioned factorization system (`factorizations/`) for HiTOP hierarchy
  variants (Working Model, Externalizing, Psychosis, Emotional Dysfunction,
  Bass-Ackwards, DZPG-MDS) with schema validation and RDF generation
  (`docs/factorizations.md`).
- RDF conversion scripts (`scripts/rdf2ttl.py`, `scripts/rdf2owl.py`).
- Local validation suite (`validation/`) and documentation code-example
  validator (`scripts/validate_hitop_suffix_docs.py`).
- Clinical review scaffolding: `docs/references.md` (citation tracking per
  concept) and `docs/governance/clinical-annotation-notes.md` (boundary-case decisions).
