# Faktorisierungen

Status: Aktuelle Spezifikation
Bezug: `factorizations/`, `schema/factorization-hierarchy.schema.json`

## 1. Zweck

Die HiTOP-Ontologie (`ontology/hitop.rdf`) ist ein Bausteinkasten: sie
definiert stabile, wiederverwendbare Konzeptklassen (Superspectra, Spectra,
Subfaktoren, Komponenten, Traits) sowie das gemeinsame Vokabular, mit dem
diese Bausteine zu einer Hierarchie zusammengesetzt werden
(`hitop:hasTier`, `hitop:hasLevel` — siehe Abschnitt 4).

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
   hinzugefügt. `hitop:hasTier` und `hitop:hasLevel` sind zwar im Kern
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
   konkreten Faktorisierung — deshalb ist `hitop:hasLevel` ein freier String
   und keine feste, im Kern aufgezählte Klasse (siehe Abschnitt 4).
4. Jede Faktorisierungsversion ist ein eigener, in sich abgeschlossener
   Ordner. Eine neue Version berührt nie den Ordner einer älteren Version.
5. Faktorisierungs-Dateien sind eigene Aussagen mit Provenienz, Status und
   Review-Level – analog zu den Mapping-Artefakten in
   [`mapping-und-harmonisierung.md`](mapping-und-harmonisierung.md).
6. Eine Faktorisierung kann mehrere bestehende Konzepte zu einer neuen,
   nur für diese Faktorisierung gültigen Zusammenfassung gruppieren (z. B.
   werden `Internalizing` und `Thought Disorder` in einer Faktorisierung zu
   einem gemeinsamen Superspectrum zusammengeführt), ohne dass dafür ein
   neues Konzept im Kern angelegt wird. Solche Knoten sind `kind: collection`
   (siehe Abschnitt 4).

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

## 4. Vokabular: `hasTier`, `hasLevel`, Collection-Knoten

Der Kern definiert eine einzige offene, erweiterbare Klasse für alle
konkreten HiTOP-Konzepte:

| Klasse | Zweck |
| --- | --- |
| `hitop:O002sP` (`Tier`) | Alle konkreten HiTOP-Konzeptklassen (Internalizing, Anxiousness, …). Offen, erweiterbar. |

Es gibt bewusst **keine** Klasse mehr, die "Level" als festen, im Kern
aufgezählten Satz von Subklassen (Factor, Superspectrum, Spectrum,
Subfactor, Component, Trait) modelliert. Grund: die Zahl möglicher Ebenen
ist nicht abschließend bekannt (manche Faktorisierungen brauchen
`Subfactor`, andere zusätzlich `Sub-subfactor` oder tiefer) und die
Level-Zuordnung eines Konzepts ist ohnehin faktorisierungsabhängig (Punkt 3
in Abschnitt 2) — eine feste Kernklasse pro Ebene würde bei jeder neuen
Kombination eine Kernänderung erzwingen.

Zwei Properties setzen `Tier`-Konzepte zueinander in Beziehung:

- **`hitop:hasTier`** (Tier → Tier): die konkrete Eltern-Kind-Beziehung
  zwischen zwei HiTOP-Konzepten in *dieser* Faktorisierung (z. B.
  Internalizing hasTier Anxiousness). Entspricht der `children`-Verschachtelung
  eines YAML-Knotens. **Diese Kante allein bestimmt die vertikale Ordnung**
  eines Faktorisierungsbaums: ein Kind steht per Konstruktion immer genau
  eine Ebene unter seinem Elternteil (Tiefe = Anzahl `hasTier`-Schritte ab
  der Wurzel). Es wird keine separate Rangliste benötigt, um diese Ordnung
  zu prüfen — eine Ordnungsverletzung kann strukturell gar nicht auftreten.
- **`hitop:hasLevel`** (Tier → String): ein rein beschreibendes,
  freies Text-Label (z. B. `"Spectrum"`, `"Component"`, `"Sub-subfactor"`),
  das benennt, welche Rolle ein Konzept in *dieser* Faktorisierung spielt.
  Entspricht dem `level`-Feld eines YAML-Knotens. Es ist **kein** festes
  Vokabular im Kern hinterlegt und wird **nicht** auf Tiefen-Konsistenz
  geprüft: reale HiTOP-Bäume sind unregelmäßig — manche Spectra springen
  direkt zu `Component`, andere über einen `Subfactor` — daher kann
  dieselbe Bezeichnung innerhalb *eines* Baums auf unterschiedlichen Tiefen
  auftauchen (genau wie in etablierten taxonomischen Rangsystemen, z. B.
  NCBI Taxonomy, Ränge übersprungen werden dürfen).

`hitop:hasTier`-Aussagen verwenden die HiTOP-Konzeptklassen-IRIs (z. B.
`hitop:P002nf`) direkt als Subjekt/Objekt einer Objekt-Property-Aussage
(OWL2-Punning: die Klassen-IRI wird zugleich als Individuum verwendet). Ein
Standard-Reasoner leitet daraus keine automatische Subsumption ab —
sämtliche Konsistenzprüfungen (Referenzintegrität, doppelte Codes) laufen
über die projekteigene Validierung (`validation/test_factorizations.py`),
nicht über einen Reasoner.

### Collection-Knoten (`kind: collection`) für faktorisierungslokale Zusammenführungen

Manchmal führt eine Faktorisierung mehrere bestehende Konzepte zu einem
neuen, nur in dieser einen Faktorisierung gültigen Knoten zusammen (z. B.
werden `Internalizing` und `Thought Disorder` zu einem gemeinsamen
Superspectrum zusammengefasst). Ist diese Zusammenfassung kein
eigenständiges, wiederverwendbares HiTOP-Konstrukt aus der zitierten
Literatur, wird sie **nicht** als neues Konzept in den Kern aufgenommen
(das widerspräche Grundprinzip 1), sondern als lokaler `skos:Collection`
-Knoten modelliert:

- YAML-Knoten erhält `kind: collection` (statt des impliziten Default
  `concept`); sein `code` ist eine faktorisierungslokale ID, die **nicht**
  gegen `ontology/hitop.ttl` geprüft wird.
- Im generierten RDF bekommt der Knoten `rdf:type skos:Collection` und eine
  eigene, im Faktorisierungs-Namensraum liegende IRI
  (`http://purl.org/hitop/factorizations/<id>/v<version>#<code>`) statt
  einer Kern-IRI.
- Er trägt ganz normal `hitop:hasLevel` (z. B. `"Superspectrum"`) und
  `hitop:hasTier` zu seinen `children` — genau die zusammengeführten
  Konzepte (Internalizing, Thought Disorder) sind seine Kinder. Es ist
  keine zusätzliche Property nötig, um "Mitglieder" separat von
  "Kindern" zu erfassen.

Dieses Muster folgt dem SKOS-Standardunterschied zwischen `skos:Concept`
(bedeutungstragende Einheit, hier: `Tier`) und `skos:Collection` (rein
organisatorische Gruppierung ohne eigene Konzept-Identität).

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
| `level` | ja | freier Text, benennt die Rolle dieses Knotens in dieser Faktorisierung (siehe Abschnitt 4) |
| `code` | ja | für `kind: concept`: `hitop_base_code` aus `ontology/hitop.ttl`; für `kind: collection`: faktorisierungslokale ID |
| `kind` | nein | `concept` (Default) oder `collection` (faktorisierungslokale Zusammenführung, siehe Abschnitt 4) |
| `children` | nein | untergeordnete Knoten, eine Ebene tiefer; bestimmt die Baumtiefe/Ordnung |
| `bridge` | nein | reine Doku-Angabe: Labels anderer Knoten, mit denen dieses Konzept empirisch cross-loaded. Erzeugt **keine** zweite `hasTier`-Kante und wird nicht gegen Codes validiert. |
| `provisional` | nein | markiert einen einzelnen Knoten als vorläufig, unabhängig von `meta.status` |

`validation/test_factorizations.py` prüft:

- Schema-Konformität gegen `factorization-hierarchy.schema.json`,
- dass jeder `code` eines `kind: concept`-Knotens (rekursiv über den ganzen
  Baum) tatsächlich als Klasse in `ontology/hitop.ttl` existiert
  (referenzielle Integrität; `kind: collection`-Knoten sind hiervon
  ausgenommen). Die vertikale Ordnung selbst ergibt sich bereits strukturell
  aus der `children`-Verschachtelung und wird nicht separat geprüft; `level`
  wird bewusst nicht auf Tiefen-Konsistenz geprüft (siehe Abschnitt 4),
- dass innerhalb eines Baums kein `code` doppelt vorkommt,
- dass derselbe `code` nicht in verschiedenen Dateien mit unterschiedlichem
  `label` auftaucht (fängt Code-Kollisionen wie Tippfehler bei der
  Kuratierung ab).

## 6. Generierte Faktorisierungs-Ontology

`scripts/generate_factorization_ontology.py` liest eine `<version>_hierarchy.yaml`,
validiert sie mit derselben Prüflogik wie die Pytest-Suite
(`src/hitop/factorization/validate.py`) und erzeugt standardmäßig
`<version>_factorization.rdf` (RDF/XML) im selben Ordner — die Übergabeform
für `scripts/rdf2ttl.py` und `scripts/rdf2owl.py`, die daraus die Turtle-
bzw. OWL/RDF-XML-Geschwisterdateien ableiten; `--format ttl`/`--format both`
erzeugen Turtle direkt. Für jeden Knoten wird ein `hitop:hasLevel`-Literal-
Tripel gesetzt, für jede Eltern-Kind-Kante ein `hitop:hasTier`-Tripel, für
`kind: collection`-Knoten zusätzlich `rdf:type skos:Collection` mit lokaler
IRI, sowie ein Ontology-Header aus `meta`. Zusätzlich kopiert der Generator
für jeden regulären Konzeptknoten dessen `rdfs:label` (und, sofern
vorhanden, `rdfs:comment`) aus der Core-Ontologie in die generierte Datei —
ausschließlich zur Lesbarkeit, damit eine Faktorisierungsdatei für sich
verständlich ist, ohne die IRI im Core nachschlagen zu müssen. `rdf:type`
und `rdfs:subClassOf` eines Konzepts werden dabei nie dupliziert; die
Core-Ontologie bleibt alleinige Quelle der Wahrheit für Label/Comment.
Diese generierten Dateien werden nicht von Hand gepflegt — bei einer
Änderung des YAML werden sie neu erzeugt und die alten Fassungen ersetzt.

## 7. Diagramm-Daten und zentrale Farbregel

`scripts/generate_factorization_diagram_data.py` liest eine
`<version>_hierarchy.yaml`, validiert sie mit derselben Prüflogik wie die
Pytest-Suite und erzeugt standardmäßig `<version>_diagram.json` im selben
Ordner — ein minimaler Baum (`label`/`level`/`code`/`kind`/`branch`/`color`/
`children`), direkt geeignet als Input für `d3.hierarchy()` +
`d3.partition()` (Icicle-Diagramm).

Die Farbvergabe folgt einer einzigen, faktorisierungsübergreifenden Regel
(`src/hitop/factorization/colors.py`), damit alle Diagramme visuell
konsistent sind:

- Eine feste 24-Farben-Palette (von dunklem Blau bis hellem Rosa) wird auf
  jeden Knoten mit `level` in `{Factor, Superspectrum, Spectrum, Subfactor}`
  verteilt — jeder dieser Knoten bekommt eine eigene, unmittelbar aus der
  Palette entnommene Farbe.
- Die Verteilung erfolgt in der Baum-Reihenfolge (Tiefensuche, so wie der
  Baum im YAML geschrieben ist), gleichmäßig über die gesamte Palette
  gestreckt — unabhängig davon, wie viele solcher Knoten eine konkrete
  Faktorisierung hat. Das ergibt einen durchgehenden Farbverlauf entlang der
  Baumstruktur, analog dazu, wie die originalen HiTOP-Abbildungen einen
  ganzen Zweig konsistent einfärben.
- `Component`- und `Trait`-Knoten sind nicht Teil der Palette. Jeder solche
  Knoten bekommt stattdessen eine aufgehellte, leicht entsättigte Variante
  der Farbe seines direkten Elternknotens (HSL: Lightness je Tiefenstufe
  unterhalb des nächsten Paletten-Knotens erhöht, Saturation leicht
  reduziert) — verschachtelte Component/Trait-Knoten werden mit jeder Stufe
  weiter aufgehellt.

Diese Regel ist bewusst in einem eigenen Modul (`hitop.factorization.colors`)
gekapselt, das sowohl vom Diagramm-Generator als auch von künftigen
Renderern importiert werden kann, statt die Farblogik in einem Renderer zu
duplizieren. `<version>_diagram.json` wird wie die anderen generierten
Dateien nicht von Hand gepflegt.

## 8. Eine neue Faktorisierung oder Version anlegen

1. Ordner `factorizations/<factorization-id>/v<N>/` anlegen.
2. `<version>_hierarchy.yaml` nach obigem Schema befüllen; `meta.status: draft`,
   solange der Baum unvollständig ist.
3. `README.md` mit Kurzbeschreibung und Zitation ergänzen.
4. `.venv/bin/python -m pytest validation/test_factorizations.py` ausführen.
5. `scripts/generate_factorization_ontology.py` ausführen, um
   `<version>_factorization.ttl` zu erzeugen.
6. `scripts/generate_factorization_diagram_data.py` ausführen, um
   `<version>_diagram.json` (inkl. Farben nach der zentralen Regel aus
   Abschnitt 7) zu erzeugen.
7. `meta.status` erst auf `active` setzen, wenn der Baum vollständig und
   fachlich geprüft ist.
