# Code system

<div class="hitop-page-intro">
  <p>The HiTOP code system separates stable concept identity from optional, locally governed manifestations.</p>
  <span class="hitop-source">Status · Maintained specification</span>
  <span class="hitop-source">Source · <a href="https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/docs/codesystem.md">docs/codesystem.md</a> · <a href="https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/ontology/hitop.rdf">ontology/hitop.rdf</a></span>
</div>

## Canonical structure

```text
SSccXX.M-<TT>-<NS>-<SLUG>
```

| Part | Function |
| --- | --- |
| `SS` | Encodes the hierarchy segment and nesting level |
| `cc` | Provides the local Base62 concept identifier |
| `XX` | Provides the two-character Base62 check component |
| `.M-<TT>-<NS>-<SLUG>` | Optional manifestation suffix |

The stable base identifier is `SSccXX`. A manifestation suffix may extend that identifier without changing the identity of the underlying concept.

## Hierarchy segments

| Segment | Level |
| --- | --- |
| `F` | Factorization |
| `S` | Superspectrum |
| `P` | Spectrum |
| `U` | Subfactor |
| `C` | Component |
| `T` | Trait |

The numeric character following the segment records additional nesting. Level `0` represents the base level; deeper structures increment the value.

## Concept and check components

The local concept component uses two Base62 characters (`0–9`, `A–Z`, and `a–z`), allowing 3,844 values per segment and nesting level. The final two characters are derived from the fixed internal input `HiTOP-<segment>-<concept-code>`. `HiTOP` is not configurable and is not emitted as part of the identifier. The check characters carry no clinical meaning; they make accidental edits and transcription errors easier to detect while keeping identifiers reproducible.

## Manifestations

Manifestations use `<HITOP_BASE_CODE>.M-<TT>-<NS>-<SLUG>`. `TT` is a controlled manifestation type, `NS` isolates the assigning authority, and `SLUG` is its readable local identifier. See the [manifestation suffix specification](manifestation-suffixes.md).

## Machine-readable representation

The canonical machine-readable representation is [`ontology/hitop.rdf`](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/ontology/hitop.rdf). See [Standards alignment](../project/about-the-project.md#standards-alignment) for the maintained overview of RDF, OWL, SKOS, Dublin Core Terms, versioning, licensing, and reproducible validation used by the ontology.

The complete repository specification remains available in [`docs/codesystem.md`](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/docs/codesystem.md).
