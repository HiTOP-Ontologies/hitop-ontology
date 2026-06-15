### 1. Code

#### Code
HiTOPSSccXX.M-<TT>-<NS>-<SLUG>

#### Basis-Code
HiTOPSSccXX

#### Manifestationscodes
M-<TT>-<NS>-<SLUG>

### 2. Präfix

Es wird ein Präfix im Codesystem eingesetzt, um die Eindeutigkeit und Wiedererkennung in komplexen oder integrierten Datenumgebungen zu gewährleisten. Dadurch wird eine sofortige Zuordnung des Codes zu einem spezifischen System oder Kontext ermöglicht und die Koexistenz heterogener Codierungsstandards in interoperablen Szenarien adressiert. Des Weiteren erleichtert der Präfix die Skalierbarkeit des Systems und verhindert, dass Codierungen unterschiedlicher Herkunft verwechselt werden. Somit unterstützt der Präfix die langfristige Flexibilität, Lesbarkeit und sichere Interoperabilität des Codes im wissenschaftlichen und datenorientierten Einsatzumfeld. Im Rahmen der Meta-Ontologie dient der Präfix als Indikator zur eindeutigen Identifizierung der Teilontologien. Um die Maschinenlesbarkeit zu verbessern, wird seine Länge auf 3 bis 5 alphanumerische Zeichen begrenzt. Der Präfix für die HiTOP-Ontologie lautet „HiTOP“.

### 3. Segmentierung

Die Segmentierung umfasst eine zweistellige Ziffer, wobei die erste aus Buchstaben und die zweite aus numerischen Werten besteht. Die Segmentierung gibt das Hierarchie-Level eines HiTOP-Konzepts an. Die erste Ziffer umfasst in Anlehnung an das HiTOP Working Model Werte aus der folgenden Menge {F, S, P, U, C, T} wobei F für die Faktorisierung steht, S für das Superspektrum, P für das Spektrum, U für die Subfaktoren, C für die Komponenten und T für die Traits. Die zweite Ziffer gibt an, ob die Konzepte weiter strukturiert vorliegen. Der Standardwert ist Null. Sollten Konzepte weiter verschachtelt im Rahmen einer HiTOP Faktorisierung vorliegen, wird pro Ebene der numerische Wert nach oben gezählt, also von 1 bis n.

Zum Beispiel: U0 (Subfaktor aus dem Working Model), U1 (Sub-Subfaktor aus dem MDS), U2 (Sub-Sub-Subfaktor aus dem MDS)

### 4. Konzepte

Durch die Kodierung der Konzepte wir eine präzise und differenzierte Identifikation der spezifischen psychologischen Superspectra, Spectra, Subfaktoren, Komponenten und Traits ermöglicht, die zur Erklärung von Verhaltens- und Erlebnisdimensionen beitragen. Jeder Code wird durch eine zweistellige alphanumerische Zeichenabfolge dargestellt, die auf dem Base-62-System basiert, wodurch bis zu 3.844 (62²) einzigartige Komponenten kodiert werden können. Diese Struktur nutzt Ziffern (0–9), Großbuchstaben (A–Z) und Kleinbuchstaben (a–z), um eine effiziente Klassifizierung und zukünftige Erweiterungen zu ermöglichen. Durch die Implementierung dieser Kodierung wird sichergestellt, dass alle gegenwärtigen und potenziellen Konzepte im Kontext der personalisierten Medizin und psychologischen Forschung systematisch erfasst werden können.

### 5. Prüfziffer

Der Basiscode endet mit einer zweistelligen Prüfziffer. Diese Prüfziffer wird
automatisch aus dem Präfix, der Segmentierung und dem lokalen Konzeptcode
abgeleitet. Sie trägt keine fachliche Bedeutung, sondern stabilisiert die
Codevergabe und hilft dabei, Tippfehler oder unbeabsichtigte Änderungen
leichter zu erkennen. Die Ziffer wird immer mit zwei Base62-Zeichen geschrieben.

### 6. Modulares namespaced Suffix-Schema

Der HiTOP-Basiscode bleibt unverändert. Danach folgt ein punkt-separierter Manifestationssuffix mit kontrolliertem Typ, Namespace und lokalem Slug.

Ausführliche Spezifikation, Governance-Regeln und Beispiele: [modular-namespaced-suffix-schema.md](modular-namespaced-suffix-schema.md).

**Syntax**: 

```text
<HiTOP>.M-<TT>-<NS>-<SLUG>
```

mit 

<HiTOP>: HiTOP Code s.o.

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
HiTOPU0d1XX.M-AF-ROR3J2WQSVQFFIKK-PHQ4_1
HiTOPP0ssXX.M-SS-ROR3J2WQSVQFFIKK-DSM5CC_9
HiTOPC00gvD.M-CS-ROR3J2WQSVQFFIKK-LEC5_A1
HiTOPS0adXX.M-IM-ROR3J2WQSVQFFIKK-PF_AFFECT_DIFF_2
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
