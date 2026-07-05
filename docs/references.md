# Referenzen und Quellenbelege für HiTOP-Konzepte

Status: Vorlage — von der Arbeitsgruppe Klinik zu befüllen
Version: 0.1.0
Datum: 2026-07-05

## 1. Zweck

Jede Konzeptklasse in `ontology/hitop.rdf` hat aktuell nur ein `rdfs:label`,
eine Definition (`obo:iaoIAO_0000115` bzw. `rdfs:comment`) und optional ein
`skos:changeNote`. Es gibt **keine** Quellenangabe pro Klasse und **keine**
Bibliographie im Repository.

Dieses Dokument schließt diese Lücke. Es beantwortet für jedes zentrale
HiTOP-Konzept die Frage: *Aus welcher publizierten Quelle stammen Label und
Definition, und wer hat das geprüft.

## 2. Geltungsbereich

Dieses Dokument deckt ab:

- Literaturquellen für Konzeptlabels und -definitionen der Kernontologie
  (Superspektrum, Spektrum, Subfaktor, Komponente, Trait).

Dieses Dokument deckt **nicht** ab:

- Mapping-Evidenz für Manifestationssuffixe. Das gehört, sobald relevant, in
  [`mapping-und-harmonisierung.md`](mapping-und-harmonisierung.md).
- Provenienz einzelner Faktorisierungen (z. B. Quelle einer konkreten
  Baumstruktur). Das steht in der jeweiligen
  `factorizations/<factorization-id>/v<N>/README.md`.

## 3. Aufbau: zwei Teile

Das Dokument besteht aus zwei Tabellen, die zusammengehören:

- **Teil A** listet jede zitierte Quelle genau einmal, mit einem stabilen
  Kurzschlüssel (`citation_key`).
- **Teil B** ordnet jedem HiTOP-Code einen oder mehrere `citation_key`-Werte
  aus Teil A zu.

Eine Quelle wird nie direkt in Teil B ausgeschrieben — dort steht immer nur
der Schlüssel. Das verhindert, dass dieselbe Quelle mehrfach leicht
unterschiedlich zitiert wird.

## 4. Teil A — Bibliographie

| Feld | Pflicht | Bedeutung |
| --- | --- | --- |
| `citation_key` | ja | stabiler Kurzschlüssel, Form `<erster-autor><jahr>` in Kleinbuchstaben, z. B. `kotov2017`; bei mehreren Quellen desselben Autors/Jahres Suffix `a`, `b`, … anhängen |
| `Vollständige Referenz` | ja | ausgeschriebene Referenz im Vancouver-Stil (Autor:innen, Titel, Journal, Jahr, Band, Seiten) — Vancouver-Stil, weil das Zielformat für das Paper (Journal of Biomedical Semantics) diesen Stil verlangt |
| `DOI/URL` | ja, falls vorhanden | persistenter Link; wenn keine DOI existiert, stabile URL eintragen; wenn keine von beiden existiert, Feld auf `keine` setzen, nicht leer lassen |
| `Deckt ab` | ja | in einem Satz: was diese Quelle grundsätzlich beschreibt (z. B. "Gesamtmodell und alle Superspektren", "Aktualisierung des Internalizing-Spektrums") |

Tabelle (Startzustand — die erste Zeile ist ein Beispiel und MUSS vor dem
produktiven Gebrauch entfernt oder durch echte Prüfung bestätigt werden):

| citation_key | Vollständige Referenz | DOI/URL | Deckt ab |
| --- | --- | --- | --- |
| `kotov2017` *(BEISPIEL)* | Kotov R, Krueger RF, Watson D, et al. The Hierarchical Taxonomy of Psychopathology (HiTOP): A dimensional alternative to traditional nosologies. J Abnorm Psychol. 2017;126(4):454-477. | https://doi.org/10.1037/abn0000258 | Gesamtmodell und ursprüngliche Superspektren |

## 5. Teil B — Quellenzuordnung pro Konzept

| Feld | Pflicht | Bedeutung |
| --- | --- | --- |
| `HiTOP-Code` | ja | `hitop_base_code` aus `ontology/hitop.rdf`, z. B. `S0013h` |
| `Label` | ja | aktuelles `rdfs:label` der Klasse, zum schnellen Abgleich ohne die RDF-Datei zu öffnen |
| `citation_key(s)` | ja | ein oder mehrere Schlüssel aus Teil A, durch Komma getrennt; mindestens ein Schlüssel ist Pflicht, außer bei `status: pending` |
| `Abschnitt/Seite` | nein | optionaler Verweis auf Abschnitt, Tabelle oder Seite in der Quelle, an der genau dieses Konzept definiert wird (erleichtert Nachprüfung durch Reviewer) |
| `Anmerkung` | nein | z. B. "Label leicht angepasst gegenüber Quelle", "Definition paraphrasiert, nicht wörtlich übernommen" |
| `status` | ja | einer von: `reviewed` (Quelle geprüft und bestätigt), `draft` (Quelle vorgeschlagen, noch nicht geprüft), `pending` (noch keine Quelle gefunden), `excluded` (Konzept bewusst ohne externe Quelle, z. B. rein strukturelles Hilfskonzept — Begründung dann in `Anmerkung`) |
| `geprüft von` | ja, sobald `status: reviewed` | Name oder Initialen der prüfenden Person aus der Owner-Liste (`CLIN-C5-01`) |
| `Datum` | ja, sobald `status: reviewed` | Datum der Prüfung, Format `YYYY-MM-DD` |

Tabelle: automatisch aus allen 163 Klassen in `ontology/hitop.rdf` generiert
(Stand 2026-07-05; `HiTOP-Code` und `Label` sind bereits befüllt). Die acht
strukturellen Schema-Klassen (`Level`, `Tier` und die sechs Level-Subklassen
`Factor`/`Superspectrum`/`Spectrum`/`Subfactor`/`Component`/`Trait`, siehe
[`docs/factorizations.md`](factorizations.md) Abschnitt 4) sind bereits mit
`status: excluded` vorbelegt, weil sie keine domänenspezifischen HiTOP-Konzepte
sind. Alle übrigen 155 Zeilen stehen auf `status: pending` und müssen von der
Arbeitsgruppe Klinik um `citation_key(s)`, `status` und ggf. `Abschnitt/Seite`
ergänzt werden. Wird die Ontologie geändert (neue/entfernte Klassen), muss
diese Tabelle neu generiert werden, damit sie mit `ontology/hitop.rdf`
deckungsgleich bleibt.

| HiTOP-Code | Label | citation_key(s) | Abschnitt/Seite | Anmerkung | status | geprüft von | Datum |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `C001qy` | Conversion | | |  | pending | | |
| `C00217` | Somatization | | |  | pending | | |
| `C0033z` | Malaise | | |  | pending | | |
| `C00416` | Head Pain | | |  | pending | | |
| `C005Sv` | Gastrointestinal | | |  | pending | | |
| `C006MD` | Cognitive | | |  | pending | | |
| `C00JTU` | Interactive anxiety | | |  | pending | | |
| `C00KL0` | Performance anxiety | | |  | pending | | |
| `C00LqY` | Public places | | |  | pending | | |
| `C00Mpl` | Enclosed spaces | | |  | pending | | |
| `C00N4I` | Animal phobia | | |  | pending | | |
| `C00OuR` | Situational phobia | | |  | pending | | |
| `C00Pjp` | Blood-injection-injury | | |  | pending | | |
| `C00Q1t` | Physiological panic | | |  | pending | | |
| `C00RGy` | Psychological panic | | |  | pending | | |
| `C00S9m` | Cleaning | | |  | pending | | |
| `C00TgL` | Rituals | | |  | pending | | |
| `C00Urw` | Checking | | |  | pending | | |
| `C00VHv` | Dysphoria | | |  | pending | | |
| `C00WJc` | Lassitude | | |  | pending | | |
| `C00XyI` | Anhedonia | | |  | pending | | |
| `C00Y8j` | Insomnia | | |  | pending | | |
| `C00ZyP` | Suicidality | | |  | pending | | |
| `C00aMF` | Agitation | | |  | pending | | |
| `C00bEx` | Retardation | | |  | pending | | |
| `C00cSn` | Appetite loss | | |  | pending | | |
| `C00dc1` | Appetite gain | | |  | pending | | |
| `C00e0L` | (low) Wellbeing | | |  | pending | | |
| `C00fKQ` | Generalized anxiety disorder symptoms | | |  | pending | | |
| `C00gvD` | Re-experiencing | | |  | pending | | |
| `C00hPJ` | Avoidance | | |  | pending | | |
| `C00iAh` | Hyperarousal | | |  | pending | | |
| `C00jw5` | Numbing | | |  | pending | | |
| `C00kEN` | Dissociation | | |  | pending | | |
| `C00l5y` | Irritability | | |  | pending | | |
| `C00mpe` | Pure obsessions | | |  | pending | | |
| `C00nyb` | Euphoric activation | | |  | pending | | |
| `C00oKM` | Hyperactive cognition | | |  | pending | | |
| `C00pnZ` | Reckless overconfidence | | |  | pending | | |
| `C00qSD` | Psychotic | | |  | pending | | |
| `C00rnS` | Disorganized | | |  | pending | | |
| `C00sWr` | Inexpressivity | | |  | pending | | |
| `C00tUQ` | Avolition | | |  | pending | | |
| `C01DAb` | Alcohol use | | |  | pending | | |
| `C01Elz` | Alcohol problems | | |  | pending | | |
| `C01FDy` | Marijuana use | | |  | pending | | |
| `C01GEY` | Marijuana problems | | |  | pending | | |
| `C01HGq` | Drug use | | |  | pending | | |
| `C01Ip4` | Drug problems | | |  | pending | | |
| `C01JH8` | Physical aggression | | |  | pending | | |
| `C01KXo` | Destructive aggression | | |  | pending | | |
| `C01LSp` | Relational aggression | | |  | pending | | |
| `C01MjB` | Fraud | | |  | pending | | |
| `F001Hw` | General Psychopathology | | |  | pending | | |
| `O001Ih` | Level | | | strukturelle Schema-Klasse (Level-/Tier-Vokabular aus `docs/factorizations.md`), kein domänenspezifisches HiTOP-Konzept | excluded | | |
| `O004Hd` | Factor | | | strukturelle Schema-Klasse (Level-/Tier-Vokabular aus `docs/factorizations.md`), kein domänenspezifisches HiTOP-Konzept | excluded | | |
| `O005pp` | Superspectrum | | | strukturelle Schema-Klasse (Level-/Tier-Vokabular aus `docs/factorizations.md`), kein domänenspezifisches HiTOP-Konzept | excluded | | |
| `O006lN` | Spectrum | | | strukturelle Schema-Klasse (Level-/Tier-Vokabular aus `docs/factorizations.md`), kein domänenspezifisches HiTOP-Konzept | excluded | | |
| `O007SH` | Subfactor | | | strukturelle Schema-Klasse (Level-/Tier-Vokabular aus `docs/factorizations.md`), kein domänenspezifisches HiTOP-Konzept | excluded | | |
| `O008Ob` | Component | | | strukturelle Schema-Klasse (Level-/Tier-Vokabular aus `docs/factorizations.md`), kein domänenspezifisches HiTOP-Konzept | excluded | | |
| `O009zM` | Trait | | | strukturelle Schema-Klasse (Level-/Tier-Vokabular aus `docs/factorizations.md`), kein domänenspezifisches HiTOP-Konzept | excluded | | |
| `O002sP` | Tier | | | strukturelle Schema-Klasse (Level-/Tier-Vokabular aus `docs/factorizations.md`), kein domänenspezifisches HiTOP-Konzept | excluded | | |
| `P001Y2` | Somatoform | | |  | pending | | |
| `P002nf` | Internalizing | | |  | pending | | |
| `P003SL` | Thought Disorder | | |  | pending | | |
| `P004R1` | Detachment | | |  | pending | | |
| `P005xY` | Disinhibited Externalizing | | |  | pending | | |
| `P006gM` | Antagonistic Externalizing | | |  | pending | | |
| `S0013h` | Externalizing | | |  | pending | | |
| `S002SE` | Emotional dysfunction | | |  | pending | | |
| `S003TB` | Psychosis | | |  | pending | | |
| `T007eM` | Anxiousness | | |  | pending | | |
| `T008mD` | Emotional lability | | |  | pending | | |
| `T0094I` | Hostility | | |  | pending | | |
| `T00A0Z` | Perseveration | | |  | pending | | |
| `T00BXK` | (low) Restricted affectivity | | |  | pending | | |
| `T00Cgy` | Separation insecurity | | |  | pending | | |
| `T00D42` | Submissiveness | | |  | pending | | |
| `T00Eht` | Identity problems | | |  | pending | | |
| `T00Fe0` | Negative relationships | | |  | pending | | |
| `T00G3d` | Fragility | | |  | pending | | |
| `T00HCy` | Ineptitude | | |  | pending | | |
| `T00IAT` | (low) Invulnerability | | |  | pending | | |
| `T00ua9` | Eccentricity | | |  | pending | | |
| `T00vjR` | Cognitive perceptual dysregulation | | |  | pending | | |
| `T00wk6` | Unusual beliefs and experiences | | |  | pending | | |
| `T00xLn` | Fantasy proneness | | |  | pending | | |
| `T00yfU` | Depressivity | | |  | pending | | |
| `T00zDk` | Intimacy avoidance | | |  | pending | | |
| `T010c6` | Suspiciousness | | |  | pending | | |
| `T011K6` | Withdrawal | | |  | pending | | |
| `T012QL` | Interpersonal passivity | | |  | pending | | |
| `T013F1` | Disaffiliativeness | | |  | pending | | |
| `T014BA` | (low) Attention seeking | | |  | pending | | |
| `T015o8` | Problematic impulsivity | | |  | pending | | |
| `T016k0` | Irresponsibility | | |  | pending | | |
| `T0177S` | Theft | | |  | pending | | |
| `T018ir` | Distractibility | | |  | pending | | |
| `T019Cj` | Risk taking | | |  | pending | | |
| `T01A5i` | (low) Rigid perfectionism | | |  | pending | | |
| `T01BfQ` | (low) Ruminative deliberation | | |  | pending | | |
| `T01C1W` | (low) Workaholism | | |  | pending | | |
| `T01Neb` | Impatient urgency | | |  | pending | | |
| `T01OY2` | (low) Planful control | | |  | pending | | |
| `T01PMW` | (low) Dependability | | |  | pending | | |
| `T01QNN` | Alienation | | |  | pending | | |
| `T01RYG` | Boredom proneness | | |  | pending | | |
| `T01SYW` | Blame externalization | | |  | pending | | |
| `T01T3u` | (low) Honesty | | |  | pending | | |
| `T01UGN` | Rebelliousness | | |  | pending | | |
| `T01VXq` | (low) Empathy | | |  | pending | | |
| `T01W1E` | Excitement seeking | | |  | pending | | |
| `T01XQi` | Attention seeking | | |  | pending | | |
| `T01Y7w` | Callousness | | |  | pending | | |
| `T01Ziz` | Deceitfulness | | |  | pending | | |
| `T01a7u` | Grandiosity | | |  | pending | | |
| `T01bz7` | Manipulativeness | | |  | pending | | |
| `T01cX5` | Rudeness | | |  | pending | | |
| `T01d9I` | Egocentricity | | |  | pending | | |
| `T01eG6` | Dominance | | |  | pending | | |
| `T01fc8` | Flirtatiousness | | |  | pending | | |
| `T01gKP` | (low) Timorousness | | |  | pending | | |
| `T01hQc` | Anhedonia | | |  | pending | | |
| `C01i7x` | Pain | | |  | pending | | |
| `C01jKN` | Fatigue | | |  | pending | | |
| `C01kKJ` | Neurological | | |  | pending | | |
| `C01l9M` | Cardiopulmonary | | |  | pending | | |
| `C01mPz` | Negative emotionality | | |  | pending | | |
| `C01nVp` | Anger/irritability | | |  | pending | | |
| `C01oMk` | Behavioral avoidance | | |  | pending | | |
| `C01pc6` | Anxiety sensitivity | | |  | pending | | |
| `C01qTa` | BII phobia | | |  | pending | | |
| `C01rfi` | Body dissatisfaction | | |  | pending | | |
| `C01s9T` | Binge eating | | |  | pending | | |
| `C01tAk` | Cognitive restraint | | |  | pending | | |
| `C01ueZ` | Purging | | |  | pending | | |
| `C01vT5` | Excessive exercise | | |  | pending | | |
| `C01wSl` | Restricting | | |  | pending | | |
| `C01xzj` | Muscle building | | |  | pending | | |
| `C01yno` | Negative attitudes toward obesity | | |  | pending | | |
| `C01zXz` | Low sexual desire | | |  | pending | | |
| `C020XA` | Difficulties with arousal | | |  | pending | | |
| `C021Q0` | Low orgasmic function | | |  | pending | | |
| `C022PW` | Sex-related distress | | |  | pending | | |
| `C0237W` | Decreased need for sleep | | |  | pending | | |
| `C024WG` | Physiological anxiety | | |  | pending | | |
| `C025ex` | Health/Illness anxiety | | |  | pending | | |
| `T026cQ` | Peculiarity | | |  | pending | | |
| `C0277d` | Reality distortion | | |  | pending | | |
| `T028jy` | Emotional detachment | | |  | pending | | |
| `T029jr` | Social withdrawal | | |  | pending | | |
| `T02A06` | Romantic disinterest | | |  | pending | | |
| `C02BO8` | Inattention | | |  | pending | | |
| `C02CiQ` | Destruction of property | | |  | pending | | |
| `C02DSC` | Exhibitionism | | |  | pending | | |
| `U0012Y` | Sexual Problems | | |  | pending | | |
| `U002SC` | Eating Pathology | | |  | pending | | |
| `U0036N` | Fear | | |  | pending | | |
| `U004dm` | Distress | | |  | pending | | |
| `U0050q` | Mania | | |  | pending | | |
| `U0061L` | Harmful Substance Abuse | | |  | pending | | |
| `U007EJ` | Antisocial Behavior | | |  | pending | | |
| `0004KV` | Version | | |  | pending | | |

## 6. Regeln für neue Einträge

1. Jede Zeile in Teil B MUSS genau einen `HiTOP-Code` beschreiben. Für jeden
   Code, der klinisch reviewt wird (`CLIN-C1-01`), MUSS es genau eine Zeile
   in Teil B geben — auch wenn `status: pending`.
2. Bevor ein `citation_key` in Teil B verwendet wird, MUSS er zuerst in
   Teil A angelegt werden.
3. Zeilen werden nie kommentarlos gelöscht. Ändert sich die Quellenlage,
   wird `Anmerkung` ergänzt und `status` angepasst; der Verlauf bleibt über
   Git-Historie nachvollziehbar.
4. Wenn ein Konzept aus mehreren Quellen zusammengeführt wurde (z. B.
   ursprüngliches Modell plus spätere Aktualisierung eines Spektrums),
   MÜSSEN alle relevanten `citation_key`-Werte eingetragen werden, nicht nur
   der aktuellste.
5. Gibt es keine passende externe Quelle (z. B. für ein rein strukturelles
   Hilfskonzept ohne eigene HiTOP-Literatur), wird `status: excluded` gesetzt
   und der Grund in `Anmerkung` genannt — das Feld bleibt nicht einfach leer.
