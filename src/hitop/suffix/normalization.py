"""Normalization helpers used by namespace, slug, and mapping algorithms."""

from __future__ import annotations

import re
import unicodedata

WHITESPACE_RE = re.compile(r"\s+")
NON_AZ09_RE = re.compile(r"[^A-Z0-9]+")


def normalize_identifier(value: object) -> str:
    """Return the canonical identifier normalization used before hashing.

    The function follows the specification language:

    * Unicode NFKC normalization
    * trim
    * lowercase
    * collapse internal whitespace to a single space

    Parameters
    ----------
    value:
        Any value that can be converted to text.

    Returns
    -------
    str
        A stable, lower-case string suitable for deterministic hashing.
    """

    normalized = unicodedata.normalize("NFKC", str(value))
    normalized = normalized.strip().lower()
    return WHITESPACE_RE.sub(" ", normalized)


def transliterate_to_ascii(value: str) -> str:
    """Transliterate Unicode text to ASCII by dropping unsupported marks."""

    normalized = unicodedata.normalize("NFKD", value)
    return normalized.encode("ascii", "ignore").decode("ascii")


def normalize_text(value: object) -> str:
    """Normalize free text for matching and scoring.

    This is intentionally stronger than identifier normalization: punctuation is
    converted to spaces and all whitespace is collapsed. The result is suitable
    for token-based matching, but must not be used as a persistent identifier.
    """

    text = transliterate_to_ascii(str(value))
    text = unicodedata.normalize("NFKC", text).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return WHITESPACE_RE.sub(" ", text).strip()


def slug_text(value: str) -> str:
    """Normalize human-readable text into an uppercase slug candidate."""

    text = transliterate_to_ascii(value).upper()
    text = NON_AZ09_RE.sub("_", text)
    text = re.sub(r"_+", "_", text)
    return text.strip("_")

