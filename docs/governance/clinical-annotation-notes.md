# Klinische Annotation Notes für Grenzfälle

Status: Befüllt — alle Grenzfälle entschieden
Version: 0.2.0
Datum: 2026-11-02
Gilt für: Konzeptklassen in [`ontology/hitop.rdf`](../ontology/hitop.rdf)

## 1. Zweck

Manche HiTOP-Konzepte lassen sich nicht ohne zusätzliche Erklärung eindeutig
einem Spektrum, Level oder einer Komponente zuordnen — z. B. weil ein
Konzept in mehreren Quellpapieren mit leicht unterschiedlichem Zuschnitt
auftaucht, weil zwei im Quellpaper getrennte Konstrukte im Working Model
zusammengeführt wurden, oder weil ein generischer Begriff mit einer
spezifischeren bestehenden Komponente verwechselt werden kann.

Dieses Dokument sammelt genau diese Grenzfälle mit Begründung, damit spätere
Leser:innen (Reviewer, Autor:innen des Papers, künftige Kurator:innen) nicht
denselben Klärungsaufwand wiederholen müssen. Es ist die Umsetzung von
`CLIN-C1-05`.

Die drei aktuell offenen Issues aus Block `C0`
(`CLIN-C0-01`, `CLIN-C0-02`, `CLIN-C0-03` — Vollständigkeitsabgleich gegen
die Superspectrum-Quellpapiere) sind die ersten konkreten Kandidaten für
Einträge hier: Sobald eine Entscheidung getroffen ist, wird die Begründung
als Zeile in Teil 3 ergänzt.

## 2. Geltungsbereich

Dieses Dokument deckt ab:

- Grenzfall-Beschreibungen und Entscheidungsbegründungen für einzelne
  HiTOP-Konzepte.

Dieses Dokument deckt **nicht** ab:

- die vollständige fachliche Definition eines Konzepts (das ist `CLIN-C1-01`,
  sichtbar direkt in `ontology/hitop.rdf` als `rdfs:comment`/`obo:iaoIAO_0000115`),
- Literaturquellen und Bibliographie (das ist [`references.md`](references.md)),
- Mapping-Entscheidungen zwischen Manifestationssuffixen (das ist
  [`mapping-und-harmonisierung.md`](mapping-und-harmonisierung.md)

## 3. Grenzfall-Tabelle

| Feld | Pflicht | Bedeutung |
| --- | --- | --- |
| `HiTOP-Code` | ja, sobald verfügbar | `hitop_base_code` aus `ontology/hitop.rdf`; solange eine Entscheidung noch aussteht (z. B. neuer Code noch nicht angelegt), Platzhaltertext `TBD (siehe <Issue>)` verwenden |
| `Label` | ja | aktuelles oder vorgeschlagenes `rdfs:label` |
| `Grenzfall-Beschreibung` | ja | in 1-3 Sätzen: warum ist die Zuordnung nicht ohne Weiteres eindeutig |
| `Entscheidung` | ja, sobald getroffen | die getroffene fachliche Entscheidung inkl. kurzer Begründung; solange offen: `ausstehend` |
| `Bezug` | ja | verweisendes Issue oder Task-ID (z. B. `CLIN-C0-01`) |
| `status` | ja | einer von: `offen` (Entscheidung steht aus), `entschieden` (Entscheidung getroffen, Umsetzung in `hitop.rdf` noch offen), `umgesetzt` (Entscheidung getroffen und in `hitop.rdf`/Faktorisierungen umgesetzt) |
| `geprüft von` | ja, sobald `status: entschieden` oder `umgesetzt` | Name oder Initialen der entscheidenden Person aus der Owner-Liste (`CLIN-C5-01`) |
| `Datum` | ja, sobald `status: entschieden` oder `umgesetzt` | Datum der Entscheidung, Format `YYYY-MM-DD` |

Stand 2026-11-02: Alle Fälle sind entschieden. Maßgeblich sind die am
2026-11-02 durch R. Blitz final freigegebenen Faktorisierungen. Die Spalte
`Entscheidung` nennt den Knotentyp: `concept` (inhaltliche Identität),
`partial` (nur Überschneidung) oder `collection` (lokale Gruppierung). Nach
Regel 3 werden die Zeilen mit dem Release-Commit auf `umgesetzt` gehoben.

| HiTOP-Code | Label | Grenzfall-Beschreibung | Entscheidung | Bezug | status | geprüft von | Datum |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `U0061L` | Harmful Substance Use | Externalizing-Paper (Krueger 2021) führt generische „Substance Use“/„Substance Problems“, das Working Model nur substanzspezifische Komponenten. | „Substance abuse“ ≡ `U0061L` (`concept`). Generische Use/Problems werden als `collection` über den substanzspezifischen Komponenten abgebildet; kein neuer Kerncode. | CLIN-C0-01 (#39), CLIN-C0-22 (#60) | entschieden | M. Richter, F. G. Verhees | 2026-09-30 |
| `C01HGq` | Drug use | DZPG-MDS erhebt „Smoking“; dafür gibt es keinen Kerncode. | „Smoking“ als `partial` (provisional) zu `C01HGq`; keine Äquivalenz. | Freigabe V10dzp | entschieden | R. Blitz | 2026-11-02 |
| `C00rnS` | Disorganized | Formale Denkstörung (Kotov 2020); früher fälschlich `T01OY2`. | Psychosis: „Disorganization“ ≡ `C00rnS` (`concept`, lokales Paper-Label). | CLIN-C0-02 (#40), CLIN-C0-11 (#49) | entschieden | M. Richter, L. R. Otto | 2026-09-30 |
| `C020XA` | Disorganization | Alltags-Desorganisiertheit (Disinhibition, Krueger 2021) ist etwas anderes als die formale Denkstörung. | Eigenes Kernkonzept; Externalizing nutzt `C020XA`, Psychosis behält `C00rnS`. Präzisiert #49 für Externalizing. | Review-Tabelle A. Kerber Nr. 35; Freigabe V108kx | entschieden | R. Blitz | 2026-11-02 |
| `C01zXz` | Hyperactivity | Krueger 2021 führt Hyperactivity neben Inattention. | Eigenes Kernkonzept; Externalizing ≡ `C01zXz` (`concept`). Hyperactive cognition (`C00oKM`) bleibt Mania-Komponente. | CLIN-C0-10 (#48), Review Nr. 34 | entschieden | R. Blitz | 2026-11-02 |
| `T018ir` | Distractibility | Externalizing-Paper führt Inattention (Symptom) getrennt vom Trait. | „Inattention“ als `partial` zu `T018ir`. | Review Nr. 30; Freigabe V108kx | entschieden | R. Blitz | 2026-11-02 |
| `T01A5i` | (low) Rigid perfectionism | Paper: „(low) perfectionism“ = niedrige Standards. | Externalizing: „(Low) Perfectionism“ als `partial`; präzisiert #58 („gleiche Dimension“) zu Überschneidung ohne Äquivalenz. | CLIN-C0-20 (#58); Freigabe V108kx | entschieden | M. Richter; Freigabe: R. Blitz | 2026-11-02 |
| `T00wk6` | Unusual beliefs and experiences | Psychosis-Paper nennt Beliefs und Experiences getrennt. | Ein gemeinsamer Knoten; keine Kernerweiterung. | CLIN-C0-03 (#41) | entschieden | F. G. Verhees, A. Kerber | 2026-09-30 |
| `T00vjR` | Cognitive dysregulation | Review Nr. 33 sah ein gemeinsames Konzept „Cognitive/perceptual dysregulation“. | Aufteilung in `T00vjR` und `T021iZ` durch das verbindliche Working Model bestätigt (Option a). | Review Nr. 33; Freigabe V1052k | entschieden | R. Blitz | 2026-11-02 |
| `T021iZ` | Perceptual dysregulation | wie oben | Eigenes Kernkonzept; Working Model und DZPG-MDS verwenden `T021iZ`. Review Nr. 33 ist damit revidiert. | Review Nr. 33; Freigabe V1052k, V10dzp | entschieden | R. Blitz | 2026-11-02 |
| `C00OuR` | Situational phobia | „Specific Phobia“ liegt als Störung über Situational/Animal/BII-Phobie. | „Specific Phobia“ als `collection` über `C00N4I`, `C00Pjp`, `C00OuR`. | CLIN-C0-06 (#44) | entschieden | F. G. Verhees, A. Kerber | 2026-09-30 |
| `C01l9M` | Body dissatisfaction | „ED Thoughts“ (Bass-Ackwards) ist nicht gleich „Body dissatisfaction“. | „ED Thoughts“ als `partial` zu `C01l9M`. Ersetzt die provisorische Collection aus #50; die Nicht-Äquivalenz bleibt gewahrt. | CLIN-C0-12 (#50); Freigabe V10bak | entschieden | L. R. Otto; Freigabe: R. Blitz | 2026-11-02 |
| `C01mPz` | Binge eating | „ED Bulimic“ ist weiter gefasst als ein Einzelsymptom. | „ED Bulimic“ als `partial` zu `C01mPz` (Bass-Ackwards, DZPG-MDS). Ersetzt die Collection aus #51 (Purging + Binge eating); Purging (`C01oMk`) ist dort nicht mehr verknüpft. | CLIN-C0-13 (#51); Freigabe V10bak, V10dzp | entschieden | M. Richter; Freigabe: R. Blitz | 2026-11-02 |
| `C01qTa` | Restricting | „ED Anorectic“ ist weiter gefasst als Restricting. | „ED Anorectic“ als `partial` zu `C01qTa` (Bass-Ackwards, DZPG-MDS). | CLIN-C0-14 (#52); Freigabe V10bak, V10dzp | entschieden | M. Richter; Freigabe: R. Blitz | 2026-11-02 |
| `C00XyI` | Anhedonia (Component) | Component und Trait mit identischem Label. | Labels „Anhedonia (Component)“ und „Anhedonia (Trait)“; keine prefLabel/altLabel. | CLIN-C0-23 (#61) | entschieden | M. Richter | 2026-08-04 |
| `T01hQc` | Anhedonia (Trait) | wie oben | wie oben | CLIN-C0-23 (#61) | entschieden | M. Richter | 2026-08-04 |
| `T00ua9` | Eccentricity | Psychosis-Paper: „Peculiarity“. | „Peculiarity“ ≡ `T00ua9` (`concept`). | Review Nr. 25 | entschieden | A. Kerber | 2026-10-18 |
| `T00BXK` | (low) Restricted affectivity | Kotov 2020: „Emotional detachment“ meint den hohen Pol; das Working Model führt den niedrigen Pol. | „Emotional detachment“ (Psychosis) und „Restricted affectivity“ (DZPG-MDS) als `partial`, also ohne Polbehauptung. | Review Nr. 27; Freigabe V10749, V10dzp | entschieden | R. Blitz | 2026-11-02 |
| `T00zDk` | Intimacy avoidance | Romantic disinterest (schizoid) vs. Vermeidung (auch angstbedingt). | „Romantic disinterest“ als `partial`. | Review Nr. 29; Freigabe V10749 | entschieden | R. Blitz | 2026-11-02 |
| `C001qy` | Conversion | Watson 2022: „Neurological“ = Konversion + Neurasthenie. | „Neurological“ als `partial` zu `C001qy`. | Review Nr. 3; Freigabe V106mv | entschieden | R. Blitz | 2026-11-02 |
| `C00Q1t` | Physiological panic | Watson 2022: Cardiopulmonary und Physiological anxiety, eingeordnet zwischen Somatoform und Distress. | Beide als `partial` zu `C00Q1t`; Physiological anxiety mit `bridge: [Somatoform, Distress]`. Der Spaltenwiderspruch in Review Nr. 23 ist damit zugunsten von Physiological panic entschieden. | Review Nr. 4, 23; Freigabe V106mv | entschieden | R. Blitz | 2026-11-02 |
| `C00RGy` | Psychological panic | Anxiety sensitivity ist bei Watson eine traitartige Vulnerabilität. | „Anxiety sensitivity“ als `partial` zu `C00RGy`. | Review Nr. 8; Freigabe V106mv | entschieden | R. Blitz | 2026-11-02 |
| `P002nf` | Internalizing | „Negative emotionality“ entspricht laut Watson der Spektrumsebene. | „Negative emotionality“ als `partial` zu `P002nf`. | Review Nr. 5; Freigabe V106mv | entschieden | R. Blitz | 2026-11-02 |
| `C01yno` | Health/Illness anxiety | Watson 2022 hält die Einordnung ausdrücklich offen. | Konzept mit `bridge: [Somatoform, Distress]`; Definition bleibt `draft`. | Review Nr. 24; Freigabe V106mv | entschieden | R. Blitz | 2026-11-02 |
| `C00e0L` | (low) Wellbeing | DZPG-MDS erhebt „Low self esteem“. | `partial` zu `C00e0L`. | Freigabe V10dzp | entschieden | R. Blitz | 2026-11-02 |
| `C00mpe` | Pure obsessions | DZPG-MDS erhebt „OCD“ als Störungsbegriff. | `partial` zu `C00mpe`. | Freigabe V10dzp | entschieden | R. Blitz | 2026-11-02 |
| `C00217` | Somatization | DZPG-MDS führt „Somatoform“ auf Spektrumsebene mit `kind: concept` auf `C00217` (Somatization, Component), obwohl das Spektrum `P001Y2` „Somatoform“ existiert. | **Gewollt** (Bestätigung R. Blitz, 2026-11-02): Der DZPG-MDS-Knoten „Somatoform“ ist inhaltlich identisch mit `C00217` Somatization (`concept`), nicht mit dem Spektrum `P001Y2`. | Freigabe V10dzp | entschieden | R. Blitz | 2026-11-02 |

## 4. Regeln für neue Einträge

1. Jede Zeile beschreibt genau einen Grenzfall zu genau einem (späteren)
   `HiTOP-Code`. Betrifft ein Grenzfall mehrere Codes (z. B. eine
   Aufsplitten-Entscheidung wie bei `CLIN-C0-03`), wird nach der Umsetzung
   pro neuem Code eine eigene Zeile ergänzt; die ursprüngliche Zeile bleibt
   mit `status: umgesetzt` und Verweis auf die neuen Codes erhalten.
2. Zeilen werden nie kommentarlos gelöscht. Ändert sich der Status, wird
   `Entscheidung`, `status`, `geprüft von` und `Datum` aktualisiert; der
   Verlauf bleibt über Git-Historie nachvollziehbar.
3. `status: umgesetzt` darf erst gesetzt werden, wenn die Entscheidung
   tatsächlich in `ontology/hitop.rdf` bzw. den betroffenen
   Faktorisierungsdateien nachvollziehbar ist (Commit-Referenz in
   `Entscheidung` ergänzen).
4. Neue Grenzfälle, die nicht aus einem bestehenden Issue stammen, MÜSSEN
   trotzdem einen `Bezug` bekommen — notfalls ein neu angelegtes Issue,
   nicht nur einen Freitext-Verweis.
