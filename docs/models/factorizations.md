# Factorizations

<div class="hitop-page-intro">
  <p>Versioned HiTOP structures show how stable core concepts are arranged and grouped within a specific model or publication.</p>
  <span class="hitop-source">Generated source · <a href="https://github.com/HiTOP-Ontologies/hitop-ontology/tree/main/factorizations">factorizations/*/v*/README.md</a></span>
</div>

## Purpose

The core ontology (`ontology/hitop.rdf`) is a kit of stable, reusable building blocks — Superspectra, Spectra, Subfactors, Components, Traits — plus the shared vocabulary used to compose them into a hierarchy. A factorization is a concrete, versioned composition of those blocks into one particular published structure. It never defines a new concept and never redefines what a core code means; it only records how an existing set of codes is ordered and grouped for one specific, citable model.

## Catalog

<!-- BEGIN GENERATED FACTORIZATION CATALOG -->
| Factorization | Directory version | Status |
| --- | --- | --- |
| [HiTOP Working Model — v1 (V1052k)](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/factorizations/working-model/v1/README.md) | `v1` | **active** |
| [Emotional Dysfunction Superspectrum — v1 (V106mv)](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/factorizations/emotional-dysfunction/v1/README.md) | `v1` | **active** |
| [Externalizing Superspectrum — v1 (V108kx)](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/factorizations/externalizing/v1/README.md) | `v1` | **active** |
| [Psychosis Superspectrum — v1 (V10749)](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/factorizations/psychosis/v1/README.md) | `v1` | **active** |
| [DZPG Minimal Data Set — v1 (V10dzp)](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/factorizations/dzpg-mds/v1/README.md) | `v1` | **active** |
| [Bass-Ackwards Structure — v1 (V10bak)](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/factorizations/bass-ackwards/v1/README.md) | `v1` | **active** |
<!-- END GENERATED FACTORIZATION CATALOG -->

## How the model works

Each factorization's `<version>_hierarchy.yaml` file is a recursive tree that records parent-child order and the role each concept plays in that particular model. A `kind: concept` node references an existing core code with the same meaning, allowing equivalent local wording. A `kind: partial` node represents partial overlap with an existing core concept, using a required stable local `id` and an optional `mapping_note` to describe the overlap. A `kind: collection` node is a factorization-local grouping. `level` is always a free string, because the same concept can sit at a different level in different factorizations.

[Read the specification](specification.md){ .hitop-button }
[Create a factorization](create-a-factorization.md){ .hitop-button .hitop-button--primary }

## Diagrams

Every diagram renders as an icicle layout, one row per hierarchy level, colored by a single, factorization-wide palette rule. It is compiled straight from the same hierarchy YAML listed in the catalog above — `scripts/generate_factorization_diagram_data.py` validates it with the same logic as the test suite and writes the result into `<version>_diagram.json`, so a diagram can never drift from the data it represents.

[View the diagrams](diagrams.md){ .hitop-button .hitop-button--primary }
