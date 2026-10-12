"""Validation and generation support for HiTOP factorization hierarchy files.

See ``docs/factorizations.md`` for the governance model.
"""

from __future__ import annotations

from .colors import PALETTE, PALETTE_LEVELS, annotate_colors
from .validate import (
    ALLOWED_META_FIELDS,
    ALLOWED_NODE_FIELDS,
    CANONICAL_ONTOLOGY_IRI,
    NODE_KINDS,
    STATUSES,
    check_labels_match_core,
    collect_codes_with_labels,
    discover_hierarchy_files,
    iter_nodes,
    load_core_class_labels,
    load_core_class_local_names,
    load_hierarchy_document,
    validate_hierarchy_document,
    validate_meta,
    validate_node_shape,
)

__all__ = [
    "ALLOWED_META_FIELDS",
    "ALLOWED_NODE_FIELDS",
    "CANONICAL_ONTOLOGY_IRI",
    "NODE_KINDS",
    "PALETTE",
    "PALETTE_LEVELS",
    "STATUSES",
    "annotate_colors",
    "check_labels_match_core",
    "collect_codes_with_labels",
    "discover_hierarchy_files",
    "iter_nodes",
    "load_core_class_labels",
    "load_core_class_local_names",
    "load_hierarchy_document",
    "validate_hierarchy_document",
    "validate_meta",
    "validate_node_shape",
]
