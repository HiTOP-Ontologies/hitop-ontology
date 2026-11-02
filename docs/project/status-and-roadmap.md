# Status & roadmap

<div class="hitop-page-intro">
  <p>A current overview of the ontology, tooling, supported environments, and the next documented development steps.</p>
  <span class="hitop-source">Source · <a href="https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/README.md#status">README.md / Status</a> · <a href="../../reference/release-checklist/">docs/reference/release-checklist.md</a></span>
</div>

## Current state

| Item | Current state |
| --- | --- |
| Ontology IRI | `http://purl.org/hitop` |
| Canonical ontology source | `ontology/hitop.rdf` |
| Ontology version | `{{ hitop_ontology_version }}` |
| Python package | `hitop-ontology-tools` version `{{ hitop_ontology_version }}` |
| Primary format | RDF/XML |
| Generated formats | Turtle and OWL/RDF XML |
| Supported Python | 3.10, 3.11, 3.12 |
| License | MIT |

The technical tooling supports local generation, validation, conversion, and release checks. Version `{{ hitop_ontology_version }}` is the first public release: its clinical content, the six factorizations, and the manifestation-suffix specification were reviewed and released by the Clinical Lab, and HiTOP base codes are frozen from this release on.

## Website roadmap

- Living documentation built from the repository Markdown sources
- Generated catalog of versioned factorizations
- Data-driven icicle diagrams from hierarchy YAML
- Browser-based learning module for authoring a factorization
- Accessible light and dark modes, local search, and responsive navigation
- Pages deployment only after repository validation succeeds

See the [release checklist](../reference/release-checklist.md) for the authoritative release gates.
