"""Regression tests for the production HiTOP checksum generator."""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from hitop.base.HITOPChecksum import (
    HITOPChecksum,
    HITOPChecksumError,
    base62_encode,
    calculate_check_digit,
)
from hitop.base import hitop
from hitop.base.hitop import HiTOPCSVError, process_csv


class HITOPChecksumTests(unittest.TestCase):
    """Known examples from the repository CSV fixtures."""

    def test_known_hitop_checksum_values(self) -> None:
        """Protect documented HiTOP checksum outputs for core fixture rows."""

        self.assertEqual(calculate_check_digit("HiTOP", "C0", "01"), "qy")
        self.assertEqual(calculate_check_digit("HiTOP", "C0", "02"), "17")
        self.assertEqual(calculate_check_digit("HiTOP", "C0", "03"), "3z")

    def test_known_mds_checksum_value(self) -> None:
        """Verify that changing the code-system prefix changes the checksum."""

        self.assertEqual(calculate_check_digit("MDS", "C0", "01"), "y6")

    def test_legacy_get_code_uses_canonical_algorithm(self) -> None:
        """Keep the historical ``getCode`` API bound to the canonical algorithm."""

        self.assertEqual(HITOPChecksum("C001").getCode(), "C001qy")

    def test_explicit_parts_are_supported(self) -> None:
        """Verify the preferred explicit construction path for production use."""

        checksum = HITOPChecksum.from_parts(
            prefix="HiTOP",
            segment="U0",
            concept_code="d1",
        )
        self.assertEqual(checksum.code, "U0d1")
        self.assertEqual(checksum.with_check_digit(), "U0d19R")

    def test_numeric_segment_from_existing_vocabulary_is_supported(self) -> None:
        """Ensure numeric-only hierarchy segments from source data remain valid."""

        self.assertEqual(calculate_check_digit("HiTOP", "00", "04"), "KV")

    def test_invalid_base62_input_is_rejected(self) -> None:
        """Reject concept codes that cannot be represented in the Base62 alphabet."""

        with self.assertRaises(HITOPChecksumError):
            calculate_check_digit("HiTOP", "C0", "not-valid")

    def test_base62_encoding(self) -> None:
        """Cover Base62 boundary values and backwards-compatible module exports."""

        self.assertEqual(base62_encode(0), "0")
        self.assertEqual(base62_encode(61), "z")
        self.assertEqual(base62_encode(62), "10")
        self.assertEqual(hitop.base62_encode(62), "10")
        self.assertEqual(hitop.base62_alphabet[-1], "z")


class HiTOPCSVGenerationTests(unittest.TestCase):
    """CSV generation behavior for the ``hitop.py`` entry point."""

    def test_process_csv_writes_check_digit_and_code_columns(self) -> None:
        """Generate checksum and local code columns without mutating source fields."""

        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "input.csv"
            output_path = Path(tmp) / "output.csv"
            input_path.write_text(
                "Code;Label;Segment;Segment Level\n"
                "01;Conversion;C;0\n"
                "02;Somatization;C;0\n",
                encoding="utf-8",
            )

            process_csv(input_path, output_path)

            with output_path.open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle, delimiter=";"))

        self.assertEqual(rows[0]["CheckDigit"], "qy")
        self.assertEqual(rows[0]["HiTOP"], "C001qy")
        self.assertEqual(rows[1]["CheckDigit"], "17")
        self.assertEqual(rows[1]["HiTOP"], "C00217")

    def test_process_csv_rejects_missing_required_columns(self) -> None:
        """Fail fast when required CSV columns are absent."""

        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "input.csv"
            output_path = Path(tmp) / "output.csv"
            input_path.write_text("Code;Label\n01;Conversion\n", encoding="utf-8")

            with self.assertRaises(HiTOPCSVError):
                process_csv(input_path, output_path)


if __name__ == "__main__":
    unittest.main()
