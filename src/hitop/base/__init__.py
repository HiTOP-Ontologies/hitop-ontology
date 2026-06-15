"""HiTOP base-code checksum and CSV generation utilities."""

from __future__ import annotations

from typing import Any

from .HITOPChecksum import (
    BASE62_ALPHABET,
    DEFAULT_PREFIX,
    HITOPChecksum,
    HITOPChecksumError,
    base62_encode,
    base62_to_char,
    calculate_check_digit,
    char_to_base62,
)

_CSV_EXPORTS = {"HiTOPCSVError", "build_hitop_code", "process_csv"}

__all__ = [
    "BASE62_ALPHABET",
    "DEFAULT_PREFIX",
    "HITOPCSVError",
    "HITOPChecksum",
    "HITOPChecksumError",
    "base62_encode",
    "base62_to_char",
    "build_hitop_code",
    "calculate_check_digit",
    "char_to_base62",
    "process_csv",
]


def __getattr__(name: str) -> Any:
    """Load CSV-generation helpers lazily to keep module execution warning-free."""

    if name in _CSV_EXPORTS:
        from . import hitop as hitop_module

        return getattr(hitop_module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
