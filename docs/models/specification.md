# Specification

<div class="hitop-page-intro">
  <p>Specification for creating, validating, and publishing versioned HiTOP factorization models.</p>
  <span class="hitop-source">Status · Maintained specification</span>
  <span class="hitop-source">Source · <a href="https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/docs/factorizations.md">docs/factorizations.md</a></span>
  <span class="hitop-source">Applies to · <a href="https://github.com/HiTOP-Ontologies/hitop-ontology/tree/main/factorizations">factorizations/</a> · <a href="https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/schema/factorization-hierarchy.schema.json">schema/factorization-hierarchy.schema.json</a></span>
</div>

## Purpose

The core ontology (`ontology/hitop.rdf`) is a kit of parts: it defines stable, reusable concept classes (Superspectra, Spectra, Subfactors, Components, Traits) and the shared vocabulary used to compose them into a hierarchy (`hitop:hasTier`, `hitop:hasLevel` — see [Vocabulary](#vocabulary)).

A factorization is a concrete, versioned composition of those parts into one particular HiTOP structure. It is maintained as a single, human-readable YAML document, which a generator script (`scripts/generate_factorization_ontology.py`) mechanically compiles into a formal RDF ontology that references only the stable core classes.

## Principles

1. A factorization MUST NOT define new concepts. It may only reference `hitop_base_code` values that already exist in `ontology/hitop.ttl`.
2. A factorization adds no triples to the core ontology. `hitop:hasTier` and `hitop:hasLevel` are declared in the core, but are only ever asserted inside a factorization file, never in the core itself.
3. The same concept can hold a different level in different factorizations. Level is therefore never a property of the class itself, only a statement inside one particular factorization — which is why `hitop:hasLevel` is a free string rather than a fixed class enumerated in the core (see [Vocabulary](#vocabulary)).
4. Every factorization version is its own, self-contained directory. A new version never touches an older version's directory.
5. Factorization files are independent statements with provenance, status, and review level — analogous to the mapping artifacts in [Mapping & harmonization](../concepts/mapping-harmonization.md).
6. A factorization MAY group several existing concepts into a new grouping valid only within that one factorization, without creating a new concept in the core. Such a node is `kind: collection` (see [Vocabulary](#vocabulary)).

## Structure

```text
factorizations/<factorization-id>/v<N>/
```

| File | Required | Meaning |
| --- | --- | --- |
| `<version>_hierarchy.yaml` | Yes | Tree structure, provenance, ontology pin |
| `README.md` | Yes | Short description, citation, status |
| `<version>_factorization.ttl` | Generated | See [Generated factorization ontology](#generated-factorization-ontology); never hand-maintained |

`<factorization-id>` is a stable kebab-case identifier — for example `working-model`, `bass-ackwards`, `dzpg-mds`, `psychosis`, `externalizing`, `emotional-dysfunction`. `<version>` is the hierarchy file's filename prefix (for example `V1052k`) — not a running count, but a stable identifier assigned once per curation run.

## Vocabulary

The core defines a single open, extensible class for every concrete HiTOP concept:

| Class | Purpose |
| --- | --- |
| `hitop:O002sP` (`Tier`) | Every concrete HiTOP concept class (Internalizing, Anxiousness, …). Open, extensible. |

There is deliberately **no** class modeling "level" as a fixed set of core-enumerated subclasses (Factor, Superspectrum, Spectrum, Subfactor, Component, Trait). The number of possible levels is not exhaustively known — some factorizations need `Subfactor`, others additionally `Sub-subfactor` or deeper — and a concept's level assignment is factorization-dependent regardless (Principle 3). A fixed core class per level would force a core change for every new combination.

Two properties relate `Tier` concepts to each other:

<div class="hitop-vocabulary-table" markdown="1">

| Aspect | `hitop:hasTier` | `hitop:hasLevel` |
| --- | --- | --- |
| Relation | Tier → Tier | Tier → String |
| YAML source | A node's `children` nesting | A node's free-text `level` value |
| Function | Defines the parent-child relationship and therefore the tree's vertical order | Describes the role a concept plays within this factorization |
| Interpretation | Every child is exactly one step below its parent; depth is the number of `hasTier` steps from the root | Values may include `Spectrum`, `Component`, or `Sub-subfactor` |
| Validation consequence | No separate rank list is required to determine vertical order | Levels are not checked against depth; irregular trees may skip ranks or reuse a level label at different depths |

</div>

#### RDF interpretation

`hitop:hasTier` uses HiTOP concept-class IRIs, such as `hitop:P002nf`,
directly as subject and object. In OWL 2 this is known as *punning*: the same IRI
identifies a class and also acts as an individual in the factorization.

- Reasoning boundary: These statements do not create automatic subclass
  relationships.
- Validation boundary: Referential-integrity and duplicate-code checks are
  performed by `validation/test_factorizations.py`.

#### Collection nodes

<p class="hitop-section-kicker"><code>kind: collection</code> · factorization-local grouping</p>

Sometimes a factorization merges several existing concepts into a new node valid only within that one factorization — for example, merging `Internalizing` and `Thought Disorder` into one shared superspectrum. When that grouping is not an independent, reusable HiTOP construct from the cited literature, it is **not** added to the core as a new concept (that would violate Principle 1). It is instead modeled as a local `skos:Collection` node:

- **YAML:** the node gets `kind: collection` (instead of the implicit default `concept`); its `code` is a factorization-local id that is **not** checked against `ontology/hitop.ttl`.
- **Generated RDF:** the node gets `rdf:type skos:Collection` and its own IRI in the factorization namespace (`http://purl.org/hitop/factorizations/<id>/v<version>#<code>`) instead of a core IRI.
- **Hierarchy:** it carries `hitop:hasLevel` (for example `"Superspectrum"`) and `hitop:hasTier` to its `children` exactly like any other node — the merged concepts (Internalizing, Thought Disorder) are simply its children. No separate property is needed to record "members" apart from "children".

This pattern follows the standard SKOS distinction between `skos:Concept` (a meaning-bearing unit, here: `Tier`) and `skos:Collection` (a purely organizational grouping with no concept identity of its own).

## Hierarchy file format

The hierarchy file is the editable source of a factorization version. It keeps
the identity and provenance of the version together with the actual concept
tree, so reviewers can understand who created the structure, which ontology
version it uses, and how its nodes are arranged without reading generated RDF.

Each `<version>_hierarchy.yaml` file has two top-level sections: `meta` records
the factorization's identity, status, source, ontology reference, and
provenance; `hierarchy` contains the recursive tree of concepts and optional
collection nodes. The example below shows their relationship. The schema then
checks the document against the maintained contract in
[`schema/factorization-hierarchy.schema.json`](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/schema/factorization-hierarchy.schema.json)
before any ontology or diagram artifact is generated.

```yaml
meta:
  factorization_id: working-model
  version: V1052k
  label: HiTOP Working Model
  status: draft
  source: data/hitop/images/hitop_working_model.png
  based_on:
    ontology_iri: "http://purl.org/hitop"
    ontology_version: "{{ hitop_ontology_version }}"
  provenance:
    created_by:
      - orcid: "https://orcid.org/0000-0002-4505-4593"
        name: "Rogério Blitz"
    contributors:
      - orcid: "https://orcid.org/0000-0002-4505-4593"
        name: "Rogério Blitz"
    contributions: "http://purl.org/hitop/contributions"
    created_at: "2026-07-03"

hierarchy:
  label: General Factor of Psychopathology (p-factor)
  level: Factor
  code: F001Hw
  children:
    - label: Externalizing
      level: Superspectrum
      code: S0013h
      children: [...]
```

<a href="../assets/downloads/factorization-hierarchy.template.yaml" download="hitop-factorization-hierarchy-template.yaml">Download the YAML starter template</a>

The starter template distinguishes required, conditional, and optional fields. Replace every `<REPLACE_WITH_…>` placeholder before validation. YAML comments document controlled values and when optional fields should be enabled; the commented-out `children` block shows the node shape to repeat for every level of the tree.

### Field reference

This reference covers every `meta` and node field defined by [`schema/factorization-hierarchy.schema.json`](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/schema/factorization-hierarchy.schema.json). It initially shows mandatory fields; use the filter to inspect conditional, optional, or all fields. `Node` rows apply to every node in the `hierarchy` tree, recursively, not only to the root.

<div class="hitop-metadata-reference" markdown="1">
  <label class="hitop-metadata-filter">Requirement
    <select data-metadata-filter>
      <option value="mandatory" selected>Mandatory</option>
      <option value="conditional">Conditional</option>
      <option value="optional">Optional</option>
      <option value="all">All fields</option>
    </select>
  </label>
  <span class="hitop-metadata-count" data-metadata-count aria-live="polite"></span>

| Structure | Field path | Requirement | Meaning |
| --- | --- | --- | --- |
| Meta | `meta.factorization_id` | Mandatory | MUST match the directory name |
| Meta | `meta.version` | Mandatory | MUST match the hierarchy file's filename prefix |
| Meta | `meta.label` | Mandatory | Human-readable factorization name |
| Meta | `meta.status` | Mandatory | `draft`, `active`, or `deprecated` |
| Meta | `meta.source` | Optional | Origin of the factor structure, for example a source image or dataset path |
| Meta | `meta.paper` | Optional | Citation for the publication this factorization is derived from |
| Ontology pin | `meta.based_on.ontology_iri` | Mandatory | Always `http://purl.org/hitop` |
| Ontology pin | `meta.based_on.ontology_version` | Mandatory | The `owl:versionInfo` state that `code` values were resolved against |
| Ontology pin | `meta.based_on.commit` | Optional | Git commit hash pinning the exact ontology state codes were resolved against |
| Provenance | `meta.provenance.created_by` | Mandatory | List of people with `orcid` and `name`; legacy name strings remain accepted |
| Provenance | `meta.provenance.contributors` | Optional | List of people with `orcid` and `name` contributing to this factorization |
| Provenance | `meta.provenance.contributions` | Optional | PURL for the central contribution record; defaults to `http://purl.org/hitop/contributions` |
| Provenance | `meta.provenance.created_at` | Mandatory | Date this factorization version was created |
| Provenance | `meta.provenance.notes` | Optional | Free-text provenance notes, for example differences from a previous version |
| Hierarchy | `hierarchy` | Conditional | The recursive tree root; MAY be `null` only while `meta.status` is `draft` and the tree has not been populated yet |
| Node | `label` | Mandatory | Human-readable name |
| Node | `level` | Mandatory | Free text naming this node's role in this factorization (see [Vocabulary](#vocabulary)) |
| Node | `code` | Mandatory | For `kind: concept`: a `hitop_base_code` from `ontology/hitop.ttl`; for `kind: collection`: a factorization-local id |
| Node | `kind` | Optional | `concept` (default) or `collection` (factorization-local grouping, see [Vocabulary](#vocabulary)) |
| Node | `children` | Optional | Child nodes, one level deeper; determines tree depth and order |
| Node | `bridge` | Optional | Documentation only: labels of other nodes this concept empirically cross-loads onto. Creates **no** second `hasTier` edge and is not validated against codes |
| Node | `provisional` | Optional | Marks a single node as provisional, independent of `meta.status` |

</div>

`validation/test_factorizations.py` checks:

- schema conformance against `factorization-hierarchy.schema.json`;
- that every `kind: concept` node's `code` (recursively, across the whole tree) actually exists as a class in `ontology/hitop.ttl` — referential integrity; `kind: collection` nodes are exempt. Vertical order itself already follows structurally from the `children` nesting and is not checked separately; `level` is deliberately not checked for depth consistency (see [Vocabulary](#vocabulary));
- that no `code` occurs twice within one tree;
- that every `kind: concept` node's `label` matches the `rdfs:label` of its code in `ontology/hitop.ttl` (case-insensitive; `kind: collection` nodes are exempt) — this catches code collisions such as curation typos. Each factorization is checked against the core ontology only, never against other factorizations, because factorizations are authored independently. A synonym belongs in the core as a mapping; a construct with a different meaning is modelled as `kind: collection`.

## Generated factorization ontology

Each hierarchy can be published as a machine-readable factorization ontology.
The generated artifact preserves the version's structure and provenance while
linking every referenced concept back to its stable identity in the HiTOP core
ontology. This makes a factorization independently citable and usable by other
semantic-web tools without creating a second source of truth.

For every regular concept node, the generator additionally copies its `rdfs:label` (and, where present, `rdfs:comment`) from the core ontology into the generated file — purely for readability, so a factorization file is understandable on its own without looking up the IRI in the core. A concept's `rdf:type` and `rdfs:subClassOf` are never duplicated; the core ontology remains the sole source of truth for label and comment. These generated files are never hand-maintained — when the YAML changes, they are regenerated and the old versions replaced.

**Command**

```bash
.venv/bin/python scripts/generate_factorization_ontology.py \
  factorizations/psychosis/v1/V10749_hierarchy.yaml
```

**Output**

```json
{
  "valid": true,
  "input": "factorizations/psychosis/v1/V10749_hierarchy.yaml",
  "output": [
    "factorizations/psychosis/v1/V10749_factorization.rdf"
  ]
}
```

See the [generated ontology](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/factorizations/psychosis/v1/V10749_factorization.rdf) this example produces.

## Diagram data and the central color rule

Each factorization can also be explored as an interactive diagram. The diagram
data is generated from the same reviewed hierarchy as the ontology artifact,
so labels, levels, branches, and provenance remain consistent across the
documentation and downloadable files. The generated data is a presentation
format and is therefore rebuilt from the hierarchy rather than edited by hand.

**Command**

```bash
.venv/bin/python scripts/generate_factorization_diagram_data.py \
  factorizations/psychosis/v1/V10749_hierarchy.yaml
```

**Output**

```json
{
  "valid": true,
  "input": "factorizations/psychosis/v1/V10749_hierarchy.yaml",
  "output": "factorizations/psychosis/v1/V10749_diagram.json"
}
```

See the [generated diagram data](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/factorizations/psychosis/v1/V10749_diagram.json) this example produces.

Color assignment follows a single, factorization-wide rule (`src/hitop/factorization/colors.py`), so every diagram stays visually consistent:

- A fixed 24-color palette (from dark blue to light pink) is spread across every node whose `level` is in `{Factor, Superspectrum, Spectrum, Subfactor}` — each such node gets its own color, drawn directly from the palette.
- The palette is spread in tree order (depth-first, the order the tree is written in the YAML), evenly across the whole palette regardless of how many such nodes a given factorization has. This produces a continuous color gradient along the tree structure, the same way the original HiTOP figures color a whole branch consistently.
- `Component` and `Trait` nodes are not part of the palette. Each instead gets a lightened, slightly desaturated variant of its direct parent's color (HSL: lightness increased per depth step below the nearest palette node, saturation slightly reduced) — nested Component/Trait nodes get progressively lighter with each step.

This rule is deliberately encapsulated in its own module (`hitop.factorization.colors`), importable by both the diagram generator and any future renderer, instead of duplicating the color logic in a renderer. `<version>_diagram.json` is, like the other generated files, never hand-maintained. See the [diagram viewer](diagrams.md) for every factorization rendered live with this rule.
