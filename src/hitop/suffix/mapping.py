"""Mapping candidate scoring utilities.

The scoring implementation is intentionally transparent and deterministic. It
is suitable for candidate ranking and review triage, but it is not a replacement
for curated mapping decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any

from .normalization import normalize_text


def _similarity(left: str, right: str) -> float:
    """Return a stable string similarity score in the range 0..1."""

    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0
    return SequenceMatcher(None, left, right).ratio()


def _token_jaccard(left: str, right: str) -> float:
    """Return token-set Jaccard similarity for normalized free text."""

    left_tokens = set(normalize_text(left).split())
    right_tokens = set(normalize_text(right).split())
    if not left_tokens and not right_tokens:
        return 1.0
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def _get(record: dict[str, Any], dotted_key: str, default: str = "") -> str:
    """Read a nested mapping value using a dotted key path."""

    value: Any = record
    for part in dotted_key.split("."):
        if not isinstance(value, dict):
            return default
        value = value.get(part, default)
    if value is None:
        return default
    return str(value)


@dataclass(frozen=True, slots=True)
class MappingFeatures:
    """Feature vector used to score a mapping candidate."""

    base_code_match: float
    manifestation_type_match: float
    slug_similarity: float
    label_similarity: float
    definition_similarity: float
    operationalization_similarity: float
    hierarchy_similarity: float
    external_mapping_support: float
    context_penalty: float

    def score(self) -> float:
        """Return the weighted score described in the mapping specification."""

        # Keep the weighted sum visible instead of hiding it in configuration:
        # release reviewers need to audit why a candidate lands in a score band.
        raw_score = (
            0.20 * self.base_code_match
            + 0.10 * self.manifestation_type_match
            + 0.10 * self.slug_similarity
            + 0.15 * self.label_similarity
            + 0.20 * self.definition_similarity
            + 0.15 * self.operationalization_similarity
            + 0.05 * self.hierarchy_similarity
            + 0.05 * self.external_mapping_support
            + self.context_penalty
        )
        return max(0.0, min(1.0, raw_score))


def compute_features(
    source: dict[str, Any],
    target: dict[str, Any],
    *,
    hierarchy_similarity: float = 0.0,
    external_mapping_support: float = 0.0,
    context_penalty: float = 0.0,
) -> MappingFeatures:
    """Compute mapping features for two metadata records."""

    source_operationalization = " ".join(
        [
            _get(source, "operationalization.instrument"),
            _get(source, "operationalization.time_window"),
            _get(source, "operationalization.threshold"),
            _get(source, "operationalization.scoring_rule"),
        ]
    )
    target_operationalization = " ".join(
        [
            _get(target, "operationalization.instrument"),
            _get(target, "operationalization.time_window"),
            _get(target, "operationalization.threshold"),
            _get(target, "operationalization.scoring_rule"),
        ]
    )

    # Clamp externally supplied signals so one bad caller cannot move a score
    # outside the documented 0..1 range or turn a penalty into a bonus.
    return MappingFeatures(
        base_code_match=float(source.get("hitop_base_code") == target.get("hitop_base_code")),
        manifestation_type_match=float(
            source.get("manifestation_type") == target.get("manifestation_type")
        ),
        slug_similarity=_similarity(
            normalize_text(source.get("slug", "")),
            normalize_text(target.get("slug", "")),
        ),
        label_similarity=_token_jaccard(
            source.get("preferred_label", ""),
            target.get("preferred_label", ""),
        ),
        definition_similarity=_token_jaccard(
            source.get("definition", ""),
            target.get("definition", ""),
        ),
        operationalization_similarity=_token_jaccard(
            source_operationalization,
            target_operationalization,
        ),
        hierarchy_similarity=max(0.0, min(1.0, hierarchy_similarity)),
        external_mapping_support=max(0.0, min(1.0, external_mapping_support)),
        context_penalty=max(-1.0, min(0.0, context_penalty)),
    )


def score_band(score: float) -> str:
    """Return the configured score band."""

    if score >= 0.90:
        return "very_high"
    if score >= 0.75:
        return "high"
    if score >= 0.50:
        return "medium"
    return "low"


def propose_relation(features: MappingFeatures) -> str:
    """Propose a conservative SKOS relation for review triage."""

    score = features.score()
    if score < 0.50:
        return "noMap"
    if (
        score >= 0.90
        and features.definition_similarity >= 0.90
        and features.operationalization_similarity >= 0.80
        and features.manifestation_type_match == 1.0
    ):
        return "skos:exactMatch"
    if score >= 0.75:
        return "skos:closeMatch"
    return "skos:relatedMatch"
