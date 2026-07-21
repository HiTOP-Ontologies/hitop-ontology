"""Command line interface for HiTOP suffix tooling."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .code import build_code, validate_code
from .disambiguator import (
    attach_disambiguator,
    build_disambiguation_basis,
    generate_disambiguator,
)
from .exceptions import HiTOPSuffixError
from .mapping import compute_features, propose_relation, score_band
from .metadata import load_yaml, validate_metadata
from .namespace import (
    canonicalize_namespace_identifier,
    generate_namespace_token,
)
from .slug import slugify


def _print_json(value: Any) -> None:
    """Write stable, human-readable JSON to stdout."""

    # Sorted keys make CLI output deterministic for docs, regression tests, and
    # simple shell-based comparisons.
    print(json.dumps(value, indent=2, sort_keys=True))


def _cmd_namespace(args: argparse.Namespace) -> int:
    """Generate and print a canonical namespace identifier and token."""

    canonical = canonicalize_namespace_identifier(args.kind, args.identifier)
    token = generate_namespace_token(args.kind, args.identifier)
    _print_json({"canonical_identifier": canonical, "namespace_token": token})
    return 0


def _cmd_slug(args: argparse.Namespace) -> int:
    """Generate and print a normalized manifestation slug."""

    _print_json({"slug": slugify(args.label)})
    return 0


def _cmd_disambiguator(args: argparse.Namespace) -> int:
    """Generate disambiguation metadata for a possible local slug collision."""

    basis = build_disambiguation_basis(
        namespace_identifier=args.namespace_identifier,
        hitop_base_code=args.hitop,
        manifestation_type=args.manifestation_type,
        study_id=args.study_id,
        instrument=args.instrument,
        item_id_or_local_concept_id=args.item_id,
    )
    disambiguator = generate_disambiguator(basis)
    payload = {
        "basis": basis,
        "disambiguator": disambiguator,
    }
    if args.base_slug:
        payload["slug"] = attach_disambiguator(args.base_slug, basis)
    _print_json(payload)
    return 0


def _cmd_build_code(args: argparse.Namespace) -> int:
    """Build and print a canonical full manifestation suffix code."""

    code = build_code(
        hitop_base_code=args.hitop,
        manifestation_type=args.manifestation_type,
        namespace_token=args.namespace_token,
        slug=args.slug,
    )
    _print_json({"code": code})
    return 0


def _cmd_validate_code(args: argparse.Namespace) -> int:
    """Validate one manifestation suffix code and return a shell-safe status."""

    errors = validate_code(args.code)
    _print_json({"valid": not errors, "errors": errors})
    return 0 if not errors else 1


def _cmd_validate_metadata(args: argparse.Namespace) -> int:
    """Validate one YAML metadata record and print a structured report."""

    record = load_yaml(args.path)
    report = validate_metadata(record)
    _print_json(report.as_dict())
    return 0 if report.valid else 1


def _cmd_mapping_score(args: argparse.Namespace) -> int:
    """Score a mapping candidate from two YAML metadata records."""

    source = load_yaml(args.source)
    target = load_yaml(args.target)
    features = compute_features(
        source,
        target,
        hierarchy_similarity=args.hierarchy_similarity,
        external_mapping_support=args.external_mapping_support,
        context_penalty=args.context_penalty,
    )
    score = features.score()
    _print_json(
        {
            "features": asdict(features),
            "score": score,
            "band": score_band(score),
            "proposed_relation": propose_relation(features),
        }
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""

    parser = argparse.ArgumentParser(
        prog="hitop-suffix",
        description="Tools for HiTOP modular namespaced manifestation suffixes.",
    )
    # Each subcommand stores a handler with the same return-code contract:
    # 0 means success, 1 means validation failed, and 2 means tooling misuse.
    subparsers = parser.add_subparsers(dest="command", required=True)

    namespace = subparsers.add_parser("namespace", help="Generate a namespace token.")
    namespace.add_argument("kind", help="Three-letter namespace kind, e.g. ROR.")
    namespace.add_argument("identifier", help="Source identifier, e.g. a ROR URL.")
    namespace.set_defaults(func=_cmd_namespace)

    slug = subparsers.add_parser("slug", help="Generate a normalized slug.")
    slug.add_argument("label", help="Human-readable label.")
    slug.set_defaults(func=_cmd_slug)

    disambiguator = subparsers.add_parser(
        "disambiguator",
        help="Generate a six-character disambiguator from stable source metadata.",
    )
    disambiguator.add_argument("--namespace-identifier", required=True)
    disambiguator.add_argument("--hitop", required=True)
    disambiguator.add_argument("--manifestation-type", required=True)
    disambiguator.add_argument("--study-id", required=True)
    disambiguator.add_argument("--instrument", required=True)
    disambiguator.add_argument("--item-id", required=True)
    disambiguator.add_argument("--base-slug")
    disambiguator.set_defaults(func=_cmd_disambiguator)

    build = subparsers.add_parser("build-code", help="Build a manifestation code.")
    build.add_argument("--hitop", required=True)
    build.add_argument("--manifestation-type", required=True)
    build.add_argument("--namespace-token", required=True)
    build.add_argument("--slug", required=True)
    build.set_defaults(func=_cmd_build_code)

    validate_code_parser = subparsers.add_parser(
        "validate-code", help="Validate a manifestation code."
    )
    validate_code_parser.add_argument("code")
    validate_code_parser.set_defaults(func=_cmd_validate_code)

    metadata = subparsers.add_parser("validate-metadata", help="Validate a YAML metadata record.")
    metadata.add_argument("path", type=Path)
    metadata.set_defaults(func=_cmd_validate_metadata)

    mapping = subparsers.add_parser(
        "mapping-score", help="Score a mapping candidate from two YAML records."
    )
    mapping.add_argument("source", type=Path)
    mapping.add_argument("target", type=Path)
    mapping.add_argument("--hierarchy-similarity", type=float, default=0.0)
    mapping.add_argument("--external-mapping-support", type=float, default=0.0)
    mapping.add_argument("--context-penalty", type=float, default=0.0)
    mapping.set_defaults(func=_cmd_mapping_score)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the command line interface."""

    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except HiTOPSuffixError as exc:
        _print_json({"valid": False, "errors": [str(exc)]})
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
