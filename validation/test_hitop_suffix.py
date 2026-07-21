"""Regression tests for HiTOP suffix tooling."""

from __future__ import annotations

import unittest

from hitop.suffix.code import build_code, parse_code, validate_code
from hitop.suffix.disambiguator import (
    attach_disambiguator,
    build_disambiguation_basis,
    generate_disambiguator,
)
from hitop.suffix.exceptions import InvalidCodeError, InvalidNamespaceError, InvalidSlugError
from hitop.suffix.mapping import compute_features, propose_relation, score_band
from hitop.suffix.metadata import validate_metadata
from hitop.suffix.namespace import (
    canonicalize_namespace_identifier,
    generate_namespace_token,
    validate_namespace_kind,
)
from hitop.suffix.slug import slugify, split_disambiguated_slug, validate_slug


class NamespaceTests(unittest.TestCase):
    """Namespace token examples from the documentation."""

    def test_documented_namespace_tokens(self) -> None:
        """Protect namespace token fixtures published in the suffix schema."""

        self.assertEqual(generate_namespace_token("HTP", "hitop:core"), "HTPAJIPZH4KRXKXK")
        self.assertEqual(
            generate_namespace_token("ROR", "https://ror.org/03yrm5c26"),
            "ROR3FG46LQKYZLLX",
        )
        self.assertEqual(
            generate_namespace_token("ORC", "https://orcid.org/0000-0002-4505-4593"),
            "ORCMS547FBEVZ5LD",
        )
        self.assertEqual(
            generate_namespace_token("DOI", "https://doi.org/10.1234/example.study.v1"),
            "DOICRZ5I6RDFXGS7",
        )
        self.assertEqual(
            generate_namespace_token("DNS", "dns:de.uniklinikum-jena.psychiatry"),
            "DNS4HX35F6TKVT6R",
        )
        self.assertEqual(
            generate_namespace_token("ROR", "https://ror.org/00tkfw097"),
            "ROR3J2WQSVQFFIKK",
        )

    def test_ror_canonicalization(self) -> None:
        """Accept compact ROR IDs while storing the canonical URL form."""

        self.assertEqual(
            canonicalize_namespace_identifier("ROR", "00TKFW097"),
            "https://ror.org/00tkfw097",
        )

    def test_unsupported_namespace_kind_is_rejected(self) -> None:
        """Reject a namespace kind outside the controlled SUPPORTED_NAMESPACE_KINDS set."""

        with self.assertRaises(InvalidNamespaceError):
            validate_namespace_kind("XYZ")

    def test_malformed_ror_identifier_is_rejected(self) -> None:
        """Reject a ROR identifier that does not match the expected 9-character ROR ID form."""

        with self.assertRaises(InvalidNamespaceError):
            canonicalize_namespace_identifier("ROR", "not-a-ror-id")


class SlugTests(unittest.TestCase):
    """Slug and disambiguator behavior."""

    def test_slugify(self) -> None:
        """Normalize human-readable labels into schema-compliant slugs."""

        self.assertEqual(slugify("Chronic worry"), "CHRONIC_WORRY")
        self.assertEqual(slugify("Resting palpitations"), "RESTING_PALPITATIONS")
        self.assertTrue(validate_slug("REJECTION_SENSITIVITY"))

    def test_invalid_slug_is_rejected(self) -> None:
        """Reject slugs with leading/trailing underscores or disallowed characters."""

        self.assertFalse(validate_slug("_LEADING_UNDERSCORE"))
        self.assertFalse(validate_slug("TRAILING_UNDERSCORE_"))
        self.assertFalse(validate_slug("has lowercase and spaces"))

    def test_slugify_rejects_labels_with_no_usable_characters(self) -> None:
        """Raise InvalidSlugError when a label normalizes to an empty slug."""

        with self.assertRaises(InvalidSlugError):
            slugify("!!!")

    def test_disambiguator(self) -> None:
        """Verify deterministic collision disambiguation from stable metadata."""

        basis = build_disambiguation_basis(
            namespace_identifier="https://ror.org/03yrm5c26",
            hitop_base_code="HiTOPU0aB2X",
            manifestation_type="AF",
            study_id="study-a",
            instrument="instrument-x",
            item_id_or_local_concept_id="item-17",
        )
        self.assertEqual(
            basis,
            "https://ror.org/03yrm5c26|hitopu0ab2x|m|af|study-a|instrument-x|item-17",
        )
        self.assertEqual(generate_disambiguator(basis), "CGREBL")
        self.assertEqual(attach_disambiguator("CHRONIC_WORRY", basis), "CHRONIC_WORRY_CGREBL")
        self.assertEqual(
            split_disambiguated_slug("CHRONIC_WORRY_CGREBL"),
            ("CHRONIC_WORRY", "CGREBL"),
        )


class CodeTests(unittest.TestCase):
    """Manifestation code parsing and validation."""

    def test_build_parse_validate(self) -> None:
        """Round-trip a canonical manifestation code through build, parse, validate."""

        code = build_code(
            hitop_base_code="HiTOPU0aB2X",
            manifestation_type="AF",
            namespace_token="ROR3FG46LQKYZLLX",
            slug="CHRONIC_WORRY",
        )
        self.assertEqual(code, "HiTOPU0aB2X.M-AF-ROR3FG46LQKYZLLX-CHRONIC_WORRY")
        parsed = parse_code(code)
        self.assertEqual(parsed.hitop_base_code, "HiTOPU0aB2X")
        self.assertEqual(parsed.manifestation_type, "AF")
        self.assertEqual(validate_code(code), [])

    def test_invalid_short_form(self) -> None:
        """Reject short-form suffixes that omit the required namespace token."""

        errors = validate_code("HiTOPU0aB2X.M-AF-CHRONIC_WORRY")
        self.assertTrue(errors)

    def test_invalid_manifestation_type_is_rejected(self) -> None:
        """Reject a manifestation type outside the controlled MANIFESTATION_TYPES set."""

        with self.assertRaises(InvalidCodeError):
            build_code(
                hitop_base_code="HiTOPU0aB2X",
                manifestation_type="ZZ",
                namespace_token="ROR3FG46LQKYZLLX",
                slug="CHRONIC_WORRY",
            )

    def test_invalid_namespace_token_in_code_is_rejected(self) -> None:
        """Reject a namespace token that does not match the fixed-length pattern."""

        with self.assertRaises(InvalidCodeError):
            build_code(
                hitop_base_code="HiTOPU0aB2X",
                manifestation_type="AF",
                namespace_token="TOO_SHORT",
                slug="CHRONIC_WORRY",
            )


class MetadataTests(unittest.TestCase):
    """YAML-compatible metadata validation."""

    def test_valid_metadata_record(self) -> None:
        """Accept a complete, internally consistent manifestation metadata record."""

        report = validate_metadata(
            {
                "code": "HiTOPU0aB2X.M-AF-ROR3FG46LQKYZLLX-CHRONIC_WORRY",
                "hitop_base_code": "HiTOPU0aB2X",
                "suffix_block": "M",
                "manifestation_type": "AF",
                "namespace": {
                    "token": "ROR3FG46LQKYZLLX",
                    "kind": "ROR",
                    "identifier": "https://ror.org/03yrm5c26",
                },
                "slug": "CHRONIC_WORRY",
                "preferred_label": "Chronic worry",
                "definition": "Persistent or recurrent worry.",
                "source": {
                    "study_id": "study-a",
                    "instrument": "instrument-x",
                    "item_id": "item-17",
                },
                "status": "active",
                "created": "2026-05-31",
                "version": "1",
                "mappings": [],
            }
        )
        self.assertTrue(report.valid, report.errors)

    def test_namespace_mismatch_is_invalid(self) -> None:
        """Reject records whose namespace token no longer matches the source ID."""

        report = validate_metadata(
            {
                "code": "HiTOPU0aB2X.M-AF-ROR3FG46LQKYZLLX-CHRONIC_WORRY",
                "hitop_base_code": "HiTOPU0aB2X",
                "suffix_block": "M",
                "manifestation_type": "AF",
                "namespace": {
                    "token": "ROR3FG46LQKYZLLX",
                    "kind": "ROR",
                    "identifier": "https://ror.org/00tkfw097",
                },
                "slug": "CHRONIC_WORRY",
                "preferred_label": "Chronic worry",
                "definition": "Persistent or recurrent worry.",
                "source": {
                    "study_id": "study-a",
                    "instrument": "instrument-x",
                    "item_id": "item-17",
                },
                "status": "active",
                "created": "2026-05-31",
                "version": "1",
                "mappings": [],
            }
        )
        self.assertFalse(report.valid)

    def test_missing_required_field_is_invalid(self) -> None:
        """Reject a record missing a required top-level field such as preferred_label."""

        report = validate_metadata(
            {
                "code": "HiTOPU0aB2X.M-AF-ROR3FG46LQKYZLLX-CHRONIC_WORRY",
                "hitop_base_code": "HiTOPU0aB2X",
                "suffix_block": "M",
                "manifestation_type": "AF",
                "namespace": {
                    "token": "ROR3FG46LQKYZLLX",
                    "kind": "ROR",
                    "identifier": "https://ror.org/03yrm5c26",
                },
                "slug": "CHRONIC_WORRY",
                "definition": "Persistent or recurrent worry.",
                "source": {
                    "study_id": "study-a",
                    "instrument": "instrument-x",
                    "item_id": "item-17",
                },
                "status": "active",
                "created": "2026-05-31",
                "version": "1",
                "mappings": [],
            }
        )
        self.assertFalse(report.valid)

    def test_missing_source_item_reference_is_invalid(self) -> None:
        """Reject a record whose source has neither item_id nor local_concept_id."""

        report = validate_metadata(
            {
                "code": "HiTOPU0aB2X.M-AF-ROR3FG46LQKYZLLX-CHRONIC_WORRY",
                "hitop_base_code": "HiTOPU0aB2X",
                "suffix_block": "M",
                "manifestation_type": "AF",
                "namespace": {
                    "token": "ROR3FG46LQKYZLLX",
                    "kind": "ROR",
                    "identifier": "https://ror.org/03yrm5c26",
                },
                "slug": "CHRONIC_WORRY",
                "preferred_label": "Chronic worry",
                "definition": "Persistent or recurrent worry.",
                "source": {
                    "study_id": "study-a",
                    "instrument": "instrument-x",
                },
                "status": "active",
                "created": "2026-05-31",
                "version": "1",
                "mappings": [],
            }
        )
        self.assertFalse(report.valid)


class MappingTests(unittest.TestCase):
    """Transparent mapping candidate scoring."""

    def test_mapping_score_and_relation(self) -> None:
        """Score a plausible related symptom mapping into a reviewable relation."""

        source = {
            "hitop_base_code": "HiTOPU0aB2X",
            "manifestation_type": "AF",
            "slug": "CHRONIC_WORRY",
            "preferred_label": "Chronic worry",
            "definition": "Persistent or recurrent worry.",
            "operationalization": {"instrument": "instrument-x", "time_window": "past 2 weeks"},
        }
        target = {
            "hitop_base_code": "HiTOPU0aB2X",
            "manifestation_type": "AF",
            "slug": "EXCESSIVE_WORRY",
            "preferred_label": "Excessive worry",
            "definition": "Persistent or recurrent excessive worry.",
            "operationalization": {"instrument": "instrument-x", "time_window": "past 2 weeks"},
        }
        features = compute_features(source, target)
        score = features.score()
        self.assertGreaterEqual(score, 0.50)
        self.assertIn(score_band(score), {"medium", "high", "very_high"})
        self.assertIn(
            propose_relation(features),
            {"skos:relatedMatch", "skos:closeMatch", "skos:exactMatch"},
        )


if __name__ == "__main__":
    unittest.main()
