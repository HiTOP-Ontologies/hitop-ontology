"""Shared validation logic for HiTOP factorization hierarchy YAML files.

Both ``validation/test_factorizations.py`` and
``scripts/generate_factorization_ontology.py`` import this module so the
rules that decide whether a ``*_hierarchy.yaml`` is valid live in exactly
one place. See ``docs/factorizations.md`` for the governance model and
``schema/factorization-hierarchy.schema.json`` for the declarative schema
this module enforces by hand (no ``jsonschema`` dependency is introduced;
the checks below mirror the schema field by field, matching the existing
project convention in the former manifest validator).

Vertical ordering of a factorization tree comes entirely from
``hitop:hasTier`` nesting: a child is always exactly one step narrower than
its parent by construction, so no fixed, core-ontology-defined Level ladder
is needed to keep a tree internally ordered. ``level`` is a free-text label
(``hitop:hasLevel``) describing the role a node plays in *this* tree and is
purely descriptive: it is intentionally **not** checked for depth
consistency, because real HiTOP trees are irregular -- different branches
skip intermediate levels (for example some Spectra go straight to
Component, others via an intervening Subfactor), so the same label
legitimately occurs at different depths within one tree, exactly as
established taxonomic rank systems (e.g. NCBI Taxonomy) allow ranks to be
skipped or left unassigned per lineage.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from difflib import get_close_matches
from pathlib import Path
from typing import Any

import yaml
from rdflib import OWL, RDF, RDFS, Graph, Namespace

HITOP = Namespace("http://purl.org/hitop#")
CANONICAL_ONTOLOGY_IRI = "http://purl.org/hitop"

FACTORIZATION_ID_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
BASE_CODE_RE = re.compile(r"^[A-Za-z0-9]+$")
ORCID_RE = re.compile(r"^https://orcid\.org/\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")
STATUSES = {"draft", "active", "deprecated"}
NODE_KINDS = {"concept", "partial", "collection"}

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
OPTIONAL_NODE_FIELDS = {"bridge", "provisional", "children", "kind", "id", "mapping_note"}
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
            names.add(subject_iri[len(prefix) :])
    return names


def load_core_class_labels(ontology_ttl: Path) -> dict[str, set[str]]:
    """Return ``{local-name: {rdfs:label, ...}}`` for every class in the core ontology."""

    graph = Graph()
    graph.parse(ontology_ttl, format="turtle")
    prefix = str(HITOP)
    labels: dict[str, set[str]] = {}
    for subject in graph.subjects(RDF.type, OWL.Class):
        subject_iri = str(subject)
        if subject_iri.startswith(prefix):
            labels[subject_iri[len(prefix) :]] = {
                str(label) for label in graph.objects(subject, RDFS.label)
            }
    return labels


def iter_nodes(
    node: dict[str, Any],
) -> Iterator[tuple[dict[str, Any], dict[str, Any] | None]]:
    """Yield every ``(node, parent_node)`` pair in a hierarchy tree, depth-first.

    A child's position under its parent's ``children`` is what establishes
    it as exactly one step narrower than its parent (``hitop:hasTier``);
    that ordering is guaranteed by construction and needs no separate rank
    lookup against the core ontology.
    """

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
        f"meta.factorization_id {factorization_id!r} does not match "
        f"directory name {factorization_dir!r}.",
    )
    _require(
        isinstance(factorization_id, str)
        and bool(FACTORIZATION_ID_RE.match(factorization_id or "")),
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
    _require(
        status in STATUSES, errors, f"meta.status {status!r} must be one of {sorted(STATUSES)}."
    )

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
                f"meta.provenance.{field} must not be empty.",
            )
        for field in ("created_by", "contributors"):
            people = provenance.get(field, [])
            # Legacy creator strings remain readable; new sources use identified people.
            if field == "created_by" and isinstance(people, str):
                continue
            if not isinstance(people, list) or (field == "created_by" and not people):
                errors.append(f"meta.provenance.{field} must be a list of people.")
                continue
            seen = set()
            for person in people:
                if not isinstance(person, dict):
                    errors.append(f"meta.provenance.{field} entries must be mappings.")
                    continue
                orcid = person.get("orcid")
                valid = isinstance(orcid, str) and bool(ORCID_RE.fullmatch(orcid))
                if valid:
                    digits = orcid.rsplit("/", 1)[-1].replace("-", "")
                    total = 0
                    for digit in digits[:-1]:
                        total = (total + int(digit)) * 2
                    check = (12 - total % 11) % 11
                    valid = digits[-1] == ("X" if check == 10 else str(check))
                _require(valid, errors, f"Invalid ORCID in meta.provenance.{field}: {orcid!r}.")
                name = person.get("name")
                _require(
                    isinstance(name, str) and bool(name.strip()),
                    errors,
                    f"meta.provenance.{field} entries require a non-empty name.",
                )
                if isinstance(orcid, str):
                    _require(orcid not in seen, errors, f"Duplicate person in {field}: {orcid}.")
                    seen.add(orcid)
                _require(
                    not (set(person) - {"orcid", "name"}),
                    errors,
                    f"Unknown person field in meta.provenance.{field}.",
                )
        if "contributions" in provenance:
            link = provenance["contributions"]
            _require(
                isinstance(link, str) and bool(re.fullmatch(r"https?://[^\s]+", link)),
                errors,
                "meta.provenance.contributions must be an absolute HTTP(S) URI.",
            )
    else:
        errors.append("meta.provenance must be a mapping.")

    return errors


def validate_node_shape(node: Any, *, context: str) -> list[str]:
    """Check the field-level shape of a single node (not its position in the tree).

    ``level`` is free text (see module docstring): it is not checked against
    a fixed vocabulary, since the set of level names is intentionally open
    and varies per factorization.
    """

    errors: list[str] = []
    if not isinstance(node, dict):
        return [f"{context}: node must be a mapping."]

    unknown = set(node) - ALLOWED_NODE_FIELDS
    _require(not unknown, errors, f"{context}: unknown field(s): {sorted(unknown)}")

    missing = REQUIRED_NODE_FIELDS - node.keys()
    _require(not missing, errors, f"{context}: missing required field(s): {sorted(missing)}")

    label = node.get("label")
    _require(
        isinstance(label, str) and bool(label),
        errors,
        f"{context}: label must be a non-empty string.",
    )

    level = node.get("level")
    _require(
        isinstance(level, str) and bool(level),
        errors,
        f"{context}: level must be a non-empty string.",
    )

    code = node.get("code")
    _require(
        isinstance(code, str) and bool(BASE_CODE_RE.match(code or "")),
        errors,
        f"{context}: code {code!r} is not a valid HiTOP base code.",
    )

    kind = node.get("kind", "concept")
    _require(
        kind in NODE_KINDS, errors, f"{context}: kind {kind!r} must be one of {sorted(NODE_KINDS)}."
    )

    if kind == "partial":
        local_id = node.get("id")
        _require(
            isinstance(local_id, str) and bool(BASE_CODE_RE.fullmatch(local_id)),
            errors,
            f"{context}: partial nodes require an alphanumeric id.",
        )
    elif "id" in node:
        errors.append(f"{context}: id is only allowed for partial nodes.")
    if "mapping_note" in node:
        _require(
            kind == "partial"
            and isinstance(node["mapping_note"], str)
            and bool(node["mapping_note"].strip()),
            errors,
            f"{context}: mapping_note must be non-empty text on a partial node.",
        )

    if "bridge" in node:
        bridge = node["bridge"]
        _require(
            isinstance(bridge, list)
            and bool(bridge)
            and all(isinstance(item, str) and bool(item.strip()) for item in bridge),
            errors,
            f"{context}: bridge must be a non-empty list of non-blank strings.",
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


def _validate_bridge_targets(hierarchy: dict[str, Any], *, path: Path) -> list[str]:
    """Resolve exact labels within this tree, regardless of node kind or core labels."""
    nodes = [node for node, _ in iter_nodes(hierarchy) if isinstance(node, dict)]
    labels: dict[str, list[dict[str, Any]]] = {}
    for node in nodes:
        label = node.get("label")
        if isinstance(label, str):
            labels.setdefault(label, []).append(node)
    errors: list[str] = []
    for node in nodes:
        bridge = node.get("bridge")
        if not isinstance(bridge, list):
            continue
        seen: set[str] = set()
        for target in bridge:
            if not isinstance(target, str) or not target.strip():
                continue  # Shape validation reports these entries.
            context = f"{path.name}:{node.get('label', '<unlabeled>')}"
            if target in seen:
                errors.append(f"{context}: duplicate bridge target {target!r}.")
            seen.add(target)
            matches = labels.get(target, [])
            if not matches:
                suggestions = get_close_matches(target, labels, n=1, cutoff=0.6)
                hint = f" Did you mean {suggestions[0]!r}?" if suggestions else ""
                errors.append(
                    f"{context}: bridge target {target!r} does not exist in this tree.{hint}"
                )
            elif len(matches) > 1:
                errors.append(f"{context}: bridge target {target!r} is ambiguous in this tree.")
            if any(match is node for match in matches):
                errors.append(f"{context}: bridge target {target!r} is a self-reference.")
    return errors


def validate_hierarchy_document(
    record: Any,
    *,
    path: Path,
    core_class_names: set[str],
) -> list[str]:
    """Validate one loaded ``*_hierarchy.yaml`` document.

    Checks schema shape, that ``meta`` matches the file's directory/name,
    referential integrity of every concept ``code`` against the core
    ontology (``kind: collection`` nodes are exempt, since they name a
    factorization-local synthesis rather than a core Tier concept), and that
    no ``code`` repeats within one tree. Vertical ordering needs no check: a
    node's depth is defined by its position under ``children``, so a child
    is always exactly one step below its parent by construction. ``level``
    is not checked for consistency across the tree -- real HiTOP branches
    legitimately skip levels (see the module docstring), so the same label
    can occur at different depths. Returns a list of human-readable error
    strings; empty means valid.
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

    seen_identities: set[tuple[str, str]] = set()
    for node, _parent in iter_nodes(hierarchy):
        node_label = node.get("label", "<unlabeled>") if isinstance(node, dict) else "<invalid>"
        context = f"{path.name}:{node_label}"
        errors.extend(validate_node_shape(node, context=context))
        if not isinstance(node, dict):
            continue

        code = node.get("code")
        if isinstance(code, str):
            namespace = "core" if node.get("kind", "concept") == "concept" else "local"
            identifier = node.get("id", "") if node.get("kind") == "partial" else code
            identity = (namespace, identifier) if isinstance(identifier, str) else (namespace, "")
            if identity in seen_identities:
                errors.append(
                    f"{context}: {namespace} identity for code {code!r} "
                    "appears more than once in this tree."
                )
            else:
                seen_identities.add(identity)
            if node.get("kind", "concept") != "collection" and code not in core_class_names:
                errors.append(
                    f"{context}: code {code!r} does not exist as a class in ontology/hitop.ttl."
                )

    errors.extend(_validate_bridge_targets(hierarchy, path=path))
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


def check_labels_match_core(
    record: dict[str, Any],
    *,
    path: Path,
    core_labels: dict[str, set[str]],
) -> list[str]:
    """Allow factorization-local wording for concept and partial nodes.

    Retained as a compatibility hook for existing callers. Identity is asserted
    by kind=concept plus a validated core code, rather than label equality.
    Referential integrity remains enforced by validate_hierarchy_document.
    """
    return []
