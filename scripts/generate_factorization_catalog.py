#!/usr/bin/env python3
# ruff: noqa: E501 -- generated Markdown paragraphs stay readable as source text.
"""Generate the website factorization catalog from version README files."""

from __future__ import annotations

from _factorization_catalog_shared import ROOT, catalog_rows

OUTPUT = ROOT / "docs" / "models" / "factorizations.md"
START = "<!-- BEGIN GENERATED FACTORIZATION CATALOG -->"
END = "<!-- END GENERATED FACTORIZATION CATALOG -->"


def main() -> None:
    rows = catalog_rows()
    table = "\n".join(
        f"| [{row.title}](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/{row.readme_relative}) "
        f"| `{row.version}` | **{row.status}** |"
        for row in rows
    )
    generated = f"""| Factorization | Directory version | Status |
| --- | --- | --- |
{table}
"""
    content = OUTPUT.read_text(encoding="utf-8")
    if content.count(START) != 1 or content.count(END) != 1:
        raise RuntimeError(f"{OUTPUT} must contain exactly one generated catalog marker pair")
    before, remainder = content.split(START, 1)
    _, after = remainder.split(END, 1)
    OUTPUT.write_text(f"{before}{START}\n{generated}{END}{after}", encoding="utf-8")


if __name__ == "__main__":
    main()
