#!/usr/bin/env python3
"""Shared catalog data for the generated factorization website pages.

Used by both ``generate_factorization_catalog.py`` (the catalog table) and
``generate_diagram_viewer_page.py`` (the interactive diagram dropdown), so
the display order and title cleanups can never drift between the two pages.
This module has no ``main()`` — it is not a script, only a shared import.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Display order: the integrative Working Model first, then the three
# published Kotov et al. superspectrum factorizations, then the applied
# DZPG minimal-dataset mapping, then the empirically derived bass-ackwards
# structure. A directory not listed here (a newly added factorization)
# sorts alphabetically after all listed ones, so a build never silently
# drops a row.
CATALOG_ORDER = [
    "working-model",
    "emotional-dysfunction",
    "externalizing",
    "psychosis",
    "dzpg-mds",
    "bass-ackwards",
]

# Display-only title cleanups, keyed by factorization directory id. These do
# not touch the source README.md — only how its title renders on the
# website.
TITLE_OVERRIDES = {
    "dzpg-mds": lambda title: title.removeprefix("HiTOP "),
}


@dataclass(frozen=True, slots=True)
class FactorizationRow:
    """One factorization, as displayed on the website."""

    factorization_id: str
    title: str
    version: str
    status: str
    readme_relative: str
    diagram_json_relative: str | None


def _extract(readme: Path) -> FactorizationRow:
    text = readme.read_text(encoding="utf-8")
    title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    status_match = re.search(r"^Status:\s+\*\*(draft|active|deprecated)\*\*", text, re.MULTILINE)
    factorization_id = readme.parent.parent.name
    title = title_match.group(1).strip() if title_match else factorization_id
    title = TITLE_OVERRIDES.get(factorization_id, lambda value: value)(title)
    status = status_match.group(1) if status_match else "unknown"
    version = readme.parent.name
    diagram_candidates = sorted(readme.parent.glob("*_diagram.json"))
    diagram_relative = (
        diagram_candidates[0].relative_to(ROOT).as_posix() if diagram_candidates else None
    )
    return FactorizationRow(
        factorization_id=factorization_id,
        title=title,
        version=version,
        status=status,
        readme_relative=readme.relative_to(ROOT).as_posix(),
        diagram_json_relative=diagram_relative,
    )


def _sort_key(row: FactorizationRow) -> tuple[int, str]:
    if row.factorization_id in CATALOG_ORDER:
        return (CATALOG_ORDER.index(row.factorization_id), "")
    return (len(CATALOG_ORDER), row.factorization_id)


def catalog_rows() -> list[FactorizationRow]:
    """Return every factorization's current README metadata, in display order."""

    rows = [_extract(path) for path in sorted((ROOT / "factorizations").glob("*/v*/README.md"))]
    rows.sort(key=_sort_key)
    return rows
