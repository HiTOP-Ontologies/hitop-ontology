#!/usr/bin/env python3
"""Validate code examples embedded in the HiTOP suffix documentation.

The script extracts manifestation code examples from Markdown files in ``docs``
and validates them with the package parser. The ``<HITOP_BASE_CODE>`` placeholder
is normalized to a representative base code before parsing.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from hitop.suffix.code import validate_code

ROOT_DIR = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT_DIR / "docs"
PLACEHOLDER_HITOP = "U0aB2X"

CODE_RE = re.compile(
    r"(?P<code>(?:[0-9A-Za-z][0-9][0-9A-Za-z]{4}|<HITOP_BASE_CODE>)\.M-"
    r"(?:GS|CS|SY|AF|CG|PC|BH|SS|SL|SU|IR|IM)-"
    r"[A-Z]{3}[A-Z2-7]{13}-[A-Z0-9_]+)"
)


def normalize_placeholder(code: str) -> str:
    """Replace documentation placeholders with a concrete representative code."""

    return code.replace("<HITOP_BASE_CODE>", PLACEHOLDER_HITOP)


def iter_markdown_files() -> list[Path]:
    """Return website and source-specification Markdown files below ``docs``."""

    excluded_directories = {"assets", "audit", "overrides"}
    return sorted(
        path
        for path in DOCS_DIR.rglob("*.md")
        if not excluded_directories.intersection(path.relative_to(DOCS_DIR).parts)
    )


def main() -> int:
    """Run documentation example validation."""

    failures: list[str] = []
    checked = 0

    for path in iter_markdown_files():
        text = path.read_text(encoding="utf-8")
        for match in CODE_RE.finditer(text):
            raw_code = match.group("code")
            code = normalize_placeholder(raw_code)
            errors = validate_code(code)
            checked += 1
            if errors:
                failures.append(f"{path}:{match.start()}: {raw_code}: {errors}")

    if failures:
        print("Documentation code validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print(f"Validated {checked} documentation code example(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
