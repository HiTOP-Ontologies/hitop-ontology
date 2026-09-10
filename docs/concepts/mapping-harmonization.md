# Mapping & harmonization

<div class="hitop-page-intro">
  <p>Versioned mapping artifacts make relationships between decentralized HiTOP manifestations explicit, reviewable, and reproducible.</p>
  <span class="hitop-source">Status · Maintained specification</span>
  <span class="hitop-source">Specification version · 1.0.0</span>
  <span class="hitop-source">Source · <a href="https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/docs/mapping-und-harmonisierung.md">docs/mapping-und-harmonisierung.md</a></span>
</div>

## Purpose

Namespaces prevent technical collisions, but different studies or organizations may still represent similar manifestations under different local slugs. Harmonization therefore uses explicit mappings instead of renaming published identifiers. This specification extends the [manifestation suffix schema](manifestation-suffixes.md) with a mapping and review method; it does not change suffix syntax.

## Scope

This page defines a mapping data model, relation types and decision criteria, candidate generation and scoring, review levels, conflict handling, and publication formats. It does not define the clinical truth of a mapping, automatic approval without expert review, a central governance body, or a mandatory software implementation.

Requirements on this page follow the site-wide [documentation conventions](../project/about-the-project.md#documentation-conventions).

## Principles

1. A mapping is an independent statement with provenance, status, and review level.
2. It never changes its source or target identifier.
3. A published code is never semantically redefined because of a mapping.
4. Automated methods may propose candidates but cannot replace expert review.
5. Mapping relations MUST be directed, justified, and versioned.
6. Decisions consider definitions, operationalization, evidence, context, and hierarchy—not labels alone.
7. Uncertainty and disagreement remain explicit.

## Mapping artifact

A mapping artifact describes a directed relationship between a source code and a target code, together with its relation, confidence, review state, and provenance.

```yaml
mapping_id: "map-2026-000001"
source:
  system: "http://purl.org/hitop"
  code: "U0aB2X.M-AF-ROR3J2WQSVQFFIKK-CHRONIC_WORRY"
target:
  system: "http://purl.org/hitop"
  code: "U0aB2X.M-AF-RORYLBKANYXUGB6O-EXCESSIVE_WORRY"
relation:
  skos: "skos:closeMatch"
  fhir: "related-to"
confidence:
  score: 0.82
  band: "high"
review:
  status: "curated"
  level: 3
  reviewer: "curation-board-or-person-id"
  date: "2026-05-31"
status: "active"
```

A complete artifact also carries `evidence` (the feature-level similarity values behind the score) and `provenance` (creator, creation date, and the source and target record versions). See the full [mapping artifact structure](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/docs/mapping-und-harmonisierung.md#4-mapping-artefakt).

## Relations

Mappings use directed [SKOS](https://www.w3.org/TR/skos-reference/) relations, or `noMap` where no candidate is valid.

| Relation | Meaning | Use |
| --- | --- | --- |
| `skos:exactMatch` | Same meaning in a broad application context | Only with very high definitional and operational agreement |
| `skos:closeMatch` | Very similar but not fully interchangeable | Default relation for a high but imperfect match |
| `skos:broadMatch` | Target is broader than source | Source is more specific |
| `skos:narrowMatch` | Target is narrower than source | Source is more general |
| `skos:relatedMatch` | Related in subject matter, without hierarchy or equivalence | Associative relationship |
| `noMap` | No valid mapping | Candidate was reviewed and rejected |

`skos:exactMatch` MUST NOT be assigned when the two manifestations differ in severity threshold, in a clinically relevant time window, in syndrome-versus-single-symptom granularity, in scale-versus-clinical-manifestation type, or in a population or context that changes meaning.

## Candidate generation and scoring

Candidate generation MAY combine several sources: shared HiTOP base code, shared manifestation type, an identical normalized slug, label and synonym comparison, definition comparison, operationalization comparison, hierarchy context, external terminologies (SNOMED CT, LOINC, ICD, UMLS, OMOP), and existing curated mappings.

A fixed feature vector produces a `0`–`1` score used only to prioritize review; it does not establish semantic equivalence, and normative data products still rely on the curated review status.

| Score | Band | Recommended handling |
| --- | --- | --- |
| ≥ 0.90 | `very_high` | Priority review for `exactMatch` or `closeMatch` |
| 0.75–0.89 | `high` | Review for `closeMatch`, `broadMatch`, or `narrowMatch` |
| 0.50–0.74 | `medium` | Manual review, no automatic relation |
| < 0.50 | `low` | Not prioritized unless a domain reason exists |

Scores MUST NOT silently override an existing curated decision; a changed source or target record only returns a mapping to review. Automatically generated candidates stay marked `machine_suggested` or `unreviewed` until approved. The feature weights and bands above are score model `mapping-score-v1`; changing them requires a new, separately versioned model.

The repository provides an executable scorer through the `hitop-suffix` CLI:

**Command**

```bash
.venv/bin/hitop-suffix mapping-score \
  source-record.yaml target-record.yaml \
  --hierarchy-similarity 0.5
```

**Output**

```json
{
  "band": "medium",
  "features": {
    "base_code_match": 1.0,
    "context_penalty": 0.0,
    "definition_similarity": 0.82,
    "external_mapping_support": 0.0,
    "hierarchy_similarity": 0.5,
    "label_similarity": 0.33,
    "manifestation_type_match": 1.0,
    "operationalization_similarity": 0.75,
    "slug_similarity": 0.57
  },
  "proposed_relation": "skos:relatedMatch",
  "score": 0.71
}
```

`source-record.yaml` and `target-record.yaml` are two [manifestation metadata records](manifestation-suffixes.md#required-metadata). The scorer proposes a relation for review; it does not publish a mapping.

## Review levels

Mappings SHOULD be published with a review level.

| Level | Status | Meaning |
| --- | --- | --- |
| 0 | `unreviewed` | Automatically generated candidate, not approved |
| 1 | `machine_suggested` | Algorithmic proposal with score and evidence |
| 2 | `single_reviewed` | Checked by one qualified person |
| 3 | `curated` | Approved by at least two people or a board |
| 4 | `endorsed` | Formally approved by a responsible authority |

Only level 3 or 4 SHOULD be used for normative data products. Conflicting, superseded, and rejected decisions remain available for auditability.

## Conflict handling

Conflicts arise when several target codes are candidates for the same source, or when existing mappings contradict each other.

1. Multiple `exactMatch` targets for one source MUST be justified.
2. Transitive chains of `exactMatch` SHOULD be checked for contradictions.
3. `closeMatch` SHOULD NOT be treated as transitive.
4. Where relations conflict, the higher review level is preferred.
5. At equal review level, the more recent decision is not automatically preferred; provenance decides.

## Publication

Mappings may be published as tabular review exports, SKOS/RDF statements, or FHIR `ConceptMap` resources. Every format should retain the relation, confidence, review status, provenance, and source and target versions.

**Tabular export**

```text
source_code,target_code,relation,score,review_level,status,created,source_version,target_version
```

**SKOS/RDF**

```turtle
<http://purl.org/hitop#U0aB2X.M-AF-ROR3J2WQSVQFFIKK-CHRONIC_WORRY>
  skos:closeMatch
    <http://purl.org/hitop#U0aB2X.M-AF-RORYLBKANYXUGB6O-EXCESSIVE_WORRY> .
```

**FHIR `ConceptMap`**

```json
{
  "resourceType": "ConceptMap",
  "status": "draft",
  "group": [
    {
      "source": "http://purl.org/hitop",
      "target": "http://purl.org/hitop",
      "element": [
        {
          "code": "U0aB2X.M-AF-ROR3J2WQSVQFFIKK-CHRONIC_WORRY",
          "target": [
            {
              "code": "U0aB2X.M-AF-RORYLBKANYXUGB6O-EXCESSIVE_WORRY",
              "relationship": "related-to"
            }
          ]
        }
      ]
    }
  ]
}
```

## Recommended workflow

1. The suffix schema defines only stable identifiers.
2. Mapping and harmonization are maintained in a separate mapping artifact.
3. Automated algorithms generate candidates and scores.
4. Domain reviewers decide the relation and status.
5. Normative data products use only curated mappings.
6. FHIR `ConceptMap` and SKOS/RDF are the primary publication formats.
7. Tabular exports support review and data-pipeline processes.

## References

| Area | Relevance for HiTOP | Reference |
| --- | --- | --- |
| HL7 FHIR ConceptMap | Suffixes stay stable; harmonization is published as a separate, directed `ConceptMap` | [FHIR ConceptMap](https://hl7.org/fhir/R5/conceptmap.html) |
| SKOS mapping properties | `closeMatch` is the safe default for similar but not fully interchangeable manifestations | [W3C SKOS Reference](https://www.w3.org/TR/skos-reference/) |
| OHDSI / OMOP | Automated matching tools produce candidate lists; they do not publish final mappings without review | [OHDSI Vocabulary](https://ohdsi.github.io/CommonDataModel/vocabulary.html) |
| UMLS Metathesaurus | Local codes and slugs stay source-near; harmonization runs through explicit concept relations | [UMLS Metathesaurus](https://www.nlm.nih.gov/research/umls/new_users/online_learning/Meta_005.html) |
| BioPortal / OntoPortal | Mapping artifacts are versioned and published separately from code syntax | [BioPortal Mappings](https://www.bioontology.org/wiki/BioPortal_Mappings) |

The complete methodological specification, including scoring, exclusions, conflict handling, and publication examples, is maintained in [`docs/mapping-und-harmonisierung.md`](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/docs/mapping-und-harmonisierung.md).
