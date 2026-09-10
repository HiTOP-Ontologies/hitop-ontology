"""Manifestation code parsing, building, and validation."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .constants import (
    DISAMBIGUATED_SUFFIX_RE,
    FULL_CODE_RE,
    HITOP_BASE_CODE_PATTERN,
    MANIFESTATION_TYPES,
    NAMESPACE_RE,
    SLUG_RE,
)
from .exceptions import InvalidCodeError
from .slug import split_disambiguated_slug

HITOP_BASE_CODE_RE = re.compile(f"^{HITOP_BASE_CODE_PATTERN}$")


@dataclass(frozen=True, slots=True)
class ManifestationCode:
    """Structured representation of a HiTOP manifestation suffix code."""

    hitop_base_code: str
    manifestation_type: str
    namespace_token: str
    slug: str

    @property
    def suffix(self) -> str:
        """Return the suffix block without the HiTOP base code."""

        return f"M-{self.manifestation_type}-{self.namespace_token}-{self.slug}"

    @property
    def code(self) -> str:
        """Return the full manifestation code."""

        return f"{self.hitop_base_code}.{self.suffix}"

    @property
    def base_slug(self) -> str | None:
        """Return the base slug when this code is explicitly disambiguated."""

        split = split_disambiguated_slug(self.slug)
        return split[0] if split else None

    @property
    def disambiguator(self) -> str | None:
        """Return the six-character disambiguator when present."""

        split = split_disambiguated_slug(self.slug)
        return split[1] if split else None


def parse_code(code: str) -> ManifestationCode:
    """Parse a full HiTOP manifestation code.

    Raises
    ------
    InvalidCodeError
        If the code does not match the canonical syntax.
    """

    match = FULL_CODE_RE.fullmatch(code)
    if not match:
        raise InvalidCodeError(f"Invalid manifestation code: {code!r}.")
    return ManifestationCode(
        hitop_base_code=match.group("hitop"),
        manifestation_type=match.group("manifestation_type"),
        namespace_token=match.group("namespace"),
        slug=match.group("slug"),
    )


def build_code(
    *,
    hitop_base_code: str,
    manifestation_type: str,
    namespace_token: str,
    slug: str,
) -> str:
    """Build and validate a canonical manifestation code."""

    manifestation_type = manifestation_type.strip().upper()
    if manifestation_type not in MANIFESTATION_TYPES:
        raise InvalidCodeError(f"Unsupported manifestation type {manifestation_type!r}.")
    if not NAMESPACE_RE.fullmatch(namespace_token):
        raise InvalidCodeError(f"Invalid namespace token {namespace_token!r}.")
    if not SLUG_RE.fullmatch(slug):
        raise InvalidCodeError(f"Invalid slug {slug!r}.")
    if not HITOP_BASE_CODE_RE.fullmatch(hitop_base_code):
        raise InvalidCodeError("HiTOP base code must match the canonical prefix-free form.")
    return ManifestationCode(
        hitop_base_code=hitop_base_code,
        manifestation_type=manifestation_type,
        namespace_token=namespace_token,
        slug=slug,
    ).code


def validate_code(code: str) -> list[str]:
    """Return validation errors for a code; return an empty list when valid."""

    errors: list[str] = []
    try:
        parsed = parse_code(code)
    except InvalidCodeError as exc:
        return [str(exc)]

    if parsed.manifestation_type not in MANIFESTATION_TYPES:
        errors.append("Manifestation type is not supported.")
    if not NAMESPACE_RE.fullmatch(parsed.namespace_token):
        errors.append("Namespace token does not match [A-Z]{3}[A-Z2-7]{13}.")
    if not SLUG_RE.fullmatch(parsed.slug):
        errors.append("Slug does not match the normative slug pattern.")

    if parsed.disambiguator and not DISAMBIGUATED_SUFFIX_RE.fullmatch(parsed.suffix):
        errors.append("Disambiguated slug does not match the strict disambiguator form.")
    return errors
