"""Structural and referential-integrity checks for factorization hierarchy files.

The actual rules live in ``hitop.factorization.validate`` so that this test
suite and ``scripts/generate_factorization_ontology.py`` never drift apart.
See ``docs/factorizations.md`` for the governance model.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from hitop.factorization import (
    check_cross_file_label_consistency,
    discover_hierarchy_files,
    load_core_class_local_names,
    load_hierarchy_document,
    load_level_ranks,
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
        cls.level_ranks = load_level_ranks(ONTOLOGY_TTL)
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
                    level_ranks=self.level_ranks,
                )
                self.assertFalse(errors, "; ".join(errors))

    def test_codes_have_consistent_labels_across_files(self) -> None:
        """Catch code collisions where the same hitop_base_code names two different constructs."""

        errors = check_cross_file_label_consistency(self.documents)
        self.assertFalse(errors, "; ".join(errors))


if __name__ == "__main__":
    unittest.main()
