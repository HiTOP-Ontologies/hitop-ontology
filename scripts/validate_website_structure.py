#!/usr/bin/env python3
"""Validate structural conventions for pages registered in ``mkdocs.yml``."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _nav_pages(items):
    for item in items:
        for label, value in item.items():
            if isinstance(value, list):
                yield from _nav_pages(value)
            else:
                yield label, value


def main() -> int:
    config = yaml.safe_load((ROOT / "mkdocs.yml").read_text(encoding="utf-8"))
    errors: list[str] = []
    for label, relative in _nav_pages(config["nav"]):
        path = ROOT / "docs" / relative
        if not path.is_file():
            errors.append(f"{relative}: nav target does not exist")
            continue
        text = path.read_text(encoding="utf-8")
        if relative == "index.md":
            if "<h1>" not in text:
                errors.append(f"{relative}: missing HTML H1")
            continue
        headings = re.findall(r"^# (.+)$", text, re.MULTILINE)
        if len(headings) != 1:
            errors.append(f"{relative}: expected exactly one H1, found {len(headings)}")
        elif headings[0].strip() != label.strip():
            errors.append(f"{relative}: nav label {label!r} differs from H1 {headings[0]!r}")
        if '<div class="hitop-page-intro">' not in text:
            errors.append(f"{relative}: missing .hitop-page-intro")
    if errors:
        print("Website structure validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Website structure validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
