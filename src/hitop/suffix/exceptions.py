"""Domain-specific exceptions for HiTOP suffix tooling."""

from __future__ import annotations


class HiTOPSuffixError(ValueError):
    """Base exception for recoverable validation and generation errors."""


class InvalidNamespaceError(HiTOPSuffixError):
    """Raised when a namespace kind, identifier, or token is invalid."""


class InvalidSlugError(HiTOPSuffixError):
    """Raised when a slug cannot be generated or validated."""


class InvalidCodeError(HiTOPSuffixError):
    """Raised when a manifestation suffix code is syntactically invalid."""
