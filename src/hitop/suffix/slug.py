"""Slug generation and validation."""

from __future__ import annotations

from .constants import BASE_SLUG_RE, DISAMBIGUATOR_RE, SLUG_RE
from .exceptions import InvalidSlugError
from .normalization import slug_text


def slugify(label: str) -> str:
    """Generate a normalized HiTOP slug from a human-readable label."""

    slug = slug_text(label)
    if not slug:
        raise InvalidSlugError("Slug generation produced an empty value.")
    if len(slug) > 40:
        raise InvalidSlugError(
            "Generated slug is longer than 40 characters; shorten the label manually."
        )
    if not validate_slug(slug):
        raise InvalidSlugError(f"Generated slug {slug!r} is not valid.")
    return slug


def validate_slug(slug: str) -> bool:
    """Return ``True`` if a slug matches the normative 3-to-40 character form."""

    return bool(SLUG_RE.fullmatch(slug))


def validate_base_slug(base_slug: str) -> bool:
    """Return ``True`` if a base slug is valid for a disambiguated slug."""

    return bool(BASE_SLUG_RE.fullmatch(base_slug))


def split_disambiguated_slug(slug: str) -> tuple[str, str] | None:
    """Return ``(base_slug, disambiguator)`` when a slug is explicitly disambiguated.

    The final underscore-delimited token is treated as a disambiguator only if it
    matches ``[A-Z2-7]{6}`` and the base slug is valid.
    """

    if "_" not in slug:
        return None
    base_slug, disambiguator = slug.rsplit("_", 1)
    if not DISAMBIGUATOR_RE.fullmatch(disambiguator):
        return None
    if not validate_base_slug(base_slug):
        return None
    return base_slug, disambiguator
