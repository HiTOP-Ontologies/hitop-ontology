"""Validation and generation support for HiTOP factorization hierarchy files.

See ``docs/factorizations.md`` for the governance model.
"""

from __future__ import annotations

from .validate import (
    ALLOWED_META_FIELDS,
    ALLOWED_NODE_FIELDS,
    CANONICAL_ONTOLOGY_IRI,
    NODE_KINDS,
    STATUSES,
    check_cross_file_label_consistency,
    collect_codes_with_labels,
    discover_hierarchy_files,
    iter_nodes,
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
    "STATUSES",
    "check_cross_file_label_consistency",
    "collect_codes_with_labels",
    "discover_hierarchy_files",
    "iter_nodes",
    "load_core_class_local_names",
    "load_hierarchy_document",
    "validate_hierarchy_document",
    "validate_meta",
    "validate_node_shape",
]
