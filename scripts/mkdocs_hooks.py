"""Inject release metadata into MkDocs pages from canonical project files."""

from __future__ import annotations

import json
import re
from html import escape
from pathlib import Path

from rdflib import OWL, RDF, RDFS, Graph

ROOT = Path(__file__).resolve().parents[1]
VERSION_TOKEN = "{{ hitop_ontology_version }}"
STATUS_TOKEN = "{{ hitop_project_status }}"
CORE_CONCEPTS_TOKEN = "{{ hitop_core_concepts_json }}"
LEGACY_ROUTES = {
    "about": "project/about-the-project",
    "about-the-project": "project/about-the-project",
    "status": "project/status-and-roadmap",
    "status-and-roadmap": "project/status-and-roadmap",
    "publication": "project/publication-and-citation",
    "publication-and-citation": "project/publication-and-citation",
    "hitop_base_vocabulary": "concepts/core-vocabulary",
    "core-vocabulary": "concepts/core-vocabulary",
    "concept-code-system": "concepts/code-system",
    "code-system": "concepts/code-system",
    "manifestation-suffixes": "concepts/manifestation-suffixes",
    "mapping-harmonization": "concepts/mapping-harmonization",
    "factorization-catalog": "models/factorizations",
    "factorizations": "models/factorizations",
    "diagram-viewer": "models/diagrams",
    "diagrams": "models/diagrams",
    "factorization-specification": "models/specification",
    "specification": "models/specification",
    "learning-factorization": "models/create-a-factorization",
    "create-a-factorization": "models/create-a-factorization",
    "tooling_examples": "reference/tooling-and-cli",
    "tooling-and-cli": "reference/tooling-and-cli",
    "build_and_installation": "reference/build-and-installation",
    "build-and-installation": "reference/build-and-installation",
    "quality": "reference/validation-and-quality",
    "validation-and-quality": "reference/validation-and-quality",
    "release_checklist": "reference/release-checklist",
    "release-checklist": "reference/release-checklist",
    "references": "reference/references",
}


def _release_metadata() -> dict[str, str]:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    version_match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject, re.MULTILINE)
    status_match = re.search(r'"Development Status :: \d+ - ([^"]+)"', pyproject)
    if not version_match or not status_match:
        raise RuntimeError("pyproject.toml has no project version or development-status classifier")
    version = version_match.group(1)
    development = status_match.group(1)
    ontology = (ROOT / "ontology" / "hitop.rdf").read_text(encoding="utf-8")
    match = re.search(r"<owl:versionInfo[^>]*>([^<]+)</owl:versionInfo>", ontology)
    if not match:
        raise RuntimeError("ontology/hitop.rdf has no owl:versionInfo")
    ontology_version = match.group(1).strip()
    if ontology_version != version:
        raise RuntimeError(
            f"Version drift: pyproject.toml={version}, ontology/hitop.rdf={ontology_version}"
        )
    return {"ontology_version": version, "project_status": development}


def _core_concepts_json() -> str:
    """Serialize canonical codes and labels for browser-side authoring validation."""

    graph = Graph()
    graph.parse(ROOT / "ontology" / "hitop.rdf", format="xml")
    namespace = "http://purl.org/hitop#"
    concepts = []
    for subject in graph.subjects(RDF.type, OWL.Class):
        iri = str(subject)
        if not iri.startswith(namespace):
            continue
        code = iri.removeprefix(namespace)
        label = next((str(value) for value in graph.objects(subject, RDFS.label)), code)
        comment = next((str(value) for value in graph.objects(subject, RDFS.comment)), "")
        concepts.append({"code": code, "label": label, "comment": comment})
    concepts.sort(key=lambda concept: concept["code"])
    return json.dumps(concepts, separators=(",", ":"))


def on_config(config):
    """Expose canonical release metadata to templates."""
    metadata = _release_metadata()
    config.extra["hitop"] = metadata
    return config


def on_page_markdown(markdown, **_kwargs):
    """Replace explicit metadata tokens in page Markdown."""
    metadata = _release_metadata()
    return (
        markdown.replace(VERSION_TOKEN, metadata["ontology_version"])
        .replace(STATUS_TOKEN, metadata["project_status"])
        .replace(CORE_CONCEPTS_TOKEN, escape(_core_concepts_json(), quote=False))
    )


def on_post_build(config, **_kwargs):
    """Create static redirects without keeping legacy Markdown pages in docs/."""

    site_dir = Path(config["site_dir"])
    for old_route, canonical_route in LEGACY_ROUTES.items():
        destination = f"../{canonical_route}/"
        redirect_dir = site_dir / old_route
        redirect_dir.mkdir(parents=True, exist_ok=True)
        (redirect_dir / "index.html").write_text(
            "<!doctype html>\n"
            '<html lang="en">\n'
            "<head>\n"
            '  <meta charset="utf-8">\n'
            f'  <meta http-equiv="refresh" content="0; url={escape(destination)}">\n'
            f'  <link rel="canonical" href="{escape(destination)}">\n'
            "  <title>Page moved</title>\n"
            "</head>\n"
            "<body>\n"
            f'  <p>This page has moved to <a href="{escape(destination)}">'
            f"{escape(canonical_route)}</a>.</p>\n"
            "</body>\n"
            "</html>\n",
            encoding="utf-8",
        )
