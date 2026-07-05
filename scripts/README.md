# HiTOP Suffix Tooling Scripts

This directory contains repository-local entry points for the HiTOP modular
namespaced suffix tooling, ontology conversion, and local release validation.

Run every command from the repository root unless a command explicitly says
otherwise.

## Bootstrap

```bash
scripts/bootstrap_hitop_suffix_tools.sh
```

Creates `.venv` and installs the local package in editable mode with developer
dependencies from `pyproject.toml`.

Inputs:

| Input | Default |
| --- | --- |
| Python interpreter | `python3` on `PATH` |
| Constraints file | `requirements-lock.txt` |
| Package source | repository root |

Outputs:

| Output | Meaning |
| --- | --- |
| `.venv/` | Local virtual environment |
| `.venv/bin/hitop-codegen` | Console entry point for base-code generation |
| `.venv/bin/hitop-suffix` | Console entry point for suffix tooling |

Common failure signals:

| Signal | Likely cause | Resolution |
| --- | --- | --- |
| `python3: command not found` | Python is missing from `PATH` | Install Python 3.10, 3.11, or 3.12 |
| pip dependency resolution error | Constraints and `pyproject.toml` no longer align | Refresh the lock file as a release maintenance task |
| network or index error | Build host cannot reach the Python package index | Retry on an approved network or use the organization's package mirror |

## CLI

```bash
.venv/bin/hitop-suffix --help
```

or:

```bash
.venv/bin/python -m hitop.suffix --help
```

See `../docs/tooling_examples.md` for copyable command line and Python API
examples with expected output.

## Validation

```bash
scripts/validate_hitop_suffix_tooling.sh
```

Compiles the Python sources, runs unit tests from `validation`, and validates
manifestation code examples embedded in documentation files under `docs`.

Inputs:

| Input | Purpose |
| --- | --- |
| `src/` | Import and syntax validation |
| `scripts/` | Import and syntax validation |
| `validation/` | Regression tests |
| `docs/*.md` | Manifestation-code example validation |

Success output includes `OK` from `unittest` and a line similar to
`Validated 24 documentation code example(s).`

Common failure signals:

| Signal | Likely cause | Resolution |
| --- | --- | --- |
| `Missing .venv` | Bootstrap was not run | Run `scripts/bootstrap_hitop_suffix_tools.sh` |
| `SyntaxError` or compile failure | Python source does not parse | Fix the reported file and line |
| test failure | Behavior changed without updated regression coverage | Fix the implementation or update tests intentionally |
| documentation code validation failed | A documented code example is invalid | Correct the example or the parser expectation |

## Ontology Conversion

```bash
.venv/bin/python scripts/rdf2ttl.py --help
.venv/bin/python scripts/rdf2owl.py --help
```

Both scripts default to reading `ontology/hitop.rdf` and writing generated
ontology artifacts under `ontology/`. Pass `--output` to write to a different
location during review or CI checks.

### `rdf2ttl.py`

Purpose: convert RDF/XML to reviewed Turtle while normalizing known source
literal issues.

| Input | Default |
| --- | --- |
| `--input` | `ontology/hitop.rdf` |
| `--output` | `ontology/hitop.ttl` |

Success output reports the loaded RDF/XML triple count, normalization counts,
validated Turtle triple count, and final output path.

Common failure signals:

| Signal | Likely cause | Resolution |
| --- | --- | --- |
| file-not-found error | `--input` path is wrong or the source RDF is not present | Use the canonical `ontology/hitop.rdf` or pass a valid path |
| RDF/XML parse error | Source ontology is malformed | Fix the RDF/XML source before regenerating artifacts |
| Turtle validation error | Formatting or graph serialization produced invalid Turtle | Treat as a release blocker and inspect the converter diff |

### `rdf2owl.py`

Purpose: convert RDF/XML to cleaned OWL/RDF XML for downstream ontology
validation workflows.

| Input | Default |
| --- | --- |
| `--input` | `ontology/hitop.rdf` |
| `--output` | `ontology/hitop.owl` |

Success output reports the loaded triple count, decimal-literal normalization,
ontology-node merge count, cleaned annotation count, restored
`rdfs:isDefinedBy` references, and final output path.

Common failure signals:

| Signal | Likely cause | Resolution |
| --- | --- | --- |
| file-not-found error | `--input` path is wrong or the source RDF is not present | Use the canonical `ontology/hitop.rdf` or pass a valid path |
| RDF/XML parse error | Source ontology is malformed | Fix the RDF/XML source before regenerating artifacts |
| XML serialization error | The graph contains content that cannot be represented in the target XML form | Treat as a release blocker and inspect source triples |

## Generate a Factorization Ontology

```bash
.venv/bin/python scripts/generate_factorization_ontology.py \
  factorizations/working-model/v1/V1052k_hierarchy.yaml
```

Validates a `<version>_hierarchy.yaml` with the same rules as
`validation/test_factorizations.py` (`hitop.factorization.validate`) and
compiles it into an RDF factorization ontology: one `hitop:hasLevelType`
triple per node and one `hitop:hasTier` triple per parent-child edge,
referencing the stable classes in `ontology/hitop.ttl` by IRI. See
`docs/factorizations.md` for the underlying vocabulary.

Inputs:

| Input | Default |
| --- | --- |
| positional `input_yaml` | required `factorizations/<id>/v<N>/<version>_hierarchy.yaml` |
| `--ontology` | `ontology/hitop.ttl` |
| `--output` | `<version>_factorization.ttl` next to the input file |

Outputs:

| Output | Meaning |
| --- | --- |
| `<version>_factorization.ttl` | Generated factorization ontology; not hand-maintained, regenerate after editing the hierarchy YAML |
| JSON stdout | `{ "valid": true, ... }` on success or `{ "valid": false, "errors": [...] }` on validation failure |

Common failure signals:

| Signal | Likely cause | Resolution |
| --- | --- | --- |
| `code '...' does not exist as a class in ontology/hitop.ttl` | A node references a code that was never added to the core ontology, or a typo | Fix the code in the hierarchy YAML or add the class to the core ontology first |
| `level '...' must be strictly below parent level '...'` | A child node's `level` is not narrower than its parent's on the `hitop:hasLevel` ladder | Fix the `level` value or the tree position |
| `code '...' appears more than once in this tree` | The same `code` is used twice within one hierarchy | Remove the duplicate or assign the correct distinct code |

## Generate CSV-Derived Records

```bash
.venv/bin/python scripts/generate_hitop_suffixes_from_csv.py \
  "data/HiTOP DZPG MDS - Tabellenblatt1 2039067e65908120a48cd06c3b2c2d41.csv"
```

Generates full YAML metadata records and a compact CSV review table under
`data/generated`.

Inputs:

| Input | Default |
| --- | --- |
| positional `input_csv` | required source CSV containing at least a `Label` column |
| `--hitop-vocabulary` | `src/data/hitop_base_vocabulary.csv` |
| `--output-yaml` | `data/generated/hitop_dzpg_mds_suffixes.yaml` |
| `--output-csv` | `data/generated/hitop_dzpg_mds_suffixes_review.csv` |
| `--source-url` | empty |
| `--status` | `draft` |
| `--created`, `--modified`, `--version` | release metadata values for generated records |

Outputs:

| Output | Meaning |
| --- | --- |
| YAML records | Full generated metadata records for validation and downstream review |
| CSV review table | Compact table for clinical and technical review |
| JSON stdout | `{ "valid": true, ... }` on success or `{ "valid": false, ... }` on validation failure |

Common failure signals:

| Signal | Likely cause | Resolution |
| --- | --- | --- |
| `Unsupported manifestation type label` | Source CSV has a label outside the configured mapping | Extend the mapping intentionally or fix the source value |
| `Could not resolve HiTOP base code` | Source row lacks a usable base code and vocabulary lookup failed | Add a reviewed vocabulary entry or provide the base code in the CSV |
| `Generated invalid record` | Generated metadata violates suffix validation rules | Treat as a blocker and inspect the reported row |

## Documentation Example Validation

```bash
.venv/bin/python scripts/validate_hitop_suffix_docs.py
```

Scans public Markdown files under `docs/` for manifestation-code examples and
validates them with the package parser. Placeholder examples that use
`<HiTOP>` are normalized to a representative base code before parsing.

Common failure signal: `Documentation code validation failed` followed by the
file path, byte offset, raw code, and validation error list. Fix the documented
example or update the parser only when the specification changed intentionally.
