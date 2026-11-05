"""Keep diagram JSON inert when Material replays scripts on instant navigation."""

import json
import runpy
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class PayloadParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.payloads = {}
        self.scripts = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script":
            self.scripts.append(attrs)
        if attrs.get("id", "").startswith("data-") or "data-hitop-core-concepts" in attrs:
            self.current = attrs.get("id", "core-concepts")
            self.payloads[self.current] = {"tag": tag, "attrs": attrs, "text": ""}

    def handle_data(self, data):
        if self.current:
            self.payloads[self.current]["text"] += data

    def handle_endtag(self, tag):
        if self.current and self.payloads[self.current]["tag"] == tag:
            self.current = None


class DiagramPayloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch.object(sys, "path", [str(ROOT / "scripts"), *sys.path]):
            cls.generator = runpy.run_path(str(ROOT / "scripts/generate_diagram_viewer_page.py"))
        cls.hooks = runpy.run_path(str(ROOT / "scripts/mkdocs_hooks.py"))

    def test_special_labels_roundtrip_as_inert_text(self):
        diagram = {
            "meta": {"label": "A & B"},
            "hierarchy": {
                "label": '</div><script>window.injected=true</script> "Ä" &amp; <node>',
                "mapping_note": 'Quotes " and <tags> must remain data.',
            },
        }
        block = self.generator["diagram_data_block"]("example", diagram)
        parser = PayloadParser()
        parser.feed(block)
        self.assertEqual(parser.scripts, [])
        payload = parser.payloads["data-example"]
        self.assertEqual(payload["tag"], "div")
        self.assertIn("hidden", payload["attrs"])
        self.assertEqual(json.loads(payload["text"]), diagram)

    def test_viewer_embeds_all_current_diagrams_without_scripts(self):
        parser = PayloadParser()
        parser.feed((ROOT / "docs/models/diagrams.md").read_text())
        rows = self.generator["catalog_rows"]()
        for row in rows:
            if not row.diagram_json_relative:
                continue
            payload = parser.payloads["data-" + row.factorization_id]
            self.assertEqual(payload["tag"], "div")
            self.assertIn("hidden", payload["attrs"])
            expected = json.loads((ROOT / row.diagram_json_relative).read_text())
            self.assertEqual(json.loads(payload["text"]), expected)
        self.assertEqual(parser.scripts, [])

    def test_editor_core_vocabulary_is_inert_and_preserved(self):
        markdown = (ROOT / "docs/models/create-a-factorization.md").read_text()
        rendered = self.hooks["on_page_markdown"](markdown)
        parser = PayloadParser()
        parser.feed(rendered)
        payload = parser.payloads["core-concepts"]
        self.assertEqual(payload["tag"], "div")
        self.assertIn("hidden", payload["attrs"])
        self.assertEqual(
            json.loads(payload["text"]), json.loads(self.hooks["_core_concepts_json"]())
        )
        self.assertEqual(parser.scripts, [])
