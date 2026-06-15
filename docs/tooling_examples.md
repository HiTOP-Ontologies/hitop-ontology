# HiTOP Tooling Examples

This document contains copyable examples for the installed console entry points
and the public Python API. Run commands from the repository root after local
setup:

```bash
scripts/bootstrap_hitop_suffix_tools.sh
```

## `hitop-codegen`

Generate checksum and local HiTOP code columns for the base vocabulary without
modifying the source file:

```bash
.venv/bin/hitop-codegen \
  src/data/hitop_base_vocabulary.csv \
  /tmp/hitop_base_vocabulary.generated.csv
```

The command is quiet on success. Inspect the first generated rows:

```bash
sed -n '1,5p' /tmp/hitop_base_vocabulary.generated.csv
```

Expected output:

```csv
Code;Label;Segment;Segment Level;CheckDigit;HiTOP
01;Conversion;C;0;qy;C001qy
02;Somatization;C;0;17;C00217
03;Malaise;C;0;3z;C0033z
04;Head Pain;C;0;16;C00416
```

Use an explicit prefix when validating a non-default code system:

```bash
.venv/bin/hitop-codegen \
  src/data/hitop_base_vocabulary.csv \
  /tmp/hitop_base_vocabulary.mds.csv \
  --prefix MDS
```

The generated `HiTOP` column intentionally remains the local code stem plus
checksum. The prefix is part of checksum input, not part of that output column.

## `hitop-suffix`

Generate the DZPG ROR namespace token:

```bash
.venv/bin/hitop-suffix namespace ROR https://ror.org/00tkfw097
```

Expected output:

```json
{
  "canonical_identifier": "https://ror.org/00tkfw097",
  "namespace_token": "ROR3J2WQSVQFFIKK"
}
```

Normalize a label into a manifestation slug:

```bash
.venv/bin/hitop-suffix slug "Chronic worry"
```

Expected output:

```json
{
  "slug": "CHRONIC_WORRY"
}
```

Build a full manifestation code:

```bash
.venv/bin/hitop-suffix build-code \
  --hitop HiTOPU0aB2X \
  --manifestation-type AF \
  --namespace-token ROR3J2WQSVQFFIKK \
  --slug CHRONIC_WORRY
```

Expected output:

```json
{
  "code": "HiTOPU0aB2X.M-AF-ROR3J2WQSVQFFIKK-CHRONIC_WORRY"
}
```

Validate a full manifestation code:

```bash
.venv/bin/hitop-suffix validate-code \
  HiTOPU0aB2X.M-AF-ROR3J2WQSVQFFIKK-CHRONIC_WORRY
```

Expected output:

```json
{
  "errors": [],
  "valid": true
}
```

Inspect validation failure output without stopping an interactive shell:

```bash
.venv/bin/hitop-suffix validate-code HiTOPU0aB2X.M-AF-CHRONIC_WORRY || true
```

Expected output and exit status: JSON with `valid: false`; command exit status
is `1`.

```json
{
  "errors": [
    "Invalid manifestation code: 'HiTOPU0aB2X.M-AF-CHRONIC_WORRY'."
  ],
  "valid": false
}
```

Generate deterministic disambiguation metadata for a local slug collision:

```bash
.venv/bin/hitop-suffix disambiguator \
  --namespace-identifier https://ror.org/00tkfw097 \
  --hitop HiTOPU0aB2X \
  --manifestation-type AF \
  --study-id study-a \
  --instrument instrument-x \
  --item-id item-17 \
  --base-slug CHRONIC_WORRY
```

Expected output:

```json
{
  "basis": "https://ror.org/00tkfw097|hitopu0ab2x|m|af|study-a|instrument-x|item-17",
  "disambiguator": "YBNIBQ",
  "slug": "CHRONIC_WORRY_YBNIBQ"
}
```

## Python API

Generate a base-code checksum from a CSV-like row:

```python
from hitop.base.hitop import build_hitop_code

row = {"Segment": "C", "Segment Level": "0", "Code": "01"}
check_digit, local_code = build_hitop_code(row, prefix="HiTOP", row_number=2)

print(check_digit)
print(local_code)
```

Expected output:

```text
qy
C001qy
```

Build a manifestation suffix code using the public suffix API:

```python
from hitop.suffix import build_code, generate_namespace_token, slugify

namespace = generate_namespace_token("ROR", "https://ror.org/00tkfw097")
slug = slugify("Chronic worry")

print(
    build_code(
        hitop_base_code="HiTOPU0aB2X",
        manifestation_type="AF",
        namespace_token=namespace,
        slug=slug,
    )
)
```

Expected output:

```text
HiTOPU0aB2X.M-AF-ROR3J2WQSVQFFIKK-CHRONIC_WORRY
```

Parse and inspect a manifestation code:

```python
from hitop.suffix import parse_code

parsed = parse_code("HiTOPU0aB2X.M-AF-ROR3J2WQSVQFFIKK-CHRONIC_WORRY")

print(parsed.hitop_base_code)
print(parsed.manifestation_type)
print(parsed.namespace_token)
print(parsed.slug)
```

Expected output:

```text
HiTOPU0aB2X
AF
ROR3J2WQSVQFFIKK
CHRONIC_WORRY
```

## Release Gate Examples

Run the local quality gate:

```bash
scripts/validate_hitop_suffix_tooling.sh
```

Expected success signals:

```text
Ran 18 tests
OK
Validated 24 documentation code example(s).
```

Run ontology conversion gates without modifying repository artifacts:

```bash
.venv/bin/python scripts/rdf2ttl.py --output /tmp/hitop_release_gate.ttl
.venv/bin/python scripts/rdf2owl.py --output /tmp/hitop_release_gate.owl
```

Expected success signals include `Validated 1046 Turtle triples` for the Turtle
gate and `Wrote /tmp/hitop_release_gate.owl` for the OWL/RDF XML gate.
