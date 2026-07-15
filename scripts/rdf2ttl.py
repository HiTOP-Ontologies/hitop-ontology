#!/usr/bin/env python3
"""Convert the HiTOP RDF/XML ontology export to Turtle.

The converter reads the canonical RDF/XML source, removes invalid ontology-level
definition annotations, normalizes literal whitespace, serializes the graph as
Turtle, and validates the generated Turtle before writing it to disk.
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

from rdflib import OWL, RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT_DIR / "ontology" / "hitop.rdf"
DEFAULT_OUTPUT = ROOT_DIR / "ontology" / "hitop.ttl"

HITOP = Namespace("http://purl.org/hitop#")
OBO = Namespace("http://purl.obolibrary.org/obo/")
DC = Namespace("http://purl.org/dc/elements/1.1/")
DCTERMS = Namespace("http://purl.org/dc/terms/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
IAO_DEFINITION_PROPERTIES = (
    OBO["IAO_0000115"],
    URIRef("http://purl.obolibrary.org/obo/iaoIAO_0000115"),
)


def parse_rdf_xml(input_path: Path) -> Graph:
    """Parse RDF/XML while suppressing rdflib's noisy invalid-literal traceback."""

    # rdflib logs invalid literal diagnostics during parsing even when callers
    # normalize those literals afterward; keep the CLI output release-oriented.
    previous_level = logging.getLogger("rdflib.term").level
    logging.getLogger("rdflib.term").setLevel(logging.CRITICAL)
    try:
        graph = Graph()
        graph.parse(input_path, format="xml")
        return graph
    finally:
        logging.getLogger("rdflib.term").setLevel(previous_level)


def bind_namespaces(graph: Graph) -> None:
    """Bind the namespace prefixes expected in generated Turtle output."""

    graph.bind("hitop", HITOP)
    graph.bind("obo", OBO)
    graph.bind("dc", DC)
    graph.bind("dcterms", DCTERMS)
    graph.bind("foaf", FOAF)
    graph.bind("rdf", RDF)
    graph.bind("rdfs", RDFS)
    graph.bind("owl", OWL)
    graph.bind("xsd", XSD)


def normalize_invalid_decimal_literals(graph: Graph) -> int:
    """Convert invalid ``xsd:decimal`` literals to plain string literals."""

    changed = 0
    for subject, predicate, obj in list(graph):
        if not isinstance(obj, Literal) or obj.datatype != XSD.decimal:
            continue
        try:
            Decimal(str(obj))
        except InvalidOperation:
            # Preserve the lexical value but remove the invalid datatype so the
            # serialized graph can be parsed by strict downstream tooling.
            graph.remove((subject, predicate, obj))
            graph.add((subject, predicate, Literal(str(obj), lang=obj.language)))
            changed += 1
    return changed


def remove_invalid_ontology_definitions(graph: Graph) -> int:
    """Remove empty or malformed ontology-level IAO definition annotations."""

    removed = 0
    for ontology in graph.subjects(RDF.type, OWL.Ontology):
        for definition_property in IAO_DEFINITION_PROPERTIES:
            for _, predicate, obj in list(graph.triples((ontology, definition_property, None))):
                is_empty_literal = isinstance(obj, Literal) and str(obj).strip() == ""
                is_malformed_iao_uri = (
                    not isinstance(obj, Literal)
                    and re.search(r"\.owl$", str(obj)) is not None
                    and "iao" in str(obj)
                )
                if is_empty_literal or is_malformed_iao_uri:
                    graph.remove((ontology, predicate, obj))
                    removed += 1
    return removed


def normalize_literal_whitespace(graph: Graph) -> int:
    """Collapse newlines and repeated whitespace in literal values."""

    changed = 0
    for subject, predicate, obj in list(graph):
        if not isinstance(obj, Literal):
            continue
        value = str(obj)
        if "\n" not in value and "\r" not in value:
            continue
        cleaned = re.sub(r"\s+", " ", value.strip())
        graph.remove((subject, predicate, obj))
        graph.add((subject, predicate, Literal(cleaned, lang=obj.language, datatype=obj.datatype)))
        changed += 1
    return changed


_LITERAL_TOKEN_RE = re.compile(r'"""(?:[^"\\]|\\.|"(?!""))*"""|"(?:[^"\\]|\\.)*"')


def _sub_outside_literals(pattern: re.Pattern[str], repl: str, line: str) -> str:
    """Apply ``pattern.sub(repl, ...)`` only to the parts of *line* outside quoted literals.

    Turtle punctuation-spacing cleanup must never touch the inside of a
    string literal -- otherwise prose commas/periods in an ``rdfs:comment``
    or definition get a spurious space inserted before them. This walks the
    line, leaving each quoted token (short ``"..."`` or long ``\"\"\"...\"\"\"``)
    untouched and only rewriting the Turtle syntax between them.
    """

    parts: list[str] = []
    last_end = 0
    for match in _LITERAL_TOKEN_RE.finditer(line):
        start, end = match.span()
        parts.append(pattern.sub(repl, line[last_end:start]))
        parts.append(line[start:end])
        last_end = end
    parts.append(pattern.sub(repl, line[last_end:]))
    return "".join(parts)


def format_turtle(turtle_data: str) -> str:
    """Apply conservative formatting cleanup to rdflib Turtle output."""

    turtle_data = turtle_data.encode("utf-8").decode("utf-8-sig")
    turtle_data = re.sub(r"^\ufeff", "", turtle_data)
    turtle_data = re.sub(r"@prefix\s+([a-zA-Z0-9_-]+)\s+:", r"@prefix \1:", turtle_data)
    turtle_data = re.sub(r'"""\s+', '"""', turtle_data)
    turtle_data = re.sub(r'\s+"""', '"""', turtle_data)

    formatted_lines: list[str] = []
    for line in turtle_data.splitlines():
        # rdflib serialization is valid but not review-friendly; this pass keeps
        # diffs stable without changing triples. Each substitution skips over
        # quoted literal content so prose punctuation is never rewritten.
        line = line.replace("\t", " ")
        line = _sub_outside_literals(re.compile(r"\s*;\s*"), " ; ", line)
        line = _sub_outside_literals(re.compile(r"\s*,\s*"), " , ", line)
        line = _sub_outside_literals(re.compile(r"\s*\.\s*$"), " .", line)
        line = _sub_outside_literals(re.compile(r"\s{2,}"), " ", line)

        if re.match(r"^\s*(rdfs:|owl:|hitop:|obo:|xsd:|skos:|dc:|dcterms:|foaf:)", line):
            line = "    " + line.strip()
        formatted_lines.append(line.rstrip())

    cleaned_lines: list[str] = []
    for line in formatted_lines:
        cleaned_lines.append(line)
        if line.strip().endswith(" ."):
            cleaned_lines.append("")

    return re.sub(r"\n{3,}", "\n\n", "\n".join(cleaned_lines).strip()) + "\n"


def convert_rdf_to_turtle(input_path: Path, output_path: Path) -> int:
    """Convert ``input_path`` RDF/XML to validated Turtle at ``output_path``."""

    graph = parse_rdf_xml(input_path)
    bind_namespaces(graph)

    invalid_decimals = normalize_invalid_decimal_literals(graph)
    removed = remove_invalid_ontology_definitions(graph)
    normalized = normalize_literal_whitespace(graph)
    turtle_data = format_turtle(graph.serialize(format="turtle"))

    validation_graph = Graph()
    validation_graph.parse(data=turtle_data, format="turtle")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(turtle_data, encoding="utf-8", newline="\n")

    print(f"Loaded {len(graph)} RDF/XML triples from {input_path}")
    print(f"Normalized {invalid_decimals} invalid decimal literal(s)")
    print(f"Removed {removed} invalid ontology definition annotation(s)")
    print(f"Normalized {normalized} literal value(s)")
    print(f"Validated {len(validation_graph)} Turtle triples")
    print(f"Wrote {output_path}")
    return len(validation_graph)


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for RDF/XML to Turtle conversion."""

    parser = argparse.ArgumentParser(description="Convert HiTOP RDF/XML to Turtle.")
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
        help=f"Output Turtle path (default: {DEFAULT_OUTPUT}).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point returning a process exit status."""

    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        convert_rdf_to_turtle(args.input, args.output)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
