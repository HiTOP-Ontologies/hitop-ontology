# Klinische Annotation Notes für Grenzfälle

Status: Vorlage — von der Arbeitsgruppe Clinical Lab zu befüllen
Version: 0.1.0
Datum: 2026-07-06
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

Startzustand — die ersten drei Zeilen sind die noch offenen `C0`-Fälle:

| HiTOP-Code | Label | Grenzfall-Beschreibung | Entscheidung | Bezug | status | geprüft von | Datum |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `TBD (siehe CLIN-C0-01)` | Substance Use / Substance Problems | Externalizing-Superspectrum-Paper (wps.20844) führt generische "Substance Use"/"Substance Problems" auf; das Working Model kennt nur substanzspezifische Komponenten (Alcohol/Marijuana/Drug use/problems) unter "Harmful Substance Abuse" (`U0061L`). Die Externalizing-Faktorisierung verwendet aktuell fälschlich die Drug-Codes (`C01HGq`, `C01Ip4`) dafür. | ausstehend | CLIN-C0-01 | offen | | |
| `TBD (siehe CLIN-C0-02)` | Disorganization | Konzept taucht sowohl im Externalizing- (wps.20844) als auch im Psychosis-Superspectrum-Paper (wps.20730) auf. Es existiert kein eigener Code; beide Faktorisierungen verwenden fälschlich `T01OY2` ("(low) Planful control" im Working Model). | ausstehend | CLIN-C0-02 | offen | | |
| `TBD (siehe CLIN-C0-03)` | Unusual Beliefs / Unusual Experiences | Psychosis-Superspectrum-Paper (wps.20730) führt beide Konstrukte einzeln auf; Working Model und Psychosis-Faktorisierung führen sie aktuell als ein Trait (`T00wk6`, "Unusual beliefs and experiences") zusammen. | ausstehend | CLIN-C0-03 | offen | | |

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
