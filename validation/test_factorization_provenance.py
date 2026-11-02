"""Verify identified factorization contributors and lossless RDF conversions."""

import copy
import json
import runpy
import socket
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import jsonschema
import yaml
from rdflib import OWL, RDF, Graph, Namespace, URIRef
from rdflib.compare import isomorphic

from hitop.factorization import validate_meta

ROOT = Path(__file__).resolve().parents[1]
DCTERMS = Namespace("http://purl.org/dc/terms/")
PROV = Namespace("http://www.w3.org/ns/prov#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
HITOP = Namespace("http://purl.org/hitop#")
ROGERIO = "https://orcid.org/0000-0002-4505-4593"
ANDRE = "https://orcid.org/0000-0002-8588-7784"


class FactorizationProvenanceTests(unittest.TestCase):
    """Check metadata generation, rejection of bad identities and offline conversion."""

    def setUp(self) -> None:
        self.generator = runpy.run_path(str(ROOT / "scripts/generate_factorization_ontology.py"))
        self.meta = {
            "factorization_id": "example",
            "version": "V1test",
            "label": "Example factorization",
            "status": "draft",
            "based_on": {"ontology_iri": "http://purl.org/hitop", "ontology_version": "0.1.0"},
            "provenance": {
                "created_by": [{"orcid": ROGERIO, "name": "Rogério Blitz"}],
                "contributors": [{"orcid": ANDRE, "name": "André Kerber"}],
                "contributions": "http://purl.org/hitop/contributions",
                "created_at": "2026-07-03",
            },
        }
        self.path = Path("factorizations/example/v1/V1test_hierarchy.yaml")

    def test_metadata_and_both_converters_preserve_factorization_graph_offline(self) -> None:
        """Do not rewrite factorization identity, people, imports or structure during conversion."""
        graph, order = self.generator["build_factorization_graph"](
            {
                "meta": self.meta,
                "hierarchy": {
                    "label": "Example group",
                    "level": "Factor",
                    "code": "COLLexample",
                    "kind": "collection",
                },
            }
        )
        ontology = order[0]
        self.assertEqual(set(graph.objects(ontology, DCTERMS.creator)), {URIRef(ROGERIO)})
        self.assertEqual(set(graph.objects(ontology, DCTERMS.contributor)), {URIRef(ANDRE)})
        with (
            tempfile.TemporaryDirectory() as temporary,
            patch.object(socket, "create_connection", side_effect=AssertionError("Network access")),
            patch.object(socket.socket, "connect", side_effect=AssertionError("Network access")),
            patch.object(socket, "getaddrinfo", side_effect=AssertionError("Network access")),
        ):
            source = Path(temporary) / "factorization.rdf"
            source.write_text(self.generator["serialize_flat_rdf_xml"](graph, order))
            self.assertTrue(isomorphic(graph, Graph().parse(source, format="xml")))
            for name, syntax in (("rdf2ttl.py", "turtle"), ("rdf2owl.py", "xml")):
                converter = runpy.run_path(str(ROOT / "scripts" / name))
                output = Path(temporary) / name
                self.assertEqual(
                    converter["main"](["--input", str(source), "--output", str(output)]), 0
                )
                converted = Graph().parse(output, format=syntax)
                self.assertTrue(isomorphic(graph, converted), name)
                self.assertEqual(set(converted.subjects(RDF.type, OWL.Ontology)), {ontology})

    def test_metadata_only_preserves_existing_structure_and_full_generation_still_rejects_it(
        self,
    ) -> None:
        """Metadata refresh must not pretend to validate a hierarchy containing unknown codes."""
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary) / "example/v1"
            folder.mkdir(parents=True)
            source = folder / "V1test_hierarchy.yaml"
            record = {
                "meta": self.meta,
                "hierarchy": {"label": "Unknown", "level": "Factor", "code": "UNKNOWN"},
            }
            source.write_text(yaml.safe_dump(record))
            graph, order = self.generator["build_factorization_graph"](record)
            rdf = folder / "V1test_factorization.rdf"
            rdf.write_text(self.generator["serialize_flat_rdf_xml"](graph, order))
            record["meta"]["provenance"]["created_by"] = [{"orcid": ANDRE, "name": "André Kerber"}]
            source.write_text(yaml.safe_dump(record))
            with self.assertRaises(self.generator["GenerationError"]):
                self.generator["generate"](source, ontology_ttl=ROOT / "ontology/hitop.ttl")
            self.generator["generate"](
                source, ontology_ttl=ROOT / "ontology/hitop.ttl", metadata_only=True
            )
            updated = Graph().parse(rdf, format="xml")
            for predicate in (HITOP.hasLevel, HITOP.hasTier):
                self.assertEqual(
                    set(graph.triples((None, predicate, None))),
                    set(updated.triples((None, predicate, None))),
                )
            self.assertEqual(set(updated.objects(order[0], DCTERMS.creator)), {URIRef(ANDRE)})

    def test_invalid_and_duplicate_orcids_are_rejected(self) -> None:
        """Catch invalid list shape, missing names, bad checksums and duplicate identities."""
        for people in (
            [],
            ["unidentified"],
            [{"orcid": ROGERIO}],
            [{"orcid": ROGERIO[:-1] + "0", "name": "Rogério Blitz"}],
            [{"orcid": ROGERIO, "name": "Rogério Blitz"}] * 2,
        ):
            meta = copy.deepcopy(self.meta)
            meta["provenance"]["created_by"] = people
            self.assertTrue(validate_meta(meta, path=self.path), people)

    def test_repository_metadata_matches_schema_and_runtime(self) -> None:
        """Validate the new fields in all maintained source manifests against both contracts."""
        schema = json.loads((ROOT / "schema/factorization-hierarchy.schema.json").read_text())
        jsonschema.Draft202012Validator.check_schema(schema)
        validator = jsonschema.Draft202012Validator(schema)
        for path in (ROOT / "factorizations").glob("*/v*/*_hierarchy.yaml"):
            record = yaml.safe_load(path.read_text())
            self.assertFalse(validate_meta(record["meta"], path=path))
            self.assertFalse(list(validator.iter_errors(record)))
