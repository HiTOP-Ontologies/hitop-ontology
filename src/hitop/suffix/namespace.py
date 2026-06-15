"""Namespace token generation and validation."""

from __future__ import annotations

import base64
import hashlib
import re

from .constants import NAMESPACE_RE, SUPPORTED_NAMESPACE_KINDS
from .exceptions import InvalidNamespaceError
from .normalization import normalize_identifier

ROR_RE = re.compile(r"^(?:https?://ror\.org/)?(?P<id>[a-z0-9]{9})$", re.IGNORECASE)
ORCID_RE = re.compile(r"^(?:https?://orcid\.org/)?(?P<id>[0-9Xx\-]{16,19})$")


def _base32_sha256(value: str) -> str:
    """Return an unpadded RFC 4648 Base32 SHA-256 digest."""

    digest = hashlib.sha256(value.encode("utf-8")).digest()
    return base64.b32encode(digest).decode("ascii").rstrip("=")


def validate_namespace_kind(kind: str) -> str:
    """Validate and normalize a namespace source kind."""

    normalized = kind.strip().upper()
    if not re.fullmatch(r"[A-Z]{3}", normalized):
        raise InvalidNamespaceError("Namespace kind must match [A-Z]{3}.")
    if normalized not in SUPPORTED_NAMESPACE_KINDS:
        raise InvalidNamespaceError(
            f"Unsupported namespace kind {normalized!r}. "
            f"Supported kinds: {', '.join(sorted(SUPPORTED_NAMESPACE_KINDS))}."
        )
    return normalized


def canonicalize_namespace_identifier(kind: str, source_identifier: str) -> str:
    """Return the source-specific canonical identifier used for token hashing.

    The function implements the canonical forms documented in the suffix schema.
    It accepts common compact inputs for ROR, ORCID, DOI, and DNS values, but the
    returned value is always the canonical string that should be stored in
    metadata.
    """

    normalized_kind = validate_namespace_kind(kind)
    value = normalize_identifier(source_identifier)

    if normalized_kind == "HTP":
        if value in {"", "hitop", "hitop:core", "htp"}:
            return "hitop:core"
        return value

    if normalized_kind == "ROR":
        match = ROR_RE.match(value)
        if not match:
            raise InvalidNamespaceError(
                "ROR identifiers must be a ROR ID or https://ror.org/<id>."
            )
        return f"https://ror.org/{match.group('id').lower()}"

    if normalized_kind == "ORC":
        match = ORCID_RE.match(value)
        if not match:
            raise InvalidNamespaceError(
                "ORCID identifiers must be an ORCID iD or https://orcid.org/<id>."
            )
        compact = match.group("id").replace("-", "").upper()
        if len(compact) != 16:
            raise InvalidNamespaceError("ORCID identifiers must contain 16 characters.")
        hyphenated = "-".join(
            compact[index : index + 4] for index in range(0, len(compact), 4)
        )
        return f"https://orcid.org/{hyphenated}"

    if normalized_kind == "DOI":
        if value.startswith("https://doi.org/"):
            doi = value.removeprefix("https://doi.org/")
        elif value.startswith("http://doi.org/"):
            doi = value.removeprefix("http://doi.org/")
        elif value.startswith("doi:"):
            doi = value.removeprefix("doi:")
        else:
            doi = value
        if not doi.startswith("10."):
            raise InvalidNamespaceError("DOI identifiers must start with '10.'.")
        return f"https://doi.org/{doi}"

    if normalized_kind == "ARK":
        if value.startswith("ark:/"):
            return value
        raise InvalidNamespaceError("ARK identifiers must use the 'ark:/' form.")

    if normalized_kind == "DNS":
        if value.startswith("dns:"):
            return value
        parts = [part for part in value.split(".") if part]
        if len(parts) < 2:
            raise InvalidNamespaceError(
                "DNS identifiers must be 'dns:<namespace>' or a dotted domain."
            )
        return "dns:" + ".".join(reversed(parts))

    if normalized_kind == "SRC":
        if not value:
            raise InvalidNamespaceError("SRC identifiers must not be empty.")
        return value

    raise InvalidNamespaceError(f"Unsupported namespace kind {normalized_kind!r}.")


def generate_namespace_token(kind: str, source_identifier: str) -> str:
    """Generate a fixed-length namespace token.

    The token format is ``[A-Z]{3}[A-Z2-7]{13}``: a three-character kind prefix
    followed by 13 Base32 SHA-256 digest characters.
    """

    normalized_kind = validate_namespace_kind(kind)
    canonical = canonicalize_namespace_identifier(normalized_kind, source_identifier)
    return normalized_kind + _base32_sha256(canonical)[:13]


def validate_namespace_token(token: str) -> bool:
    """Return ``True`` if a namespace token is syntactically valid."""

    return bool(NAMESPACE_RE.fullmatch(token))
