"""Generate canonical HiTOP local concept codes from a CSV file.

The script reads rows with ``Code``, ``Segment`` and ``Segment Level`` columns,
calculates a deterministic two-character checksum, and writes the original rows
plus two output columns:

``CheckDigit``
    The two-character Base62 checksum.

``HiTOP``
    The local concept code stem plus checksum, for example ``C001qy``.  For
    backwards compatibility this column does not include the ``HiTOP`` prefix;
    the prefix is used only as checksum input.

Example
-------

```bash
hitop-codegen src/data/hitop_base_vocabulary.csv /tmp/hitop_base_vocabulary.csv --prefix HiTOP
```
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections.abc import Iterable
from pathlib import Path

try:
    from .HITOPChecksum import (
        BASE62_ALPHABET,
        DEFAULT_PREFIX,
        HITOPChecksum,
        HITOPChecksumError,
        base62_encode,  # noqa: F401 -- re-exported as hitop.base62_encode
    )
    from .HITOPChecksum import (
        calculate_check_digit as _calculate_check_digit,
    )
except ImportError:  # pragma: no cover - direct script execution fallback
    from HITOPChecksum import (
        BASE62_ALPHABET,
        DEFAULT_PREFIX,
        HITOPChecksum,
        HITOPChecksumError,
    )
    from HITOPChecksum import (
        calculate_check_digit as _calculate_check_digit,
    )

REQUIRED_COLUMNS = ("Code", "Segment", "Segment Level")
CHECK_DIGIT_COLUMN = "CheckDigit"
CODE_COLUMN = "HiTOP"

# Backwards-compatible public names from the original script.
base62_alphabet = BASE62_ALPHABET


class HiTOPCSVError(ValueError):
    """Raised when the input CSV cannot be converted into HiTOP codes."""


def calculate_check_digit(prefix: str, segment: str, code: str) -> str:
    """Calculate the canonical two-character checksum.

    This wrapper preserves the historical public function from ``hitop.py``.
    The implementation lives in ``HITOPChecksum.py`` so both entry points use the
    same production algorithm.
    """

    return _calculate_check_digit(prefix, segment, code)


def _ensure_required_columns(fieldnames: Iterable[str] | None) -> list[str]:
    """Return validated field names or raise a CSV-specific error."""

    if fieldnames is None:
        raise HiTOPCSVError("Input CSV has no header row.")

    normalized = [field.strip() for field in fieldnames]
    duplicates = sorted({field for field in normalized if normalized.count(field) > 1})
    if duplicates:
        raise HiTOPCSVError(
            "Input CSV contains duplicate column(s) after trimming whitespace: "
            + ", ".join(duplicates)
        )

    missing = [column for column in REQUIRED_COLUMNS if column not in normalized]
    if missing:
        raise HiTOPCSVError("Input CSV is missing required column(s): " + ", ".join(missing))
    return normalized


def _output_fieldnames(fieldnames: list[str]) -> list[str]:
    """Append generated columns once, replacing stale generated values."""

    preserved = [field for field in fieldnames if field not in {CHECK_DIGIT_COLUMN, CODE_COLUMN}]
    return [*preserved, CHECK_DIGIT_COLUMN, CODE_COLUMN]


def _row_value(row: dict[str, str], column: str, row_number: int) -> str:
    """Read a non-empty cell value with a row-aware error message."""

    value = (row.get(column) or "").strip()
    if not value:
        raise HiTOPCSVError(f"Row {row_number}: column {column!r} is empty.")
    return value


def build_hitop_code(row: dict[str, str], *, prefix: str, row_number: int) -> tuple[str, str]:
    """Build ``(check_digit, local_code)`` for one CSV row."""

    segment = _row_value(row, "Segment", row_number) + _row_value(row, "Segment Level", row_number)
    concept_code = _row_value(row, "Code", row_number)
    checksum = HITOPChecksum.from_parts(
        prefix=prefix,
        segment=segment,
        concept_code=concept_code,
    )
    return checksum.check_digit, checksum.with_check_digit()


def process_csv(
    input_file: Path,
    output_file: Path,
    prefix: str = DEFAULT_PREFIX,
    *,
    delimiter: str = ";",
) -> None:
    """Read a source CSV and write generated checksum/code columns.

    Parameters
    ----------
    input_file:
        Source CSV path.  The file must contain ``Code``, ``Segment`` and
        ``Segment Level`` columns.
    output_file:
        Destination CSV path.  Parent directories are created automatically.
    prefix:
        Code system prefix used as part of the checksum input.
    delimiter:
        CSV delimiter.  The repository source files use semicolons.
    """

    if len(delimiter) != 1:
        raise HiTOPCSVError("CSV delimiter must be exactly one character.")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with input_file.open("r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile, delimiter=delimiter)
        input_fieldnames = _ensure_required_columns(reader.fieldnames)
        reader.fieldnames = input_fieldnames
        fieldnames = _output_fieldnames(input_fieldnames)

        with output_file.open("w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(
                outfile,
                fieldnames=fieldnames,
                delimiter=delimiter,
                extrasaction="ignore",
            )
            writer.writeheader()

            # DictReader starts data rows after the header, so row 2 is the
            # first user-visible row in spreadsheet tools.
            for row_number, row in enumerate(reader, start=2):
                check_digit, hitop_code = build_hitop_code(
                    row,
                    prefix=prefix,
                    row_number=row_number,
                )
                row[CHECK_DIGIT_COLUMN] = check_digit
                row[CODE_COLUMN] = hitop_code
                writer.writerow(row)


def build_parser() -> argparse.ArgumentParser:
    """Create the command line parser for CSV code generation."""

    parser = argparse.ArgumentParser(
        description="Generate HiTOP local concept codes from a CSV file."
    )
    parser.add_argument("input_file", type=Path, help="Path to the input CSV file.")
    parser.add_argument("output_file", type=Path, help="Path to the output CSV file.")
    parser.add_argument(
        "--prefix",
        default=DEFAULT_PREFIX,
        help=f"Prefix used for checksum generation (default: {DEFAULT_PREFIX}).",
    )
    parser.add_argument(
        "--delimiter",
        default=";",
        help="Single-character CSV delimiter (default: ';').",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point returning a process exit status."""

    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        process_csv(
            args.input_file,
            args.output_file,
            args.prefix,
            delimiter=args.delimiter,
        )
    except (OSError, csv.Error, HiTOPCSVError, HITOPChecksumError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
