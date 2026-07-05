#!/usr/bin/env python3
"""Compile a HiTOP factorization hierarchy YAML into an RDF factorization ontology.

The script implements the generation half of the process described in
``docs/factorizations.md``:

* load and validate a ``<version>_hierarchy.yaml`` with the same rules used
  by ``validation/test_factorizations.py`` (``hitop.factorization.validate``)
* for every node, assert ``hitop:hasLevelType`` against the matching core
  Level subclass
* for every parent-child edge, assert ``hitop:hasTier``
* record ``provisional``/``bridge`` as ``skos:changeNote`` annotations
  (documentation only, never a structural edge)
* write an ``owl:Ontology`` header derived from the file's ``meta`` block

The generated file references the stable HiTOP base codes from
``ontology/hitop.ttl`` by IRI; it never redefines, copies, or duplicates
core class content.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rdflib import RDF, RDFS, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, SKOS, XSD

from hitop.factorization import (
    load_core_class_local_names,
    load_hierarchy_document,
    load_level_local_codes,
    load_level_ranks,
    validate_hierarchy_document,
)

HITOP = Namespace("http://purl.org/hitop#")
FACTORIZATION_NS = "http://purl.org/hitop/factorizations/"

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_ONTOLOGY_TTL = ROOT_DIR / "ontology" / "hitop.ttl"


class GenerationError(ValueError):
    """Raised when the input hierarchy YAML fails validation."""


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser."""

    parser = argparse.ArgumentParser(
        description="Generate an RDF factorization ontology from a hierarchy YAML."
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
        help="Core ontology Turtle file to validate codes and Level types against.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output Turtle path (default: <version>_factorization.ttl next to the input file).",
    )
    return parser


def _default_output_path(input_yaml: Path, meta: dict) -> Path:
    return input_yaml.parent / f"{meta['version']}_factorization.ttl"


def _add_meta_header(graph: Graph, *, factorization_iri: URIRef, meta: dict) -> None:
    graph.add((factorization_iri, RDF.type, OWL.Ontology))
    graph.add((factorization_iri, RDFS.label, Literal(meta["label"], lang="en")))
    graph.add((factorization_iri, OWL.versionInfo, Literal(meta["version"])))
    graph.add((factorization_iri, OWL.imports, URIRef(meta["based_on"]["ontology_iri"])))
    graph.add(
        (
            factorization_iri,
            DCTERMS.isVersionOf,
            Literal(meta["based_on"]["ontology_version"]),
        )
    )
    graph.add((factorization_iri, DCTERMS.creator, Literal(meta["provenance"]["created_by"])))
    graph.add(
        (
            factorization_iri,
            DCTERMS.created,
            Literal(meta["provenance"]["created_at"], datatype=XSD.date),
        )
    )
    graph.add((factorization_iri, SKOS.changeNote, Literal(f"status: {meta['status']}", lang="en")))
    if meta.get("source"):
        graph.add((factorization_iri, DCTERMS.source, Literal(meta["source"])))
    if meta.get("paper"):
        graph.add((factorization_iri, DCTERMS.bibliographicCitation, Literal(meta["paper"])))


def build_factorization_graph(record: dict, *, level_codes: dict[str, str]) -> Graph:
    """Walk a validated hierarchy document and build its RDF factorization graph."""

    graph = Graph()
    graph.bind("hitop", HITOP)
    graph.bind("skos", SKOS)
    graph.bind("dcterms", DCTERMS)

    meta = record["meta"]
    factorization_iri = URIRef(
        f"{FACTORIZATION_NS}{meta['factorization_id']}/v{meta['version']}"
    )
    _add_meta_header(graph, factorization_iri=factorization_iri, meta=meta)

    hierarchy = record.get("hierarchy")
    if hierarchy is None:
        return graph

    def _walk(node: dict, parent: dict | None) -> None:
        subject = HITOP[node["code"]]
        level_class = HITOP[level_codes[node["level"]]]
        graph.add((subject, HITOP.hasLevelType, level_class))

        if node.get("provisional"):
            graph.add(
                (subject, SKOS.changeNote, Literal("provisional: true", lang="en"))
            )
        bridge = node.get("bridge")
        if bridge:
            note = "Bridges: " + ", ".join(bridge)
            graph.add((subject, SKOS.changeNote, Literal(note, lang="en")))

        if parent is not None:
            parent_subject = HITOP[parent["code"]]
            graph.add((parent_subject, HITOP.hasTier, subject))

        for child in node.get("children") or []:
            _walk(child, node)

    _walk(hierarchy, None)
    return graph


def generate(input_yaml: Path, *, ontology_ttl: Path, output: Path | None) -> Path:
    """Validate ``input_yaml`` and write the generated factorization Turtle file.

    Raises ``GenerationError`` if the document fails validation. Returns the
    path the Turtle file was written to.
    """

    record = load_hierarchy_document(input_yaml)
    core_class_names = load_core_class_local_names(ontology_ttl)
    level_ranks = load_level_ranks(ontology_ttl)
    errors = validate_hierarchy_document(
        record,
        path=input_yaml,
        core_class_names=core_class_names,
        level_ranks=level_ranks,
    )
    if errors:
        raise GenerationError("; ".join(errors))

    level_codes = load_level_local_codes(ontology_ttl)
    graph = build_factorization_graph(record, level_codes=level_codes)

    output_path = output or _default_output_path(input_yaml, record["meta"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    graph.serialize(destination=output_path, format="turtle")
    return output_path


def main() -> int:
    """Run hierarchy-YAML-to-Turtle generation."""

    parser = build_parser()
    args = parser.parse_args()

    try:
        output_path = generate(args.input_yaml, ontology_ttl=args.ontology, output=args.output)
    except GenerationError as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, indent=2))
        return 1

    print(
        json.dumps(
            {
                "valid": True,
                "input": str(args.input_yaml),
                "output": str(output_path),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
