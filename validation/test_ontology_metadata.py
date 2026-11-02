"""Verify that contribution metadata remains usable without network access."""

import runpy
import socket
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from rdflib import RDF, Graph, Namespace, URIRef

ROOT = Path(__file__).resolve().parents[1]
DCTERMS = Namespace("http://purl.org/dc/terms/")
PROV = Namespace("http://www.w3.org/ns/prov#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
ONTOLOGY = URIRef("http://purl.org/hitop")
CONTRIBUTIONS = URIRef("http://purl.org/hitop/contributions")


class OfflineContributionMetadataTests(unittest.TestCase):
    """Exercise local parsing and both converters with network access denied."""

    def test_parse_and_convert_without_remote_contribution_record(self) -> None:
        """Keep names, provenance and identity links usable when URLs are unavailable."""
        with (
            tempfile.TemporaryDirectory() as directory,
            patch.object(socket, "create_connection", side_effect=AssertionError("Network access")),
            patch.object(socket.socket, "connect", side_effect=AssertionError("Network access")),
            patch.object(socket, "getaddrinfo", side_effect=AssertionError("Network access")),
        ):
            graphs = [Graph().parse(ROOT / "ontology/hitop.rdf", format="xml")]
            record = Graph().parse(ROOT / "ontology/contributions.rdf", format="xml")
            record_people = set(record.subjects(RDF.type, PROV.Person))
            for script, suffix, syntax in (
                ("rdf2ttl.py", "ttl", "turtle"),
                ("rdf2owl.py", "owl", "xml"),
            ):
                output = Path(directory) / f"ontology.{suffix}"
                converter = runpy.run_path(str(ROOT / "scripts" / script))
                self.assertEqual(
                    converter["main"](
                        ["--input", str(ROOT / "ontology/hitop.rdf"), "--output", str(output)]
                    ),
                    0,
                )
                graphs.append(Graph().parse(output, format=syntax))

            for graph in graphs:
                with self.subTest(triples=len(graph)):
                    self.assertEqual(
                        set(graph.objects(ONTOLOGY, PROV.has_provenance)), {CONTRIBUTIONS}
                    )
                    contributors = set(graph.objects(ONTOLOGY, DCTERMS.contributor))
                    self.assertEqual(len(contributors), 11)
                    self.assertEqual(contributors, record_people)
                    self.assertTrue(
                        all(str(person).startswith("https://orcid.org/") for person in contributors)
                    )
                    self.assertTrue(all(graph.value(person, RDFS.label) for person in contributors))
                    self.assertTrue(
                        all(
                            not str(graph.value(person, RDFS.label)).startswith(("Dr.", "Prof."))
                            for person in contributors
                        )
                    )
                    self.assertTrue(graph.value(CONTRIBUTIONS, RDFS.label))
                    for predicate in (DCTERMS.creator, DCTERMS.publisher, DCTERMS.rightsHolder):
                        self.assertEqual(
                            set(graph.objects(ONTOLOGY, predicate)),
                            {URIRef("https://orcid.org/0000-0002-4505-4593")},
                        )
