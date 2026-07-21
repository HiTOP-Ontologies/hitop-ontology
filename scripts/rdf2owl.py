#!/usr/bin/env python3
"""Convert the HiTOP RDF/XML ontology export to cleaned OWL/RDF XML.

The converter normalizes the ontology declaration, merges duplicate ontology
nodes, cleans annotation literals, preserves class-level ``rdfs:isDefinedBy``
references, and writes an OWL/RDF XML file suitable for downstream ROBOT
validation workflows.
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
import warnings
from decimal import Decimal, InvalidOperation
from pathlib import Path

from lxml import etree
from rdflib import OWL, RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT_DIR / "ontology" / "hitop.rdf"
DEFAULT_OUTPUT = ROOT_DIR / "ontology" / "hitop.owl"
CANONICAL_ONTOLOGY_IRI = URIRef("http://purl.org/hitop")

OBO = Namespace("http://purl.obolibrary.org/obo/")
DC = Namespace("http://purl.org/dc/elements/1.1/")
DCTERMS = Namespace("http://purl.org/dc/terms/")
XML_NS = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "owl": "http://www.w3.org/2002/07/owl#",
}


def _suppress_rdflib_bnode_warning() -> None:
    """Hide a known rdflib serializer warning for anonymous ontology nodes."""

    warnings.filterwarnings(
        "ignore",
        message="Assertions on rdflib.term.BNode",
        category=UserWarning,
        module="rdflib.plugins.serializers.rdfxml",
    )


def parse_rdf_xml(input_path: Path) -> Graph:
    """Parse RDF/XML while suppressing rdflib's noisy invalid-literal traceback."""

    # Invalid source literals are normalized after parsing; suppress the parser
    # logger here so the CLI reports only actionable conversion results.
    previous_level = logging.getLogger("rdflib.term").level
    logging.getLogger("rdflib.term").setLevel(logging.CRITICAL)
    try:
        graph = Graph()
        graph.parse(input_path, format="xml")
        return graph
    finally:
        logging.getLogger("rdflib.term").setLevel(previous_level)


def normalize_invalid_decimal_literals(graph: Graph) -> int:
    """Convert invalid ``xsd:decimal`` literals to plain string literals."""

    changed = 0
    for subject, predicate, obj in list(graph):
        if not isinstance(obj, Literal) or obj.datatype != XSD.decimal:
            continue
        try:
            Decimal(str(obj))
        except InvalidOperation:
            # Retain the original lexical value while removing a datatype that
            # makes downstream OWL/RDF XML validation fail.
            graph.remove((subject, predicate, obj))
            graph.add((subject, predicate, Literal(str(obj), lang=obj.language)))
            changed += 1
    return changed


def is_primary_ontology_ref(graph: Graph, node: object) -> bool:
    """Return ``True`` when ``node`` references the primary ontology."""

    return (node, RDF.type, OWL.Ontology) in graph or str(node).rstrip("#/") == str(
        CANONICAL_ONTOLOGY_IRI
    )


def ensure(graph: Graph, subject: URIRef, property_iri: URIRef, value: object) -> None:
    """Add a metadata triple only when the subject lacks that property."""

    if (subject, property_iri, None) not in graph:
        graph.add((subject, property_iri, value))


def clean_literal(text: str) -> str:
    """Collapse repeated whitespace inside an annotation literal."""

    return re.sub(r"\s+", " ", text.strip())


def select_primary_ontology_node(graph: Graph) -> URIRef:
    """Return the primary ontology node, creating one when absent."""

    ontology_nodes = [subject for subject, _, _ in graph.triples((None, RDF.type, OWL.Ontology))]
    for node in ontology_nodes:
        if str(node).rstrip("#/") == str(CANONICAL_ONTOLOGY_IRI):
            return node
    if ontology_nodes:
        return ontology_nodes[0]

    graph.add((CANONICAL_ONTOLOGY_IRI, RDF.type, OWL.Ontology))
    return CANONICAL_ONTOLOGY_IRI


def merge_duplicate_ontology_nodes(graph: Graph, primary: URIRef) -> int:
    """Merge non-primary ontology nodes into ``primary`` and return the count."""

    merged = 0
    ontology_nodes = [subject for subject, _, _ in graph.triples((None, RDF.type, OWL.Ontology))]
    for duplicate in [node for node in ontology_nodes if node != primary]:
        # Move outgoing and incoming triples so metadata survives while the
        # release artifact exposes a single canonical ontology declaration.
        for _, predicate, obj in list(graph.triples((duplicate, None, None))):
            graph.add((primary, predicate, obj))
            graph.remove((duplicate, predicate, obj))
        for subject, predicate, _ in list(graph.triples((None, None, duplicate))):
            graph.add((subject, predicate, primary))
            graph.remove((subject, predicate, duplicate))
        graph.remove((duplicate, RDF.type, OWL.Ontology))
        merged += 1
    return merged


def collect_and_remove_is_defined_by(graph: Graph) -> set[str]:
    """Remove primary ontology references and return affected class IRIs."""

    classes_with_reference: set[str] = set()
    for subject, predicate, obj in list(graph.triples((None, RDFS.isDefinedBy, None))):
        if is_primary_ontology_ref(graph, obj):
            # rdflib may serialize ontology-level self references in a form that
            # is hard to preserve; restore them in XML after serialization.
            classes_with_reference.add(str(subject))
            graph.remove((subject, predicate, obj))
    return classes_with_reference


def ensure_ontology_metadata(graph: Graph, primary: URIRef) -> None:
    """Ensure required ontology metadata triples are present."""

    title = "Hierarchical Taxonomy of Psychopathology (HiTOP) Ontology"
    description = (
        "The HiTOP ontology implements a structured representation of the "
        "Hierarchical Taxonomy of Psychopathology. It supports an open and "
        "extensible framework for modeling mental health dimensions, factor "
        "structures, and taxonomy variants."
    )
    ensure(graph, primary, RDFS.label, Literal(title, lang="en"))
    ensure(graph, primary, DC["title"], Literal(title, lang="en"))
    ensure(graph, primary, DC["description"], Literal(description, lang="en"))
    ensure(graph, primary, DCTERMS["license"], URIRef("https://opensource.org/licenses/MIT"))
    ensure(graph, primary, OWL.versionInfo, Literal("0.1.0"))


def force_canonical_ontology_declaration(graph: Graph) -> None:
    """Remove anonymous ontology nodes and set the canonical ontology IRI."""

    for subject in list(graph.subjects(RDF.type, OWL.Ontology)):
        if isinstance(subject, URIRef) and str(subject).startswith("http"):
            continue
        graph.remove((subject, None, None))

    graph.set((CANONICAL_ONTOLOGY_IRI, RDF.type, OWL.Ontology))
    graph.set(
        (
            CANONICAL_ONTOLOGY_IRI,
            DC["title"],
            Literal("Hierarchical Taxonomy of Psychopathology (HiTOP) Ontology", lang="en"),
        )
    )
    graph.set(
        (
            CANONICAL_ONTOLOGY_IRI,
            DC["description"],
            Literal(
                "Implements a structured representation of the Hierarchical Taxonomy "
                "of Psychopathology (HiTOP) for modeling mental health dimensions, "
                "factor structures, and taxonomy variants.",
                lang="en",
            ),
        )
    )
    graph.set(
        (CANONICAL_ONTOLOGY_IRI, DC["license"], URIRef("https://opensource.org/licenses/MIT"))
    )
    graph.set(
        (
            CANONICAL_ONTOLOGY_IRI,
            DCTERMS["license"],
            URIRef("https://opensource.org/licenses/MIT"),
        )
    )


def clean_annotation_literals(graph: Graph) -> int:
    """Normalize annotation literal whitespace and return the changed count."""

    changed = 0
    properties = [
        RDFS.label,
        RDFS.comment,
        DC["description"],
        DCTERMS["description"],
        OBO["IAO_0000111"],
        OBO["IAO_0000115"],
        OBO["IAO_0000602"],
    ]
    for property_iri in properties:
        for subject, predicate, literal in list(graph.triples((None, property_iri, None))):
            if not isinstance(literal, Literal):
                continue
            cleaned = clean_literal(str(literal))
            if cleaned == str(literal):
                continue
            graph.remove((subject, predicate, literal))
            graph.add((subject, predicate, Literal(cleaned, lang=literal.language)))
            changed += 1
    return changed


def find_class(root: etree._Element, iri: str) -> list[etree._Element]:
    """Find OWL class XML nodes by their ``rdf:about`` IRI."""

    return root.xpath(f"//owl:Class[@rdf:about='{iri}']", namespaces=XML_NS)


def add_simple_ref(element: etree._Element, namespace: str, tag: str, iri: str) -> bool:
    """Append ``<namespace:tag rdf:resource='iri'/>`` when it is absent."""

    qualified_tag = etree.QName(XML_NS[namespace], tag)
    existing = element.xpath(
        f"./{namespace}:{tag}[@rdf:resource='{iri}']",
        namespaces=XML_NS,
    )
    if existing:
        return False
    child = etree.Element(qualified_tag)
    child.set(etree.QName(XML_NS["rdf"], "resource"), iri)
    element.append(child)
    return True


def restore_is_defined_by(output_path: Path, class_iris: set[str]) -> int:
    """Restore removed ``rdfs:isDefinedBy`` references in serialized XML."""

    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(output_path), parser)
    root = tree.getroot()

    added = 0
    ontology_iri = str(CANONICAL_ONTOLOGY_IRI)
    for iri in sorted(class_iris):
        nodes = find_class(root, iri)
        if nodes and add_simple_ref(nodes[0], "rdfs", "isDefinedBy", ontology_iri):
            added += 1

    tree.write(str(output_path), encoding="utf-8", xml_declaration=True, pretty_print=True)
    return added


def convert_rdf_to_owl(input_path: Path, output_path: Path) -> int:
    """Convert ``input_path`` RDF/XML to cleaned OWL/RDF XML at ``output_path``.

    ``ensure_ontology_metadata`` and ``force_canonical_ontology_declaration``
    hardcode the core HiTOP ontology's own title, description, and IRI, so
    they only run when ``input_path`` actually declares that canonical
    ontology. A factorization file (or any other RDF/XML with its own,
    different ``owl:Ontology`` IRI) is converted without those two steps, so
    its own header is preserved instead of being overwritten with the core's.
    """

    _suppress_rdflib_bnode_warning()
    graph = parse_rdf_xml(input_path)

    invalid_decimals = normalize_invalid_decimal_literals(graph)
    primary = select_primary_ontology_node(graph)
    merged = merge_duplicate_ontology_nodes(graph, primary)
    classes_with_is_defined_by = collect_and_remove_is_defined_by(graph)
    is_core_ontology = str(primary).rstrip("#/") == str(CANONICAL_ONTOLOGY_IRI)
    if is_core_ontology:
        ensure_ontology_metadata(graph, primary)
        force_canonical_ontology_declaration(graph)
    cleaned_literals = clean_annotation_literals(graph)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    graph.serialize(destination=str(output_path), format="pretty-xml", encoding="utf-8")
    # XML post-processing is intentionally last because rdflib owns graph
    # semantics while lxml gives deterministic control over selected elements.
    restored = restore_is_defined_by(output_path, classes_with_is_defined_by)

    print(f"Loaded {len(graph)} RDF/XML triples from {input_path}")
    print(f"Normalized {invalid_decimals} invalid decimal literal(s)")
    print(f"Merged {merged} duplicate ontology node(s)")
    print(f"Cleaned {cleaned_literals} annotation literal(s)")
    print(f"Restored {restored} rdfs:isDefinedBy reference(s)")
    print(f"Wrote {output_path}")
    return len(graph)


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for RDF/XML to OWL conversion."""

    parser = argparse.ArgumentParser(description="Convert HiTOP RDF/XML to cleaned OWL/RDF XML.")
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Input RDF/XML path (default: {DEFAULT_INPUT}).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output OWL/RDF XML path (default: {DEFAULT_OUTPUT}).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point returning a process exit status."""

    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        convert_rdf_to_owl(args.input, args.output)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
