# Modulares Namespaced Suffix Schema

Status: Entwurf  
Version: 0.2.0  
Letzte Aktualisierung: 2026-05-31  
Gilt fuer: HiTOP-Manifestationssuffixe  
Primaerformat: `<HITOP_BASE_CODE>.M-<TT>-<NS>-<SLUG>`

## 1. Zweck

Diese Spezifikation definiert ein modulares Suffix-Format, mit dem stabile
HiTOP-Basiscodes um manifestationsspezifische Identifier erweitert werden. Sie
ist fuer dezentrale wissenschaftliche Anwendungsfaelle gedacht, in denen
verschiedene Studien, Instrumente, Institutionen und Fachdisziplinen verwandte
Manifestationen kodieren, ohne dass eine zentrale Vergabestelle existiert.

Das Schema trennt vier Verantwortlichkeiten:

| Aspekt | Feld | Verantwortung |
| --- | --- | --- |
| HiTOP-Konzeptidentitaet | `<HITOP_BASE_CODE>` | stabiler Basiscode des HiTOP-Codesystems |
| Manifestationskategorie | `<TT>` | kontrollierter Manifestationstyp |
| lokaler Authority-Raum | `<NS>` | fixlaengiges Namespace-Token zur Kollisionsisolierung |
| lesbarer lokaler Name | `<SLUG>` | lokal lesbarer Identifier |

Das Namespace-Token verhindert unbeabsichtigte Kollisionen. Der Slug bleibt
lesbar. Semantische Harmonisierung erfolgt ueber Metadaten und Mappings, nicht
durch das vollstaendige Kodieren der Bedeutung im Code-String.

## 2. Geltungsbereich

Dieses Dokument definiert:

1. die kanonische Suffix-Syntax
2. die Generierung von Namespace-Token
3. die Slug-Normalisierung
4. die Generierung von Disambiguatoren
5. erforderliche Metadaten
6. Validierungsregeln
7. den Verweis auf eine gesonderte Mapping- und Harmonisierungsspezifikation

Dieses Dokument definiert nicht:

1. das Format des HiTOP-Basiscodes selbst
2. die klinische Bedeutung einzelner Manifestationslabels
3. einen zentralen Registry-Prozess
4. Governance fuer Mapping-Reviews
5. die Versionierung der vollstaendigen HiTOP-Ontologie
6. Mapping-Algorithmen, Mapping-Review oder Harmonisierungsgovernance

## 3. Normative Sprache

Die Begriffe `MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT` und `MAY` werden im
Sinn von RFC 2119 verwendet.

Erlaeuternder Fliesstext ist nicht normativ, ausser er ist direkt mit einem
dieser Schluesselwoerter verbunden oder steht in einer normativen Grammatik,
einem Regex, einer Tabelle oder einem Algorithmusblock.

## 4. Identifier-Modell

### 4.1 Kanonische Form

Neue Manifestationssuffixe MUST diese kanonische Form verwenden:

```text
<HITOP_BASE_CODE>.M-<TT>-<NS>-<SLUG>
```

Beispiel:

```text
U0aB2X.M-AF-RORPLACEHOLDERAB-CHRONIC_WORRY
```

### 4.2 Felduebersicht

| Feld | Erforderlich | Form | Beispiel |
| --- | --- | --- | --- |
| `<HITOP_BASE_CODE>` | ja | HiTOP-Basiscode | `U0aB2X` |
| `M` | ja | literaler Suffix-Block | `M` |
| `<TT>` | ja | Manifestationstyp | `AF` |
| `<NS>` | ja | fixlaengiges Namespace-Token | `RORPLACEHOLDERAB` |
| `<SLUG>` | ja | normalisierter lokaler Slug | `CHRONIC_WORRY` |

Der Code-String MUST ASCII sein. Der Code-String MUST NOT Leerzeichen enthalten.
Die Suffix-Felder MUST durch Bindestriche (`-`) getrennt werden. Das
Namespace-Token MUST NOT Unterstriche enthalten. Der Slug MAY Unterstriche
enthalten.

## 5. Manifestationstypen

`<TT>` MUST einer der folgenden zweistelligen Codes sein:

| Code | Typ | Hinweis |
| --- | --- | --- |
| `GS` | General symptom | nur Fallback |
| `CS` | Clinical sign | beobachtbares oder extern beurteiltes Zeichen |
| `SY` | Syndrome / cluster | explizite Symptomkombination |
| `AF` | Affective symptom | affektive oder stimmungsbezogene Manifestation |
| `CG` | Cognitive symptom | kognitive Manifestation |
| `PC` | Perceptual symptom | wahrnehmungsbezogene Manifestation |
| `BH` | Behavioral symptom | beobachtbares Verhalten |
| `SS` | Somatic symptom | koerperliche oder vegetative Manifestation |
| `SL` | Sleep / circadian | Schlaf- oder zirkadiane Manifestation |
| `SU` | Substance-related | substanzbezogene Manifestation |
| `IR` | Interpersonal / relational | interpersonale oder relationale Manifestation |
| `IM` | Impairment / functioning | Beeintraechtigung oder Funktionsniveau |

`GS` SHOULD vermieden werden, wenn ein spezifischerer Typ fachlich vertretbar
ist.

## 6. Namespace-Token

### 6.1 Zweck

`<NS>` identifiziert den lokalen Authority-Raum, in dem der Slug eindeutig ist.
Es ist ein Mechanismus zur Kollisionsisolierung, kein semantisches Label. Die
Quell-Authority MUST in den Metadaten gespeichert werden.

### 6.2 Normative Form

`<NS>` MUST exakt 16 Zeichen lang sein:

```text
[A-Z]{3}[A-Z2-7]{13}
```

Struktur:

| Segment | Laenge | Form | Bedeutung |
| --- | --- | --- | --- |
| `<KIND>` | 3 | `[A-Z]{3}` | Typ der Namespace-Quelle |
| `<DIGEST>` | 13 | `[A-Z2-7]{13}` | erste 13 Zeichen eines Base32-SHA256-Digests |

Der Digest nutzt 65 Bit Hash-Material. Die Laenge ist bewusst fix: Namespace-
Token sind maschinenorientiert und sollen in Tabellen, Parsern und Exporten
vorhersagbar bleiben.

### 6.3 Unterstuetzte Quellenarten

| Kind | Quelle | Beispiel fuer kanonischen Identifier |
| --- | --- | --- |
| `HTP` | HiTOP-kuratierter Namespace | `hitop:core` |
| `ROR` | ROR-Organisations-ID | `<ROR_URL>` |
| `ORC` | ORCID-Personen-ID | `<ORCID_URL>` |
| `DOI` | DOI-basierte Studie, Datensatz, Instrument oder Publikation | `https://doi.org/10.1234/example.study.v1` |
| `ARK` | ARK-Namespace | `ark:/12345/example` |
| `DNS` | Reverse-DNS-Projekt- oder Organisationsnamespace | `<DNS_NAMESPACE>` |
| `SRC` | stabiler Source-String als Fallback | implementierungsspezifische kanonische URI oder ID |

ROR- und ORCID-Werte werden in dieser generischen Spezifikation nur als
Platzhalter gezeigt. Konkrete Organisations- oder Personenidentifier gehoeren
in die projektspezifischen Metadaten eines Datensatzes.

Neue `KIND`-Codes MAY eingefuehrt werden, wenn sie dokumentiert sind und eine
stabile Regel fuer den kanonischen Identifier besitzen.

### 6.4 Kanonisierung

Implementierungen MUST Namespace-Quellidentifier vor dem Hashing kanonisieren.

Generische Kanonisierung:

```text
normalize_identifier(value):
  unicode_nfkc(value)
  trim
  lowercase
  collapse_internal_whitespace_to_single_space
```

Empfohlene source-spezifische kanonische Formen:

| Kind | Kanonische Form |
| --- | --- |
| `HTP` | `hitop:core` |
| `ROR` | `<ROR_URL>` |
| `ORC` | `<ORCID_URL>` |
| `DOI` | `https://doi.org/<lowercase-doi>` |
| `ARK` | `ark:/<naan>/<name>` |
| `DNS` | `dns:<reverse-domain-or-project-namespace>` |
| `SRC` | stabile URI oder lokale ID unter Kontrolle des Producers |

### 6.5 Generierungsalgorithmus

Generierung des Namespace-Tokens:

```text
kind = three-character source kind
canonical = normalize_identifier(source_identifier)
digest = base32(sha256(utf8(canonical))) without padding
namespace_token = kind + first_13_chars(digest)
```

Das Base32-Alphabet MUST das RFC-4648-Grossbuchstabenalphabet `A-Z2-7` sein.

Beispiele:

| Kind | Kanonischer Identifier | Namespace-Token |
| --- | --- | --- |
| `HTP` | `hitop:core` | `HTPAJIPZH4KRXKXK` |
| `ROR` | `<ROR_URL>` | `RORPLACEHOLDERAB` |
| `ORC` | `<ORCID_URL>` | `ORCPLACEHOLDERAB` |
| `DOI` | `https://doi.org/10.1234/example.study.v1` | `DOICRZ5I6RDFXGS7` |
| `DNS` | `<DNS_NAMESPACE>` | `DNSPLACEHOLDERAB` |

## 7. Slug

### 7.1 Zweck

`<SLUG>` ist der lokal lesbare Name der Manifestation. Er ist nicht die
vollstaendige Definition und MUST NOT als alleinige Quelle der Semantik
verwendet werden.

### 7.2 Normative Form

Ein Slug MUST 3 bis 40 Zeichen lang sein und SHOULD 12 bis 28 Zeichen lang sein.

Strenge Form:

```text
[A-Z0-9](?:[A-Z0-9_]{1,38}[A-Z0-9])
```

Das bedeutet:

1. nur ASCII-Grossbuchstaben
2. erlaubte Zeichen sind `A-Z`, `0-9` und `_`
3. kein fuehrender `_`
4. kein abschliessender `_`
5. keine Leerzeichen
6. Gesamtlaenge von 3 bis 40 Zeichen

### 7.3 Slug-Normalisierung

Die Slug-Generierung SHOULD das bevorzugte englische Label oder ein stabiles,
normalisiertes Quelllabel verwenden.

Algorithmus:

```text
slugify(label):
  unicode_nfkd(label)
  transliterate_to_ascii
  uppercase
  replace_every_run_of_non_AZ09_with_single_underscore
  remove_leading_and_trailing_underscore
  collapse_multiple_underscores
```

Beispiele:

| Label | Slug |
| --- | --- |
| Chronic worry | `CHRONIC_WORRY` |
| Panic attack cluster | `PANIC_ATTACK_CLUSTER` |
| Work impairment | `WORK_IMPAIRMENT` |
| Resting palpitations | `RESTING_PALPITATIONS` |
| Rejection sensitivity | `REJECTION_SENSITIVITY` |

### 7.4 Inhaltliche Slug-Regeln

Slugs SHOULD beschreibend, aber kompakt sein. Slugs SHOULD NOT Informationen
enthalten, die in Metadaten gehoeren.

| Vermeiden | Schlechtes Beispiel | Besser |
| --- | --- | --- |
| Autor oder Jahr | `WORRY_SMITH_2024` | Zitation in Metadaten speichern |
| Versionsnummer | `PANIC_ATTACK_V2` | neuen Code erzeugen und `replaces` nutzen |
| opake lokale Abkuerzung | `CW01` | `CHRONIC_WORRY` |
| generisches Label | `SYMPTOM` | spezifischen Slug verwenden oder `<TT>` pruefen |

Wenn die Normalisierung einen Slug mit mehr als 40 Zeichen erzeugt, SHOULD der
Producer das Label manuell kuerzen. Automatische Trunkierung MAY verwendet
werden, wenn der gekuerzte Slug weiterhin verstaendlich ist und auf lokale
Kollisionen geprueft wurde.

## 8. Disambiguator

### 8.1 Zweck

Ein Disambiguator loest eine lokale Slug-Kollision innerhalb desselben Tupels:

```text
<HITOP_BASE_CODE> + M + <TT> + <NS>
```

Er MUST nur verwendet werden, wenn zwei unterschiedliche Manifestationen sonst
denselben normalisierten Slug erhalten wuerden. Er ist ein technischer
Kollisionsaufloeser, kein semantisches Label.

### 8.2 Normative Form

Disambiguierter Slug:

```text
<BASE_SLUG>_<DISAMBIGUATOR>
```

Feldregeln:

| Feld | Form | Laenge |
| --- | --- | --- |
| `<BASE_SLUG>` | `[A-Z0-9](?:[A-Z0-9_]{1,31}[A-Z0-9])` | 3 bis 33 |
| `<DISAMBIGUATOR>` | `[A-Z2-7]{6}` | exakt 6 |

Der Disambiguator nutzt 30 Bit Hash-Material. Der Base-Slug ist auf 33 Zeichen
begrenzt, damit der finale Slug innerhalb der 40-Zeichen-Grenze bleibt:

```text
33 + 1 + 6 = 40
```

Das letzte durch `_` getrennte Token mit dem Muster `[A-Z2-7]{6}` ist fuer den
Disambiguator reserviert. Ein nicht-disambiguierter Slug SHOULD NOT mit
`_[A-Z2-7]{6}` enden.

### 8.3 Disambiguator-Basis

Der Disambiguator MUST aus stabilen lokalen Quellidentifiern abgeleitet werden,
nicht allein aus redaktionell veraenderbarem Freitext.

Kanonische Basis:

```text
canonical_disambiguation_basis =
  normalize(namespace.identifier) + "|" +
  normalize(hitop_base_code) + "|" +
  "m" + "|" +
  normalize(manifestation_type) + "|" +
  normalize(source.study_id) + "|" +
  normalize(source.instrument) + "|" +
  normalize(source.item_id_or_local_concept_id)
```

Normalisierung:

```text
normalize(value):
  unicode_nfkc(value)
  trim
  lowercase
  collapse_internal_whitespace_to_single_space
```

Wenn `source.item_id` nicht verfuegbar ist, MUST ein anderer stabiler lokaler
Quellidentifier verwendet und als `source.local_concept_id` gespeichert werden.

### 8.4 Generierungsalgorithmus

```text
canonical = canonical_disambiguation_basis
digest = base32(sha256(utf8(canonical))) without padding
disambiguator = first_6_chars(digest)
slug = base_slug + "_" + disambiguator
```

Beispiel:

```text
canonical_disambiguation_basis =
  <ROR_URL>|u0ab2x|m|af|study-a|instrument-x|item-17

disambiguator = ALN53Q
slug = CHRONIC_WORRY_ALN53Q
```

## 9. Erforderliche Metadaten

Jeder kanonische Suffix-Code MUST von Metadaten begleitet werden, die ausreichen,
um das Namespace-Token zu rekonstruieren, den Slug zu interpretieren und
Mappings zu unterstuetzen.

Minimale YAML-Struktur:

```yaml
code: "U0aB2X.M-AF-RORPLACEHOLDERAB-CHRONIC_WORRY"
hitop_base_code: "U0aB2X"
suffix_block: "M"
manifestation_type: "AF"
namespace:
  token: "RORPLACEHOLDERAB"
  kind: "ROR"
  identifier: "<ROR_URL>"
slug: "CHRONIC_WORRY"
preferred_label: "Chronic worry"
definition: "Persistent or recurrent worry as operationalized in the source context."
source:
  study_id: "study-a"
  instrument: "instrument-x"
  item_id: "item-17"
  citation: "doi-or-bibliographic-reference"
status: "active"
created: "2026-05-31"
version: "1"
mappings: []
```

Empfohlene optionale Felder:

| Feld | Zweck |
| --- | --- |
| `alt_labels` | Synonyme, lokale Labels, Uebersetzungen |
| `operationalization` | Instrument, Item, Schwellenwert, Zeitfenster, Scoring-Regel, Skalentyp (`scale_type`), Wertebereich (`value_range`), Auswahlverhalten (`selection_type`), Datentyp (`data_type`) |
| `population` | Zielpopulation oder Stichprobenkontext |
| `disambiguator` | sechsstelliger Disambiguator, falls verwendet |
| `disambiguation_basis` | kanonische Basis zur Ableitung des Disambiguators |
| `replaces` | vorheriger Code, der durch diesen Code ersetzt wird |
| `replaced_by` | Nachfolgecode, falls dieser Code deprecated ist |
| `mapping_review_status` | z. B. `unreviewed`, `automatic`, `curated` |
| `provenance` | Ersteller, Datum, Quelle der Vergabeentscheidung |

Vollstaendige YAML-Struktur mit allen empfohlenen optionalen Feldern:

```yaml
code: "U0aB2X.M-AF-RORPLACEHOLDERAB-CHRONIC_WORRY_ALN53Q"
hitop_base_code: "U0aB2X"
suffix_block: "M"
manifestation_type: "AF"
namespace:
  token: "RORPLACEHOLDERAB"
  kind: "ROR"
  identifier: "<ROR_URL>"
  label: "Example source organization"
  acronym: "EXORG"
slug: "CHRONIC_WORRY_ALN53Q"
base_slug: "CHRONIC_WORRY"
disambiguator: "ALN53Q"
disambiguation_basis: "<ROR_URL>|u0ab2x|m|af|study-a|instrument-x|item-17"
preferred_label: "Chronic worry"
alt_labels:
  - "Persistent worry"
  - "Excessive worry"
definition: "Persistent or recurrent worry as operationalized in the source context."
operationalization:
  instrument: "instrument-x"
  item_id: "item-17"
  item_text: "source item text or controlled item reference"
  response_scale: "source response scale"
  time_window: "past 2 weeks"
  threshold: "source-specific threshold or scoring rule"
  scoring_rule: "source-specific scoring description"
  scale_type: "Likert"
  value_range: "1 to 5"
  selection_type: "single choice"
  data_type: "numeric"
population:
  description: "target population or sampling context"
  age_range: "adult"
  setting: "clinical or study context"
source:
  study_id: "study-a"
  instrument: "instrument-x"
  item_id: "item-17"
  local_concept_id: "optional-local-concept-id"
  citation: "doi-or-bibliographic-reference"
  source_url: "https://example.org/source-or-specification"
status: "active"
created: "2026-05-31"
modified: "2026-05-31"
version: "1"
replaces: []
replaced_by: []
mapping_review_status: "unreviewed"
mappings:
  - target_code: "U0aB2X.M-AF-ROROTHERTOKENABC-EXCESSIVE_WORRY"
    relation: "skos:closeMatch"
    mapping_artifact: "docs/mapping-und-harmonisierung.md"
provenance:
  created_by: "person-or-system-id"
  created_at: "2026-05-31"
  reviewed_by: []
  review_status: "draft"
  decision_note: "Initial namespace and slug assignment."
```

### 9.1 Extension-Felder (`x_*`)

`schema/manifestation-record.schema.json` erlaubt zusaetzliche Top-Level-Felder,
deren Name auf `x_` folgt von `[A-Za-z0-9_]+` matcht (Muster
`^x_[A-Za-z0-9_]+$`), mit beliebigem JSON-Wert.

`x_*`-Felder SHOULD nur fuer Producer-spezifische Zusatzdaten verwendet
werden, fuer die es kein Kernfeld in diesem Dokument gibt. Der Praefix
verhindert Namenskollisionen mit kuenftigen Kernfeldern. `x_*`-Felder
SHOULD NOT fuer Daten verwendet werden, fuer die bereits ein Kernfeld
existiert (z. B. nicht `x_instrument`, wenn `operationalization.instrument`
gemeint ist) -- das wuerde dieselbe Information an zwei Stellen
inkonsistent haltbar machen. Consumer MUST unbekannte `x_*`-Felder
tolerieren, statt den Datensatz deswegen abzulehnen.

## 10. Validierung

### 10.1 Syntaxvalidierung

Ein kanonischer Manifestationssuffix ist syntaktisch gueltig, wenn:

1. `<HITOP_BASE_CODE>` vorhanden ist
2. der Suffix-Block literal `M` ist
3. `<TT>` ein erlaubter Manifestationstyp ist
4. `<NS>` dem Muster `[A-Z]{3}[A-Z2-7]{13}` entspricht
5. `<SLUG>` dem Muster `[A-Z0-9](?:[A-Z0-9_]{1,38}[A-Z0-9])` entspricht
6. die Slug-Gesamtlaenge 3 bis 40 Zeichen betraegt

Regex fuer den Suffix-Block ohne `<HITOP_BASE_CODE>.`:

```text
^M-(GS|CS|SY|AF|CG|PC|BH|SS|SL|SU|IR|IM)-[A-Z]{3}[A-Z2-7]{13}-[A-Z0-9](?:[A-Z0-9_]{1,38}[A-Z0-9])$
```

Regex fuer explizit disambiguierte Suffixe:

```text
^M-(GS|CS|SY|AF|CG|PC|BH|SS|SL|SU|IR|IM)-[A-Z]{3}[A-Z2-7]{13}-[A-Z0-9](?:[A-Z0-9_]{1,31}[A-Z0-9])_[A-Z2-7]{6}$
```

### 10.2 Semantische Validierung

Ein Code ist semantisch gueltig, wenn:

1. der HiTOP-Basiscode existiert
2. das Namespace-Token zu den dokumentierten Namespace-Metadaten passt
3. der Slug innerhalb von `<HITOP_BASE_CODE> + M + <TT> + <NS>` eindeutig ist
4. disambiguierte Slugs `disambiguator` und `disambiguation_basis` enthalten
5. Definition und Source-Metadaten vorhanden sind

### 10.3 Validator-Verhalten

Validatoren SHOULD getrennte Fehler melden fuer:

1. ungueltigen Manifestationstyp
2. ungueltige Namespace-Laenge oder ungueltiges Namespace-Alphabet
3. Namespace-Token, das nicht zu den Metadaten passt
4. ungueltiges Slug-Alphabet oder ungueltige Slug-Laenge
5. fuehrenden oder abschliessenden Unterstrich im Slug
6. doppelten Code im selben Publikationsartefakt
7. nicht aufgeloeste lokale Kollision
8. fehlende Pflichtmetadaten

Validatoren MUST NOT publizierte Codes stillschweigend umschreiben.
Vorgeschlagene normalisierte Formen MAY als Warnungen ausgegeben werden.

## 11. Beispiele

Die folgenden HiTOP-Basiscodes sind illustrativ.

### 11.1 HiTOP-kuratierter Namespace

```text
U0aB2X.M-AF-HTPAJIPZH4KRXKXK-CHRONIC_WORRY
```

Bedeutung: affektive Manifestation `CHRONIC_WORRY` im HiTOP-kuratierten
Namespace.

### 11.2 Organisationsnamespace ueber ROR

```text
U0aB2X.M-SS-RORPLACEHOLDERAB-RESTING_PALPITATIONS
```

Bedeutung: somatische Manifestation im Namespace, der aus
`<ROR_URL>` abgeleitet wurde.

### 11.3 Studien- oder Datensatznamespace ueber DOI

```text
C1mQ8Z.M-CG-DOICRZ5I6RDFXGS7-ATTENTION_LAPSE
```

Bedeutung: kognitive Manifestation in einem DOI-abgeleiteten Studien- oder
Datensatznamespace.

### 11.4 Personennamespace ueber ORCID

```text
C0bF4K.M-IR-ORCPLACEHOLDERAB-REJECTION_SENSITIVITY
```

Bedeutung: interpersonale Manifestation in einem ORCID-abgeleiteten Namespace.

### 11.5 Projektnamespace ueber Reverse DNS

```text
T0cR7M.M-BH-DNSPLACEHOLDERAB-AVOIDANCE_BEHAVIOR
```

Bedeutung: behaviorale Manifestation in einem Reverse-DNS-Projektnamespace.

### 11.6 Gleicher Slug, anderer Namespace

```text
U0aB2X.M-AF-RORPLACEHOLDERAB-CHRONIC_WORRY
U0aB2X.M-AF-ROROTHERTOKENABC-CHRONIC_WORRY
```

Diese Codes kollidieren nicht, weil die Namespace-Token unterschiedlich sind.
Ob die Konzepte aequivalent, verwandt, breiter oder enger sind, muss ueber
Mappings dargestellt werden.

### 11.7 Gleicher Slug, gleicher Namespace

```text
U0aB2X.M-AF-RORPLACEHOLDERAB-CHRONIC_WORRY
U0aB2X.M-AF-RORPLACEHOLDERAB-CHRONIC_WORRY_ALN53Q
```

Der zweite Code verwendet einen Disambiguator, weil der lokale Namespace bereits
eine andere Manifestation mit dem Base-Slug `CHRONIC_WORRY` enthaelt.

## 12. Mapping und Harmonisierung

Dezentrale Suffix-Vergabe verhindert unbeabsichtigte technische Kollisionen,
kann semantische Redundanz aber nicht vollstaendig verhindern. Mapping und
Harmonisierung sind deshalb eigene Artefakte und werden nicht in dieser
Identifier-Spezifikation definiert.

Normative Anforderungen in diesem Dokument:

1. Codes MUST stabil bleiben, auch wenn spaeter Mappings entstehen.
2. Mappings MUST ausserhalb des Codes als versionierte Artefakte publiziert
   werden.
3. Der Slug MUST NOT als alleinige Grundlage fuer semantische Gleichsetzung
   verwendet werden.
4. Implementierungen SHOULD Mapping-Artefakte ueber FHIR `ConceptMap`,
   SKOS/RDF oder tabellarische Review-Exporte bereitstellen.

Die detaillierte Methodik fuer Kandidatengenerierung, Scoring, Review-Level,
Relationstypen und Publikationsformate ist in einem gesonderten Dokument
beschrieben: [mapping-und-harmonisierung.md](mapping-und-harmonisierung.md).

## 13. Lifecycle-Regeln

Publizierte Codes MUST NOT semantisch umdefiniert werden. Wenn sich die
Bedeutung aendert, MUST ein neuer Code erzeugt werden.

Statuswerte SHOULD diese Werte verwenden:

| Status | Bedeutung |
| --- | --- |
| `active` | gueltig fuer die Verwendung |
| `deprecated` | nicht mehr empfohlen, aber historisch gueltig |
| `replaced` | durch einen anderen Code ersetzt |
| `draft` | noch nicht stabil |

Replacement-Metadaten:

```yaml
status: "replaced"
replaced_by: "U0aB2X.M-AF-RORPLACEHOLDERAB-EXCESSIVE_WORRY"
change_reason: "Label and operationalization harmonized with source instrument."
```

## 14. Implementierungscheckliste

Producer SHOULD folgenden Workflow implementieren:

1. HiTOP-Basiscode waehlen
2. Manifestationstyp waehlen
3. geeigneten Namespace-Quellidentifier auswaehlen
4. fixlaengiges Namespace-Token generieren
5. Base-Slug aus einem stabilen Label generieren
6. lokale Eindeutigkeit innerhalb von `<HITOP_BASE_CODE> + M + <TT> + <NS>` pruefen
7. Disambiguator nur bei lokaler Kollision anhaengen
8. erforderliche Metadaten mit dem Code publizieren
9. Mappings publizieren, wenn aequivalente oder verwandte Manifestationen bekannt sind
10. publizierte Codes nie in place umschreiben

Consumer SHOULD:

1. den Code syntaktisch parsen
2. Namespace-Metadaten validieren, wenn sie verfuegbar sind
3. den Slug nur als Label-Hinweis behandeln
4. Mappings und Definitionen fuer semantische Harmonisierung verwenden
5. unbekannte Namespace-Token erhalten, statt sie zu verwerfen

## 15. Entwurfsbegruendung

### 15.1 Fixes Namespace-Token

Ein fixlaengiges Namespace-Token wird bevorzugt, weil der Namespace primaer eine
maschinenorientierte Kollisionsgrenze ist. Ein variabler Namespace waere in
einigen Faellen lesbarer, wuerde aber Parser-Komplexitaet erhoehen und dazu
verleiten, instabile semantische Information in den Namespace einzubetten.

### 15.2 Variable Slug-Laenge

Eine fixe Slug-Laenge wird nicht empfohlen. Slugs sind die menschenlesbare
Komponente; eine fixe Laenge wuerde Padding, kuenstliche Abkuerzungen oder opake
Trunkierung erzwingen. Eine begrenzte variable Laenge ist nuetzlicher: 3 bis 40
Zeichen, mit 12 bis 28 Zeichen als praktischer Zielgroesse.

### 15.3 Fixer Disambiguator

Der Disambiguator ist auf 6 Base32-Zeichen festgelegt, weil er in einem deutlich
kleineren Kollisionsraum arbeitet als das Namespace-Token. Er unterscheidet nur
Manifestationen, die bereits denselben HiTOP-Basiscode, Suffix-Block,
Manifestationstyp, Namespace und Base-Slug teilen.

## 16. Referenzen und analoge Muster

| Bereich | Muster | Referenz |
| --- | --- | --- |
| URI-Syntax | ASCII-sichere Identifier und reservierte Trennzeichen | RFC 3986: https://www.ietf.org/rfc/rfc3986 |
| Base32-Encoding | Alphabet `A-Z2-7` | RFC 4648: https://www.rfc-editor.org/rfc/rfc4648 |
| CURIEs | Prefix plus lokale Referenz | W3C CURIE Syntax: https://www.w3.org/TR/curie/ |
| Ontologie-IDs | IDSPACE plus LOCALID und PURL-Mapping | OBO Foundry Identifier Policy: https://obofoundry.org/id-policy.html |
| FHIR-Terminologie | CodeSystem-URI plus Code; Mapping ueber ConceptMap | HL7 FHIR CodeSystem: https://hl7.org/fhir/codesystem.html |
| SKOS | Mapping-Relationen zwischen Concept Schemes | W3C SKOS Reference: https://www.w3.org/TR/skos-reference/ |
| SNOMED CT | Extension-Namespace verhindert organisatorische Kollisionen | SNOMED SCTID Representation: https://docs.snomed.org/snomed-ct-specifications/snomed-ct-release-file-specification/snomed-ct-identifiers/6.2-sctid-representation |
| Persistente Identifier | DOI-Prefix/Suffix; keine Abhaengigkeit von semantischen Suffixen | DataCite DOI Basics: https://support.datacite.org/docs/doi-basics |
| Organisations-PIDs | persistente Organisationsidentifier | ROR Registry: <ROR_REGISTRY_URL> |
| Personen-PIDs | persistente Forschenden-Identifier | ORCID: <ORCID_REGISTRY_URL> |
| Software-Namespaces | Reverse-DNS zur Kollisionsvermeidung | Maven Naming Conventions: https://maven.apache.org/guides/mini/guide-naming-conventions.html |
| Objektmetadaten | optionaler DNS-Prefix plus lokaler Name | Kubernetes Labels: https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/ |
| Slug-Felder | URL-sichere Labels, keine globale Governance | Django SlugField: https://docs.djangoproject.com/en/stable/ref/models/fields/#slugfield |
| Slug-Normalisierung | Transliteration und Separatornormalisierung | Rails `parameterize`: https://api.rubyonrails.org/classes/ActiveSupport/Inflector.html |
