#!/usr/bin/env python3
"""Compile a HiTOP factorization hierarchy YAML into D3-icicle-ready JSON.

Validates a ``<version>_hierarchy.yaml`` with the same rules used by
``validation/test_factorizations.py`` and ``generate_factorization_ontology.py``
(``hitop.factorization.validate``), then emits a minimal tree
(``label``/``level``/``code``/``kind``/``branch``/``color``/``children``)
suitable as the direct input to ``d3.hierarchy()`` + ``d3.partition()`` for
an icicle-style diagram. ``branch`` is the index of the node's top-level
ancestor (the root's direct child it descends from) and is constant across
an entire subtree, so a renderer can group an entire branch if it wants to.

``color`` is assigned by the shared, cross-factorization color rule in
``hitop.factorization.colors`` (see that module and docs/factorizations.md
for the full rule): every Factor/Superspectrum/Spectrum/Subfactor node
draws its own color from one fixed 24-color palette, spread evenly across
the tree; Component/Trait nodes take a lightened shade of their own
parent's color. A renderer can use ``color`` directly and does not need to
reimplement the rule. The root node's ``branch`` is ``null``.

If ``hierarchy`` is ``null`` (a placeholder factorization whose tree has not
been curated yet, see ``docs/factorizations.md`` section 7), the output is
``{"meta": {...}, "hierarchy": null}`` so a renderer can show an explicit
"not yet populated" state instead of an empty diagram.

The generated file is written next to the input, alongside the
``<version>_factorization.rdf``/``.ttl``/``.owl`` siblings, and is treated the
same way: generated, committed, and never hand-edited. Re-run this script
whenever the source ``hierarchy.yaml`` changes.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from hitop.factorization import (
    annotate_colors,
    load_core_class_local_names,
    load_hierarchy_document,
    validate_hierarchy_document,
)

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_ONTOLOGY_TTL = ROOT_DIR / "ontology" / "hitop.ttl"


class GenerationError(ValueError):
    """Raised when the input hierarchy YAML fails validation."""


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser."""

    parser = argparse.ArgumentParser(
        description="Generate D3-icicle diagram JSON from a factorization hierarchy YAML."
    )
    parser.add_argument(
        "input_yaml",
        type=Path,
        help="Path to a factorizations/<id>/v<N>/<version>_hierarchy.yaml file.",
    )
    parser.add_argument(
        "--ontology",
        type=Path,
        default=DEFAULT_ONTOLOGY_TTL,
        help="Core ontology Turtle file to validate concept codes against.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path (default: <version>_diagram.json next to the input file).",
    )
    return parser


def _default_output_path(input_yaml: Path, meta: dict[str, Any]) -> Path:
    return input_yaml.parent / f"{meta['version']}_diagram.json"


def _node_to_dict(node: dict[str, Any], *, branch: int | None) -> dict[str, Any]:
    out: dict[str, Any] = {
        "label": node["label"],
        "level": node["level"],
        "code": node["code"],
        "kind": node.get("kind", "concept"),
        "branch": branch,
        "color": node["color"],
    }
    for field in ("id", "mapping_note"):
        if field in node:
            out[field] = node[field]
    if "bridge" in node:
        out["bridge"] = node["bridge"]
    if node.get("provisional"):
        out["provisional"] = True

    children = node.get("children") or []
    if children:
        out["children"] = [_node_to_dict(child, branch=branch) for child in children]
    return out


def build_diagram_tree(hierarchy: dict[str, Any]) -> dict[str, Any]:
    """Convert a validated ``hierarchy`` mapping into the D3-icicle JSON shape.

    Every direct child of the root starts a new ``branch`` index; that index
    is then held constant through the rest of its subtree, so a renderer can
    color an entire top-level branch (e.g. one Spectrum and everything under
    it) with a single color, as in the official HiTOP figure. The root itself
    gets ``branch: null`` since it has no single-color ancestor branch.
    """

    root = _node_to_dict(hierarchy, branch=None)
    top_children = hierarchy.get("children") or []
    if top_children:
        root["children"] = [
            _node_to_dict(child, branch=index) for index, child in enumerate(top_children)
        ]
    return root


def generate(
    input_yaml: Path,
    *,
    ontology_ttl: Path,
    output: Path | None = None,
) -> Path:
    """Validate ``input_yaml`` and write the generated diagram JSON.

    Raises ``GenerationError`` if the document fails validation. Returns the
    path written.
    """

    record = load_hierarchy_document(input_yaml)
    core_class_names = load_core_class_local_names(ontology_ttl)
    errors = validate_hierarchy_document(
        record,
        path=input_yaml,
        core_class_names=core_class_names,
    )
    if errors:
        raise GenerationError("; ".join(errors))

    meta = record["meta"]
    hierarchy = record.get("hierarchy")
    if hierarchy is not None:
        hierarchy = annotate_colors(hierarchy)
    payload = {
        "meta": {
            "factorization_id": meta["factorization_id"],
            "version": meta["version"],
            "label": meta["label"],
            "status": meta["status"],
        },
        "hierarchy": build_diagram_tree(hierarchy) if hierarchy is not None else None,
    }

    output_path = output or _default_output_path(input_yaml, meta)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    output_path.write_text(rendered, encoding="utf-8")
    return output_path


def main() -> int:
    """Run hierarchy-YAML-to-diagram-JSON generation."""

    parser = build_parser()
    args = parser.parse_args()

    try:
        output_path = generate(
            args.input_yaml,
            ontology_ttl=args.ontology,
            output=args.output,
        )
    except GenerationError as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, indent=2))
        return 1

    print(
        json.dumps(
            {"valid": True, "input": str(args.input_yaml), "output": str(output_path)},
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
