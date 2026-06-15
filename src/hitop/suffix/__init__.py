"""Utilities for HiTOP modular namespaced manifestation suffixes.

The package implements the algorithms described in
``docs/modular-namespaced-suffix-schema.md`` and related documentation:

* namespace token generation
* slug normalization and validation
* disambiguator generation
* manifestation code parsing and validation
* metadata validation
* mapping candidate scoring
"""

from .code import ManifestationCode, build_code, parse_code, validate_code
from .disambiguator import (
    build_disambiguation_basis,
    generate_disambiguator,
)
from .namespace import (
    canonicalize_namespace_identifier,
    generate_namespace_token,
    validate_namespace_token,
)
from .slug import slugify, validate_slug

__all__ = [
    "ManifestationCode",
    "build_code",
    "build_disambiguation_basis",
    "canonicalize_namespace_identifier",
    "generate_disambiguator",
    "generate_namespace_token",
    "parse_code",
    "slugify",
    "validate_code",
    "validate_namespace_token",
    "validate_slug",
]
