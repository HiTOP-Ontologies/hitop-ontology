# Mapping und Harmonisierung fuer HiTOP-Manifestationssuffixe

Status: Produktionsreife Spezifikation  
Version: 1.0.0  
Datum: 2026-05-31  
Bezug: Modulares Namespaced Suffix Schema  
Ziel: methodische Spezifikation fuer Mapping, Review und Harmonisierung

## 1. Zweck

Dieses Dokument beschreibt ein kontrolliertes Verfahren, um dezentrale
HiTOP-Manifestationssuffixe semantisch miteinander zu vergleichen, zu mappen
und zu harmonisieren. Es ergaenzt das `Modulare Namespaced Suffix Schema`, ohne
die Identifier-Syntax selbst zu veraendern.

Das Suffix-Schema verhindert technische Kollisionen. Es verhindert aber nicht,
dass unterschiedliche Studien, Standorte oder Module aehnliche oder gleiche
Manifestationen unter unterschiedlichen Slugs kodieren. Diese semantische
Redundanz wird nicht ueber Umbenennung geloest, sondern ueber explizite,
versionierte und reviewbare Mapping-Artefakte.

## 2. Grundprinzipien

1. Mappings sind eigene Aussagen mit Provenienz, Status und Review-Level.
2. Ein Mapping veraendert den Quellcode nicht.
3. Ein publizierter Code wird nicht wegen eines Mappings semantisch umdefiniert.
4. Automatische Verfahren duerfen Kandidaten erzeugen, aber keine kuratierten
   Mappings ersetzen.
5. Mapping-Relationen muessen gerichtet, begruendet und versioniert sein.
6. Der Slug ist nur ein Hinweis; die Entscheidung beruht auf Definition,
   Operationalisierung, Quelle, Kontext und Hierarchie.
7. Unsicherheit wird explizit dokumentiert, nicht implizit versteckt.

## 3. Abgrenzung

Dieses Dokument definiert:

1. ein Mapping-Datenmodell
2. Relationstypen und Entscheidungskriterien
3. einen Algorithmus zur Kandidatengenerierung
4. ein Scoring-Modell fuer Mapping-Vorschlaege
5. Review-Level und Qualitaetsregeln
6. Publikationsformate fuer SKOS, FHIR ConceptMap und tabellarische Exporte

Dieses Dokument definiert nicht:

1. die klinische Wahrheit eines Mappings
2. automatische Freigabe ohne fachlichen Review
3. ein zentrales Governance-Gremium
4. eine verpflichtende Softwareimplementierung

## 4. Mapping-Artefakt

Ein Mapping-Artefakt beschreibt eine Beziehung zwischen einem Quellcode und
einem Zielcode.

Minimalstruktur:

```yaml
mapping_id: "map-2026-000001"
source:
  system: "http://purl.org/hitop"
  code: "U0aB2X.M-AF-ROR3J2WQSVQFFIKK-CHRONIC_WORRY"
target:
  system: "http://purl.org/hitop"
  code: "U0aB2X.M-AF-RORYLBKANYXUGB6O-EXCESSIVE_WORRY"
relation:
  skos: "skos:closeMatch"
  fhir: "related-to"
confidence:
  score: 0.82
  band: "high"
review:
  status: "curated"
  level: 3
  reviewer: "curation-board-or-person-id"
  date: "2026-05-31"
evidence:
  label_similarity: 0.71
  definition_similarity: 0.84
  manifestation_type_match: true
  hitop_base_code_match: true
  operationalization_match: "partial"
  notes: "Operationalization differs in time window; concepts are close but not exact."
provenance:
  created_by: "mapping-pipeline-or-curator"
  created_at: "2026-05-31"
  source_version: "1"
  target_version: "1"
status: "active"
```

## 5. Relationstypen

### 5.1 Empfohlene Relationstabelle

| Relation | Bedeutung | Verwendung |
| --- | --- | --- |
| `skos:exactMatch` | gleiche Bedeutung in breitem Anwendungskontext | nur bei sehr hoher definitorischer und operationaler Uebereinstimmung |
| `skos:closeMatch` | sehr aehnlich, aber nicht voll austauschbar | Standardrelation fuer hohe, aber nicht perfekte Uebereinstimmung |
| `skos:broadMatch` | Ziel ist breiter als Quelle | Quelle ist spezifischer |
| `skos:narrowMatch` | Ziel ist enger als Quelle | Quelle ist allgemeiner |
| `skos:relatedMatch` | fachlich verwandt, aber keine Hierarchie oder Aequivalenz | assoziative Beziehung |
| `noMap` | kein gueltiges Mapping | Kandidat wurde geprueft und verworfen |

### 5.2 Entscheidungskriterien

`skos:exactMatch` SHOULD nur vergeben werden, wenn:

1. HiTOP-Basiscode oder Zielkonzept semantisch deckungsgleich ist
2. Manifestationstyp identisch oder fachlich aequivalent ist
3. Definitionen deckungsgleich sind
4. Operationalisierung kompatibel ist
5. kein relevanter Unterschied in Zeitfenster, Schweregrad, Population oder
   Messinstrument besteht

`skos:closeMatch` SHOULD verwendet werden, wenn:

1. Labels und Definitionen stark ueberlappen
2. die Konzepte in vielen Retrieval- oder Analysekontexten gemeinsam nutzbar
   sind
3. aber mindestens ein relevanter Unterschied in Operationalisierung, Kontext
   oder Messlogik besteht

`skos:broadMatch` und `skos:narrowMatch` SHOULD verwendet werden, wenn:

1. ein Konzept die Bedeutung des anderen einschliesst
2. die Richtung eindeutig ist
3. die Beziehung nicht bloss assoziativ ist

`skos:relatedMatch` SHOULD verwendet werden, wenn:

1. eine fachliche Naehe besteht
2. aber weder Aequivalenz noch klare Breiter-/Enger-Beziehung vorliegt

## 6. Kandidatengenerierung

Mapping-Kandidaten SHOULD automatisch erzeugt und danach fachlich reviewed
werden.

### 6.1 Eingabedaten

Fuer jeden Code sollten mindestens folgende Felder indexiert werden:

```yaml
code
hitop_base_code
manifestation_type
namespace.token
namespace.identifier
slug
preferred_label
alt_labels
definition
operationalization
source.instrument
source.item_id
population
mappings
```

### 6.2 Normalisierung

Vor der Kandidatensuche werden alle Textfelder normalisiert:

```text
normalize_text(value):
  unicode_nfkc(value)
  lowercase
  transliterate_to_ascii
  replace_punctuation_with_space
  collapse_whitespace
  trim
```

Zusaetzlich SHOULD eine tokenisierte Form erzeugt werden:

```text
tokens = remove_stopwords(split(normalize_text(value)))
```

### 6.3 Kandidatenquellen

Kandidaten SHOULD aus mehreren Quellen kombiniert werden:

| Quelle | Beschreibung |
| --- | --- |
| gleicher HiTOP-Basiscode | sehr starker Kandidatenhinweis |
| gleicher Manifestationstyp | Filter oder positiver Score |
| identischer normalisierter Slug | starker Kandidatenhinweis |
| Label- und Synonymvergleich | bevorzugtes Label, alternative Labels, Uebersetzungen |
| Definitionsvergleich | semantischer Vergleich der Definitionen |
| Operationalisierungsvergleich | Instrument, Item, Antwortskala, Zeitfenster, Schwelle |
| Hierarchie | Parent-/Child-Beziehungen im HiTOP-Kontext |
| externe Terminologien | SNOMED CT, LOINC, ICD, DSM/ICD-Domaenen, UMLS, OMOP |
| vorhandene Mappings | bereits kuratierte SKOS/FHIR/OMOP-Mappings |

## 7. Scoring-Modell

Das Scoring dient zur Priorisierung von Review-Kandidaten und zur
nachvollziehbaren Dokumentation algorithmischer Evidenz. Es ersetzt keine
fachliche Entscheidung und darf nicht als automatische Freigabe eines Mappings
verstanden werden. Fuer normative Datenprodukte zaehlt weiterhin der
kuratierte Review-Status.

### 7.1 Feature-Vektor

Der Score wird aus einem festen Feature-Vektor berechnet. Alle numerischen
Features werden vor der Berechnung auf ihren definierten Wertebereich begrenzt.
Binare Features werden als `0` oder `1` abgebildet. Fehlende oder nicht
auswertbare Evidenz muss im Mapping-Artefakt sichtbar bleiben und darf nicht
allein zur fachlichen Freigabe fuehren.

| Feature | Wertebereich | Bedeutung |
| --- | --- | --- |
| `base_code_match` | 0 oder 1 | gleicher HiTOP-Basiscode |
| `manifestation_type_match` | 0 oder 1 | gleicher Manifestationstyp |
| `slug_similarity` | 0..1 | String-Aehnlichkeit normalisierter Slugs |
| `label_similarity` | 0..1 | Label-/Synonymaehnlichkeit |
| `definition_similarity` | 0..1 | semantische Definitionsaehnlichkeit |
| `operationalization_similarity` | 0..1 | Messlogik, Instrument, Zeitfenster |
| `hierarchy_similarity` | 0..1 | Naehe in der HiTOP-Hierarchie |
| `external_mapping_support` | 0..1 | Unterstuetzung durch externe Terminologien |
| `context_penalty` | -1..0 | Abzug fuer widerspruechliche Population, Schweregrad, Zeitfenster |

### 7.2 Score-Berechnung

Die folgende Berechnung ist das verbindliche Score-Modell `mapping-score-v1`.
Der Rohscore wird als gewichtete Summe berechnet und anschliessend auf den
Bereich `0..1` begrenzt.

```text
raw_score =
  0.20 * base_code_match +
  0.10 * manifestation_type_match +
  0.10 * slug_similarity +
  0.15 * label_similarity +
  0.20 * definition_similarity +
  0.15 * operationalization_similarity +
  0.05 * hierarchy_similarity +
  0.05 * external_mapping_support +
  context_penalty

score = min(1.0, max(0.0, raw_score))
```

Die Gewichte von `mapping-score-v1` sind fix. Aenderungen an Features,
Gewichten, Normalisierung oder Score-Baendern erzeugen ein neues Score-Modell
mit eigener Versionskennung, Begruendung, Testbericht und Migrationshinweis.
Dadurch bleiben Scores zwischen Releases und Datenlieferungen vergleichbar.

### 7.3 Score-Baender

| Score | Band | Empfohlenes Vorgehen |
| --- | --- | --- |
| `>= 0.90` | very_high | prioritaerer Review fuer `exactMatch` oder `closeMatch` |
| `0.75 - 0.89` | high | Review fuer `closeMatch`, `broadMatch` oder `narrowMatch` |
| `0.50 - 0.74` | medium | manueller Review, keine automatische Relation |
| `< 0.50` | low | nicht priorisieren, ausser fachlicher Anlass besteht |

Die Score-Baender sind operative Priorisierungsbaender fuer `mapping-score-v1`.
Sie beschreiben Review-Prioritaet, nicht Wahrheit oder Austauschbarkeit der
Konzepte. Schwellenwerte duerfen nur mit einem neuen Score-Modell geaendert
werden.

### 7.4 Produktionsregeln

Fuer den produktiven Betrieb muss jeder berechnete Score zusammen mit dem
verwendeten Score-Modell, allen Feature-Werten, den Versionen der Quell- und
Zieldaten sowie dem Erzeugungszeitpunkt gespeichert werden. Dadurch bleibt
nachvollziehbar, warum ein Mapping-Kandidat priorisiert wurde.

Scores duerfen bestehende kuratierte Entscheidungen nicht stillschweigend
ueberschreiben. Wenn sich Quell- oder Zieldaten aendern, wird der Score neu
berechnet und das Mapping erneut als Review-Kandidat markiert, sofern die
Aenderung die Bedeutung, Operationalisierung oder Hierarchie betreffen kann.

Produktive Exporte enthalten nur aktive Mappings mit dokumentierter Provenienz
und Review-Level. Automatisch erzeugte Kandidaten bleiben als
`machine_suggested` oder `unreviewed` gekennzeichnet, bis sie fachlich
freigegeben wurden. Jede Datenfreigabe enthaelt die verwendete Version des
Score-Modells, den Exportzeitpunkt und ein Aenderungsprotokoll.

## 8. Relationsermittlung

Nach dem Scoring wird die Relation regelbasiert vorgeschlagen.

### 8.1 Entscheidungslogik

```text
if no meaningful overlap:
  relation = noMap
else if definitions equivalent and operationalization compatible:
  relation = skos:exactMatch
else if strong semantic overlap and operationalization partially differs:
  relation = skos:closeMatch
else if source meaning is included in target meaning:
  relation = skos:broadMatch
else if target meaning is included in source meaning:
  relation = skos:narrowMatch
else:
  relation = skos:relatedMatch
```

### 8.2 Ausschlussregeln

`skos:exactMatch` MUST NOT vergeben werden, wenn:

1. unterschiedliche Schweregradschwellen vorliegen
2. unterschiedliche Zeitfenster fachlich relevant sind
3. ein Konzept ein Syndrom und das andere ein Einzelsymptom ist
4. ein Konzept eine Messskala und das andere eine klinische Manifestation ist
5. Population oder Kontext die Bedeutung wesentlich veraendern

## 9. Review-Level

Mappings SHOULD mit einem Review-Level publiziert werden.

| Level | Status | Bedeutung |
| --- | --- | --- |
| 0 | `unreviewed` | automatisch erzeugter Kandidat, nicht freigegeben |
| 1 | `machine_suggested` | algorithmischer Vorschlag mit Score und Evidenz |
| 2 | `single_reviewed` | durch eine fachkundige Person geprueft |
| 3 | `curated` | durch mindestens zwei Personen oder ein Board freigegeben |
| 4 | `endorsed` | durch verantwortliche Authority formal freigegeben |

Nur Level 3 oder 4 SHOULD fuer normative Datenprodukte verwendet werden.

## 10. Konfliktbehandlung

Konflikte treten auf, wenn mehrere Zielcodes fuer dieselbe Quelle in Frage
kommen oder bestehende Mappings widerspruechlich sind.

Regeln:

1. Mehrere `exactMatch`-Ziele fuer eine Quelle MUST begruendet werden.
2. Transitive Ketten von `exactMatch` SHOULD auf Widersprueche geprueft werden.
3. `closeMatch` SHOULD nicht transitiv weiterverwendet werden.
4. Bei Konflikten wird der hoechste Review-Level bevorzugt.
5. Bei gleichem Review-Level wird die juengere Entscheidung nicht automatisch
   bevorzugt; die Provenienz entscheidet.

## 11. Publikationsformate

### 11.1 Tabellarischer Export

Minimaler TSV/CSV-Export:

```text
source_code,target_code,relation,score,review_level,status,created,source_version,target_version
```

### 11.2 SKOS/RDF

```turtle
<http://purl.org/hitop#U0aB2X.M-AF-ROR3J2WQSVQFFIKK-CHRONIC_WORRY>
  skos:closeMatch
    <http://purl.org/hitop#U0aB2X.M-AF-RORYLBKANYXUGB6O-EXCESSIVE_WORRY> .
```

### 11.3 FHIR ConceptMap

FHIR `ConceptMap` SHOULD verwendet werden, wenn Mappings in FHIR-Terminologie-
Infrastruktur publiziert oder ueber `$translate` nutzbar gemacht werden sollen.

```json
{
  "resourceType": "ConceptMap",
  "status": "draft",
  "group": [
    {
      "source": "http://purl.org/hitop",
      "target": "http://purl.org/hitop",
      "element": [
        {
          "code": "U0aB2X.M-AF-ROR3J2WQSVQFFIKK-CHRONIC_WORRY",
          "target": [
            {
              "code": "U0aB2X.M-AF-RORYLBKANYXUGB6O-EXCESSIVE_WORRY",
              "relationship": "related-to"
            }
          ]
        }
      ]
    }
  ]
}
```

## 12. Industrielle und wissenschaftliche Praxis

### 12.1 HL7 FHIR

In FHIR werden Mappings als eigene `ConceptMap`-Ressourcen modelliert. FHIR
trennt CodeSysteme von den Beziehungen zwischen Codes. Mappings sind gerichtet
und enthalten eine explizite Beziehung zwischen Source und Target.

Relevanz fuer HiTOP: HiTOP-Suffixe sollten nicht umbenannt werden, wenn spaeter
Harmonisierung noetig ist. Stattdessen sollten ConceptMaps publiziert werden.

### 12.2 SKOS

SKOS stellt etablierte Mapping-Properties fuer Concept Schemes bereit:
`exactMatch`, `closeMatch`, `broadMatch`, `narrowMatch` und `relatedMatch`.
Besonders wichtig ist, dass `closeMatch` nicht transitiv behandelt wird.

Relevanz fuer HiTOP: `closeMatch` ist der sichere Default fuer aehnliche, aber
nicht voll austauschbare Manifestationen.

### 12.3 OHDSI / OMOP

OHDSI/OMOP trennt lokale Source Codes von Standard Concepts. Lokale Codes
werden auf Standardkonzepte gemappt; Mapping ist ein eigener kuratierter
Schritt. Werkzeuge wie Usagi unterstuetzen die Kandidatensuche, ersetzen aber
nicht die fachliche Kuratierung.

Relevanz fuer HiTOP: automatische Matching-Verfahren sollten Kandidatenlisten
erzeugen, aber keine finalen Mappings ohne Review publizieren.

### 12.4 UMLS

Die UMLS Metathesaurus-Logik trennt Quellvokabulare, Strings, Atome und
Konzepte. Ein zentrales Prinzip ist, unterschiedliche Namen aus
Quellvokabularen nach Bedeutung zu Konzepten zusammenzufuehren und dabei
Quelltransparenz zu behalten.

Relevanz fuer HiTOP: lokale Codes und Slugs sollten als Source-nahe Einheiten
erhalten bleiben; Harmonisierung wird durch explizite Konzeptbeziehungen
hergestellt.

### 12.5 BioPortal / OntoPortal

BioPortal/OntoPortal behandelt Ontologien als eigenstaendige Artefakte und
stellt Mappings zwischen Termen bereit. Mappings werden als separate
Ressourcen verwaltet und koennen unterschiedliche Herkunft haben.

Relevanz fuer HiTOP: Mapping-Artefakte sollten getrennt von der Codesyntax
versioniert und publiziert werden.

## 13. Empfehlung fuer HiTOP

Fuer HiTOP-Manifestationssuffixe wird folgendes Vorgehen empfohlen:

1. Das Suffix-Schema definiert nur stabile Identifier.
2. Mapping und Harmonisierung werden in einem separaten Mapping-Artefakt
   gepflegt.
3. Automatische Algorithmen erzeugen Kandidaten und Scores.
4. Fachliche Reviewer entscheiden Relation und Status.
5. Normative Datenprodukte verwenden nur kuratierte Mappings.
6. FHIR ConceptMap und SKOS/RDF werden als primaere Publikationsformate
   unterstuetzt.
7. Tabellarische Exporte werden fuer Review- und Data-Pipeline-Prozesse
   bereitgestellt.

## 14. Quellen

| Bereich | Quelle |
| --- | --- |
| FHIR ConceptMap | https://hl7.org/fhir/R5/conceptmap.html |
| FHIR ConceptMap `$translate` | https://hl7.org/fhir/R5/conceptmap-operation-translate.html |
| FHIR Concept Map Relationship | https://fhir.hl7.org/fhir/valueset-concept-map-relationship.html |
| SKOS Mapping Properties | https://www.w3.org/TR/skos-reference/ |
| OHDSI Vocabulary | https://ohdsi.github.io/CommonDataModel/vocabulary.html |
| OHDSI Usagi | https://www.ohdsi.org/analytic-tools/usagi/ |
| UMLS Metathesaurus Identifiers | https://www.nlm.nih.gov/research/umls/new_users/online_learning/Meta_005.html |
| UMLS Metathesaurus Reference | https://www.ncbi.nlm.nih.gov/books/NBK9684/ |
| BioPortal Mappings | https://www.bioontology.org/wiki/BioPortal_Mappings |
