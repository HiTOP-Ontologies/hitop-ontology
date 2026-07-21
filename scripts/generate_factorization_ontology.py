#!/usr/bin/env python3
"""Compile a HiTOP factorization hierarchy YAML into an RDF factorization ontology.

The script implements the generation half of the process described in
``docs/factorizations.md``:

* load and validate a ``<version>_hierarchy.yaml`` with the same rules used
  by ``validation/test_factorizations.py`` (``hitop.factorization.validate``)
* for every node, assert ``hitop:hasLevel`` as a free-text literal naming
  the role the node plays in this factorization
* for every parent-child edge, assert ``hitop:hasTier`` -- this alone
  determines the tree's vertical ordering, so no core Level lookup is
  needed to resolve a node's level
* for a ``kind: collection`` node (a factorization-local synthesis of
  several existing concepts, never a core Tier concept), assert
  ``rdf:type skos:Collection`` and mint its IRI inside this factorization's
  own namespace instead of the shared core namespace
* record ``provisional``/``bridge`` as ``skos:changeNote`` annotations
  (documentation only, never a structural edge)
* write an ``owl:Ontology`` header derived from the file's ``meta`` block
* copy each concept's ``rdfs:label`` (and ``rdfs:comment``, when present)
  from the core ontology onto its ``rdf:Description`` in this file, purely
  so a reader can tell what a node is without cross-referencing the core

The generated file references the stable HiTOP base codes from
``ontology/hitop.ttl`` by IRI; it never redefines a concept's ``rdf:type``
or ``rdfs:subClassOf``, and the core ontology remains the sole source of
truth for a concept's identity -- only the two human-readable annotation
fields above are copied in, for readability of the generated file itself.

The default output is RDF/XML (``<version>_factorization.rdf``), the
canonical hand-off format for ``scripts/rdf2ttl.py`` and
``scripts/rdf2owl.py``, which derive the Turtle and OWL/RDF-XML siblings
from it. Pass ``--format ttl`` or ``--format both`` to write Turtle
directly instead of (or in addition to) the RDF/XML file.

The RDF/XML is written with one flat ``<rdf:Description>`` block per
subject, in the same depth-first order as the hierarchy YAML, and every
``hitop:hasTier`` edge is always a plain ``rdf:resource`` reference. This is
deliberate: rdflib's built-in ``pretty-xml`` serializer "stripes" (nests)
whichever occurrence of a repeated subject it encounters first during its
own internal graph traversal and leaves bare references at every other
occurrence, which reads as if data were missing at the un-nested spot even
though the graph is complete. A flat, one-block-per-concept file avoids
that ambiguity entirely.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

from rdflib import RDF, RDFS, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, SKOS, XSD

from hitop.factorization import (
    load_core_class_local_names,
    load_hierarchy_document,
    validate_hierarchy_document,
)

HITOP = Namespace("http://purl.org/hitop#")
FACTORIZATION_NS = "http://purl.org/hitop/factorizations/"

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_ONTOLOGY_TTL = ROOT_DIR / "ontology" / "hitop.ttl"

_SERIALIZATION_BY_FORMAT = {"ttl": "turtle"}


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
        "--format",
        choices=["rdf", "ttl", "both"],
        default="rdf",
        help="Output serialization: RDF/XML (default, hand-off format for "
        "rdf2ttl.py/rdf2owl.py), Turtle, or both.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path (default: <version>_factorization.<rdf|ttl> next to the "
        "input file). Not valid with --format both, which always writes both "
        "default paths.",
    )
    return parser


def _default_output_path(input_yaml: Path, meta: dict, *, suffix: str) -> Path:
    return input_yaml.parent / f"{meta['version']}_factorization.{suffix}"


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


def _subject_iri(node: dict, *, factorization_iri: URIRef) -> URIRef:
    """Return the IRI for a node: the core namespace for a concept, else local."""

    if node.get("kind", "concept") == "collection":
        return URIRef(f"{factorization_iri}#{node['code']}")
    return HITOP[node["code"]]


def load_core_class_annotations(ontology_ttl: Path) -> dict[str, dict[str, Literal]]:
    """Return ``{code: {"label": Literal, "comment": Literal}}`` from the core ontology.

    Used only to copy each concept's ``rdfs:label``/``rdfs:comment`` onto its
    node in the generated factorization file, so the file is readable on its
    own. The core ontology stays the sole source of truth for these values;
    a concept's ``rdf:type``/``rdfs:subClassOf`` are never copied.
    """

    graph = Graph()
    graph.parse(str(ontology_ttl), format="turtle")
    prefix = str(HITOP)

    annotations: dict[str, dict[str, Literal]] = {}
    for cls in graph.subjects(RDF.type, OWL.Class):
        iri = str(cls)
        if not iri.startswith(prefix):
            continue
        entry: dict[str, Literal] = {}
        label = graph.value(cls, RDFS.label)
        if label is not None:
            entry["label"] = label
        comment = graph.value(cls, RDFS.comment)
        if comment is not None:
            entry["comment"] = comment
        if entry:
            annotations[iri[len(prefix) :]] = entry
    return annotations


def build_factorization_graph(
    record: dict, *, core_annotations: dict[str, dict[str, Literal]] | None = None
) -> tuple[Graph, list[URIRef]]:
    """Walk a validated hierarchy document and build its RDF factorization graph.

    Returns the graph together with the subject IRIs in the order they were
    first visited (the ontology header, then a depth-first walk of the
    hierarchy tree matching the YAML's own nesting) so a caller can render
    RDF/XML in that same, predictable order instead of rdflib's internal
    traversal order.
    """

    graph = Graph()
    graph.bind("hitop", HITOP)
    graph.bind("skos", SKOS)
    graph.bind("dcterms", DCTERMS)

    core_annotations = core_annotations or {}
    meta = record["meta"]
    factorization_iri = URIRef(f"{FACTORIZATION_NS}{meta['factorization_id']}/v{meta['version']}")
    _add_meta_header(graph, factorization_iri=factorization_iri, meta=meta)
    subject_order = [factorization_iri]

    hierarchy = record.get("hierarchy")
    if hierarchy is None:
        return graph, subject_order

    def _walk(node: dict, parent: dict | None) -> None:
        subject = _subject_iri(node, factorization_iri=factorization_iri)
        subject_order.append(subject)
        graph.add((subject, HITOP.hasLevel, Literal(node["level"])))

        if node.get("kind", "concept") == "collection":
            # A factorization-local synthesis of several existing concepts,
            # never a core Tier concept -- see docs/factorizations.md section 4.
            graph.add((subject, RDF.type, SKOS.Collection))
            graph.add((subject, RDFS.label, Literal(node["label"], lang="en")))
        else:
            annotation = core_annotations.get(node["code"], {})
            if "label" in annotation:
                graph.add((subject, RDFS.label, annotation["label"]))
            if "comment" in annotation:
                graph.add((subject, RDFS.comment, annotation["comment"]))

        if node.get("provisional"):
            graph.add((subject, SKOS.changeNote, Literal("provisional: true", lang="en")))
        bridge = node.get("bridge")
        if bridge:
            note = "Bridges: " + ", ".join(bridge)
            graph.add((subject, SKOS.changeNote, Literal(note, lang="en")))

        if parent is not None:
            parent_subject = _subject_iri(parent, factorization_iri=factorization_iri)
            graph.add((parent_subject, HITOP.hasTier, subject))

        for child in node.get("children") or []:
            _walk(child, node)

    _walk(hierarchy, None)
    return graph, subject_order


def serialize_flat_rdf_xml(graph: Graph, subject_order: list[URIRef]) -> str:
    """Serialize *graph* as RDF/XML with one flat ``<rdf:Description>`` per subject.

    Every subject in *subject_order* is rendered exactly once, in that order,
    listing all of its (predicate, object) pairs directly -- object
    resources are always ``rdf:resource`` references, never nested/striped
    descriptions. See the module docstring for why this matters here.

    Only the namespace prefixes actually used by a rendered element are
    declared, ignoring the many unrelated prefixes rdflib's namespace
    manager registers by default (brick, csvw, dcat, ...).
    """

    body_lines: list[str] = []
    used_prefixes: dict[str, str] = {"rdf": str(RDF)}
    for subject in subject_order:
        body_lines.append(f"  <rdf:Description rdf:about={quoteattr(str(subject))}>")
        for predicate, obj in graph.predicate_objects(subject):
            tag = graph.namespace_manager.qname(predicate)
            prefix, _, _local = tag.partition(":")
            used_prefixes.setdefault(prefix, str(graph.namespace_manager.store.namespace(prefix)))
            if isinstance(obj, URIRef):
                body_lines.append(f"    <{tag} rdf:resource={quoteattr(str(obj))}/>")
            else:
                attrs = ""
                if obj.language:
                    attrs = f" xml:lang={quoteattr(obj.language)}"
                elif obj.datatype:
                    attrs = f" rdf:datatype={quoteattr(str(obj.datatype))}"
                body_lines.append(f"    <{tag}{attrs}>{escape(str(obj))}</{tag}>")
        body_lines.append("  </rdf:Description>")

    lines = ['<?xml version="1.0" encoding="utf-8"?>', "<rdf:RDF"]
    for prefix, namespace in sorted(used_prefixes.items()):
        lines.append(f"  xmlns:{prefix}={quoteattr(namespace)}")
    lines.append(">")
    lines.extend(body_lines)
    lines.append("</rdf:RDF>")
    return "\n".join(lines) + "\n"


def generate(
    input_yaml: Path,
    *,
    ontology_ttl: Path,
    format: str = "rdf",
    output: Path | None = None,
) -> list[Path]:
    """Validate ``input_yaml`` and write the generated factorization file(s).

    ``format`` selects the serialization: ``"rdf"`` (RDF/XML, the default
    hand-off format for ``scripts/rdf2ttl.py``/``scripts/rdf2owl.py``),
    ``"ttl"`` (Turtle), or ``"both"``. ``output`` overrides the default path
    and is only valid for a single-format run.

    Raises ``GenerationError`` if the document fails validation. Returns the
    list of paths written.
    """

    if output is not None and format == "both":
        raise GenerationError("--output cannot be combined with --format both.")

    record = load_hierarchy_document(input_yaml)
    core_class_names = load_core_class_local_names(ontology_ttl)
    errors = validate_hierarchy_document(
        record,
        path=input_yaml,
        core_class_names=core_class_names,
    )
    if errors:
        raise GenerationError("; ".join(errors))

    core_annotations = load_core_class_annotations(ontology_ttl)
    graph, subject_order = build_factorization_graph(record, core_annotations=core_annotations)

    formats = ["rdf", "ttl"] if format == "both" else [format]
    written: list[Path] = []
    for one_format in formats:
        suffix = "rdf" if one_format == "rdf" else "ttl"
        output_path = output or _default_output_path(input_yaml, record["meta"], suffix=suffix)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if one_format == "rdf":
            output_path.write_text(serialize_flat_rdf_xml(graph, subject_order), encoding="utf-8")
        else:
            graph.serialize(destination=output_path, format=_SERIALIZATION_BY_FORMAT[one_format])
        written.append(output_path)
    return written


def main() -> int:
    """Run hierarchy-YAML-to-RDF/Turtle generation."""

    parser = build_parser()
    args = parser.parse_args()

    try:
        output_paths = generate(
            args.input_yaml,
            ontology_ttl=args.ontology,
            format=args.format,
            output=args.output,
        )
    except GenerationError as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, indent=2))
        return 1

    print(
        json.dumps(
            {
                "valid": True,
                "input": str(args.input_yaml),
                "output": [str(p) for p in output_paths],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
