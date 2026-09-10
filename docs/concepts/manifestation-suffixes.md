# Manifestation suffixes

<div class="hitop-page-intro">
  <p>A modular, namespaced suffix extends a stable HiTOP concept with a manifestation specific to a study, instrument, organization, or dataset.</p>
  <span class="hitop-source">Status · Draft specification</span>
  <span class="hitop-source">Specification version · 0.2.0</span>
  <span class="hitop-source">Source · <a href="https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/docs/modular-namespaced-suffix-schema.md">docs/modular-namespaced-suffix-schema.md</a></span>
</div>

## Purpose

This specification defines a modular suffix format for extending stable HiTOP base codes with manifestation-specific identifiers. It supports decentralized scientific settings in which studies, instruments, institutions, and disciplines encode related manifestations without a central assignment authority.

| Responsibility | Field | Function |
| --- | --- | --- |
| HiTOP concept identity | `<HITOP_BASE_CODE>` | Stable base code from the HiTOP code system |
| Manifestation category | `<TT>` | Controlled manifestation type |
| Local authority space | `<NS>` | Fixed-length namespace token for collision isolation |
| Readable local name | `<SLUG>` | Locally meaningful identifier |

The namespace prevents technical collisions. The slug remains readable. Semantic harmonization is handled through metadata and mappings rather than by encoding the complete meaning in the identifier.

## Scope

This page defines suffix syntax, namespace-token generation, slug normalization, disambiguation, metadata, validation, and mapping boundaries. It does not define the HiTOP base-code format, clinical meanings, a central registry, mapping-review governance, ontology-wide versioning, or mapping algorithms.

Requirements on this page follow the site-wide [documentation conventions](../project/about-the-project.md#documentation-conventions).

## Identifier model

A manifestation identifier combines an existing HiTOP base code with a modular suffix. The base code identifies the shared HiTOP concept; the suffix records the manifestation type, assigning namespace, and readable local identifier without changing that concept identity.

**Canonical syntax**

```text
<HITOP_BASE_CODE>.M-<TT>-<NS>-<SLUG>
```

**Example**

```text
U0aB2X.M-AF-ROR3J2WQSVQFFIKK-CHRONIC_WORRY
```

| Field | Required | Form | Example |
| --- | --- | --- | --- |
| `<HITOP_BASE_CODE>` | Yes | HiTOP base code | `U0aB2X` |
| `M` | Yes | Literal suffix block | `M` |
| `<TT>` | Yes | Manifestation type | `AF` |
| `<NS>` | Yes | Fixed-length namespace token | `ROR3J2WQSVQFFIKK` |
| `<SLUG>` | Yes | Normalized local slug | `CHRONIC_WORRY` |

The identifier MUST be ASCII and MUST NOT contain spaces. Hyphens MUST separate suffix fields. Namespace tokens MUST NOT contain underscores; slugs MAY contain them.

## Manifestation types

`<TT>` MUST be one of these two-character codes:

| Code | Type | Guidance |
| --- | --- | --- |
| `GS` | General symptom | Fallback only; avoid when a specific type is appropriate |
| `CS` | Clinical sign | Observable or externally assessed sign |
| `SY` | Syndrome / cluster | Explicit combination of symptoms |
| `AF` | Affective symptom | Affective or mood-related manifestation |
| `CG` | Cognitive symptom | Cognitive manifestation |
| `PC` | Perceptual symptom | Perception-related manifestation |
| `BH` | Behavioral symptom | Observable behavior |
| `SS` | Somatic symptom | Physical or autonomic manifestation |
| `SL` | Sleep / circadian | Sleep-related or circadian manifestation |
| `SU` | Substance-related | Substance-related manifestation |
| `IR` | Interpersonal / relational | Interpersonal or relational manifestation |
| `IM` | Impairment / functioning | Impairment or level of functioning |

## Namespace token

`<NS>` identifies the local authority space in which a slug is unique. It is a collision-isolation mechanism, not a semantic label. The source authority MUST be retained in metadata.

```text
[A-Z]{3}[A-Z2-7]{13}
```

| Segment | Length | Form | Meaning |
| --- | ---: | --- | --- |
| `<KIND>` | 3 | `[A-Z]{3}` | Namespace-source type |
| `<DIGEST>` | 13 | `[A-Z2-7]{13}` | First 13 characters of a Base32 SHA-256 digest |

The digest uses 65 bits of hash material. The token is exactly 16 characters long.

### Supported source kinds

| Kind | Source | Canonical identifier example |
| --- | --- | --- |
| `HTP` | HiTOP-curated namespace | `hitop:core` |
| `ROR` | ROR organization identifier | `https://ror.org/<id>` |
| `ORC` | ORCID person identifier | `https://orcid.org/<id>` |
| `DOI` | DOI-based study, dataset, instrument, or publication | `https://doi.org/10.1234/example.study.v1` |
| `ARK` | ARK namespace | `ark:/12345/example` |
| `DNS` | Reverse-DNS project or organization namespace | `org.example.project` |
| `SRC` | Stable source string used as fallback | Producer-controlled URI or identifier |

New kind codes MAY be introduced when documented with a stable canonicalization rule.

### Generate a namespace token

Users generate the token by supplying the source kind and stable source identifier to the command-line interface:

**Command**

```bash
.venv/bin/hitop-suffix namespace ROR https://ror.org/00tkfw097
```

**Output**

```json
{
  "canonical_identifier": "https://ror.org/00tkfw097",
  "namespace_token": "ROR3J2WQSVQFFIKK"
}
```

Canonicalization, SHA-256 hashing, RFC 4648 Base32 encoding, and truncation are performed internally; they are not separate user steps. Identical inputs always produce the same token. Technical details are available in [`namespace.py`](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/src/hitop/suffix/namespace.py).

The following tokens are calculated outputs of the implementation, not manually assigned examples:

| Kind | Input | Canonical identifier | Generated namespace token |
| --- | --- | --- | --- |
| `HTP` | `hitop:core` | `hitop:core` | `HTPAJIPZH4KRXKXK` |
| `DOI` | `10.1234/example.study.v1` | `https://doi.org/10.1234/example.study.v1` | `DOICRZ5I6RDFXGS7` |
| `ROR` | `00tkfw097` | `https://ror.org/00tkfw097` | `ROR3J2WQSVQFFIKK` |

Each row can be reproduced by passing its `Kind` and `Input` values to the same command.

## Slug

`<SLUG>` is the readable local name, not a complete definition, and MUST NOT be the sole source of semantics. It MUST contain 3–40 characters and SHOULD contain 12–28:

```text
[A-Z0-9](?:[A-Z0-9_]{1,38}[A-Z0-9])
```

It uses uppercase ASCII letters, digits, and underscores; cannot start or end with an underscore; and cannot contain spaces.

Generate the slug directly with the command-line interface:

**Command**

```bash
.venv/bin/hitop-suffix slug "Chronic worry"
```

**Output**

```json
{
  "slug": "CHRONIC_WORRY"
}
```

| Label | Slug |
| --- | --- |
| Chronic worry | `CHRONIC_WORRY` |
| Panic attack cluster | `PANIC_ATTACK_CLUSTER` |
| Work impairment | `WORK_IMPAIRMENT` |
| Resting palpitations | `RESTING_PALPITATIONS` |
| Rejection sensitivity | `REJECTION_SENSITIVITY` |

Slugs SHOULD be descriptive and compact. Author names, years, versions, opaque abbreviations, and metadata content SHOULD NOT be embedded. Labels over 40 characters SHOULD be shortened manually; automatic truncation MAY be used only if readability remains and collisions are checked.

## Disambiguator

A disambiguator resolves a local collision within the same `<HITOP_BASE_CODE> + M + <TT> + <NS>` tuple. It MUST be used only when distinct manifestations would otherwise receive the same normalized slug. It is technical, not semantic.

```text
<BASE_SLUG>_<DISAMBIGUATOR>
```

| Field | Form | Length |
| --- | --- | ---: |
| `<BASE_SLUG>` | `[A-Z0-9](?:[A-Z0-9_]{1,31}[A-Z0-9])` | 3–33 |
| `<DISAMBIGUATOR>` | `[A-Z2-7]{6}` | Exactly 6 |

The six-character digest uses 30 bits. The final token matching `_[A-Z2-7]{6}` is reserved; a normal slug SHOULD NOT end with that pattern.

Generate the disambiguator directly from stable source metadata:

**Command**

```bash
.venv/bin/hitop-suffix disambiguator \
  --namespace-identifier https://ror.org/00tkfw097 \
  --hitop U0aB2X \
  --manifestation-type AF \
  --study-id study-a \
  --instrument instrument-x \
  --item-id item-17 \
  --base-slug CHRONIC_WORRY
```

**Output**

```json
{
  "basis": "https://ror.org/00tkfw097|u0ab2x|m|af|study-a|instrument-x|item-17",
  "disambiguator": "FPQNQM",
  "slug": "CHRONIC_WORRY_FPQNQM"
}
```

Normalization and hashing are internal implementation details. Inputs MUST be stable source identifiers rather than editable free text. If `source.item_id` is unavailable, another stable identifier MUST be stored as `source.local_concept_id`.

## Required metadata

Every canonical suffix MUST have sufficient metadata to reconstruct the namespace token, interpret the slug, and support mappings.

<a href="../assets/downloads/manifestation-record.template.yaml" download="hitop-manifestation-record-template.yaml">Download the YAML starter template</a>

The starter template distinguishes required, conditional, and optional fields. Replace every `<REPLACE_WITH_…>` placeholder before validation. YAML comments document controlled values, character patterns, and when optional sections should be enabled.

**Minimal metadata example**

```yaml
code: "U0aB2X.M-AF-ROR3J2WQSVQFFIKK-CHRONIC_WORRY"
hitop_base_code: "U0aB2X"
suffix_block: "M"
manifestation_type: "AF"
namespace:
  token: "ROR3J2WQSVQFFIKK"
  kind: "ROR"
  identifier: "https://ror.org/00tkfw097"
slug: "CHRONIC_WORRY"
preferred_label: "Chronic worry"
definition: "Persistent or recurrent worry as operationalized in the source context."
source:
  study_id: "study-a"
  instrument: "instrument-x"
  item_id: "item-17"
  citation: "doi-or-bibliographic-reference"
status: "draft"
created: "2026-09-04"
version: "1"
mappings: []
```

### Metadata field reference

This reference covers every field defined by the current schema. It initially shows mandatory fields; use the filter to inspect conditional, optional, or all fields.

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

| Structure | Field path | Requirement | Function |
| --- | --- | --- | --- |
| Identity | `code` | Mandatory | Complete manifestation code |
| Identity | `hitop_base_code` | Mandatory | Stable six-character HiTOP base code |
| Identity | `suffix_block` | Mandatory | Literal value `M` |
| Identity | `manifestation_type` | Mandatory | Controlled two-character manifestation type |
| Namespace | `namespace.token` | Mandatory | Generated 16-character namespace token |
| Namespace | `namespace.kind` | Mandatory | Three-character namespace-source kind |
| Namespace | `namespace.identifier` | Mandatory | Canonical authority identifier used to generate the token |
| Namespace | `namespace.label` | Optional | Human-readable authority label |
| Namespace | `namespace.acronym` | Optional | Authority acronym or abbreviation |
| Slug | `slug` | Mandatory | Normalized local manifestation slug |
| Slug | `base_slug` | Conditional | Recommended when a disambiguator is appended |
| Slug | `disambiguator` | Conditional | Required for reproducible semantic conformance when the slug is disambiguated |
| Slug | `disambiguation_basis` | Conditional | Required for reproducible semantic conformance when the slug is disambiguated |
| Description | `preferred_label` | Mandatory | Preferred human-readable label |
| Description | `alt_labels` | Optional | Synonyms, local labels, and translations |
| Description | `definition` | Mandatory | Context-specific definition of the manifestation |
| Operationalization | `operationalization.instrument` | Optional | Instrument name or identifier |
| Operationalization | `operationalization.item_id` | Optional | Instrument item identifier |
| Operationalization | `operationalization.item_text` | Optional | Source item text or controlled reference |
| Operationalization | `operationalization.response_scale` | Optional | Response-scale labels or definition |
| Operationalization | `operationalization.time_window` | Optional | Observation or recall period |
| Operationalization | `operationalization.threshold` | Optional | Source-specific cutoff or decision threshold |
| Operationalization | `operationalization.scoring_rule` | Optional | Calculation or interpretation rule |
| Operationalization | `operationalization.scale_type` | Optional | Likert, ordinal, nominal, continuous, binary, or another documented type |
| Operationalization | `operationalization.value_range` | Optional | Permitted range or value-set summary |
| Operationalization | `operationalization.selection_type` | Optional | Single-choice, multiple-choice, or another selection behavior |
| Operationalization | `operationalization.data_type` | Optional | Data type of the recorded response |
| Population | `population.description` | Optional | Target population or sampling context |
| Population | `population.age_range` | Optional | Applicable age range |
| Population | `population.setting` | Optional | Clinical, community, research, or other setting |
| Source | `source.study_id` | Mandatory | Stable study or dataset identifier |
| Source | `source.instrument` | Mandatory | Originating instrument name or identifier |
| Source | `source.item_id` | Conditional | One of `item_id` or `local_concept_id` is mandatory |
| Source | `source.local_concept_id` | Conditional | Alternative stable identity when `item_id` is absent |
| Source | `source.citation` | Optional | DOI or bibliographic reference |
| Source | `source.source_url` | Optional | Resolvable source or specification URL |
| Source | `source.input_row_number` | Optional | Positive source-row number retained during conversion |
| Source | `source.input_hitop_concept_label` | Optional | Original concept label received as input |
| Source | `source.input_hitop_concept_url` | Optional | Original concept URL received as input |
| Source | `source.hitop_base_code_resolution` | Optional | Recorded method or outcome of base-code resolution |
| Lifecycle | `status` | Mandatory | Record lifecycle status |
| Lifecycle | `created` | Mandatory | ISO 8601 creation date |
| Lifecycle | `modified` | Optional | ISO 8601 last-modification date |
| Lifecycle | `version` | Mandatory | Record version string |
| Lifecycle | `replaces` | Optional | Previous codes replaced by this record |
| Lifecycle | `replaced_by` | Optional | Successor codes replacing this record |
| Mapping | `mapping_review_status` | Optional | Mapping review state |
| Mapping | `mappings` | Optional | Mapping relation entries |
| Mapping | `mappings[].target_code` | Conditional | Mandatory for each mapping entry |
| Mapping | `mappings[].relation` | Conditional | Mandatory SKOS relation for each mapping entry |
| Mapping | `mappings[].mapping_artifact` | Optional | Review artifact or specification reference |
| Provenance | `provenance.created_by` | Optional | Creating person or system identifier |
| Provenance | `provenance.created_at` | Optional | ISO 8601 provenance creation date |
| Provenance | `provenance.reviewed_by` | Optional | Reviewer identifiers |
| Provenance | `provenance.review_status` | Optional | Review state |
| Provenance | `provenance.decision_note` | Optional | Human-readable decision rationale |
| Extension | `x_<name>` | Optional | Producer-specific top-level value where no core field exists |

</div>

Extension names MUST match `^x_[A-Za-z0-9_]+$`. They SHOULD NOT duplicate a core field. Consumers MUST preserve and tolerate unknown `x_*` fields rather than reject the record. The authoritative definitions are maintained in [`schema/manifestation-record.schema.json`](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/schema/manifestation-record.schema.json).

## Validation

The repository provides an executable metadata validator through the `hitop-suffix` CLI.

**Command**

```bash
.venv/bin/hitop-suffix validate-metadata \
  path/to/completed-manifestation-record.yaml
```

**Output**

```json
{
  "errors": [],
  "valid": true,
  "warnings": []
}
```

### Syntax validation

A suffix is syntactically valid when the base code is present, the block is literal `M`, the type is allowed, namespace and slug match their patterns, and the slug contains 3–40 characters.

```text
^M-(GS|CS|SY|AF|CG|PC|BH|SS|SL|SU|IR|IM)-[A-Z]{3}[A-Z2-7]{13}-[A-Z0-9](?:[A-Z0-9_]{1,38}[A-Z0-9])$
```

Explicitly disambiguated suffixes:

```text
^M-(GS|CS|SY|AF|CG|PC|BH|SS|SL|SU|IR|IM)-[A-Z]{3}[A-Z2-7]{13}-[A-Z0-9](?:[A-Z0-9_]{1,31}[A-Z0-9])_[A-Z2-7]{6}$
```

### Semantic validation

A code is semantically valid when its HiTOP base code exists, its namespace token matches its metadata, its slug is unique within `<HITOP_BASE_CODE> + M + <TT> + <NS>`, disambiguated slugs include their basis and digest, and definition and source metadata are present.

### Validator behavior

Validators SHOULD report separate errors for invalid types, namespace length or alphabet, namespace/metadata mismatch, slug alphabet or length, leading or trailing underscores, duplicate codes, unresolved local collisions, and missing metadata. Validators MUST NOT silently rewrite published codes; normalized suggestions MAY be warnings.

## Examples

The HiTOP base codes below are illustrative.

| Use case | Example |
| --- | --- |
| HiTOP-curated namespace | `U0aB2X.M-AF-HTPAJIPZH4KRXKXK-CHRONIC_WORRY` |
| Organization namespace via ROR | `U0aB2X.M-SS-RORPLACEHOLDERAB-RESTING_PALPITATIONS` |
| Study or dataset namespace via DOI | `C1mQ8Z.M-CG-DOICRZ5I6RDFXGS7-ATTENTION_LAPSE` |
| Person namespace via ORCID | `C0bF4K.M-IR-ORCPLACEHOLDERAB-REJECTION_SENSITIVITY` |
| Project namespace via reverse DNS | `T0cR7M.M-BH-DNSPLACEHOLDERAB-AVOIDANCE_BEHAVIOR` |

The same slug in different namespaces does not collide:

```text
U0aB2X.M-AF-RORPLACEHOLDERAB-CHRONIC_WORRY
U0aB2X.M-AF-ROROTHERTOKENABC-CHRONIC_WORRY
```

The same slug in the same namespace requires disambiguation:

```text
U0aB2X.M-AF-RORPLACEHOLDERAB-CHRONIC_WORRY
U0aB2X.M-AF-RORPLACEHOLDERAB-CHRONIC_WORRY_2UVNQO
```

Whether manifestations are equivalent, broader, narrower, or related must be expressed through mappings.

## Mapping and harmonization

Decentralized assignment prevents technical collisions but cannot eliminate semantic redundancy. Codes MUST remain stable when mappings are added. Mappings MUST be published outside the identifier as versioned artifacts. A slug MUST NOT be the sole basis for equivalence. Implementations SHOULD provide mappings through FHIR `ConceptMap`, SKOS/RDF, or tabular review exports. See [Mapping & harmonization](mapping-harmonization.md) for candidate generation, scoring, relations, review levels, and publication formats.

## Lifecycle

Published codes MUST NOT be semantically redefined. A meaning change requires a new code.

| Status | Meaning |
| --- | --- |
| `active` | Valid for use |
| `deprecated` | No longer recommended but historically valid |
| `replaced` | Superseded by another code |
| `draft` | Not yet stable |

```yaml
status: "replaced"
replaced_by: "U0aB2X.M-AF-RORPLACEHOLDERAB-EXCESSIVE_WORRY"
change_reason: "Label and operationalization harmonized with source instrument."
```

## Implementation checklist

Producers SHOULD:

1. select the HiTOP base code and manifestation type;
2. select an appropriate stable namespace-source identifier;
3. generate the fixed-length namespace token;
4. generate a base slug from a stable label;
5. check uniqueness within `<HITOP_BASE_CODE> + M + <TT> + <NS>`;
6. append a disambiguator only for a local collision;
7. publish the required metadata with the code;
8. publish mappings for known equivalent or related manifestations; and
9. never rewrite published codes in place.

Consumers SHOULD:

1. parse the code syntactically;
2. validate namespace metadata when available;
3. treat the slug only as a label cue;
4. use mappings and definitions for semantic harmonization; and
5. preserve unknown namespace tokens rather than discard them.

## Design rationale

- **Fixed namespace length:** the namespace is a machine-oriented collision boundary. Fixed length reduces parser complexity and discourages unstable semantic content.
- **Variable slug length:** the human-readable component needs bounded flexibility. Three to 40 characters avoids padding and opaque truncation; 12–28 is the practical target.
- **Fixed disambiguator:** six Base32 characters provide 30 bits for the smaller collision space in which base code, suffix block, type, namespace, and base slug already match.

## References and analogous patterns

| Area | Pattern | Reference |
| --- | --- | --- |
| URI syntax | ASCII-safe identifiers and reserved delimiters | [RFC 3986](https://www.ietf.org/rfc/rfc3986) |
| Base32 | Uppercase alphabet `A-Z2-7` | [RFC 4648](https://www.rfc-editor.org/rfc/rfc4648) |
| CURIEs | Prefix plus local reference | [W3C CURIE Syntax](https://www.w3.org/TR/curie/) |
| Ontology identifiers | IDSPACE, LOCALID, and PURL mapping | [OBO Foundry Identifier Policy](https://obofoundry.org/id-policy.html) |
| FHIR terminology | CodeSystem URI and ConceptMap | [HL7 FHIR CodeSystem](https://hl7.org/fhir/codesystem.html) |
| Semantic mappings | Relations between concept schemes | [W3C SKOS Reference](https://www.w3.org/TR/skos-reference/) |
| Authority namespaces | Isolated local identifiers | [RFC 8141 – Uniform Resource Names](https://www.rfc-editor.org/rfc/rfc8141) |
| Persistent identifiers | Stable DOI prefix and suffix | [DataCite DOI basics](https://support.datacite.org/docs/doi-basics) |
| Organization identifiers | Persistent organizational IDs | [ROR](https://ror.org/) |
| Researcher identifiers | Persistent person IDs | [ORCID](https://orcid.org/) |
| Software namespaces | Reverse-DNS collision avoidance | [Maven naming conventions](https://maven.apache.org/guides/mini/guide-naming-conventions.html) |
| Object metadata | DNS prefix and local name | [Kubernetes labels](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/) |
| Slugs | URL-safe labels | [Django SlugField](https://docs.djangoproject.com/en/stable/ref/models/fields/#slugfield) |
| Slug normalization | Transliteration and separators | [Rails `parameterize`](https://api.rubyonrails.org/classes/ActiveSupport/Inflector.html) |

The repository source specification is retained in [`docs/modular-namespaced-suffix-schema.md`](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/docs/modular-namespaced-suffix-schema.md).
