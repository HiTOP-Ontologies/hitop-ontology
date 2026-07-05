# Faktorisierungen

Status: Aktuelle Spezifikation
Bezug: `factorizations/`, `schema/factorization-hierarchy.schema.json`

## 1. Zweck

Die HiTOP-Ontologie (`ontology/hitop.rdf`) ist ein Bausteinkasten: sie
definiert stabile, wiederverwendbare Konzeptklassen (Superspectra, Spectra,
Subfaktoren, Komponenten, Traits) sowie das gemeinsame Vokabular, mit dem
diese Bausteine zu einer Hierarchie zusammengesetzt werden
(`hitop:hasLevel`, `hitop:hasLevelType`, `hitop:hasTier` — siehe Abschnitt 4).

Eine Faktorisierung ist eine konkrete, versionierte Komposition dieser
Bausteine zu einer bestimmten HiTOP-Struktur (z. B. das HiTOP Working Model,
das Psychosis-Superspektrum oder das DZPG-MDS-Modul). Sie wird als ein
einziges, von Menschen lesbares YAML-Dokument gepflegt, damit auch
fachfremde Forscher:innen ihre eigene Faktorisierung abbilden können, ohne
RDF/OWL zu kennen. Ein Generator-Script (`scripts/generate_factorization_ontology.py`)
kompiliert dieses YAML anschließend mechanisch in eine formale RDF-Ontology,
die ausschließlich die stabilen Kernklassen referenziert.

## 2. Grundprinzipien

1. Eine Faktorisierung definiert keine neuen Konzepte. Sie referenziert nur
   `hitop_base_code`-Werte, die bereits in `ontology/hitop.ttl` existieren.
2. Der Kern-Ontologie werden durch eine Faktorisierung keine Triples
   hinzugefügt. `hitop:hasLevelType` und `hitop:hasTier` sind zwar im Kern
   deklariert, werden aber ausschließlich innerhalb einer
   Faktorisierungs-Datei asserted, nie im Kern selbst. Grund: sonst müsste
   jede wiederverwendete Klasse bei jeder neuen Faktorisierung angefasst
   werden, was Merge-Konflikte zwischen unabhängigen Faktorisierungen
   erzeugt und den Diff einer Klasse bedeutungslos macht.
3. Dasselbe Konzept kann in verschiedenen Faktorisierungen unterschiedliche
   Level einnehmen (z. B. ist `Mania` im Working Model und im Emotional-
   Dysfunction-Superspektrum ein `Subfactor`, im Psychosis-Superspektrum
   aber ein `Component`). Level ist deshalb niemals eine Eigenschaft der
   Klasse selbst, sondern ausschließlich eine Aussage innerhalb einer
   konkreten Faktorisierung.
4. Jede Faktorisierungsversion ist ein eigener, in sich abgeschlossener
   Ordner. Eine neue Version berührt nie den Ordner einer älteren Version.
5. Faktorisierungs-Dateien sind eigene Aussagen mit Provenienz, Status und
   Review-Level – analog zu den Mapping-Artefakten in
   [`mapping-und-harmonisierung.md`](mapping-und-harmonisierung.md).

## 3. Struktur

```text
factorizations/
  <factorization-id>/
    v<N>/
      <version>_hierarchy.yaml   # Pflicht: Baumstruktur, Provenienz, Ontology-Pin
      README.md                  # Pflicht: Kurzbeschreibung, Zitation, Status
      <version>_factorization.ttl  # generiert: siehe Abschnitt 6, nicht von Hand pflegen
```

`<factorization-id>` ist ein stabiler kebab-case-Bezeichner (z. B.
`working-model`, `bass-ackwards`, `dzpg-mds`, `psychosis`, `externalizing`,
`emotional-dysfunction`). `<version>` ist der Dateinamens-Präfix der
Hierarchy-Datei (z. B. `V1052k`) und entspricht keiner fortlaufenden
Zählung, sondern einer stabilen, pro Kuratierungslauf vergebenen Kennung.

## 4. Vokabular: `hasLevel`, `hasLevelType`, `hasTier`

Der Kern definiert zwei Klassenarten mit paralleler, aber getrennter Rolle:

| Klasse | Zweck |
| --- | --- |
| `hitop:O001Ih` (`Level`) | Der feste, gemeinsame vertikale Maßstab. Genau sechs Subklassen: `Factor`, `Superspectrum`, `Spectrum`, `Subfactor`, `Component`, `Trait`. |
| `hitop:O002sP` (`Tier`) | Alle konkreten HiTOP-Konzeptklassen (Internalizing, Anxiousness, …). Offen, erweiterbar. |

Drei Properties setzen diese Klassen in Beziehung:

- **`hitop:hasLevel`** (Level → Level): ordnet die sechs Level-Subklassen
  einmalig zur festen Leiter `Factor → Superspectrum → Spectrum →
  Subfactor → Component → Trait`. Wird ausschließlich im Kern asserted, nie
  in einer Faktorisierung.
- **`hitop:hasLevelType`** (Tier → Level): ordnet einem konkreten
  HiTOP-Konzept zu, welche Level-Subklasse es in *dieser* Faktorisierung
  einnimmt. Entspricht dem `level`-Feld eines YAML-Knotens.
- **`hitop:hasTier`** (Tier → Tier): die konkrete Eltern-Kind-Beziehung
  zwischen zwei HiTOP-Konzepten in *dieser* Faktorisierung (z. B.
  Internalizing hasTier Anxiousness). Entspricht der `children`-Verschachtelung
  eines YAML-Knotens.

`hitop:hasLevelType`- und `hitop:hasTier`-Aussagen verwenden die
HiTOP-Konzeptklassen-IRIs (z. B. `hitop:P002nf`) direkt als Subjekt/Objekt
einer Objekt-Property-Aussage (OWL2-Punning: die Klassen-IRI wird zugleich
als Individuum verwendet). Ein Standard-Reasoner leitet daraus keine
automatische Subsumption ab — sämtliche Konsistenzprüfungen (Referenzintegrität,
Level-Konsistenz, doppelte Codes) laufen über die projekteigene Validierung
(`validation/test_factorizations.py`), nicht über einen Reasoner.

## 5. Format der Hierarchy-Datei

`<version>_hierarchy.yaml` wird gegen
[`schema/factorization-hierarchy.schema.json`](../schema/factorization-hierarchy.schema.json)
validiert. Sie hat zwei Top-Level-Schlüssel:

```yaml
meta:
  factorization_id: working-model
  version: V1052k
  label: HiTOP Working Model
  status: draft
  source: data/hitop/images/hitop_working_model.png
  based_on:
    ontology_iri: "http://purl.org/hitop"
    ontology_version: "0.1.0"
  provenance:
    created_by: "Dr. Rogério Blitz"
    created_at: "2026-07-03"

hierarchy:
  label: General Factor of Psychopathology (p-factor)
  level: Factor
  code: F001Hw
  children:
    - label: Externalizing
      level: Superspectrum
      code: S0013h
      children: [...]
```

| Feld | Bedeutung |
| --- | --- |
| `meta.factorization_id` | muss dem Ordnernamen entsprechen |
| `meta.version` | muss dem Dateinamens-Präfix entsprechen |
| `meta.status` | `draft`, `active`, oder `deprecated` |
| `meta.based_on.ontology_iri` | immer `http://purl.org/hitop` |
| `meta.based_on.ontology_version` | `owl:versionInfo`-Stand, gegen den `code`-Werte aufgelöst wurden |
| `meta.provenance.created_by`, `.created_at` | Kuratierungs-Herkunft |
| `hierarchy` | rekursiver Baum, siehe unten |

Jeder Knoten im `hierarchy`-Baum hat:

| Feld | Pflicht | Bedeutung |
| --- | --- | --- |
| `label` | ja | menschenlesbarer Name |
| `level` | ja | eine der sechs Level-Subklassen (siehe Abschnitt 4) |
| `code` | ja | `hitop_base_code` aus `ontology/hitop.ttl` |
| `children` | nein | untergeordnete Knoten, ein Level-Schritt tiefer |
| `bridge` | nein | reine Doku-Angabe: Labels anderer Knoten, mit denen dieses Konzept empirisch cross-loaded. Erzeugt **keine** zweite `hasTier`-Kante und wird nicht gegen Codes validiert. |
| `provisional` | nein | markiert einen einzelnen Knoten als vorläufig, unabhängig von `meta.status` |

`validation/test_factorizations.py` prüft:

- Schema-Konformität gegen `factorization-hierarchy.schema.json`,
- dass jeder `code` (rekursiv über den ganzen Baum) tatsächlich als Klasse
  in `ontology/hitop.ttl` existiert (referenzielle Integrität),
- dass jedes Kind-`level` gemäß der `hasLevel`-Leiter aus dem Kern strikt
  unterhalb des Eltern-`level` liegt (Level-Konsistenz),
- dass innerhalb eines Baums kein `code` doppelt vorkommt,
- dass derselbe `code` nicht in verschiedenen Dateien mit unterschiedlichem
  `label` auftaucht (fängt Code-Kollisionen wie Tippfehler bei der
  Kuratierung ab).

## 6. Generierte Faktorisierungs-Ontology

`scripts/generate_factorization_ontology.py` liest eine `<version>_hierarchy.yaml`,
validiert sie mit derselben Prüflogik wie die Pytest-Suite
(`src/hitop/factorization/validate.py`) und erzeugt
`<version>_factorization.ttl` im selben Ordner: für jeden Knoten ein
`hitop:hasLevelType`-Tripel, für jede Eltern-Kind-Kante ein
`hitop:hasTier`-Tripel, sowie einen Ontology-Header aus `meta`. Diese
generierte Datei wird nicht von Hand gepflegt — bei einer Änderung des
YAML wird sie neu erzeugt.

## 7. Eine neue Faktorisierung oder Version anlegen

1. Ordner `factorizations/<factorization-id>/v<N>/` anlegen.
2. `<version>_hierarchy.yaml` nach obigem Schema befüllen; `meta.status: draft`,
   solange der Baum unvollständig ist.
3. `README.md` mit Kurzbeschreibung und Zitation ergänzen.
4. `.venv/bin/python -m pytest validation/test_factorizations.py` ausführen.
5. `scripts/generate_factorization_ontology.py` ausführen, um
   `<version>_factorization.ttl` zu erzeugen.
6. `meta.status` erst auf `active` setzen, wenn der Baum vollständig und
   fachlich geprüft ist.
