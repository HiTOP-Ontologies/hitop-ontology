# HiTOP Ontology Presentation Audit

Audit-ID: `20260615T194027+0200_hitop_ontology_presentation_audit`
Datum: 2026-06-15 19:40:27 +0200
Ziel: Inhaltsaudit fuer eine 10-Folien-Praesentation ueber Zweck, Nutzen, Stand und naechste Schritte der HiTOP Ontology
Scope: Repository `hitop-ontology`, HiTOP-Ontologie, Codesystem, Manifestationssuffixe, Mapping, klinische Review-Aufgaben, technische Release-Aufgaben

## Praesentationsrahmen

| Parameter | Vorgabe |
| --- | --- |
| Format | 10 Folien inklusive Titelfolie |
| Thema | Was die HiTOP Ontology fachlich ist, welches Problem sie loest, welchen Nutzen sie bringt und was noch zu tun ist |
| Zielgruppe | Klinische Fachgruppe, technische Maintainer, Daten-/Interoperabilitaetsverantwortliche, Projektleitung |
| Erzaehllinie | Von fachlichem Bedarf ueber Ontologie- und Code-Modell zu Nutzen, aktuellem Stand und Arbeitsplan |
| Content-Regel | Jede Folie enthaelt nur den Inhaltsbereich. Keine Header, Footer, Seitenzahlen, Logos, Meta-Leisten oder Quellenfusszeilen in den Prompts erzeugen. |

## Kernaussage des Decks

Die HiTOP Ontology ueberfuehrt das dimensionale HiTOP-Modell der Psychopathologie in ein maschinenlesbares, versionierbares und erweiterbares Codesystem. Sie soll psychische Gesundheitsdaten ueber Konzepte, Symptome, Instrumente, Studien und Standorte hinweg vergleichbarer machen, ohne lokale Erhebungslogiken zu verlieren.

## Folienstruktur und Content-Prompts

### Folie 1: Titelfolie

| Feld | Inhalt |
| --- | --- |
| Zweck | Thema und Nutzenversprechen der Praesentation setzen |
| Kernaussage | Die HiTOP Ontology macht dimensionale Psychopathologie als interoperables Datenmodell nutzbar. |
| Content-Prompt | Erstelle ausschliesslich den Inhaltsbereich einer 16:9-Titelfolie ohne Header und Footer. Haupttitel: "HiTOP Ontology". Untertitel: "Ein interoperables Datenmodell fuer dimensionale Psychopathologie". Fuege drei kurze Stichworte als visuelle Orientierung hinzu: "Strukturieren", "Vergleichen", "Harmonisieren". Verwende keine Seitenzahl, keine Fussnote, keine Logozeile und keine Quellenzeile. |

### Folie 2: Wofuer die HiTOP Ontology da ist

| Feld | Inhalt |
| --- | --- |
| Zweck | Inhaltliche Funktion der Ontologie erklaeren |
| Kernaussage | Die Ontologie beschreibt psychische Gesundheitsdimensionen nicht nur als Textlabels, sondern als stabile, referenzierbare Konzepte. |
| Content-Prompt | Erstelle ausschliesslich den Inhaltsbereich einer 16:9-Folie ohne Header und Footer. Erklaere, wofuer die HiTOP Ontology inhaltlich da ist: strukturierte Repraesentation der Hierarchical Taxonomy of Psychopathology, stabile Identifikation von Superspektren, Spektren, Subfaktoren, Komponenten und Traits, Verbindung von Konzepten mit Manifestationen aus Studien, Instrumenten oder Datensaetzen, Grundlage fuer vergleichbare Analysen und Mapping. Nutze eine einfache "Von Fachkonzept zu Datennutzung"-Darstellung. Keine Seitenzahl, keine Fussnote, keine Logozeile und keine Quellenzeile. |

### Folie 3: Welches Problem sie loest

| Feld | Inhalt |
| --- | --- |
| Zweck | Problemraum klar machen |
| Kernaussage | Psychische Gesundheitsdaten sind oft semantisch aehnlich, aber technisch und fachlich nicht sauber vergleichbar. |
| Content-Prompt | Erstelle ausschliesslich den Inhaltsbereich einer 16:9-Folie ohne Header und Footer. Zeige das Problem, das die HiTOP Ontology loest: heterogene Instrumente, unterschiedliche Item-Labels, uneinheitliche Diagnose- und Symptombegriffe, lokale Studiencodes, schwer vergleichbare Operationalisierungen und fehlende maschinenlesbare Beziehungen zwischen Konzepten. Stelle links den fragmentierten Ist-Zustand und rechts den Zielzustand mit stabilen Codes, Definitionen, Hierarchie und Mapping dar. Keine Seitenzahl, keine Fussnote, keine Logozeile und keine Quellenzeile. |

### Folie 4: Warum HiTOP als Modellbasis

| Feld | Inhalt |
| --- | --- |
| Zweck | Fachliche Relevanz des HiTOP-Ansatzes begruenden |
| Kernaussage | HiTOP unterstuetzt eine dimensionale, hierarchische Sicht auf Psychopathologie statt isolierter Kategorien. |
| Content-Prompt | Erstelle ausschliesslich den Inhaltsbereich einer 16:9-Folie ohne Header und Footer. Erklaere den fachlichen Vorteil von HiTOP als Modellbasis: psychische Belastung wird dimensional und hierarchisch beschrieben, Konzepte koennen auf mehreren Ebenen betrachtet werden, transdiagnostische Muster werden besser abbildbar, Symptome und Traits lassen sich differenzierter mit Daten verbinden. Visualisiere die Ebenen als einfache Hierarchie: Superspektrum, Spektrum, Subfaktor, Komponente, Trait. Keine Seitenzahl, keine Fussnote, keine Logozeile und keine Quellenzeile. |

### Folie 5: Wie die Ontologie strukturiert

| Feld | Inhalt |
| --- | --- |
| Zweck | Code- und Strukturprinzipien verstaendlich machen |
| Kernaussage | Das Codesystem trennt stabile HiTOP-Konzeptidentitaet von lokalen Manifestationen. |
| Content-Prompt | Erstelle ausschliesslich den Inhaltsbereich einer 16:9-Folie ohne Header und Footer. Beschreibe die Grundstruktur des Codesystems als zweistufiges Modell: stabiler HiTOP-Basiscode plus optionaler MNS. Stelle die Lesart `HiTOP SS cc XX + MNS` dar und erklaere die Bestandteile knapp: `HiTOP` = Praefix des Codesystems, `SS` = zweistelliges Segment fuer Hierarchieebene und Level, z.B. Superspektrum, Spektrum, Subfaktor, Komponente oder Trait, `cc` = lokaler alphanumerischer Konzeptcode, `XX` = zweistellige Pruefziffer ohne fachliche Bedeutung, `MNS` = Modularer Namespace-Suffix fuer konkrete Manifestationen. Zeige darunter die technische Form `HiTOPSSccXX.M-<TT>-<NS>-<SLUG>` und erklaere: Der Basiscode identifiziert das fachliche HiTOP-Konzept; der MNS nach dem Punkt beschreibt eine konkrete Manifestation in einem Daten-, Studien- oder Instrumentenkontext. Keine Seitenzahl, keine Fussnote, keine Logozeile und keine Quellenzeile. |

### Folie 6: Modularer Namespace-Suffix

| Feld | Inhalt |
| --- | --- |
| Zweck | Erweiterbarkeit und dezentrale Nutzbarkeit erklaeren |
| Kernaussage | Lokale Manifestationen koennen eindeutig kodiert werden, ohne die gemeinsame HiTOP-Basis zu verlieren. |
| Content-Prompt | Erstelle ausschliesslich den Inhaltsbereich einer 16:9-Folie ohne Header und Footer. Erklaere knapp, aber konkret den modularen Namespace-Suffix als Erweiterung eines stabilen HiTOP-Basiscodes. Zeige die Syntax `HiTOPSSccXX.M-<TT>-<NS>-<SLUG>` und zerlege sie visuell in vier Teile: `HiTOPSSccXX` = gemeinsames HiTOP-Konzept, `M` = Manifestationsblock, `<TT>` = kontrollierter Manifestationstyp wie `AF`, `SS` oder `IM`, `<NS>` = lokaler Authority-Raum zur Kollisionsvermeidung, `<SLUG>` = lesbarer lokaler Name. Nutze ein konkretes Beispiel aus dem Repository: `HiTOPU0d1XX.M-AF-ROR3J2WQSVQFFIKK-PHQ4_1`. Erklaere den Nutzen in maximal drei Bulletpoints: dezentrale Studien und Instrumente koennen eigene Manifestationen kodieren, lokale Slugs kollidieren nicht zwischen Datenproduzenten, die gemeinsame HiTOP-Basis bleibt fuer Vergleich und spaeteres Mapping erhalten. Keine Regex-, Hash- oder Governance-Details. Keine Seitenzahl, keine Fussnote, keine Logozeile und keine Quellenzeile. |

### Folie 7: Vorteile fuer Forschung, Klinik und Datenintegration

| Feld | Inhalt |
| --- | --- |
| Zweck | Konkreten Nutzen herausarbeiten |
| Kernaussage | Die Ontologie schafft gemeinsame Semantik, ohne lokale Datenerhebung zu vereinheitlichen. |
| Content-Prompt | Erstelle ausschliesslich den Inhaltsbereich einer 16:9-Folie ohne Header und Footer. Stelle die Vorteile der HiTOP Ontology in drei Spalten dar: Forschung, Klinik, Datenintegration. Forschung: vergleichbare Variablen, bessere Kohortenabfragen, harmonisierte Mappings. Klinik: klarere Begriffe, Review-faehige Definitionen, transdiagnostische Sicht. Datenintegration: stabile Identifier, maschinenlesbare Artefakte, FHIR/SKOS-nahe Mapping-Optionen, weniger Code-Kollisionen. Formuliere die zentrale Nutzenbotschaft: "Gemeinsame Bedeutung, lokale Flexibilitaet." Keine Seitenzahl, keine Fussnote, keine Logozeile und keine Quellenzeile. |

### Folie 8: Aktueller Stand

| Feld | Inhalt |
| --- | --- |
| Zweck | Reifegrad und vorhandene Artefakte realistisch darstellen |
| Kernaussage | Es gibt eine funktionierende technische Basis, aber noch offene fachliche und Release-bezogene Entscheidungen. |
| Content-Prompt | Erstelle ausschliesslich den Inhaltsbereich einer 16:9-Folie ohne Header und Footer. Gib den aktuellen Stand der HiTOP Ontology als Statusuebersicht wieder: RDF-Ontologie unter `ontology/hitop.rdf`, Ontologie-Version `0.1.0`, Codesystem-Dokumentation vorhanden, Basisvokabular beschrieben, Manifestationssuffix-Schema als Entwurf vorhanden, Mapping- und Harmonisierungsspezifikation in Version `1.0.0`, Python-Tooling fuer Codegenerierung und Suffixvalidierung vorhanden, lokale Tests und Validierung erfolgreich. Ergaenze die Einschraenkung: klinische Freigabe, Modellkonsistenz und Release-Gates sind noch nicht abgeschlossen. Keine Seitenzahl, keine Fussnote, keine Logozeile und keine Quellenzeile. |

### Folie 9: Was klinisch zu tun ist

| Feld | Inhalt |
| --- | --- |
| Zweck | Klinische Arbeitspakete konkret machen |
| Kernaussage | Die klinische Aufgabe ist die fachliche Absicherung von Konzepten, Definitionen, Hierarchien, Manifestationstypen und Mappings. |
| Content-Prompt | Erstelle ausschliesslich den Inhaltsbereich einer 16:9-Folie ohne Header und Footer. Zeige die klinischen To-dos als priorisierte Arbeitsliste: Klassenlabels und Definitionen reviewen, Hierarchie und Parent-Child-Beziehungen validieren, Segment- und Level-Zuordnung fachlich pruefen, Manifestationstypen und Slugs auf klinische Eindeutigkeit bewerten, Regeln fuer General-Symptom-Fallback operationalisieren, Mapping-Relationen und Review-Level 3/4 kuratieren, klinische Owner und Go/No-Go-Kriterien festlegen. Kennzeichne die wichtigste klinische Entscheidung: "Welche Inhalte sind releasefaehig und welche bleiben Draft?" Keine Seitenzahl, keine Fussnote, keine Logozeile und keine Quellenzeile. |

### Folie 10: Was technisch zu tun ist

| Feld | Inhalt |
| --- | --- |
| Zweck | Technische Umsetzungsschritte und naechste Entscheidungen klaeren |
| Kernaussage | Technisch geht es jetzt um reproduzierbare Artefakte, konsistente Datenmodelle und automatisierte Release-Validierung. |
| Content-Prompt | Erstelle ausschliesslich den Inhaltsbereich einer 16:9-Abschlussfolie ohne Header und Footer. Zeige die technischen To-dos als handlungsorientierte Liste: kanonischen Pfad fuer RDF/OWL/TTL-Artefakte festlegen, `owl:versionInfo` und Ontologie-Metadaten releasefaehig bereinigen, JSON-Schema und Python-Metadatenmodell angleichen, CI fuer Tests, Schema-Validierung und Ontologie-Konvertierung einrichten, reproduzierbare Builds und Python-Matrix 3.10 bis 3.12 absichern, README und Release-Gates finalisieren, untracked/deleted Dateien im Git-Arbeitsbaum bereinigen. Schliesse mit einer klaren Abschlussfrage: "Welche technischen Gates muessen vor der klinischen Freigabe verbindlich gruen sein?" Keine Seitenzahl, keine Fussnote, keine Logozeile und keine Quellenzeile. |

## Audit-Hinweise fuer die Folienerstellung

| Pruefpunkt | Kriterium |
| --- | --- |
| Folienanzahl | Genau 10 Folien inklusive Titelfolie |
| Prompt-Abdeckung | Jede Folie hat einen eigenen Content-Prompt |
| Header/Footer-Ausschluss | Jeder Prompt untersagt Header, Footer, Seitenzahl, Logozeile und Quellenfusszeile |
| Inhaltlicher Fokus | Die Ontologie selbst steht im Zentrum, nicht der Release-Audit-Prozess |
| Pflichtthemen | Zweck, Problem, Vorteil, Struktur, aktueller Stand, klinische To-dos, technische To-dos |
| Wiederverwendbarkeit | Prompts koennen direkt an ein Slide- oder Content-Generierungstool uebergeben werden |
