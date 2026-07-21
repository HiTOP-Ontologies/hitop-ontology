"""Schema-conformance tests for the flat manifestation-record JSON Schema.

These tests validate example records directly against
``schema/manifestation-record.schema.json``. They are independent of the
nested Python-side ``validate_metadata`` model exercised in
``test_hitop_suffix.py`` (see TECH-T5-01 for the open decision on which
shape becomes canonical).
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import jsonschema

ROOT_DIR = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT_DIR / "schema" / "manifestation-record.schema.json"

VALID_RECORD = {
    "code": "HiTOPU0aB2X.M-AF-ROR3FG46LQKYZLLX-CHRONIC_WORRY",
    "hitop_base_code": "HiTOPU0aB2X",
    "suffix": "M-AF-ROR3FG46LQKYZLLX-CHRONIC_WORRY",
    "manifestation_type": "AF",
    "namespace_token": "ROR3FG46LQKYZLLX",
    "slug": "CHRONIC_WORRY",
    "preferred_label": "Chronic worry",
    "status": "active",
    "version": "1",
}


class ManifestationRecordSchemaTests(unittest.TestCase):
    """Validate example manifestation records against the flat JSON Schema."""

    @classmethod
    def setUpClass(cls) -> None:
        with SCHEMA_PATH.open("r", encoding="utf-8") as handle:
            cls.schema = json.load(handle)
        cls.validator = jsonschema.Draft202012Validator(cls.schema)

    def test_schema_itself_is_valid(self) -> None:
        """Guard against a malformed schema document."""

        jsonschema.Draft202012Validator.check_schema(self.schema)

    def test_minimal_valid_record_is_accepted(self) -> None:
        """Accept a record containing only the required fields."""

        self.assertEqual(list(self.validator.iter_errors(VALID_RECORD)), [])

    def test_extension_field_is_accepted(self) -> None:
        """Accept a controlled x_ extension field alongside required fields."""

        record = {**VALID_RECORD, "x_local_note": "example"}
        self.assertEqual(list(self.validator.iter_errors(record)), [])

    def test_missing_required_field_is_rejected(self) -> None:
        """Reject a record missing a required field."""

        record = {key: value for key, value in VALID_RECORD.items() if key != "version"}
        self.assertTrue(list(self.validator.iter_errors(record)))

    def test_invalid_manifestation_type_is_rejected(self) -> None:
        """Reject a manifestation_type outside the controlled enum."""

        record = {**VALID_RECORD, "manifestation_type": "ZZ"}
        self.assertTrue(list(self.validator.iter_errors(record)))

    def test_malformed_namespace_token_is_rejected(self) -> None:
        """Reject a namespace_token that does not match the fixed-length pattern."""

        record = {**VALID_RECORD, "namespace_token": "short"}
        self.assertTrue(list(self.validator.iter_errors(record)))

    def test_unknown_field_is_rejected(self) -> None:
        """Reject a non-x_ field that is not part of the controlled schema."""

        record = {**VALID_RECORD, "unexpected_field": "value"}
        self.assertTrue(list(self.validator.iter_errors(record)))


if __name__ == "__main__":
    unittest.main()
