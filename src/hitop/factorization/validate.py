"""Shared validation logic for HiTOP factorization hierarchy YAML files.

Both ``validation/test_factorizations.py`` and
``scripts/generate_factorization_ontology.py`` import this module so the
rules that decide whether a ``*_hierarchy.yaml`` is valid live in exactly
one place. See ``docs/factorizations.md`` for the governance model and
``schema/factorization-hierarchy.schema.json`` for the declarative schema
this module enforces by hand (no ``jsonschema`` dependency is introduced;
the checks below mirror the schema field by field, matching the existing
project convention in the former manifest validator).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Iterator

import yaml
from rdflib import OWL, RDF, RDFS, Graph, Namespace

HITOP = Namespace("http://purl.org/hitop#")
LEVEL_CLASS = HITOP.O001Ih
HAS_LEVEL = HITOP.hasLevel
CANONICAL_ONTOLOGY_IRI = "http://purl.org/hitop"

FACTORIZATION_ID_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
BASE_CODE_RE = re.compile(r"^[A-Za-z0-9]+$")
STATUSES = {"draft", "active", "deprecated"}

REQUIRED_META_FIELDS = {
    "factorization_id",
    "version",
    "label",
    "status",
    "based_on",
    "provenance",
}
OPTIONAL_META_FIELDS = {"source", "paper"}
ALLOWED_META_FIELDS = REQUIRED_META_FIELDS | OPTIONAL_META_FIELDS

REQUIRED_NODE_FIELDS = {"label", "level", "code"}
OPTIONAL_NODE_FIELDS = {"bridge", "provisional", "children"}
ALLOWED_NODE_FIELDS = REQUIRED_NODE_FIELDS | OPTIONAL_NODE_FIELDS


def discover_hierarchy_files(factorizations_dir: Path) -> list[Path]:
    """Return every ``factorizations/<id>/v<N>/*_hierarchy.yaml``, sorted."""

    return sorted(factorizations_dir.glob("*/v*/*_hierarchy.yaml"))


def load_hierarchy_document(path: Path) -> Any:
    """Parse one ``*_hierarchy.yaml`` file into plain Python data."""

    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_core_class_local_names(ontology_ttl: Path) -> set[str]:
    """Return ``hitop:<local-name>`` identifiers for every class in the core ontology."""

    graph = Graph()
    graph.parse(ontology_ttl, format="turtle")
    prefix = str(HITOP)
    names: set[str] = set()
    for subject in graph.subjects(RDF.type, OWL.Class):
        subject_iri = str(subject)
        if subject_iri.startswith(prefix):
            names.add(subject_iri[len(prefix):])
    return names


def _level_ladder(ontology_ttl: Path) -> list[tuple[str, str]]:
    """Return ``(label, local_code)`` pairs for the six Level subclasses, in rank order."""

    graph = Graph()
    graph.parse(ontology_ttl, format="turtle")
    prefix = str(HITOP)
    subclasses = set(graph.subjects(RDFS.subClassOf, LEVEL_CLASS))
    if not subclasses:
        raise ValueError(f"No subclasses of hitop:O001Ih (Level) found in {ontology_ttl}.")

    labels: dict[Any, str] = {}
    codes: dict[Any, str] = {}
    for subject in subclasses:
        label = graph.value(subject, RDFS.label)
        if label is None:
            raise ValueError(f"Level subclass {subject} has no rdfs:label.")
        labels[subject] = str(label)
        subject_iri = str(subject)
        codes[subject] = subject_iri[len(prefix):] if subject_iri.startswith(prefix) else subject_iri

    edges: dict[Any, Any] = {}
    targets: set[Any] = set()
    for subject in subclasses:
        target = graph.value(subject, HAS_LEVEL)
        if target is not None:
            edges[subject] = target
            targets.add(target)

    roots = [subject for subject in subclasses if subject not in targets]
    if len(roots) != 1:
        raise ValueError(
            "Expected exactly one root Level subclass with no incoming "
            f"hitop:hasLevel edge, found {len(roots)}."
        )

    ladder: list[tuple[str, str]] = []
    current = roots[0]
    visited: set[Any] = set()
    while current is not None:
        if current in visited:
            raise ValueError("Cycle detected in the hitop:hasLevel ladder.")
        visited.add(current)
        ladder.append((labels[current], codes[current]))
        current = edges.get(current)

    if len(ladder) != len(subclasses):
        missing = subclasses - visited
        raise ValueError(
            "hitop:hasLevel ladder does not cover all Level subclasses; missing: "
            + ", ".join(sorted(labels[s] for s in missing))
        )
    return ladder


def load_level_ranks(ontology_ttl: Path) -> dict[str, int]:
    """Read the fixed ``hitop:hasLevel`` ladder from the core ontology.

    Returns a mapping from Level subclass label (e.g. ``"Spectrum"``) to its
    rank: 0 for the broadest Level (Factor) through 5 for the narrowest
    (Trait). The ladder is derived from ``ontology/hitop.ttl`` itself rather
    than hardcoded, so a future core change is picked up automatically.
    """

    return {label: rank for rank, (label, _code) in enumerate(_level_ladder(ontology_ttl))}


def load_level_local_codes(ontology_ttl: Path) -> dict[str, str]:
    """Read the fixed ``hitop:hasLevel`` ladder and return ``label -> hitop_base_code``.

    For example ``{"Spectrum": "O006lN", ...}``. Used by
    ``scripts/generate_factorization_ontology.py`` to resolve a node's
    ``level`` string to the core ontology class it should be tagged with via
    ``hitop:hasLevelType``.
    """

    return dict(_level_ladder(ontology_ttl))


def iter_nodes(
    node: dict[str, Any],
) -> Iterator[tuple[dict[str, Any], dict[str, Any] | None]]:
    """Yield every ``(node, parent_node)`` pair in a hierarchy tree, depth-first."""

    def _walk(
        current: dict[str, Any], parent: dict[str, Any] | None
    ) -> Iterator[tuple[dict[str, Any], dict[str, Any] | None]]:
        yield current, parent
        for child in current.get("children") or []:
            if isinstance(child, dict):
                yield from _walk(child, current)

    yield from _walk(node, None)


def _require(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def validate_meta(meta: Any, *, path: Path) -> list[str]:
    """Check ``meta`` shape and that it matches the file's directory/name."""

    errors: list[str] = []
    if not isinstance(meta, dict):
        return ["meta must be a mapping."]

    unknown = set(meta) - ALLOWED_META_FIELDS
    _require(not unknown, errors, f"meta has unknown field(s): {sorted(unknown)}")

    missing = REQUIRED_META_FIELDS - meta.keys()
    _require(not missing, errors, f"meta is missing required field(s): {sorted(missing)}")

    factorization_dir = path.parent.parent.name
    factorization_id = meta.get("factorization_id")
    _require(
        factorization_id == factorization_dir,
        errors,
        f"meta.factorization_id {factorization_id!r} does not match directory name {factorization_dir!r}.",
    )
    _require(
        isinstance(factorization_id, str) and bool(FACTORIZATION_ID_RE.match(factorization_id or "")),
        errors,
        f"meta.factorization_id {factorization_id!r} is not kebab-case.",
    )

    version = meta.get("version")
    _require(
        isinstance(version, str) and bool(version) and path.name.startswith(f"{version}_"),
        errors,
        f"meta.version {version!r} does not match filename {path.name!r}.",
    )

    status = meta.get("status")
    _require(status in STATUSES, errors, f"meta.status {status!r} must be one of {sorted(STATUSES)}.")

    based_on = meta.get("based_on")
    if isinstance(based_on, dict):
        _require(
            based_on.get("ontology_iri") == CANONICAL_ONTOLOGY_IRI,
            errors,
            f"meta.based_on.ontology_iri must be {CANONICAL_ONTOLOGY_IRI!r}.",
        )
        _require(
            bool(based_on.get("ontology_version")),
            errors,
            "meta.based_on.ontology_version must be a non-empty string.",
        )
    else:
        errors.append("meta.based_on must be a mapping.")

    provenance = meta.get("provenance")
    if isinstance(provenance, dict):
        for field in ("created_by", "created_at"):
            _require(
                bool(provenance.get(field)),
                errors,
                f"meta.provenance.{field} must be a non-empty string.",
            )
    else:
        errors.append("meta.provenance must be a mapping.")

    return errors


def validate_node_shape(node: Any, *, context: str, level_ranks: dict[str, int]) -> list[str]:
    """Check the field-level shape of a single node (not its position in the tree)."""

    errors: list[str] = []
    if not isinstance(node, dict):
        return [f"{context}: node must be a mapping."]

    unknown = set(node) - ALLOWED_NODE_FIELDS
    _require(not unknown, errors, f"{context}: unknown field(s): {sorted(unknown)}")

    missing = REQUIRED_NODE_FIELDS - node.keys()
    _require(not missing, errors, f"{context}: missing required field(s): {sorted(missing)}")

    label = node.get("label")
    _require(isinstance(label, str) and bool(label), errors, f"{context}: label must be a non-empty string.")

    level = node.get("level")
    _require(level in level_ranks, errors, f"{context}: level {level!r} must be one of {sorted(level_ranks)}.")

    code = node.get("code")
    _require(
        isinstance(code, str) and bool(BASE_CODE_RE.match(code or "")),
        errors,
        f"{context}: code {code!r} is not a valid HiTOP base code.",
    )

    if "bridge" in node:
        bridge = node["bridge"]
        _require(
            isinstance(bridge, list) and bool(bridge) and all(isinstance(item, str) for item in bridge),
            errors,
            f"{context}: bridge must be a non-empty list of strings.",
        )

    if "provisional" in node:
        _require(
            isinstance(node["provisional"], bool),
            errors,
            f"{context}: provisional must be a boolean.",
        )

    if "children" in node:
        children = node["children"]
        _require(
            isinstance(children, list) and bool(children),
            errors,
            f"{context}: children must be a non-empty list.",
        )

    return errors


def validate_hierarchy_document(
    record: Any,
    *,
    path: Path,
    core_class_names: set[str],
    level_ranks: dict[str, int],
) -> list[str]:
    """Validate one loaded ``*_hierarchy.yaml`` document.

    Checks schema shape, that ``meta`` matches the file's directory/name,
    referential integrity of every ``code`` against the core ontology,
    level-consistency of every parent-child edge against the
    ``hitop:hasLevel`` ladder, and that no ``code`` repeats within one tree.
    Returns a list of human-readable error strings; empty means valid.
    """

    errors: list[str] = []
    if not isinstance(record, dict):
        return [f"{path}: document must be a YAML mapping."]

    missing_top = {"meta", "hierarchy"} - record.keys()
    _require(not missing_top, errors, f"missing top-level field(s): {sorted(missing_top)}")

    errors.extend(validate_meta(record.get("meta"), path=path))

    hierarchy = record.get("hierarchy")
    status = (record.get("meta") or {}).get("status")
    if hierarchy is None:
        _require(status == "draft", errors, "hierarchy is null, so meta.status must be 'draft'.")
        return errors

    if not isinstance(hierarchy, dict):
        errors.append("hierarchy must be a mapping or null.")
        return errors

    seen_codes: dict[str, str] = {}
    for node, parent in iter_nodes(hierarchy):
        context = f"{path.name}:{node.get('label', '<unlabeled>') if isinstance(node, dict) else '<invalid>'}"
        errors.extend(validate_node_shape(node, context=context, level_ranks=level_ranks))
        if not isinstance(node, dict):
            continue

        code = node.get("code")
        if isinstance(code, str):
            if code in seen_codes:
                errors.append(f"{context}: code {code!r} appears more than once in this tree.")
            else:
                seen_codes[code] = node.get("label")
            if code not in core_class_names:
                errors.append(f"{context}: code {code!r} does not exist as a class in ontology/hitop.ttl.")

        level = node.get("level")
        if parent is not None and level in level_ranks and parent.get("level") in level_ranks:
            _require(
                level_ranks[level] > level_ranks[parent["level"]],
                errors,
                f"{context}: level {level!r} must be strictly below parent level {parent['level']!r}.",
            )

    return errors


def collect_codes_with_labels(record: dict[str, Any]) -> list[tuple[str, str]]:
    """Return ``(code, label)`` pairs for every node in a document's tree.

    Empty for a placeholder document whose ``hierarchy`` is ``null``.
    """

    hierarchy = record.get("hierarchy")
    if not isinstance(hierarchy, dict):
        return []
    return [
        (node["code"], node["label"])
        for node, _parent in iter_nodes(hierarchy)
        if isinstance(node, dict)
        and isinstance(node.get("code"), str)
        and isinstance(node.get("label"), str)
    ]


def check_cross_file_label_consistency(documents: list[tuple[Path, dict[str, Any]]]) -> list[str]:
    """Flag any ``hitop_base_code`` that carries a substantively different label across files.

    Comparison is case-insensitive: papers routinely differ only in casing
    for the same construct (e.g. "Sexual Problems" vs. "Sexual problems"),
    which is not a data error. A wording difference beyond casing (e.g.
    "Disinhibited Externalizing" vs. "Disinhibition") is reported, since it
    either reflects genuine terminology drift between cited papers that a
    curator should record via a mapping, or -- as with the historical
    ``T01OY2`` collision -- a real code-assignment bug.
    """

    by_code: dict[str, dict[str, tuple[str, list[str]]]] = {}
    for path, record in documents:
        for code, label in collect_codes_with_labels(record):
            key = label.casefold()
            bucket = by_code.setdefault(code, {})
            bucket.setdefault(key, (label, []))[1].append(str(path))

    errors: list[str] = []
    for code, variants in sorted(by_code.items()):
        if len(variants) > 1:
            detail = "; ".join(
                f"{label!r} in {sorted(paths)}" for label, paths in sorted(variants.values())
            )
            errors.append(f"code {code!r} has inconsistent labels across files: {detail}")
    return errors
