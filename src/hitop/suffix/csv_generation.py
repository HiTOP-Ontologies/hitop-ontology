"""CSV-to-metadata generation for HiTOP manifestation suffix records.

The module transforms tabular source material into structured metadata records
that follow ``docs/modular-namespaced-suffix-schema.md``. It is intentionally
conservative: source values are preserved in metadata, generated fields are
marked with their derivation method, and missing HiTOP base codes are resolved
only from an explicit local vocabulary file.
"""

from __future__ import annotations

import csv
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .code import build_code
from .constants import MANIFESTATION_TYPES
from .disambiguator import attach_disambiguator, build_disambiguation_basis
from .exceptions import HiTOPSuffixError
from .metadata import validate_metadata
from .namespace import generate_namespace_token
from .slug import slugify

MANIFESTATION_TYPE_LABELS: dict[str, str] = {
    "General symptom": "GS",
    "Clinical sign": "CS",
    "Syndrome / Cluster": "SY",
    "Syndrome / cluster": "SY",
    "Affective symptom": "AF",
    "Cognitive symptom": "CG",
    "Perceptual symptom": "PC",
    "Behavioral symptom": "BH",
    "Somatic symptom": "SS",
    "Sleep / circadian": "SL",
    "Substance-related": "SU",
    "Interpersonal / relational": "IR",
    "Impairment / functioning": "IM",
}

DEFAULT_DZPG_ROR_IDENTIFIER = "https://ror.org/00tkfw097"
DEFAULT_DZPG_NAMESPACE_TOKEN = "ROR3J2WQSVQFFIKK"
DEFAULT_MODULE_ID = "psychische-gesundheit-basiserfassung"
DEFAULT_INSTRUMENT = "DZPG MDS Psychische Gesundheit Basiserfassung"


@dataclass(frozen=True, slots=True)
class GenerationConfig:
    """Configuration for CSV-to-suffix generation."""

    namespace_kind: str = "ROR"
    namespace_identifier: str = DEFAULT_DZPG_ROR_IDENTIFIER
    namespace_label: str = "Deutsches Zentrum fuer Psychische Gesundheit"
    namespace_acronym: str = "DZPG"
    study_id: str = DEFAULT_MODULE_ID
    instrument: str = DEFAULT_INSTRUMENT
    source_url: str = ""
    status: str = "draft"
    version: str = "1"
    created: str = "2026-05-31"
    modified: str = "2026-05-31"
    slug_source_column: str = "Label"
    hitop_base_code_column: str = "Slug"
    label_column: str = "Label"
    manifestation_type_column: str = "Manifestationstyp"
    hitop_concept_column: str = "HiTOP Codes Einzelitems"


def sniff_csv_dialect(path: Path) -> csv.Dialect[str]:
    """Detect the CSV dialect used by a source file."""

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        sample = handle.read(8192)
    return csv.Sniffer().sniff(sample, delimiters=",;\t")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read CSV rows as dictionaries with UTF-8 BOM handling."""

    dialect = sniff_csv_dialect(path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, dialect=dialect))


def extract_concept_label_and_url(value: str) -> tuple[str, str]:
    """Extract ``Concept label`` and optional URL from a Notion-like cell."""

    text = value.strip()
    match = re.match(r"^(?P<label>.*?)\s*\((?P<url>https?://.+?)\)\s*$", text)
    if match:
        return match.group("label").strip(), match.group("url").strip()
    return text, ""


def load_hitop_vocabulary(path: Path) -> dict[str, str]:
    """Load a semicolon-delimited HiTOP vocabulary CSV as label-to-code mapping."""

    mapping: dict[str, str] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        for row in reader:
            label = row.get("Label", "").strip()
            code = row.get("HiTOP", "").strip()
            if not label or not code:
                continue
            mapping[label.lower()] = code if code.startswith("HiTOP") else f"HiTOP{code}"
    return mapping


def detect_item_text_column(fieldnames: Iterable[str]) -> str | None:
    """Return the likely item text column from the source CSV header."""

    known_columns = {
        "Checkbox",
        "?",
        "Label",
        "Segment",
        "HiTOP Spectrum",
        "HiTOP Codes Faktorebene",
        "HiTOP Codes Einzelitems",
        "Manifestationstyp",
        "Slug",
        "_P_Factor",
        "Property",
        "Status",
    }
    for fieldname in fieldnames:
        stripped = fieldname.strip()
        if stripped.endswith("?") and fieldname not in known_columns:
            return fieldname
    return None


def resolve_manifestation_type(label: str) -> str:
    """Map a source manifestation type label to the two-letter schema code."""

    if label in MANIFESTATION_TYPES:
        return label
    if label in MANIFESTATION_TYPE_LABELS:
        return MANIFESTATION_TYPE_LABELS[label]
    raise HiTOPSuffixError(f"Unsupported manifestation type label: {label!r}.")


def resolve_hitop_base_code(
    row: dict[str, str],
    *,
    config: GenerationConfig,
    vocabulary: dict[str, str],
) -> tuple[str, str, str, str]:
    """Resolve the HiTOP base code for a CSV row.

    Returns
    -------
    tuple
        ``(base_code, resolution_source, concept_label, concept_url)``.
    """

    provided = row.get(config.hitop_base_code_column, "").strip()
    concept_label, concept_url = extract_concept_label_and_url(
        row.get(config.hitop_concept_column, "")
    )
    if provided:
        return provided, "csv_column", concept_label, concept_url

    resolved = vocabulary.get(concept_label.lower())
    if resolved:
        return resolved, "hitop_vocabulary_lookup", concept_label, concept_url

    raise HiTOPSuffixError(
        "Could not resolve HiTOP base code for "
        f"{row.get(config.label_column, '<unknown>')!r} / {concept_label!r}."
    )


def _build_disambiguation_basis_for_row(
    row: dict[str, str],
    *,
    config: GenerationConfig,
    hitop_base_code: str,
    manifestation_type: str,
) -> str:
    """Build the stable disambiguation basis for one source CSV row."""

    item_id = row.get(config.label_column, "").strip()
    return build_disambiguation_basis(
        namespace_identifier=config.namespace_identifier,
        hitop_base_code=hitop_base_code,
        manifestation_type=manifestation_type,
        study_id=config.study_id,
        instrument=config.instrument,
        item_id_or_local_concept_id=item_id,
    )


def generate_records(
    rows: list[dict[str, str]],
    *,
    config: GenerationConfig,
    vocabulary: dict[str, str],
) -> list[dict[str, Any]]:
    """Generate validated metadata records from CSV rows."""

    namespace_token = generate_namespace_token(config.namespace_kind, config.namespace_identifier)
    if (
        namespace_token != DEFAULT_DZPG_NAMESPACE_TOKEN
        and config.namespace_identifier == DEFAULT_DZPG_ROR_IDENTIFIER
    ):
        raise HiTOPSuffixError("Unexpected DZPG namespace token calculation.")

    item_text_column = detect_item_text_column(rows[0].keys()) if rows else None
    prepared: list[dict[str, Any]] = []
    collision_groups: dict[tuple[str, str, str, str], list[int]] = {}

    # First pass: normalize all code-bearing fields and collect potential local
    # slug collisions before any final code is emitted.
    for index, row in enumerate(rows, start=1):
        source_label = row.get(config.label_column, "").strip()
        if not source_label:
            raise HiTOPSuffixError(f"Row {index} has no {config.label_column!r} value.")
        base_slug = slugify(row.get(config.slug_source_column, source_label))
        manifestation_type = resolve_manifestation_type(
            row.get(config.manifestation_type_column, "").strip()
        )
        hitop_base_code, base_code_source, concept_label, concept_url = resolve_hitop_base_code(
            row,
            config=config,
            vocabulary=vocabulary,
        )
        group_key = (hitop_base_code, manifestation_type, namespace_token, base_slug)
        collision_groups.setdefault(group_key, []).append(index - 1)
        prepared.append(
            {
                "row": row,
                "row_number": index,
                "source_label": source_label,
                "base_slug": base_slug,
                "manifestation_type": manifestation_type,
                "hitop_base_code": hitop_base_code,
                "base_code_source": base_code_source,
                "concept_label": concept_label,
                "concept_url": concept_url,
            }
        )

    records: list[dict[str, Any]] = []
    for prepared_index, item in enumerate(prepared):
        row = item["row"]
        slug = item["base_slug"]
        disambiguator = None
        disambiguation_basis = None
        group_key = (
            item["hitop_base_code"],
            item["manifestation_type"],
            namespace_token,
            item["base_slug"],
        )
        if len(collision_groups[group_key]) > 1:
            # Disambiguators are only attached when the final tuple would be
            # ambiguous inside the same HiTOP base concept, manifestation type,
            # namespace, and slug.
            disambiguation_basis = _build_disambiguation_basis_for_row(
                row,
                config=config,
                hitop_base_code=item["hitop_base_code"],
                manifestation_type=item["manifestation_type"],
            )
            slug = attach_disambiguator(item["base_slug"], disambiguation_basis)
            disambiguator = slug.rsplit("_", 1)[1]

        code = build_code(
            hitop_base_code=item["hitop_base_code"],
            manifestation_type=item["manifestation_type"],
            namespace_token=namespace_token,
            slug=slug,
        )
        item_text = row.get(item_text_column, "").strip() if item_text_column else ""
        record: dict[str, Any] = {
            "code": code,
            "hitop_base_code": item["hitop_base_code"],
            "suffix_block": "M",
            "manifestation_type": item["manifestation_type"],
            "namespace": {
                "token": namespace_token,
                "kind": config.namespace_kind,
                "identifier": config.namespace_identifier,
                "label": config.namespace_label,
                "acronym": config.namespace_acronym,
            },
            "slug": slug,
            "base_slug": item["base_slug"],
            "preferred_label": item["source_label"],
            "alt_labels": [item["concept_label"]] if item["concept_label"] else [],
            "definition": (
                f"Manifestation item {item['source_label']} from "
                f"{config.instrument}, mapped to {item['concept_label']}."
            ),
            "operationalization": {
                "instrument": config.instrument,
                "item_id": item["source_label"],
                "item_text": item_text,
                # Preserve the source export's verbose column names verbatim so
                # reviewers can trace generated values back to the original CSV.
                "response_scale": row.get(
                    # Exact source column header; must match verbatim, cannot be shortened.
                    "(1) Trifft gar nicht zu, (2) Trifft eher nicht zu, (3) teils/teils, (4) Trifft eher zu, (5) Trifft sehr zu        ",  # noqa: E501
                    "",
                ).strip(),
                "scale_type": row.get("Likert", "").strip(),
                "value_range": row.get("1 bis 5", "").strip(),
                "selection_type": row.get("Einfachauswahl", "").strip(),
                "data_type": row.get("Numerisch", "").strip(),
            },
            "population": {
                "description": "Universitaetskliniken in Deutschland",
                "setting": "MII/NUM rollout context",
            },
            "source": {
                "study_id": config.study_id,
                "instrument": config.instrument,
                "item_id": item["source_label"],
                "local_concept_id": item["source_label"],
                "citation": row.get("Kerber et al.", "").strip(),
                "source_url": config.source_url,
                "input_row_number": item["row_number"],
                "input_hitop_concept_label": item["concept_label"],
                "input_hitop_concept_url": item["concept_url"],
                "hitop_base_code_resolution": item["base_code_source"],
            },
            "status": config.status,
            "created": config.created,
            "modified": config.modified,
            "version": config.version,
            "replaces": [],
            "replaced_by": [],
            "mapping_review_status": "unreviewed",
            "mappings": [],
            "provenance": {
                "created_by": "scripts/generate_hitop_suffixes_from_csv.py",
                "created_at": config.created,
                "reviewed_by": [],
                "review_status": "draft",
                "decision_note": (
                    "Generated from source CSV using the documented DZPG ROR namespace."
                ),
            },
        }
        if disambiguator and disambiguation_basis:
            record["disambiguator"] = disambiguator
            record["disambiguation_basis"] = disambiguation_basis

        report = validate_metadata(record)
        if not report.valid:
            raise HiTOPSuffixError(
                f"Generated invalid record for row {item['row_number']}: {report.errors}"
            )
        if report.warnings:
            record["validation_warnings"] = report.warnings

        records.append(record)

    return records


def write_yaml(records: list[dict[str, Any]], output_path: Path) -> None:
    """Write generated metadata records as YAML."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(
            records,
            handle,
            allow_unicode=True,
            sort_keys=False,
            width=120,
        )


def write_review_csv(records: list[dict[str, Any]], output_path: Path) -> None:
    """Write a compact CSV review table for generated metadata records."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "code",
        "hitop_base_code",
        "manifestation_type",
        "namespace_token",
        "slug",
        "preferred_label",
        "input_hitop_concept_label",
        "hitop_base_code_resolution",
        "item_text",
        "status",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "code": record["code"],
                    "hitop_base_code": record["hitop_base_code"],
                    "manifestation_type": record["manifestation_type"],
                    "namespace_token": record["namespace"]["token"],
                    "slug": record["slug"],
                    "preferred_label": record["preferred_label"],
                    "input_hitop_concept_label": record["source"]["input_hitop_concept_label"],
                    "hitop_base_code_resolution": record["source"]["hitop_base_code_resolution"],
                    "item_text": record["operationalization"]["item_text"],
                    "status": record["status"],
                }
            )
