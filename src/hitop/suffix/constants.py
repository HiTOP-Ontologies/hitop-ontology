"""Shared constants for HiTOP suffix tooling."""

from __future__ import annotations

import re

MANIFESTATION_TYPES: dict[str, str] = {
    "GS": "General symptom",
    "CS": "Clinical sign",
    "SY": "Syndrome / cluster",
    "AF": "Affective symptom",
    "CG": "Cognitive symptom",
    "PC": "Perceptual symptom",
    "BH": "Behavioral symptom",
    "SS": "Somatic symptom",
    "SL": "Sleep / circadian",
    "SU": "Substance-related",
    "IR": "Interpersonal / relational",
    "IM": "Impairment / functioning",
}

# Namespace kinds are intentionally enumerated here instead of accepted as free
# text so new identifier authorities require an explicit schema decision.
SUPPORTED_NAMESPACE_KINDS: set[str] = {
    "HTP",
    "ROR",
    "ORC",
    "DOI",
    "ARK",
    "DNS",
    "SRC",
}

# Keep raw patterns as the single source of truth: they are reused in composed
# full-code regexes and compiled separately for focused field validation.
NAMESPACE_PATTERN = r"[A-Z]{3}[A-Z2-7]{13}"
SLUG_PATTERN = r"[A-Z0-9](?:[A-Z0-9_]{1,38}[A-Z0-9])"
BASE_SLUG_PATTERN = r"[A-Z0-9](?:[A-Z0-9_]{1,31}[A-Z0-9])"
DISAMBIGUATOR_PATTERN = r"[A-Z2-7]{6}"
MANIFESTATION_TYPE_PATTERN = "|".join(MANIFESTATION_TYPES)
HITOP_BASE_CODE_PATTERN = r"[0-9A-Za-z][0-9][0-9A-Za-z]{4}"

NAMESPACE_RE = re.compile(f"^{NAMESPACE_PATTERN}$")
SLUG_RE = re.compile(f"^{SLUG_PATTERN}$")
BASE_SLUG_RE = re.compile(f"^{BASE_SLUG_PATTERN}$")
DISAMBIGUATOR_RE = re.compile(f"^{DISAMBIGUATOR_PATTERN}$")

SUFFIX_RE = re.compile(
    rf"^M-(?P<manifestation_type>{MANIFESTATION_TYPE_PATTERN})-"
    rf"(?P<namespace>{NAMESPACE_PATTERN})-(?P<slug>{SLUG_PATTERN})$"
)

DISAMBIGUATED_SUFFIX_RE = re.compile(
    rf"^M-(?P<manifestation_type>{MANIFESTATION_TYPE_PATTERN})-"
    rf"(?P<namespace>{NAMESPACE_PATTERN})-"
    rf"(?P<base_slug>{BASE_SLUG_PATTERN})_(?P<disambiguator>{DISAMBIGUATOR_PATTERN})$"
)

FULL_CODE_RE = re.compile(
    rf"^(?P<hitop>{HITOP_BASE_CODE_PATTERN})\."
    rf"(?P<suffix>M-(?P<manifestation_type>{MANIFESTATION_TYPE_PATTERN})-"
    rf"(?P<namespace>{NAMESPACE_PATTERN})-(?P<slug>{SLUG_PATTERN}))$"
)
