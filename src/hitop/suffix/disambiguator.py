"""Disambiguator generation for local slug collisions."""

from __future__ import annotations

import base64
import hashlib

from .constants import MANIFESTATION_TYPES
from .exceptions import InvalidSlugError
from .normalization import normalize_identifier
from .slug import validate_base_slug


def build_disambiguation_basis(
    *,
    namespace_identifier: str,
    hitop_base_code: str,
    manifestation_type: str,
    study_id: str,
    instrument: str,
    item_id_or_local_concept_id: str,
) -> str:
    """Build the canonical disambiguation basis string.

    The returned basis follows the documented pipe-delimited order. The literal
    suffix block is represented as lower-case ``m`` because the full basis is
    normalized before hashing.
    """

    manifestation_type = manifestation_type.strip().upper()
    if manifestation_type not in MANIFESTATION_TYPES:
        raise InvalidSlugError(f"Unsupported manifestation type {manifestation_type!r}.")

    parts = [
        namespace_identifier,
        hitop_base_code,
        "m",
        manifestation_type,
        study_id,
        instrument,
        item_id_or_local_concept_id,
    ]
    if any(str(part).strip() == "" for part in parts):
        raise InvalidSlugError("Disambiguation basis parts must not be empty.")
    return "|".join(normalize_identifier(part) for part in parts)


def generate_disambiguator(canonical_basis: str) -> str:
    """Generate the six-character Base32 SHA-256 disambiguator."""

    basis = normalize_identifier(canonical_basis)
    digest = hashlib.sha256(basis.encode("utf-8")).digest()
    encoded = base64.b32encode(digest).decode("ascii").rstrip("=")
    return encoded[:6]


def attach_disambiguator(base_slug: str, canonical_basis: str) -> str:
    """Return ``<BASE_SLUG>_<DISAMBIGUATOR>`` for a local slug collision."""

    if not validate_base_slug(base_slug):
        raise InvalidSlugError(
            "Base slug must be 3 to 33 characters and must not start or end with '_'."
        )
    disambiguator = generate_disambiguator(canonical_basis)
    return f"{base_slug}_{disambiguator}"
