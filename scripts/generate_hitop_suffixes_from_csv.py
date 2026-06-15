#!/usr/bin/env python3
"""Generate HiTOP manifestation suffix metadata from a CSV source table.

The script implements the process described in the repository documentation:

* resolve HiTOP base codes from the CSV or a local HiTOP vocabulary
* generate DZPG ROR-based namespace suffixes
* derive slugs from the source ``Label`` column
* validate every generated record against the metadata rules
* emit a structured YAML file and a compact CSV review table
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hitop.suffix.csv_generation import (
    GenerationConfig,
    generate_records,
    load_hitop_vocabulary,
    read_csv_rows,
    write_review_csv,
    write_yaml,
)
from hitop.suffix.exceptions import HiTOPSuffixError


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser."""

    parser = argparse.ArgumentParser(
        description="Generate HiTOP suffix metadata records from a source CSV."
    )
    parser.add_argument("input_csv", type=Path, help="Input CSV containing a Label column.")
    parser.add_argument(
        "--hitop-vocabulary",
        type=Path,
        default=Path("src/data/hitop_base_vocabulary.csv"),
        help="Semicolon-delimited HiTOP vocabulary CSV with Label and HiTOP columns.",
    )
    parser.add_argument(
        "--output-yaml",
        type=Path,
        default=Path("data/generated/hitop_dzpg_mds_suffixes.yaml"),
        help="Output YAML file for full metadata records.",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=Path("data/generated/hitop_dzpg_mds_suffixes_review.csv"),
        help="Output CSV review table.",
    )
    parser.add_argument(
        "--source-url",
        default="",
        help="Optional canonical source URL for the CSV or module specification.",
    )
    parser.add_argument("--status", default="draft", help="Status for generated records.")
    parser.add_argument("--created", default="2026-05-31", help="Creation date.")
    parser.add_argument("--modified", default="2026-05-31", help="Modification date.")
    parser.add_argument("--version", default="1", help="Record version.")
    return parser


def main() -> int:
    """Run CSV-to-suffix generation."""

    parser = build_parser()
    args = parser.parse_args()
    try:
        rows = read_csv_rows(args.input_csv)
        vocabulary = load_hitop_vocabulary(args.hitop_vocabulary)
        config = GenerationConfig(
            source_url=args.source_url,
            status=args.status,
            created=args.created,
            modified=args.modified,
            version=args.version,
        )
        records = generate_records(rows, config=config, vocabulary=vocabulary)
        write_yaml(records, args.output_yaml)
        write_review_csv(records, args.output_csv)
    except HiTOPSuffixError as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, indent=2))
        return 1

    print(
        json.dumps(
            {
                "valid": True,
                "records": len(records),
                "output_yaml": str(args.output_yaml),
                "output_csv": str(args.output_csv),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
