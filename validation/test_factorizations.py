"""Structural and referential-integrity checks for factorization hierarchy files.

The actual rules live in ``hitop.factorization.validate`` so that this test
suite and ``scripts/generate_factorization_ontology.py`` never drift apart.
See ``docs/factorizations.md`` for the governance model.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from hitop.factorization import (
    check_labels_match_core,
    discover_hierarchy_files,
    load_core_class_labels,
    load_core_class_local_names,
    load_hierarchy_document,
    validate_hierarchy_document,
)

ROOT_DIR = Path(__file__).resolve().parents[1]
FACTORIZATIONS_DIR = ROOT_DIR / "factorizations"
ONTOLOGY_TTL = ROOT_DIR / "ontology" / "hitop.ttl"


class FactorizationHierarchyTests(unittest.TestCase):
    """Validate every factorizations/<id>/v<N>/*_hierarchy.yaml against the shared rules."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.core_class_names = load_core_class_local_names(ONTOLOGY_TTL)
        cls.core_labels = load_core_class_labels(ONTOLOGY_TTL)
        cls.hierarchy_paths = discover_hierarchy_files(FACTORIZATIONS_DIR)
        cls.documents = [(path, load_hierarchy_document(path)) for path in cls.hierarchy_paths]

    def test_at_least_one_hierarchy_file_is_discovered(self) -> None:
        """Guard against a silently empty factorizations/ tree."""

        self.assertTrue(
            self.hierarchy_paths,
            "No factorization hierarchy files were discovered under "
            "factorizations/*/v*/*_hierarchy.yaml.",
        )

    def test_hierarchy_files_are_structurally_valid(self) -> None:
        """Check schema-shape, referential integrity, and level-consistency per file."""

        for path, record in self.documents:
            with self.subTest(hierarchy=str(path.relative_to(ROOT_DIR))):
                errors = validate_hierarchy_document(
                    record,
                    path=path,
                    core_class_names=self.core_class_names,
                )
                self.assertFalse(errors, "; ".join(errors))

    def test_concept_labels_match_core(self) -> None:
        """Check each file's concept labels against the core ontology, never against other files."""

        for path, record in self.documents:
            with self.subTest(hierarchy=str(path.relative_to(ROOT_DIR))):
                errors = check_labels_match_core(record, path=path, core_labels=self.core_labels)
                self.assertFalse(errors, "; ".join(errors))

    def _fake_hierarchy_path(self) -> Path:
        """Return a synthetic path matching the meta shape used by the tests below."""

        return FACTORIZATIONS_DIR / "fake" / "v1" / "V1fake_hierarchy.yaml"

    def _fake_meta(self) -> dict:
        return {
            "factorization_id": "fake",
            "version": "V1fake",
            "label": "Fake factorization for negative testing",
            "status": "draft",
            "based_on": {
                "ontology_iri": "http://purl.org/hitop",
                "ontology_version": "0.1.0",
            },
            "provenance": {"created_by": "test", "created_at": "2026-01-01"},
        }

    def test_duplicate_code_in_tree_is_rejected(self) -> None:
        """Reject a hierarchy where the same code appears twice in one tree."""

        record = {
            "meta": self._fake_meta(),
            "hierarchy": {
                "label": "General Psychopathology",
                "level": "Factor",
                "code": "F001Hw",
                "children": [
                    {"label": "Internalizing", "level": "Superspectrum", "code": "P002nf"},
                    {"label": "Internalizing again", "level": "Superspectrum", "code": "P002nf"},
                ],
            },
        }
        errors = validate_hierarchy_document(
            record, path=self._fake_hierarchy_path(), core_class_names=self.core_class_names
        )
        self.assertTrue(
            any("appears more than once in this tree" in error for error in errors), errors
        )

    def test_unknown_core_code_is_rejected(self) -> None:
        """Reject a concept node whose code does not exist in the core ontology."""

        record = {
            "meta": self._fake_meta(),
            "hierarchy": {
                "label": "General Psychopathology",
                "level": "Factor",
                "code": "F001Hw",
                "children": [
                    {"label": "Not a real concept", "level": "Component", "code": "ZZZZZZ"},
                ],
            },
        }
        errors = validate_hierarchy_document(
            record, path=self._fake_hierarchy_path(), core_class_names=self.core_class_names
        )
        self.assertTrue(any("does not exist as a class" in error for error in errors), errors)

    def test_concept_label_differing_from_core_is_allowed(self) -> None:
        """Accept factorization-local wording for an equivalent concept."""

        record = {
            "meta": self._fake_meta(),
            "hierarchy": {
                "label": "general psychopathology",
                "level": "Factor",
                "code": "F001Hw",
                "children": [
                    {"label": "Distress symptoms", "level": "Subfactor", "code": "U004dm"},
                    {
                        "label": "Local grouping",
                        "level": "Spectrum",
                        "code": "COLLlocal",
                        "kind": "collection",
                        "children": [
                            {"label": "Internalizing", "level": "Spectrum", "code": "P002nf"},
                        ],
                    },
                ],
            },
        }
        errors = check_labels_match_core(
            record, path=self._fake_hierarchy_path(), core_labels=self.core_labels
        )
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
