"""Resolve bridges within a factorization, including local concepts and collections."""

import copy
import json
import runpy
import shutil
import subprocess
import unittest
from pathlib import Path

from rdflib import Namespace

from hitop.factorization import validate_hierarchy_document

ROOT = Path(__file__).resolve().parents[1]


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.record = {
            "meta": {
                "factorization_id": "example",
                "version": "V1test",
                "label": "Example",
                "status": "draft",
                "based_on": {"ontology_iri": "http://purl.org/hitop", "ontology_version": "0.1.0"},
                "provenance": {"created_by": "Test", "created_at": "2026-11-02"},
            },
            "hierarchy": {
                "label": "Root",
                "code": "F001Hw",
                "level": "Factor",
                "children": [
                    {"label": "Source", "code": "T00ua9", "level": "Trait"},
                    {
                        "label": "PF Problems",
                        "code": "COLLPF",
                        "level": "Trait",
                        "kind": "collection",
                    },
                    {
                        "label": "Local partial",
                        "code": "T00BXK",
                        "id": "Partial",
                        "kind": "partial",
                        "level": "Trait",
                    },
                ],
            },
        }
        self.path = ROOT / "factorizations/example/v1/V1test_hierarchy.yaml"

    def errors(self, record):
        return validate_hierarchy_document(
            record, path=self.path, core_class_names={"F001Hw", "T00ua9", "T00BXK"}
        )

    def cases(self):
        for bridge, expected in [
            (["PF Problems"], None),
            (["Local partial"], None),
            (["Root"], None),
            (["Source"], "self-reference"),
            (["Not present"], "does not exist"),
            (["pf problems"], "does not exist"),
            (["PF Problems", "PF Problems"], "duplicate"),
            (["   "], "non-blank"),
            ([""], "non-blank"),
            ([None], "non-blank"),
            ([], "non-empty"),
        ]:
            record = copy.deepcopy(self.record)
            record["hierarchy"]["children"][0]["bridge"] = bridge
            yield record, expected
        record = copy.deepcopy(self.record)
        record["hierarchy"]["children"][0]["bridge"] = ["PF Problems"]
        record["hierarchy"]["children"][2]["label"] = "PF Problems"
        yield record, "ambiguous"
        record = copy.deepcopy(self.record)
        children = record["hierarchy"]["children"]
        children[0]["bridge"] = ["PF Problems"]
        children[1]["bridge"] = ["Local partial"]
        children[2]["bridge"] = ["Source"]
        yield record, None
        record = copy.deepcopy(self.record)
        children = record["hierarchy"]["children"]
        children[0]["bridge"] = ["PF Problems"]
        children[1]["bridge"] = ["Source"]
        yield record, None

    def test_bridge_rules(self):
        for record, expected in self.cases():
            with self.subTest(expected=expected, record=record):
                errors = self.errors(record)
                if expected:
                    self.assertTrue(any(expected in error for error in errors), errors)
                else:
                    self.assertEqual(errors, [])

    def test_bridges_do_not_create_hierarchy_edges(self):
        generator = runpy.run_path(str(ROOT / "scripts/generate_factorization_ontology.py"))
        before, _ = generator["build_factorization_graph"](self.record)
        self.record["hierarchy"]["children"][0]["bridge"] = ["PF Problems"]
        after, _ = generator["build_factorization_graph"](self.record)
        h = Namespace("http://purl.org/hitop#")
        self.assertEqual(
            set(before.subject_objects(h.hasTier)), set(after.subject_objects(h.hasTier))
        )
        skos = Namespace("http://www.w3.org/2004/02/skos/core#")
        self.assertTrue(
            any(
                str(note) == "Bridges: PF Problems" for note in after.objects(None, skos.changeNote)
            )
        )

    @unittest.skipUnless(shutil.which("node"), "Node.js is needed for editor validation tests")
    def test_editor_agrees_with_python(self):
        source = (ROOT / "docs/assets/javascripts/learning-factorization.js").read_text()
        functions = source.split("  const bridgeErrors = ", 1)[1].split(
            "\n  const updateNodeMessage", 1
        )[0]
        records = []
        for record, expected in self.cases():
            nodes = [record["hierarchy"], *record["hierarchy"]["children"]]
            for node in nodes:
                # Empty bridge lists are editor state and omitted from YAML exports.
                node.setdefault("bridge", [])
                node.setdefault("kind", "concept")
                if node["kind"] == "partial":
                    node["localId"] = node["id"]
            # An empty bridge array is valid editor state, but not an explicit YAML bridge.
            empty = record["hierarchy"]["children"][0]["bridge"] == []
            records.append({"nodes": nodes, "valid": expected is None or empty})
        script = "const conceptsByCode = new Map(); const bridgeErrors = " + functions
        script += "\nconst cases = " + json.dumps(records) + ";\n"
        script += """
for (const test of cases) {
  const errors = [...bridgeErrors(test.nodes),
    ...test.nodes.flatMap(node => nodeErrors(node, "test"))];
  if ((errors.length === 0) !== test.valid) throw new Error(JSON.stringify({test, errors}));
}
"""
        result = subprocess.run(["node", "-e", script], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
