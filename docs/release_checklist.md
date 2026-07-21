# Release Checklist

Status: Vorlage
Stand: 2026-07-07
Bezug: [`ag-technik-konzept.md`](audit/20260615T191039+0200_hitop_ontology_release_audit/ag-technik-konzept.md) (Definition of Done), [`CHANGELOG.md`](../CHANGELOG.md)

## 1. Versionstabelle (TECH-T1-02)

| Artefakt | Version | Quelle |
| --- | --- | --- |
| Python-Paket (`hitop-ontology-tools`) | `0.1.0` | `pyproject.toml` |
| Ontologie (`ontology/hitop.rdf`) | `0.1.0` | `owl:versionInfo` |
| Manifestation-Record-Schema | noch nicht versioniert | offen, siehe `TECH-T5-03` |
| Suffix-Spezifikation (`docs/modular-namespaced-suffix-schema.md`) | `0.2.0` (Entwurf) | eigenständig versioniert, nicht an den Release-Tag gekoppelt |
| Mapping-Spezifikation (`docs/mapping-und-harmonisierung.md`) | `1.0.0` | eigenständig versioniert, nicht an den Release-Tag gekoppelt |

Der Release-Tag (Abschnitt 3) bezieht sich auf Python-Paket + Ontologie
gemeinsam (`v0.1.0`). Spezifikationsdokumente unter `docs/` behalten ihre
eigene, unabhängige Versionierung.

## 2. Checkliste vor Tag/Release

- [x] `git status` sauber (`TECH-T1-01`)
- [x] Versionstabelle aktuell (`TECH-T1-02`, Abschnitt 1)
- [ ] CI grün: Tests, Build, Schema-Parse, RDF-Konvertierung (`TECH-T3-01`/`02`)
- [ ] ROBOT-Validierung dokumentiert (`TECH-T4-03`)
- [x] `CHANGELOG.md` aktuell für die anstehende Version (`TECH-T1-06`)
- [x] `CITATION.cff` vorhanden, DOI-Feld noch offen (`TECH-T1-07`)
- [ ] **Clinical Lab Go/No-Go-Freigabe liegt vor (`CLIN-C5-02`) — Blocker für Abschnitt 3 und 4**

## 3. Release-Tag setzen (TECH-T1-03) — vorbereitet, nicht ausgeführt

Blockiert, bis alle CLIN-Tasks auf `done` stehen und `CLIN-C5-02` eine
Freigabe dokumentiert. Sobald freigegeben, in dieser Reihenfolge:

```bash
scripts/validate_hitop_suffix_tooling.sh
.venv/bin/tox -e py310,py311,py312
git tag -a v0.1.0 -m "HiTOP Ontology v0.1.0"
git push --tags
gh release create v0.1.0 \
  --repo HiTOP-Ontologies/hitop-ontology \
  --title "v0.1.0" \
  --notes-file <(awk '/^## \[0\.1\.0\]/{flag=1;next}/^## \[/{flag=0}flag' CHANGELOG.md)
```

Release-Notes-Inhalt kommt 1:1 aus dem `[0.1.0]`-Abschnitt in
[`CHANGELOG.md`](../CHANGELOG.md).

## 4. Zenodo-DOI erzeugen (TECH-T1-04) — vorbereitet, nicht ausgeführt

Blockiert wie Abschnitt 3. Zusätzlich ein manueller Schritt außerhalb des
Repos, der nicht per CLI erledigt werden kann: Zenodo-GitHub-Integration für
`HiTOP-Ontologies/hitop-ontology` unter den Zenodo-GitHub-Einstellungen
aktivieren (erfordert Login mit Schreibzugriff auf den `HiTOP-Ontologies`-Account).
Danach erzeugt jedes neue GitHub-Release automatisch eine archivierte Version
mit DOI.

Nach Erhalt des DOI:

1. DOI-Badge in `README.md` neben den bestehenden Badges ergänzen.
2. `doi:` Feld in [`CITATION.cff`](../CITATION.cff) ergänzen.
3. `date-released` in `CITATION.cff` auf das tatsächliche Release-Datum setzen.
