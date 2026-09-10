### 1. Code

#### Code
SSccXX.M-<TT>-<NS>-<SLUG>

#### Basis-Code
SSccXX

#### Manifestationscodes
M-<TT>-<NS>-<SLUG>

### 2. Segmentierung

Die Segmentierung umfasst eine zweistellige Ziffer, wobei die erste aus Buchstaben und die zweite aus numerischen Werten besteht. Die Segmentierung gibt das Hierarchie-Level eines HiTOP-Konzepts an. Die erste Ziffer umfasst in Anlehnung an das HiTOP Working Model Werte aus der folgenden Menge {F, S, P, U, C, T} wobei F für die Faktorisierung steht, S für das Superspektrum, P für das Spektrum, U für die Subfaktoren, C für die Komponenten und T für die Traits. Die zweite Ziffer gibt an, ob die Konzepte weiter strukturiert vorliegen. Der Standardwert ist Null. Sollten Konzepte weiter verschachtelt im Rahmen einer HiTOP Faktorisierung vorliegen, wird pro Ebene der numerische Wert nach oben gezählt, also von 1 bis n.

Zum Beispiel: U0 (Subfaktor aus dem Working Model), U1 (Sub-Subfaktor aus dem MDS), U2 (Sub-Sub-Subfaktor aus dem MDS)

### 3. Konzepte

Durch die Kodierung der Konzepte wir eine präzise und differenzierte Identifikation der spezifischen psychologischen Superspectra, Spectra, Subfaktoren, Komponenten und Traits ermöglicht, die zur Erklärung von Verhaltens- und Erlebnisdimensionen beitragen. Jeder Code wird durch eine zweistellige alphanumerische Zeichenabfolge dargestellt, die auf dem Base-62-System basiert, wodurch bis zu 3.844 (62²) einzigartige Komponenten kodiert werden können. Diese Struktur nutzt Ziffern (0–9), Großbuchstaben (A–Z) und Kleinbuchstaben (a–z), um eine effiziente Klassifizierung und zukünftige Erweiterungen zu ermöglichen. Durch die Implementierung dieser Kodierung wird sichergestellt, dass alle gegenwärtigen und potenziellen Konzepte im Kontext der personalisierten Medizin und psychologischen Forschung systematisch erfasst werden können.

### 4. Prüfziffer

Der Basiscode endet mit einer zweistelligen Prüfziffer. Diese Prüfziffer wird
automatisch aus der festen Zeichenfolge
`HiTOP-<Segment>-<Konzeptcode>` abgeleitet. `HiTOP` ist dabei ein interner,
nicht konfigurierbarer Bestandteil des Prüfziffernalgorithmus und wird nicht
als Teil des Codes ausgegeben. Die Prüfziffer trägt keine fachliche Bedeutung, sondern stabilisiert die
Codevergabe und hilft dabei, Tippfehler oder unbeabsichtigte Änderungen
leichter zu erkennen. Die Ziffer wird immer mit zwei Base62-Zeichen geschrieben.

### 5. Modulares namespaced Suffix-Schema

Der HiTOP-Basiscode bleibt unverändert. Danach folgt ein punkt-separierter Manifestationssuffix mit kontrolliertem Typ, Namespace und lokalem Slug.

Ausführliche Spezifikation, Governance-Regeln und Beispiele: [modular-namespaced-suffix-schema.md](modular-namespaced-suffix-schema.md).

**Syntax**: 

```text
<HITOP_BASE_CODE>.M-<TT>-<NS>-<SLUG>
```

mit 

<HITOP_BASE_CODE>: HiTOP Code s.o.

M: literal fuer den Manifestationssuffix

TT: Manifestationstyp

NS: Namespace-Token nach dem Muster `[A-Z]{3}[A-Z2-7]{13}`

SLUG: ASCII-Slug nach dem Muster `[A-Z0-9](?:[A-Z0-9_]{1,38}[A-Z0-9])`

**Manifestationstypen:**

| **Typ** | **Code** | **Begründung** |
| --- | --- | --- |
| General symptom (unspezifisch) | GS | Fallback, bewusst selten |
| Clinical sign (objektiv) | CS | Klassische psychopathologische Kategorie |
| Syndrome / Cluster | SY | Explizite Symptomkombination |
| Affective symptom | AF | DSM/ICD-Domäne |
| Cognitive symptom | CG | Klar getrennt von Affekt |
| Perceptual symptom | PC | Wahrnehmung ≠ Kognition |
| Behavioral symptom | BH | Beobachtbares Verhalten |
| Somatic symptom | SS | Vegetativ/körperlich |
| Sleep / circadian | SL | Eigene DSM-Domäne |
| Substance-related | SU | Eigene DSM-Domäne |
| Interpersonal / relational | IR | Querschnittsdimension |
| Impairment / functioning | IM | Funktionsniveau ≠ Symptom |

**Beispiele:**

```text
U0d1XX.M-AF-ROR3J2WQSVQFFIKK-PHQ4_1
P0ssXX.M-SS-ROR3J2WQSVQFFIKK-DSM5CC_9
C00gvD.M-CS-ROR3J2WQSVQFFIKK-LEC5_A1
S0adXX.M-IM-ROR3J2WQSVQFFIKK-PF_AFFECT_DIFF_2
```

Fuer das DZPG-MDS-Modul `Psychische Gesundheit Basiserfassung` wird der
Namespace `ROR3J2WQSVQFFIKK` verwendet. Er ist aus der Authority
`https://ror.org/00tkfw097` abgeleitet und verhindert lokale Slug-Kollisionen
zwischen unterschiedlichen Datenproduzenten.

### Anhang

Alphanumerische Codierung

In der Base-62-Codierung repräsentiert eine Zeichenreihe die Werte von 0 bis 61. Um dies zu ermöglichen, wird eine Kombination aus Ziffern, Großbuchstaben und Kleinbuchstaben genutzt. Die Ziffern 0 bis 9 decken die Werte 0 bis 9 ab, die Großbuchstaben (A–Z) decken die Werte 10 bis 35, und die Kleinbuchstaben (a–z) stehen für die Werte 36 bis 61. Diese Anordnung maximiert die Anzahl von darstellbaren Einheiten pro Stellenwert und erlaubt eine kompakte, eindeutige Repräsentation für Anwendungen, die kurze und leicht interpretierbare Codes erfordern.

**Mehrfachzuweisung**

Um den Sachverhalt zu adressieren, dass unterschiedliche Level-Items mit unterschiedlichen Gewichtungen dem gleichen Item zugeordnet sind, werden im Rahmen der Meta-Ontologie und der FHIR-Spezifikationen Mehrfachzuordnungen adressiert. Dieses Vorgehen wird bereits auch bei SNOMED CT oder UMLS angewendet, wo ein Item mehrere Codes beinhalten kann.

### RDF/OWL-Namespace-Präfixe (TECH-T4-04)

`ontology/hitop.rdf` (und die daraus generierten `ontology/hitop.ttl`/`.owl`)
verwenden eine feste, stabile Präfixliste. Neue Präfixe werden nur ergänzt,
wenn ein Konzept eine externe Ontologie/ein externes Vokabular tatsächlich
referenziert — nicht auf Vorrat.

| Präfix | Namespace-IRI | Verwendung |
| --- | --- | --- |
| (default) | `http://purl.org/hitop#` | HiTOP-Basiscodes und -Konzeptklassen |
| `hitop` | `http://purl.org/hitop#` | expliziter Alias auf denselben Namespace, z. B. in Faktorisierungs-Vokabular (`hitop:hasTier`) |
| `owl` | `http://www.w3.org/2002/07/owl#` | OWL-Kernvokabular |
| `rdf` | `http://www.w3.org/1999/02/22-rdf-syntax-ns#` | RDF-Kernvokabular |
| `rdfs` | `http://www.w3.org/2000/01/rdf-schema#` | RDFS-Kernvokabular (`label`, `comment`, `subClassOf`, `isDefinedBy`) |
| `xsd` | `http://www.w3.org/2001/XMLSchema#` | Literal-Datentypen |
| `xml` | `http://www.w3.org/XML/1998/namespace` | XML-Sprachattribute (`xml:lang`) |
| `dc` | `http://purl.org/dc/elements/1.1/` | Dublin Core (einfach), z. B. Ontologie-Titel/-Beschreibung |
| `dcterms` | `http://purl.org/dc/terms/` | Dublin Core Terms, z. B. `contributor`, `creator`, `license` |
| `foaf` | `http://xmlns.com/foaf/0.1/` | Personenangaben (`foaf:Person`, `foaf:name`) |
| `skos` | `http://www.w3.org/2004/02/skos/core#` | `skos:changeNote` |
| `obo` | `http://purl.obolibrary.org/obo/` | OBO-Foundry-Vokabular, aktuell nur `obo:IAO_0000115` (Definition) |

**Bereinigt (TECH-T4-04):** Ein zusätzlicher `iao:`-Präfix
(`http://purl.obolibrary.org/obo/iao`) war deklariert, aber nirgends
tatsächlich verwendet — die Definitions-Annotation nutzte stattdessen
fälschlich `obo:iaoIAO_0000115` (eine falsche, nicht standardkonforme IRI,
die den `iao`-Präfixnamen versehentlich in den Lokalnamen unter `obo:`
hineinkopierte, statt den `iao:`-Namespace zu nutzen). Beides wurde
korrigiert: die Definitions-Annotation heißt jetzt korrekt `obo:IAO_0000115`
(die echte OBO-IAO-"definition"-Property), der ungenutzte `iao:`-Präfix
wurde entfernt.
