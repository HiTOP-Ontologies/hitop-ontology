# About the project

<div class="hitop-page-intro">
  <p>HiTOP Ontology provides stable, machine-readable identities for dimensional psychopathology concepts while preserving the local detail required by studies, instruments, and datasets.</p>
  <span class="hitop-source">Source · <a href="https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/README.md#why-this-exists">README.md / Why this exists</a></span>
</div>

## Why this exists

Mental-health datasets often use overlapping concepts with different labels, instrument items, local codes, and operational definitions. This makes cross-study comparison and downstream integration difficult even where the underlying constructs are related.

The project separates four responsibilities:

| Responsibility | What remains stable or explicit |
| --- | --- |
| Concept identity | A stable HiTOP base code |
| Local manifestation | A namespaced suffix for an item, scale, or operationalization |
| Provenance | The authority and source behind a local identifier |
| Mapping evidence | Relation, score, review state, and supporting evidence |

The intended result is shared semantics with local flexibility. Systems can retain operational detail while referencing common HiTOP concepts.

<aside class="hitop-scope" aria-label="Project scope">
  <strong>Scope</strong>
  <p>The ontology is designed for research, semantic interoperability, and auditable ontology development. It is not a diagnostic instrument and does not provide clinical advice.</p>
</aside>

## Documentation conventions

Normative requirements across this website use the terms `MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, and `MAY` as defined by [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119). `MUST` and `MUST NOT` identify requirements necessary for conformance. `SHOULD` and `SHOULD NOT` identify strong recommendations for which a documented exception may be appropriate. `MAY` identifies an optional capability.

This convention applies consistently to all specification and validation pages. Descriptive text without one of these terms is explanatory unless it appears in an explicitly normative grammar, regular expression, table, or algorithm.

## Core artifacts

The canonical ontology source is [`ontology/hitop.rdf`](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/ontology/hitop.rdf). Schemas, versioned factorization hierarchies, conversion tools, and validation tests live alongside it in the repository. Each website section points back to those maintained sources instead of introducing a second specification.

| Artifact | Role | Current version or status |
| --- | --- | --- |
| [`ontology/hitop.rdf`](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/ontology/hitop.rdf) | Canonical ontology source | Ontology `{{ hitop_ontology_version }}` |
| [Code system](../concepts/code-system.md) | Stable concept identifiers and checksums | Specification maintained in this repository |
| [Manifestation schema](../concepts/manifestation-suffixes.md) | Namespaced local manifestations | Versioned with the repository |
| [Factorizations](../models/factorizations.md) | Versioned concept compositions | Status shown per catalog entry |
| [Validation pipeline](../reference/validation-and-quality.md) | Tests, schema checks, conversion, and quality reports | Python 3.10–3.12 |

## Standards alignment

The repository uses RDF/OWL, SKOS, Dublin Core terms, explicit versions, open licensing, and reproducible validation. Together these provide a transparent technical basis for FAIR-oriented publication and reuse.

| Standard or practice | Version / namespace | Use in HiTOP Ontology | Details |
| --- | --- | --- | --- |
| RDF | RDF 1.1; canonical serialization RDF/XML | Graph representation of ontology statements | [Canonical RDF source](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/ontology/hitop.rdf) |
| OWL | OWL 2 / RDF-based serialization | Ontology semantics and generated OWL artifact | [Build and conversion](../reference/build-and-installation.md) |
| SKOS | W3C SKOS Recommendation | Mapping relations and factorization-local collections | [Mapping specification](../concepts/mapping-harmonization.md) |
| Dublin Core Terms | `http://purl.org/dc/terms/` | Descriptive metadata and provenance-oriented annotations | [Ontology source](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/ontology/hitop.rdf) |
| Explicit versions | Ontology `{{ hitop_ontology_version }}`; package `{{ hitop_ontology_version }}`; versioned factorization directories | Reproducible references to ontology, tooling, and factor structures | [Status and roadmap](status-and-roadmap.md) |
| Open licensing | MIT License | Permits reuse and adaptation under the repository license terms | [Publication and citation](publication-and-citation.md) |
| Reproducible validation | Python 3.10–3.12; JSON Schema and ROBOT checks | Tests source, examples, schemas, conversions, and ontology quality | [Validation and quality](../reference/validation-and-quality.md) |
