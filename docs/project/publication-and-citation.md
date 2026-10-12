# Publication & citation

<div class="hitop-page-intro">
  <p>Guidance for citing HiTOP Ontology and preserving provenance when publishing, reusing, or extending its artifacts.</p>
  <span class="hitop-source">Source · <a href="https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/README.md#citation">README.md / Citation</a> · <a href="https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/CONTRIBUTING.md">CONTRIBUTING.md</a></span>
</div>

## Citation

The repository includes a maintained [`CITATION.cff`](https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/CITATION.cff). Use the citation metadata and version information associated with the release or repository state used in your work:

```bibtex
@misc{hitop_ontology_2026,
  title  = {HiTOP Ontology},
  author = {{HiTOP Ontologies contributors}},
  year   = {<release year>},
  version = {<version used>},
  url    = {https://github.com/HiTOP-Ontologies/hitop-ontology}
}
```

## Reuse

The repository is available under the MIT License. A citation records scholarly provenance; the license defines reuse permissions. Preserve version information when exporting ontology or factorization artifacts.

## Publication home and institutional references

The canonical publication home is the independent
[HiTOP Ontology repository](https://github.com/HiTOP-Ontologies/hitop-ontology).
Institutional websites or implementation repositories are references to the
project's ecosystem; they are not alternative canonical copies.

| Context | Link target | How it should be described |
| --- | --- | --- |
| German Center for Mental Health (DZPG) | [DZPG website](https://www.dzpg.org/) | Research and application context for mental health; use a website link where no institutional source-code repository exists |
| Medical Informatics Initiative (MII) | [official MII GitHub organization](https://github.com/medizininformatik-initiative) | Downstream interoperability and implementation context; replace or supplement the organization link with the exact extension-module repository when its stable public URL is known |

These references do not imply that DZPG or MII owns, endorses, or jointly
governs HiTOP Ontology. A more specific claim such as “used by” should link to
the exact public implementation or specification that demonstrates that use.

## Recommended cross-referencing pattern

1. Publish releases in the canonical repository and archive each stable
   release with a DOI-capable service such as Zenodo.
2. Cite the release DOI and version from papers, institutional project pages,
   and downstream implementation repositories.
3. Link back from this repository to the exact downstream module or
   specification under “Ecosystem and reuse”.
4. Record responsibility separately: contributors in `CITATION.cff`, funding
   in acknowledgements, and organizational affiliations only where confirmed.

This pattern keeps the software citable and discoverable while preserving the
distinction between maintainership, funding, research context, and downstream
reuse.

## Contributing

Changes should keep clinical content, ontology artifacts, tooling, schemas, and documentation reviewable as separate concerns. Read `CONTRIBUTING.md`, add relevant tests, and run the documented validation gates before opening a pull request.
