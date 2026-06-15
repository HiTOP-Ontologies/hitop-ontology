"""Metadata loading and validation for manifestation suffix records."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .code import parse_code
from .exceptions import HiTOPSuffixError
from .namespace import (
    canonicalize_namespace_identifier,
    generate_namespace_token,
)
from .slug import split_disambiguated_slug, validate_slug


@dataclass(slots=True)
class ValidationReport:
    """Structured validation result for metadata and codes."""

    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dictionary representation."""

        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def load_yaml(path: str | Path) -> Any:
    """Load a YAML document from disk using safe parsing."""

    with Path(path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _require_mapping(value: Any, label: str, errors: list[str]) -> dict[str, Any]:
    """Return ``value`` as a mapping or append a validation error."""

    if not isinstance(value, dict):
        errors.append(f"{label} must be a mapping.")
        return {}
    return value


def _require_string(mapping: dict[str, Any], key: str, errors: list[str]) -> str:
    """Return a required non-empty string value or append a validation error."""

    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{key} must be a non-empty string.")
        return ""
    return value


def validate_metadata(record: dict[str, Any]) -> ValidationReport:
    """Validate a metadata record against the suffix schema requirements."""

    errors: list[str] = []
    warnings: list[str] = []
    data = _require_mapping(record, "record", errors)
    if errors:
        return ValidationReport(False, errors, warnings)

    code_value = _require_string(data, "code", errors)
    parsed = None
    if code_value:
        try:
            parsed = parse_code(code_value)
        except HiTOPSuffixError as exc:
            errors.append(str(exc))

    for key in [
        "hitop_base_code",
        "suffix_block",
        "manifestation_type",
        "slug",
        "preferred_label",
        "definition",
        "status",
        "created",
        "version",
    ]:
        _require_string(data, key, errors)

    namespace = _require_mapping(data.get("namespace"), "namespace", errors)
    source = _require_mapping(data.get("source"), "source", errors)

    if namespace:
        token = _require_string(namespace, "token", errors)
        kind = _require_string(namespace, "kind", errors)
        identifier = _require_string(namespace, "identifier", errors)
        if token and kind and identifier:
            try:
                # Recompute the namespace token from the stored authority so a
                # record cannot silently drift after metadata edits.
                expected_token = generate_namespace_token(kind, identifier)
                canonical = canonicalize_namespace_identifier(kind, identifier)
                if token != expected_token:
                    errors.append(
                        "namespace.token does not match namespace.kind and "
                        f"namespace.identifier; expected {expected_token}."
                    )
                if identifier != canonical:
                    warnings.append(
                        "namespace.identifier is not in canonical form; "
                        f"canonical value is {canonical}."
                    )
            except HiTOPSuffixError as exc:
                errors.append(str(exc))

    if source:
        for key in ["study_id", "instrument"]:
            _require_string(source, key, errors)
        if not source.get("item_id") and not source.get("local_concept_id"):
            errors.append("source.item_id or source.local_concept_id is required.")

    slug = data.get("slug")
    if isinstance(slug, str) and not validate_slug(slug):
        errors.append("slug does not match the normative slug pattern.")

    if parsed:
        if data.get("hitop_base_code") != parsed.hitop_base_code:
            errors.append("hitop_base_code does not match code.")
        if data.get("suffix_block") != "M":
            errors.append("suffix_block must be 'M'.")
        if data.get("manifestation_type") != parsed.manifestation_type:
            errors.append("manifestation_type does not match code.")
        if namespace and namespace.get("token") != parsed.namespace_token:
            errors.append("namespace.token does not match code.")
        if data.get("slug") != parsed.slug:
            errors.append("slug does not match code.")

        split = split_disambiguated_slug(parsed.slug)
        if split:
            # A disambiguated slug is syntactically valid on its own, but the
            # basis metadata is required for reviewers to reproduce the suffix.
            base_slug, disambiguator = split
            if data.get("base_slug") and data.get("base_slug") != base_slug:
                errors.append("base_slug does not match the slug.")
            if data.get("disambiguator") and data.get("disambiguator") != disambiguator:
                errors.append("disambiguator does not match the slug.")
            if not data.get("disambiguator"):
                warnings.append("Disambiguated slug should include disambiguator metadata.")
            if not data.get("disambiguation_basis"):
                warnings.append(
                    "Disambiguated slug should include disambiguation_basis metadata."
                )

    if "mappings" in data and not isinstance(data["mappings"], list):
        errors.append("mappings must be a list.")

    return ValidationReport(valid=not errors, errors=errors, warnings=warnings)
