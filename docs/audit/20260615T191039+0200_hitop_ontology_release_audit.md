# HiTOP Ontology Release Audit

Audit-ID: `20260615T191039+0200_hitop_ontology_release_audit`
Datum: 2026-06-15 19:10:39 +0200
Ziel: Arbeitsfaehige Aufgabenliste fuer zwei Release-Arbeitsgruppen
Scope: Repository `hitop-ontology`, Ontologie, Schema, Dokumentation, Python-Tooling, Validierung

## Kurzstatus

| Bereich | Status | Release-Relevanz |
| --- | --- | --- |
| Python-Tooling | Gruen nach lokaler Validierung | nutzbar, aber CI/Build-Release fehlt |
| Ontologie-Artefakte | Teilweise offen | `hitop.rdf` ist im Git-Status als geloescht, `ontology/hitop.rdf` untracked |
| Suffix-Spezifikation | Offen | Dokument steht noch auf `Status: Entwurf` |
| Mapping-Spezifikation | Teilweise offen | Review-Level definiert, konkrete kuratierte Artefakte fehlen |
| Manifestation-Record-Schema | Offen | JSON-Schema ist flach, Python-Metadatenvalidator nutzt verschachtelte YAML-Struktur |
| Release-Dokumentation | Technische T6-Doku umgesetzt, Governance offen | Release-Gates dokumentiert; Changelog, Tagging und klinische Freigabe fehlen |
| Arbeitsbaum | Blocker | Viele Release-Dateien sind untracked; vor Release muss Commit-/Tag-Stand sauber sein |

## Aktuelle Evidenz

| Check | Ergebnis |
| --- | --- |
| `scripts/validate_hitop_suffix_tooling.sh` | 18 Tests OK, 28 Doku-Codebeispiele validiert |
| `python -m pytest -q` | 18 passed |
| `pip check` | keine broken requirements |
| `rdf2ttl.py --output /tmp/...` | erfolgreich, 1046 Turtle-Triples validiert |
| `rdf2owl.py --output /tmp/...` | erfolgreich, OWL geschrieben |
| `schema/manifestation-record.schema.json` | valides JSON |

## Release-Blocker

| ID | Blocker | Gruppe | Entscheidung/Output |
| --- | --- | --- | --- |
| R-B01 | Git-Arbeitsbaum ist nicht releasefaehig: `D hitop.rdf`, `ontology/hitop.rdf` untracked, viele neue Dateien untracked | Technik | finalen Dateipfad fuer RDF-Artefakt festlegen, Staging/Commit-Plan erstellen |
| R-B02 | Suffix-Schema ist noch `Entwurf` und nutzt Platzhalter wie `RORPLACEHOLDERAB` | Klinik + Technik | normative Version oder klarer Draft-Ausschluss fuer Release |
| R-B03 | JSON-Schema und Python-Metadatenmodell sind nicht deckungsgleich | Technik + Klinik | ein kanonisches Manifestation-Record-Modell festlegen |
| R-B04 | Mapping-Spezifikation fordert Review-Level 3/4 fuer normative Datenprodukte, aber konkrete Review-Artefakte fehlen | Klinik | Review-Board, Review-Protokoll und Freigabestatus dokumentieren |
| R-B05 | Kein CI-Workflow, kein Release-Tagging-Prozess, keine Artefakt-Checks fuer RDF/OWL/TTL im Repo | Technik | reproduzierbare Release-Pipeline definieren |

## Arbeitsgruppe Technik

### T1 Repository & Release-Management

| Task-ID | Prioritaet | Aufgabe | Deliverable |
| --- | --- | --- | --- |
| TECH-T1-02 | P0 | Alle neuen Release-Dateien bewusst stagen oder explizit ausschliessen | sauberer `git status` vor Tag |
| TECH-T1-03 | P0 | Release-Version fuer Code, Ontologie und Spezifikationen synchronisieren | Versionstabelle: Tooling, Ontologie, Schema, Docs |
| TECH-T1-04 | P1 | Release-Checkliste im Repo ergaenzen | `docs/release_checklist.md` oder README-Abschnitt |
| TECH-T1-05 | P1 | Tagging- und Changelog-Regel definieren | `CHANGELOG.md` und Tag-Konvention |

### T2 Build, Dependencies & Installation

Umsetzungsstand 2026-06-15: TECH-T2-01 bis TECH-T2-04 wurden umgesetzt. Die
kanonische Paketquelle ist `pyproject.toml`; `requirements-lock.txt` ist der
getestete Constraints-Snapshot; `tox.ini` definiert die Python-Matrix 3.10,
3.11 und 3.12; der Distributionsbuild ist dokumentierter Release-Gate;
Paketmetadaten wurden um URLs, Keywords und Classifier erweitert.

| Task-ID | Prioritaet | Aufgabe | Deliverable |
| --- | --- | --- | --- |
| TECH-T2-01 | P0 | `pyproject.toml` als offizielle Installationsquelle bestaetigen | README-Setup als normative Installationsanleitung |
| TECH-T2-02 | P1 | Entscheiden, ob ein Lockfile fuer reproduzierbare Release-Builds genutzt wird | `requirements-lock.txt` oder dokumentierter Verzicht |
| TECH-T2-03 | P1 | Minimal unterstuetzte Python-Version praktisch testen | Testmatrix fuer Python 3.10, 3.11, 3.12 |
| TECH-T2-04 | P2 | Paket-Metadaten vervollstaendigen | Projekt-URLs, classifiers, optional maintainer fields |

### T3 Validierung & CI

| Task-ID | Prioritaet | Aufgabe | Deliverable |
| --- | --- | --- | --- |
| TECH-T3-01 | P0 | CI fuer Tests, Compile, JSON-Schema-Parse und Doku-Codevalidierung einrichten | GitHub Actions oder vergleichbarer CI-Workflow |
| TECH-T3-02 | P0 | RDF/TTL/OWL-Konvertierung in CI gegen `/tmp` laufen lassen | CI-Step mit `rdf2ttl.py` und `rdf2owl.py` |
| TECH-T3-03 | P1 | JSON-Schema-Validierung fuer Manifestation Records automatisieren | Tests mit Beispielrecords |
| TECH-T3-04 | P1 | Negative Tests fuer fehlerhafte Codes, Namespaces und Metadaten erweitern | gezielte Regressionstests |
| TECH-T3-05 | P2 | Linting/Formatting-Entscheid treffen | Ruff/Black-Konfiguration oder dokumentierter Stil |

### T4 Ontologie-Artefakte

| Task-ID | Prioritaet | Aufgabe | Deliverable |
| --- | --- | --- | --- |
| TECH-T4-01 | P0 | Kanonische Source-Datei und generierte Artefakte festlegen | klare Regel: source RDF vs generierte OWL/TTL |
| TECH-T4-02 | P0 | `owl:versionInfo`-Datentypfehler in der Quelle bereinigen | kein `xsd:decimal` fuer Wert `0.1.0` |
| TECH-T4-03 | P1 | ROBOT-Validierung als externen Gate ergaenzen | dokumentierter ROBOT-Befehl und Ergebnis |
| TECH-T4-04 | P1 | Namespace-/Prefix-Policy pruefen | stabile Prefixliste fuer RDF/TTL/OWL |
| TECH-T4-05 | P2 | Generierte Artefakte deterministisch vergleichen | Hashes oder Snapshot-Diff im Release-Prozess |

### T5 Schema & Datenmodell

| Task-ID | Prioritaet | Aufgabe | Deliverable |
| --- | --- | --- | --- |
| TECH-T5-01 | P0 | Flat JSON-Schema vs verschachtelte YAML-Metadaten entscheiden | ein kanonisches Record-Format |
| TECH-T5-02 | P0 | Python-Validator, Generator und JSON-Schema angleichen | konsistente Felder: `suffix`/`suffix_block`, `namespace_token`/`namespace.token`, `description`/`definition` |
| TECH-T5-03 | P1 | Beispielrecords gegen Schema testen | valide und invalide Fixtures |
| TECH-T5-04 | P1 | Schema-Version und `$id` fuer Release fixieren | `schema/manifestation-record.schema.json` mit Release-Version |
| TECH-T5-05 | P2 | Extension-Felder `x_*` fachlich und technisch dokumentieren | kurze Extension-Policy |

### T6 Dokumentation & Developer Experience

Umsetzungsstand 2026-06-15: TECH-T6-01 bis TECH-T6-04 wurden umgesetzt.
`README.md` enthaelt Setup-, Test-, RDF-Konvertierungs- und Release-Gate-
Befehle; `scripts/README.md` dokumentiert Inputs, Outputs und Fehlerbilder der
operativen Skripte; `docs/tooling_examples.md` enthaelt kopierbare CLI- und
API-Beispiele mit erwarteter Ausgabe; `CONTRIBUTING.md` definiert den minimalen
Beitrags-, Validierungs- und Review-Prozess. Klinische Freigabe, Changelog und
Tagging bleiben eigene Aufgaben in CLIN-C5 bzw. TECH-T1.

| Task-ID | Prioritaet | Aufgabe | Deliverable |
| --- | --- | --- | --- |
| TECH-T6-01 | P0 | README um Release-spezifische Befehle erweitern | Setup, Test, RDF-Konvertierung, Release-Gates |
| TECH-T6-02 | P1 | Skript-README mit Inputs/Outputs und Fehlerbildern ergaenzen | operationalisierte Script-Doku |
| TECH-T6-03 | P1 | API-/CLI-Beispiele fuer `hitop-codegen` und `hitop-suffix` ergaenzen | kopierbare Beispiele mit erwarteter Ausgabe |
| TECH-T6-04 | P2 | Contributor-Hinweise ergaenzen | minimale `CONTRIBUTING.md` |

## Arbeitsgruppe Klinik

### C1 Ontologieinhalt & Definitionen

| Task-ID | Prioritaet | Aufgabe | Deliverable |
| --- | --- | --- | --- |
| CLIN-C1-01 | P0 | Alle Klassenlabels und Definitionen fachlich reviewen | Review-Tabelle mit Status pro Konzept |
| CLIN-C1-02 | P0 | Leere, generische oder mehrdeutige Definitionen markieren | Liste blockierender Definitionen |
| CLIN-C1-03 | P1 | Sprachkonsistenz Deutsch/Englisch entscheiden | Sprachpolicy fuer Labels, Kommentare, Definitionen |
| CLIN-C1-04 | P1 | Synonyme, Altlabels und klinisch gebraeuchliche Begriffe pruefen | kuratierte Synonymliste |
| CLIN-C1-05 | P2 | Beispiele fuer Grenzfaelle dokumentieren | klinische Annotation Notes |

### C2 Taxonomie & Hierarchie

| Task-ID | Prioritaet | Aufgabe | Deliverable |
| --- | --- | --- | --- |
| CLIN-C2-01 | P0 | Parent-Child-Beziehungen fachlich validieren | Freigabestatus fuer Hierarchie |
| CLIN-C2-02 | P0 | Segment- und Level-Zuordnung im Basisvokabular pruefen | signierte Review-Liste fuer `hitop_base_vocabulary.csv` |
| CLIN-C2-03 | P1 | Umgang mit transdiagnostischen Konzepten klaeren | Entscheidungspapier zu Mehrfachzuordnung |
| CLIN-C2-04 | P1 | Deprecated/ersetzte Konzepte identifizieren | Liste `active/deprecated/replaced_by` |

### C3 Manifestation-Suffixe

| Task-ID | Prioritaet | Aufgabe | Deliverable |
| --- | --- | --- | --- |
| CLIN-C3-01 | P0 | Manifestationstypen `GS, CS, SY, AF, CG, PC, BH, SS, SL, SU, IR, IM` klinisch bestaetigen | freigegebene Typenliste |
| CLIN-C3-02 | P0 | Regel fuer Vermeidung von `GS` fachlich operationalisieren | Entscheidungsbaum fuer Typzuordnung |
| CLIN-C3-03 | P1 | Slugs auf klinische Lesbarkeit und Eindeutigkeit pruefen | Reviewliste auffaelliger Slugs |
| CLIN-C3-04 | P1 | Disambiguator-Faelle fachlich pruefen | Freigabe fuer kollidierende Slugs |
| CLIN-C3-05 | P2 | Mindestmetadaten fuer klinische Interpretation festlegen | Pflichtfeldliste fuer Release |

### C4 Mapping & Harmonisierung

| Task-ID | Prioritaet | Aufgabe | Deliverable |
| --- | --- | --- | --- |
| CLIN-C4-01 | P0 | Review-Level-Verfahren finalisieren | Board-/Reviewer-Regel fuer Level 3/4 |
| CLIN-C4-02 | P0 | Regeln fuer `exactMatch`, `closeMatch`, `broadMatch`, `narrowMatch`, `relatedMatch` fachlich abnehmen | Mapping-Guideline mit Beispielen |
| CLIN-C4-03 | P1 | Automatische Mapping-Kandidaten gegen klinische Ausschlussregeln pruefen | kuratierte Mapping-Tabelle |
| CLIN-C4-04 | P1 | Konfliktfaelle und abweichende Schwellen/Zeitfenster dokumentieren | Konfliktregister |
| CLIN-C4-05 | P2 | Publikationsformat fuer Mappings festlegen | CSV/SKOS/FHIR ConceptMap-Entscheid |

### C5 Governance & Publikationsfreigabe

| Task-ID | Prioritaet | Aufgabe | Deliverable |
| --- | --- | --- | --- |
| CLIN-C5-01 | P0 | Klinische Verantwortliche pro Themengebiet benennen | Owner-Liste |
| CLIN-C5-02 | P0 | Freigabekriterien fuer Release definieren | klinisches Go/No-Go-Protokoll |
| CLIN-C5-03 | P1 | Umgang mit offenen Draft- oder Unreviewed-Artefakten festlegen | Release Scope: included/excluded |
| CLIN-C5-04 | P1 | Zitierfaehige Quellen und Evidenz fuer zentrale Konzepte pruefen | Quellen-/Citation-Liste |
| CLIN-C5-05 | P2 | Post-Release-Feedbackkanal definieren | Issue-/Review-Prozess |

## Empfohlene Arbeitsaufteilung

| Paket | Gruppe | Geeignete Rolle | Enthaltene Tasks |
| --- | --- | --- | --- |
| Release Engineering | Technik | DevOps/Repo Maintainer | TECH-T1, TECH-T3 |
| Ontology Build | Technik | Ontology Engineer | TECH-T4 |
| Schema & Tooling | Technik | Python/Data Engineer | TECH-T2, TECH-T5 |
| Clinical Taxonomy | Klinik | Senior Clinician/Taxonomy Lead | CLIN-C1, CLIN-C2 |
| Manifestation Review | Klinik | Instrument-/Assessment-Expert | CLIN-C3 |
| Mapping Board | Klinik | Clinical Reviewer + Methodologist | CLIN-C4 |
| Release Governance | Klinik + Technik | Product/Release Lead | CLIN-C5, TECH-T1 |

## Naechste 10 Arbeitsschritte

1. Repo-Status bereinigen: Dateiverschiebung `hitop.rdf` vs `ontology/hitop.rdf` entscheiden.
2. Schema-/Metadatenmodell-Entscheidung treffen.
3. Suffix-Spezifikation von `Entwurf` auf Release-Status bringen oder aus Release ausschliessen.
4. CI-Workflow fuer Tests und RDF-Konvertierung einrichten.
5. Klinisches Review-Board und Owner je Themengebiet benennen.
6. Ontologie-Definitionen und Hierarchie in Reviewtabellen exportieren.
7. Mapping-Review-Level und normative Mapping-Artefakte erstellen.
8. Release-Checkliste und Changelog ergaenzen.
9. ROBOT-Validierung dokumentieren und ausfuehren.
10. Sauberen Release-Commit und Tag erstellen.

## Done-Kriterien fuer Release

| Kategorie | Kriterium |
| --- | --- |
| Repo | `git status` enthaelt keine unbeabsichtigten untracked/deleted Dateien |
| Tooling | CI gruen fuer Tests, Compile, Schema-Parse, RDF-Konvertierung |
| Ontologie | RDF/OWL/TTL-Artefakte sind reproduzierbar und fachlich freigegeben |
| Schema | Manifestation-Record-Schema, Validator und Generator sind konsistent |
| Klinik | Konzepte, Definitionen, Hierarchie und Manifestationstypen sind reviewed |
| Mapping | Normative Mappings haben Review-Level 3 oder 4 oder sind explizit ausgenommen |
| Doku | README, Release Notes, Changelog und Freigabestatus sind aktualisiert |
