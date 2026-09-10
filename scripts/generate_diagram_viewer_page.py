#!/usr/bin/env python3
# ruff: noqa: E501 -- generated Markdown paragraphs stay readable as source text.
"""Generate the interactive factorization diagram viewer page.

Embeds every factorization's current ``<version>_diagram.json`` inline (no
``fetch()``, so the page works offline and from any relative depth), read
fresh from ``factorizations/*/v*/*_diagram.json`` on every run — never
copy-pasted or hand-maintained, so the page can never drift from the data
it renders.

The page itself carries no executable ``<script>`` tags — only the inert
``<script type="application/json">`` data blocks below, plus the select and
container markup. All wiring lives in
``docs/assets/javascripts/diagram-viewer.js``, loaded site-wide via
``mkdocs.yml``'s ``extra_javascript`` (alongside d3 and
``factorization-icicle.js``) and re-run on Material's ``document$`` after
every instant-navigation swap. A plain ``<script src>``/``<script>`` inside
the page's own content would work on a hard page load, but
``navigation.instant`` swaps in-app navigations via innerHTML, and a
<script> element inserted that way never executes — only a real full-page
load parses and runs it. Wiring the interaction from the persistent,
once-loaded JS file instead of the swapped content is what makes the
diagram render on an in-app click, not just on a hard reload.
"""

from __future__ import annotations

import json

from _factorization_catalog_shared import ROOT, catalog_rows

OUTPUT = ROOT / "docs" / "models" / "diagrams.md"


def main() -> None:
    rows = [row for row in catalog_rows() if row.diagram_json_relative]
    # HiTOP Working Model is the intended default view; diagram-viewer.js
    # also enforces this at runtime so a future catalog reorder can't
    # silently change it, but the `selected` attribute keeps the no-JS
    # markup correct too.
    options = "\n".join(
        f'      <option value="{row.factorization_id}"'
        f"{' selected' if row.factorization_id == 'working-model' else ''}>"
        f"{row.title}</option>"
        for row in rows
    )
    fallback_rows = "\n".join(
        f"| {row.title} | **{row.status}** | "
        f"[Hierarchy and provenance](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/{row.readme_relative}) | "
        f"[Diagram data](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/{row.diagram_json_relative}) |"
        for row in rows
    )
    data_blocks = []
    for row in rows:
        diagram = json.loads((ROOT / row.diagram_json_relative).read_text(encoding="utf-8"))
        payload = json.dumps(diagram, ensure_ascii=False, separators=(",", ":"))
        data_blocks.append(
            f'  <script type="application/json" id="data-{row.factorization_id}">{payload}</script>'
        )
    data_script_blocks = "\n".join(data_blocks)

    content = f"""# Diagrams

<div class="hitop-page-intro">
  <p>Every factorization rendered as a live icicle diagram, straight from its own generated diagram data.</p>
  <span class="hitop-source">Status · Generated and validated during the Pages build</span>
  <span class="hitop-source">Generated source · <a href="https://github.com/HiTOP-Ontologies/hitop-ontology/tree/main/factorizations">factorizations/*/v*/*_diagram.json</a></span>
</div>

### Diagram data and non-JavaScript fallback

The interactive diagram is an enhancement of the same generated data listed below. This table remains available when JavaScript is disabled and provides the status, hierarchy provenance, and complete diagram data for every selectable factorization.

| Factorization | Status | Source and provenance | Generated diagram data |
| --- | --- | --- | --- |
{fallback_rows}

## How to read it

Every diagram is an icicle layout: one row per hierarchy level (Factor, Superspectrum, Spectrum, Subfactor, with Component and Trait sharing a single bottom row, matching the official HiTOP figures), rather than one row per raw tree depth. Color follows a single, factorization-wide rule (`src/hitop/factorization/colors.py`): a fixed 24-color palette is spread evenly across every Factor, Superspectrum, Spectrum, and Subfactor node in tree order, so a whole branch reads as one continuous gradient, the same way the official HiTOP figures color a branch consistently; Component and Trait nodes take a progressively lighter, less saturated shade of their direct parent's color instead of a palette entry of their own. A dashed connector or outline marks a node the source hierarchy flags `provisional: true`.

Click any box to focus its subtree in the legend below the diagram. The toolbar above the diagram shares a link or downloads the current view as SVG, PNG, or a print-ready PDF.

<div class="hitop-diagram-viewer">
  <label for="factorization-select">Factorization<select id="factorization-select">
{options}
  </select></label>
  <div id="diagram-container"></div>
</div>

<style>
.hitop-diagram-viewer{{margin:1.5rem 0}}
.hitop-diagram-viewer label{{display:flex;align-items:center;gap:.6rem;margin-bottom:1rem;font-size:.78rem;font-weight:750;color:var(--md-default-fg-color)}}
.hitop-diagram-viewer select{{font-size:.78rem;padding:.4rem .6rem;border-radius:4px;border:1px solid var(--hitop-line, var(--md-default-fg-color--lightest));background:var(--md-default-bg-color);color:var(--md-default-fg-color)}}
.hitop-diagram-fallback{{padding:2.5rem 1.5rem;text-align:center;border:1px dashed var(--hitop-line, var(--md-default-fg-color--lightest));border-radius:6px}}
.hitop-diagram-fallback p{{margin:0 0 1rem;color:var(--md-default-fg-color--light);font-size:.82rem}}
</style>

{data_script_blocks}

Every diagram compiles mechanically from `<version>_hierarchy.yaml` via `scripts/generate_factorization_diagram_data.py`, using the same validation logic as the test suite — [see the full catalog](factorizations.md) for status and provenance, or [create a factorization](create-a-factorization.md) to compose one yourself.
"""
    OUTPUT.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
