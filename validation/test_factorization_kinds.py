"""Node identity, overlap mappings, and local labels across schema and exports."""

import copy
import json
import runpy
import shutil
import subprocess
import unittest
from pathlib import Path

import jsonschema
from rdflib import RDF, RDFS, Graph, Literal, Namespace, URIRef
from rdflib.compare import isomorphic

from hitop.factorization import validate_hierarchy_document

ROOT = Path(__file__).resolve().parents[1]
H = Namespace("http://purl.org/hitop#")
S = Namespace("http://www.w3.org/2004/02/skos/core#")


class FactorizationKindTests(unittest.TestCase):
    def setUp(self):
        self.generator = runpy.run_path(str(ROOT / "scripts/generate_factorization_ontology.py"))
        self.schema = json.loads((ROOT / "schema/factorization-hierarchy.schema.json").read_text())
        self.path = ROOT / "factorizations/example/v1/V1test_hierarchy.yaml"
        self.record = {
            "meta": {
                "factorization_id": "example",
                "version": "V1test",
                "label": "Example",
                "status": "draft",
                "based_on": {"ontology_iri": "http://purl.org/hitop", "ontology_version": "0.1.0"},
                "provenance": {"created_by": "Test", "created_at": "2026-10-23"},
            },
            "hierarchy": {
                "label": "Local grouping",
                "level": "Spectrum",
                "code": "COLLtest",
                "kind": "collection",
                "children": [
                    {"label": "Equivalent wording", "level": "Trait", "code": "T00ua9"},
                    {
                        "label": "Overlapping wording",
                        "id": "T00BXK",
                        "mapping_note": "Only the relevant affective expression overlaps.",
                        "level": "Trait",
                        "code": "T00BXK",
                        "kind": "partial",
                        "provisional": True,
                    },
                ],
            },
        }

    def test_schema_validator_exports_and_diagram(self):
        jsonschema.validate(self.record, self.schema)
        self.assertEqual(
            validate_hierarchy_document(
                self.record, path=self.path, core_class_names={"T00ua9", "T00BXK"}
            ),
            [],
        )
        g, order = self.generator["build_factorization_graph"](
            self.record,
            core_annotations={
                "T00ua9": {
                    "label": Literal("Eccentricity", lang="en"),
                    "comment": Literal("Core description", lang="en"),
                },
                "T00BXK": {"comment": Literal("Must not be inherited", lang="en")},
            },
        )
        local = URIRef(str(order[0]) + "#T00BXK")
        self.assertIn((H.T00ua9, RDFS.label, Literal("Equivalent wording", lang="en")), g)
        self.assertIn((H.T00ua9, S.altLabel, Literal("Eccentricity", lang="en")), g)
        self.assertIn((local, S.relatedMatch, H.T00BXK), g)
        self.assertIn((local, RDF.type, S.Concept), g)
        self.assertFalse(list(g.objects(local, RDFS.comment)))
        self.assertIn(
            (
                local,
                S.scopeNote,
                Literal("Only the relevant affective expression overlaps.", lang="en"),
            ),
            g,
        )
        self.assertFalse(list(g.objects(local, S.exactMatch)))
        self.assertIn((URIRef(str(order[0]) + "#COLLtest"), RDF.type, S.Collection), g)
        for fmt in ["xml", "turtle"]:
            restored = Graph().parse(data=g.serialize(format=fmt), format=fmt)
            self.assertTrue(isomorphic(g, restored))
        diagram = runpy.run_path(str(ROOT / "scripts/generate_factorization_diagram_data.py"))
        tree = copy.deepcopy(self.record["hierarchy"])

        def color(n):
            n["color"] = "#123456"
            for c in n.get("children", []):
                color(c)

        color(tree)
        output = diagram["build_diagram_tree"](tree)
        self.assertEqual(output["children"][1]["kind"], "partial")
        self.assertEqual(output["children"][0]["label"], "Equivalent wording")
        self.assertTrue(output["children"][1]["provisional"])
        self.assertEqual(output["children"][1]["id"], "T00BXK")
        self.assertEqual(
            output["children"][1]["mapping_note"],
            self.record["hierarchy"]["children"][1]["mapping_note"],
        )

    def test_partial_requires_core_code_and_unknown_kind_is_rejected(self):
        errors = validate_hierarchy_document(
            self.record, path=self.path, core_class_names={"T00ua9"}
        )
        self.assertTrue(any("T00BXK" in e for e in errors), errors)
        self.record["hierarchy"]["children"][1]["kind"] = "unknown"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(self.record, self.schema)
        errors = validate_hierarchy_document(
            self.record, path=self.path, core_class_names={"T00ua9", "T00BXK"}
        )
        self.assertTrue(any("kind" in e for e in errors), errors)

    def test_uniqueness_follows_exported_identity(self):
        """Core and local identities differ; partial and collection share local scope."""
        for first, second, allowed in [
            ("concept", "partial", True),
            ("partial", "concept", True),
            ("concept", "collection", True),
            ("concept", "concept", False),
            ("partial", "partial", False),
            ("collection", "collection", False),
            ("partial", "collection", False),
            ("collection", "partial", False),
        ]:
            with self.subTest(first=first, second=second):
                record = copy.deepcopy(self.record)
                children = record["hierarchy"]["children"]
                for node, kind in zip(children, [first, second]):
                    node["code"] = "T00ua9"
                    node["kind"] = kind
                    node.pop("mapping_note", None)
                    node.pop("id", None)
                    if kind == "partial":
                        node["id"] = "T00ua9"
                errors = validate_hierarchy_document(
                    record, path=self.path, core_class_names={"T00ua9"}
                )
                self.assertEqual(not errors, allowed, errors)
                if allowed:
                    graph, order = self.generator["build_factorization_graph"](record)
                    parent = URIRef(str(order[0]) + "#COLLtest")
                    self.assertEqual(len(set(graph.objects(parent, H.hasTier))), 2)
                    self.assertIn((parent, H.hasTier, H.T00ua9), graph)
                    self.assertIn((parent, H.hasTier, URIRef(str(order[0]) + "#T00ua9")), graph)

    @unittest.skipUnless(shutil.which("node"), "Node.js is needed for editor validation tests")
    def test_editor_uniqueness_matches_runtime(self):
        source = (ROOT / "docs/assets/javascripts/learning-factorization.js").read_text()
        function = source.split("  const nodeErrors = ", 1)[1].split(
            "\n  const updateNodeMessage", 1
        )[0]
        script = "const conceptsByCode = new Map(); const nodeErrors = " + function
        script += """
const cases = [
  ["concept", "partial", true], ["partial", "concept", true],
  ["concept", "collection", true], ["concept", "concept", false],
  ["partial", "partial", false], ["collection", "collection", false],
  ["partial", "collection", false], ["collection", "partial", false]
];
for (const [first, second, allowed] of cases) {
  const seen = new Set();
  const errors = [first, second].flatMap(kind => nodeErrors(
    {kind, localId: "T00ua9", code: "T00ua9", label: "Example", level: "Trait", bridge: []},
    "test", seen));
  if ((errors.length === 0) !== allowed) throw new Error(JSON.stringify({first, second, errors}));
}
const seen = new Set();
for (const localId of ["Cardiopulmonary", "PhysiologicalAnxiety"]) {
  const errors = nodeErrors({kind: "partial", localId, code: "T00ua9", label: "Example",
    level: "Component", bridge: []}, "test", seen);
  if (errors.length) throw new Error(JSON.stringify(errors));
}
if (!nodeErrors({kind: "partial", code: "T00ua9", label: "Missing ID",
  level: "Component", bridge: []}, "test").length) throw new Error("Missing ID accepted");
"""
        result = subprocess.run(["node", "-e", script], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_two_partial_nodes_can_reference_same_core_with_distinct_ids(self):
        record = copy.deepcopy(self.record)
        record["hierarchy"]["children"] = [
            {
                "label": "Cardiopulmonary",
                "kind": "partial",
                "id": "Cardiopulmonary",
                "code": "T00BXK",
                "level": "Component",
            },
            {
                "label": "Physiological anxiety",
                "kind": "partial",
                "id": "PhysiologicalAnxiety",
                "code": "T00BXK",
                "level": "Component",
            },
        ]
        jsonschema.validate(record, self.schema)
        self.assertEqual(
            validate_hierarchy_document(record, path=self.path, core_class_names={"T00BXK"}), []
        )
        graph, order = self.generator["build_factorization_graph"](record)
        matches = set(graph.subjects(S.relatedMatch, H.T00BXK))
        self.assertEqual(
            matches,
            {
                URIRef(str(order[0]) + "#Cardiopulmonary"),
                URIRef(str(order[0]) + "#PhysiologicalAnxiety"),
            },
        )

    def test_partial_id_required_and_other_kinds_reject_it(self):
        for local_id in [None, "", "bad id", "bad#id", []]:
            record = copy.deepcopy(self.record)
            node = record["hierarchy"]["children"][1]
            if local_id is None:
                node.pop("id")
            else:
                node["id"] = local_id
            with self.subTest(local_id=local_id):
                with self.assertRaises(jsonschema.ValidationError):
                    jsonschema.validate(record, self.schema)
                self.assertTrue(
                    validate_hierarchy_document(
                        record, path=self.path, core_class_names={"T00ua9", "T00BXK"}
                    )
                )
        for kind in ["concept", "collection"]:
            record = copy.deepcopy(self.record)
            record["hierarchy"]["children"][1]["kind"] = kind
            with self.assertRaises(jsonschema.ValidationError):
                jsonschema.validate(record, self.schema)
            self.assertTrue(
                validate_hierarchy_document(
                    record, path=self.path, core_class_names={"T00ua9", "T00BXK"}
                )
            )

    @unittest.skipUnless(shutil.which("node"), "Node.js is needed for editor export tests")
    def test_editor_exports_partial_identity_and_note(self):
        source = (ROOT / "docs/assets/javascripts/learning-factorization.js").read_text()
        exporter = source.split("  const xmlEscape = ", 1)[1].split("\n  const download", 1)[0]
        tree = copy.deepcopy(self.record["hierarchy"])

        def prepare(node):
            node["bridge"] = []
            node.setdefault("children", [])
            if node.get("kind") == "partial":
                node["localId"] = node["id"]
                node["mappingNote"] = node["mapping_note"]
            for child in node["children"]:
                prepare(child)

        prepare(tree)
        script = "const hierarchy = " + json.dumps(tree) + ";\n"
        script += (
            """
const root = {dataset: {ontologyVersion: "0.1.0"}};
const conceptsByCode = new Map();
const values = () => ({factorId: "example", versionCode: "V1test", metaLabel: "Example",
  status: "draft", createdBy: "Test", createdAt: "2026-10-23"});
const xmlEscape = """
            + exporter
            + "\nprocess.stdout.write(buildOntology());"
        )
        result = subprocess.run(["node", "-e", script], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        graph = Graph().parse(data=result.stdout, format="xml")
        subject = URIRef("http://purl.org/hitop/factorizations/example/vV1test#T00BXK")
        self.assertIn((subject, S.relatedMatch, H.T00BXK), graph)
        self.assertIn(
            (
                subject,
                S.scopeNote,
                Literal("Only the relevant affective expression overlaps.", lang="en"),
            ),
            graph,
        )
        self.assertIn((H.T00ua9, RDFS.label, Literal("Equivalent wording", lang="en")), graph)
