# Core vocabulary

<div class="hitop-page-intro">
  <p>The HiTOP base vocabulary brings together all concepts represented in the HiTOP Working Model and in the Emotional Dysfunction, Externalizing, and Psychosis superspectra.</p>
  <span class="hitop-source">Status · Maintained data artifact</span>
  <span class="hitop-source">Coverage · Working Model · Emotional Dysfunction · Externalizing · Psychosis</span>
</div>

## Purpose

The [HiTOP base vocabulary](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/src/data/hitop_base_vocabulary.csv) is the consolidated inventory of concepts represented in the HiTOP Working Model and in three published superspectrum structures. For each superspectrum, the vocabulary includes the superspectrum itself and every concept arranged beneath it in the corresponding structure.

The resulting inventory gives these concepts stable identifiers under one consistent segment, local-code, and check-digit scheme. The canonical [`ontology/hitop.rdf`](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/ontology/hitop.rdf) uses those identifiers to represent the concepts as machine-readable ontology classes; it is an implementation of the vocabulary, not an additional source of concepts for it.

## Concept sources

| Model or superspectrum | Included concept scope | Dataset | Scientific source |
| --- | --- | --- | --- |
| HiTOP Working Model | All concepts represented in the current working model | [`V1052k`](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/factorizations/working-model/v1/V1052k_hierarchy.yaml) | [Current HiTOP model](https://www.hitop-system.org/current-model) |
| Emotional Dysfunction | The superspectrum and all concepts arranged beneath it | [`V106mv`](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/factorizations/emotional-dysfunction/v1/V106mv_hierarchy.yaml) | [Kotov et al. (2021), *World Psychiatry*](https://onlinelibrary.wiley.com/doi/10.1002/wps.20943) |
| Externalizing | The superspectrum and all concepts arranged beneath it | [`V108kx`](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/factorizations/externalizing/v1/V108kx_hierarchy.yaml) | [Kotov et al. (2021), *World Psychiatry*](https://onlinelibrary.wiley.com/doi/10.1002/wps.20844) |
| Psychosis | The superspectrum and all concepts arranged beneath it | [`V10749`](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/factorizations/psychosis/v1/V10749_hierarchy.yaml) | [Kotov et al. (2020), *World Psychiatry*](https://onlinelibrary.wiley.com/doi/10.1002/wps.20730) |

## Canonical artifact

The maintained data artifact is [`src/data/hitop_base_vocabulary.csv`](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/src/data/hitop_base_vocabulary.csv). Generation and validation tools use it as the repository-local source for resolving and checking stable HiTOP base identifiers.

## Columns

| Column | Meaning |
| --- | --- |
| `Code` | Local alphanumeric concept code without segment or check digits |
| `Label` | Preferred HiTOP concept label |
| `Segment` | Hierarchy segment, for example `F`, `S`, `P`, `U`, `C`, or `T` |
| `Segment Level` | Numeric nesting level within the segment |
| `CheckDigit` | Two-character Base62 check component |
| `HiTOP` | Canonical base identifier, for example `C001qy` |

## Rebuild and validation

From the repository root:

**Command**

```bash
.venv/bin/hitop-codegen \
  src/data/hitop_base_vocabulary.csv \
  /tmp/hitop_base_vocabulary.csv
```

**Output**

```text
Generated 162 HiTOP code(s): /tmp/hitop_base_vocabulary.csv
```

The rebuild must reproduce all existing check digits without changing established identifiers. Run the focused tooling check with:

**Command**

```bash
scripts/validate_hitop_suffix_tooling.sh
```

**Output**

```text
Checking Python syntax and imports... PASS
Checking regression tests (approved label exception excluded)... PASS
Approved exceptions: 1 cross-file label-consistency check (clinical review pending)
Checking documentation code examples... PASS
Validation completed successfully.
```

The approved exception is reported explicitly and follows the same temporary
policy as CI. Set `ALLOW_KNOWN_LABEL_INCONSISTENCIES=false` to include that
check and require a fully clean clinical label-consistency result.
