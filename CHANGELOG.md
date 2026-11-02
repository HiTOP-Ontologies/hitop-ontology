# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).
Tags follow the `vMAJOR.MINOR.PATCH` convention and match the version in
`pyproject.toml` and `owl:versionInfo` in `ontology/hitop.rdf`.

## [0.1.0] - 2026-11-02

First public release. Clinical content was reviewed and released by the
Clinical Lab (`CLIN-C0` to `CLIN-C5`); HiTOP base codes are frozen from this
release on.

### Added

- HiTOP RDF/OWL ontology (`ontology/hitop.rdf`) with concept classes across
  the HiTOP hierarchy (Factor, Superspectrum, Spectrum, Subfactor, Component,
  Trait), plus generated Turtle and OWL/RDF XML artifacts.
- Ontology header with ORCID-identified creator, publisher, rights holder and
  contributors; a PURL links to `ontology/contributions.rdf` for CRediT and
  complementary project roles.
- HiTOP base vocabulary (`src/data/hitop_base_vocabulary.csv`) and code
  generation tooling (`hitop-codegen`).
- Six clinically released factorizations (`meta.status: active`): HiTOP
  Working Model, Psychosis, Externalizing, Emotional Dysfunction,
  Bass-Ackwards and DZPG Minimum Data Set. Each has a hand-authored hierarchy
  YAML and generated RDF/XML, Turtle, OWL and diagram data (`docs/factorizations.md`).
- Factorization node kinds `concept` (same concept as the core code),
  `partial` (local construct overlapping a core concept, without asserting
  equivalence) and `collection` (local grouping), validated by the
  factorization hierarchy JSON Schema (`schema/factorization-hierarchy.schema.json`).
- Factorization provenance with ORCID creators/contributors and a shared
  contributions PURL; an explicit metadata-only refresh preserves existing
  hierarchy graphs.
- Modular namespaced manifestation suffix specification 0.3.0
  (`docs/modular-namespaced-suffix-schema.md`), released, including the
  twelve manifestation types and the ordered type-assignment rule (§5.1) with
  `GS` as the last resort; `hitop-suffix` CLI/Python tooling for generation and
  validation.
- Manifestation-record JSON Schema (`schema/manifestation-record.schema.json`).
- Mapping and harmonization specification for manifestation suffixes
  (`docs/mapping-und-harmonisierung.md`).
- Verified bibliography and a source attribution for every ontology class
  (`docs/reference/references.md`), and decided clinical boundary cases
  (`docs/governance/clinical-annotation-notes.md`).
- RDF conversion scripts (`scripts/rdf2ttl.py`, `scripts/rdf2owl.py`) with
  deterministic OWL output.
- Validation suite (`validation/`), documentation code-example validator
  (`scripts/validate_hitop_suffix_docs.py`) and local quality gate
  (`scripts/validate_hitop_suffix_tooling.sh`). Each factorization's concept
  labels are checked against the core ontology only.
- CI workflow with tests on Python 3.10–3.12, Ruff lint and format checks and
  a ROBOT ontology quality report.
- Documentation website (MkDocs Material) with a factorization catalog,
  icicle diagrams and a release checklist (`docs/reference/release-checklist.md`).

### Changed

Compared with untagged pre-release snapshots of `main`:

- Core vocabulary revised after the clinical source-paper review.
  - Removed: `C021Q0`, `C022PW`, `C0237W`, `C024WG`, `C025ex`, `C0277d`,
    `C02BO8`, `C02CiQ`, `C02DSC`, `T026cQ`, `T028jy`, `T029jr`, `T02A06`,
    `T02EFv` (constructs covered by existing concepts or renumbered below).
  - Reassigned: `C01kKJ` Behavioral avoidance, `C01l9M` Body dissatisfaction,
    `C01mPz` Binge eating, `C01nVp` Cognitive restraint, `C01oMk` Purging,
    `C01pc6` Excessive exercise, `C01qTa` Restricting, `C01rfi` Muscle building,
    `C01s9T` Negative attitudes toward obesity, `C01tAk` Low sexual desire,
    `C01ueZ` Difficulties with arousal, `C01vT5` Low orgasmic function,
    `C01wSl` Sex-related distress, `C01xzj` Decreased need for sleep,
    `C01yno` Health/Illness anxiety, `C01zXz` Hyperactivity,
    `C020XA` Disorganization (previous labels are recorded in Git history).
  - Added: `T021iZ` Perceptual dysregulation.
- Source citations now name the correct first authors: Krueger et al. (2021)
  for the externalizing superspectrum, Watson et al. (2022) for the emotional
  dysfunction superspectrum and Woelke et al. (2025) for the DZPG Minimum Data Set.

[0.1.0]: https://github.com/HiTOP-Ontologies/hitop-ontology/releases/tag/v0.1.0
