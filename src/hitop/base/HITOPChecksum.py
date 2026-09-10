"""Canonical HiTOP checksum calculation.

This module contains the production checksum implementation used by
``hitop.py``.  The checksum is intentionally deterministic and depends on the
the hierarchy segment and the local concept code. ``HiTOP`` is a fixed internal
checksum namespace and is never emitted as part of a code.

Canonical checksum input::

    HiTOP-<segment>-<concept_code>

The input string is hashed twice with SHA-256.  The first 32 bits of the second
hash are reduced into the two-character Base62 checksum space.
"""

from __future__ import annotations

import hashlib
import re

BASE62_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
_CHECKSUM_NAMESPACE = "HiTOP"

SEGMENT_RE = re.compile(r"^[0-9A-Za-z][0-9]+$")
CONCEPT_CODE_RE = re.compile(r"^[0-9A-Za-z]+$")


class HITOPChecksumError(ValueError):
    """Raised when checksum input cannot be processed safely."""


def _normalize_segment(segment: str) -> str:
    """Validate and normalize the hierarchy segment, for example ``C0``."""

    value = str(segment).strip()
    if not SEGMENT_RE.fullmatch(value):
        raise HITOPChecksumError(
            "Segment must match one ASCII letter or digit followed by one or more digits."
        )
    return value


def _normalize_concept_code(concept_code: str) -> str:
    """Validate and normalize the local Base62 concept code."""

    value = str(concept_code).strip()
    if not CONCEPT_CODE_RE.fullmatch(value):
        raise HITOPChecksumError(
            "Concept code must contain one or more Base62 characters (0-9, A-Z, a-z)."
        )
    return value


def char_to_base62(char: str) -> int:
    """Return the numeric Base62 value for a single character."""

    if len(char) != 1:
        raise HITOPChecksumError("Expected exactly one character.")
    try:
        return BASE62_ALPHABET.index(char)
    except ValueError as exc:
        raise HITOPChecksumError(f"Invalid Base62 character: {char!r}.") from exc


def base62_to_char(value: int) -> str:
    """Return the Base62 character for a numeric value in the range 0..61."""

    if not 0 <= value < len(BASE62_ALPHABET):
        raise HITOPChecksumError("Base62 value must be between 0 and 61.")
    return BASE62_ALPHABET[value]


def base62_encode(number: int) -> str:
    """Encode a non-negative integer as a Base62 string."""

    if number < 0:
        raise HITOPChecksumError("Base62 encoding requires a non-negative integer.")
    if number == 0:
        return BASE62_ALPHABET[0]

    chars: list[str] = []
    quotient = number
    while quotient:
        quotient, remainder = divmod(quotient, len(BASE62_ALPHABET))
        chars.append(BASE62_ALPHABET[remainder])
    return "".join(reversed(chars))


def calculate_check_digit(segment: str, concept_code: str) -> str:
    """Calculate the two-character HiTOP checksum.

    Parameters
    ----------
    segment:
        Hierarchy segment and segment level, for example ``C0`` or ``U1``.
    concept_code:
        Local Base62 concept code without segment and without checksum.

    Returns
    -------
    str
        Two Base62 characters.  Leading zeroes are preserved.
    """

    normalized_segment = _normalize_segment(segment)
    normalized_code = _normalize_concept_code(concept_code)

    # Keep separators explicit so the checksum input remains unambiguous.
    checksum_input = f"{_CHECKSUM_NAMESPACE}-{normalized_segment}-{normalized_code}"
    first_hash = hashlib.sha256(checksum_input.encode("utf-8")).hexdigest()
    second_hash = hashlib.sha256(first_hash.encode("ascii")).hexdigest()
    checksum_value = int(second_hash[:8], 16) % (len(BASE62_ALPHABET) ** 2)
    return base62_encode(checksum_value).rjust(2, BASE62_ALPHABET[0])


class HITOPChecksum:
    """Checksum helper for a HiTOP local concept code stem.

    The preferred production path is ``from_parts(segment, concept_code)``
    because it makes all checksum inputs explicit.  Direct construction with
    ``HITOPChecksum("C001")`` is kept for backwards compatibility and interprets
    the first two characters as the segment.
    """

    def __init__(
        self,
        code: str,
        *,
        segment: str | None = None,
        concept_code: str | None = None,
    ) -> None:
        """Create a checksum helper from either legacy or explicit code parts.

        ``code`` is interpreted as the historical combined stem when
        ``segment`` and ``concept_code`` are omitted.  Production callers should
        pass explicit parts via :meth:`from_parts` so that checksum inputs remain
        auditable and unambiguous.
        """

        if segment is None and concept_code is None:
            stem = str(code).strip()
            if len(stem) < 3:
                raise HITOPChecksumError(
                    "Code stem must contain a two-character segment and a concept code."
                )
            self.segment = _normalize_segment(stem[:2])
            self.concept_code = _normalize_concept_code(stem[2:])
            self.code = f"{self.segment}{self.concept_code}"
            return

        if segment is None or concept_code is None:
            raise HITOPChecksumError("segment and concept_code must be provided together.")

        self.segment = _normalize_segment(segment)
        self.concept_code = _normalize_concept_code(concept_code)
        self.code = f"{self.segment}{self.concept_code}"

        provided_stem = str(code).strip()
        if provided_stem and provided_stem != self.code:
            raise HITOPChecksumError(
                f"Provided code stem {provided_stem!r} does not match "
                f"segment+concept_code {self.code!r}."
            )

    @classmethod
    def from_parts(
        cls,
        *,
        segment: str,
        concept_code: str,
    ) -> HITOPChecksum:
        """Create a checksum helper from explicit checksum components."""

        return cls(
            f"{segment}{concept_code}",
            segment=segment,
            concept_code=concept_code,
        )

    @staticmethod
    def char2base62(char: str) -> int:
        """Backwards-compatible alias for :func:`char_to_base62`."""

        return char_to_base62(char)

    @staticmethod
    def base622Char(value: int) -> str:
        """Backwards-compatible alias for :func:`base62_to_char`."""

        return base62_to_char(value)

    @property
    def check_digit(self) -> str:
        """Return the two-character checksum for this code stem."""

        return calculate_check_digit(self.segment, self.concept_code)

    def get_check_digit(self) -> str:
        """Return the checksum using a PEP-8 compatible method name."""

        return self.check_digit

    def with_check_digit(self) -> str:
        """Return ``<segment><concept_code><checksum>``."""

        return f"{self.code}{self.check_digit}"

    def getCode(self) -> str:
        """Backwards-compatible method returning the code with checksum."""

        return self.with_check_digit()
