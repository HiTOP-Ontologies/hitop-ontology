# Release checklist

<div class="hitop-page-intro">
  <p>A repeatable checklist for verifying, tagging, publishing, and archiving a HiTOP Ontology release.</p>
  <span class="hitop-source">Source · <a href="https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/pyproject.toml">pyproject.toml</a> · <a href="https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/CHANGELOG.md">CHANGELOG.md</a> · <a href="https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/.github/workflows/ci.yml">.github/workflows/ci.yml</a></span>
</div>

Use this page for every release. It defines durable release criteria and does
not record the current state of individual issues or work packages.

## 1. Confirm the release scope and version

The Python package and canonical ontology form one release and therefore use
the same version. Specifications and schemas distributed in the repository are
included in the tagged snapshot but may follow their own documented versioning
rules.

| Artifact | Release requirement | Authoritative source |
| --- | --- | --- |
| Python package (`hitop-ontology-tools`) | Version matches the intended release tag | `project.version` in `pyproject.toml` |
| Canonical ontology | `owl:versionInfo` matches the Python package version | `ontology/hitop.rdf` |
| Generated ontology formats | Rebuilt from the canonical RDF source | `ontology/hitop.ttl`, `ontology/hitop.owl` |
| Factorization artifacts | Rebuilt from each changed hierarchy source | `factorizations/<id>/<version>/` |
| Documentation website | Builds from the same commit that will be tagged | `docs/`, `mkdocs.yml` |
| Release notes | Matching version section describes user-visible changes | `CHANGELOG.md` |

Before continuing, confirm that the intended tag is
`v{{ hitop_ontology_version }}` and that no artifact in the release scope still
reports a different version.

## 2. Complete the pre-release checks

Treat every item as a release requirement. Check an item only after reviewing
its result for the exact commit that will receive the tag.

- [ ] The release diff contains only intended changes and the working tree is clean.
- [ ] Package and ontology versions match the intended tag.
- [ ] Generated ontology and factorization artifacts are current and reproducible.
- [ ] The changelog contains a complete section for the release version.
- [ ] Unit, schema, documentation-example, and ontology validation checks pass.
- [ ] The supported Python-version matrix passes without missing environments.
- [ ] Ruff lint and formatting checks pass.
- [ ] Source and wheel distributions build successfully and their contents are reviewed.
- [ ] `mkdocs build --strict` completes successfully.
- [ ] Required CI jobs pass for the exact release commit.
- [ ] `CITATION.cff`, licensing information, and contributor attribution are current.
- [ ] The `prov:has_provenance` link uses a configured version-specific PURL whose redirect is fixed to `ontology/contributions.rdf` at an immutable approved commit; the record is included in the release archive.
- [ ] The release tag does not already exist locally or on the remote.

## 3. Verify the release candidate

Run the repository quality gate and the complete supported Python matrix from
the repository root. Continue only when every command exits successfully; see
[Build & installation](build-and-installation.md#release-verification) and
[Validation & quality](validation-and-quality.md) for the expected success output.

**Command**

```bash
scripts/validate_hitop_suffix_tooling.sh
.venv/bin/tox -e py310,py311,py312
.venv/bin/python scripts/rdf2ttl.py --output /tmp/hitop_release_gate.ttl
.venv/bin/python scripts/rdf2owl.py --output /tmp/hitop_release_gate.owl
.venv/bin/python -m build
.venv/bin/mkdocs build --strict
```

Review the generated distributions and confirm the version before tagging:

**Command**

```bash
.venv/bin/python -m zipfile --list dist/hitop_ontology_tools-{{ hitop_ontology_version }}-py3-none-any.whl
git diff --check
git status --short
git tag --list "v{{ hitop_ontology_version }}"
```

**Output**

```text
The wheel contents are listed for review.
git diff --check: no output
git status --short: no output
git tag --list: no output; the release tag does not yet exist
```

## 4. Create and publish the tag

Create an annotated tag only after the checklist and CI results have been
reviewed. Push the explicit tag name instead of all local tags, so unrelated
local tags cannot be published accidentally.

**Command**

```bash
git tag -a v{{ hitop_ontology_version }} -m "HiTOP Ontology v{{ hitop_ontology_version }}"
git push origin v{{ hitop_ontology_version }}
```

Verify that the remote tag resolves to the reviewed release commit before
creating the GitHub release.

## 5. Create the GitHub release

Prepare and review `RELEASE_NOTES.md` from the matching changelog section, then
publish it with the annotated tag. Attach any artifacts required by the
project's distribution policy.

**Command**

```bash
gh release create v{{ hitop_ontology_version }} \
  --repo HiTOP-Ontologies/hitop-ontology \
  --title "v{{ hitop_ontology_version }}" \
  --notes-file RELEASE_NOTES.md
```

After publication, verify the release page, attached files, installation
instructions, and documentation link from a clean environment.

## 6. Archive and record the release

If repository archiving is enabled, confirm that the published GitHub release
created an immutable archive and version-specific DOI. Record newly assigned
publication metadata in the repository in a follow-up change:

1. Add or update the DOI badge in `README.md`.
2. Add the version DOI and actual release date to `CITATION.cff`.
3. Confirm that the archive metadata, authors, title, version, and license match
   the GitHub release.
4. Preserve the concept DOI for citing the project as a whole and the version
   DOI for citing this exact release.

The archive step is optional when no archival integration is configured. It
must not change the already published tag or silently replace release assets.
