# References

<div class="hitop-page-intro">
  <p>A maintained structure for recording bibliographic sources and per-concept attribution for HiTOP labels and definitions.</p>
  <span class="hitop-source">Applies to · Version {{ hitop_ontology_version }} · <a href="https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/ontology/hitop.rdf">ontology/hitop.rdf</a></span>
</div>

## 1. Purpose

Each concept class in `ontology/hitop.rdf` has an `rdfs:label`, a definition
(`obo:iaoIAO_0000115` or `rdfs:comment`), and optionally a `skos:changeNote`.
This document defines how the corresponding literature source and attribution
review are recorded consistently for every core HiTOP concept.

## 2. Scope

This document covers:

- Literature sources for concept labels and definitions in the core ontology
  (Superspectrum, Spectrum, Subfactor, Component, and Trait).

This document does **not** cover:

- Mapping evidence for manifestation suffixes. That belongs in the maintained
  [mapping and harmonization specification](../concepts/mapping-harmonization.md).
- Provenance for an individual factorization, such as the source of a concrete
  hierarchy. That belongs in its
  `factorizations/<factorization-id>/v<N>/README.md`.

## 3. Structure: two linked parts

The document consists of two linked tables:

- **Part A** lists every cited source exactly once with a stable short key
  (`citation_key`).
- **Part B** assigns one or more `citation_key` values from Part A to each
  HiTOP code.

A source is never written out in full in Part B; only its key is used there.
This prevents the same source from being cited in slightly different forms.

## 4. Part A — Bibliography

| Field | Required | Meaning |
| --- | --- | --- |
| `citation_key` | Yes | Stable lowercase key in the form `<first-author><year>`, for example `kotov2017`; append `a`, `b`, and so on for multiple sources by the same author in the same year |
| `Full reference` | Yes | Complete Vancouver-style reference (authors, title, journal, year, volume, pages), matching the target Journal of Biomedical Semantics format |
| `DOI/URL` | When available | Persistent link; use a stable URL if no DOI exists, or `-` if neither exists; do not leave the field blank |
| `Coverage` | Yes | One sentence describing what the source covers, such as the complete model or an update to the Internalizing spectrum |

The initial row is intentionally neutral. Replace each placeholder only with
verified bibliographic information:

| citation_key | Full reference | DOI/URL | Coverage |
| --- | --- | --- | --- |
| - | - | - | - |

## 5. Part B — Source attribution by concept

| Field | Required | Meaning |
| --- | --- | --- |
| `HiTOP code` | Yes | `hitop_base_code` from `ontology/hitop.rdf`, for example `S0013h` |
| `Label` | Yes | Current class `rdfs:label`, included for quick comparison without opening the RDF file |
| `citation_key(s)` | Yes | One or more comma-separated keys from Part A; at least one is required unless `status: pending` |
| `Section/page` | No | Optional section, table, or page in the source where the concept is defined |
| `Note` | No | For example, a label adapted from the source or a paraphrased definition |
| `status` | Yes | One of `reviewed`, `draft`, `pending`, or `excluded`; an excluded structural concept requires a reason in `Note` |
| `reviewed by` | When `status: reviewed` | Name or initials of the person who verified the attribution |
| `Date` | When `status: reviewed` | Review date in `YYYY-MM-DD` format |

The table mirrors the classes in `ontology/hitop.rdf`; `HiTOP code` and `Label`
are copied from that source. Structural schema classes may use
`status: excluded` with a reason because they are not domain-specific HiTOP
concepts. Use `status: pending` until an attribution has been verified, and
regenerate the table whenever classes are added to or removed from the
ontology.

| HiTOP code | Label | citation_key(s) | Section/page | Note | status | reviewed by | Date |
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
| `O002sP` | Tier | | | Structural schema class (tier vocabulary from `docs/factorizations.md`), not a domain-specific HiTOP concept | excluded | | |
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
| `U0061L` | Harmful Substance Use | | |  | pending | | |
| `U007EJ` | Antisocial Behavior | | |  | pending | | |
| `0004KV` | Version | | |  | pending | | |

## 6. Rules for new entries

1. Every row in Part B MUST describe exactly one `HiTOP code`, and every code in
   the canonical ontology MUST have exactly one row, including while its status
   is `pending`.
2. A `citation_key` MUST be created in Part A before it is used in Part B.
3. Rows are never deleted without explanation. When attribution changes, update
   `Note` and `status`; Git history preserves the review trail.
4. When a concept combines multiple sources, all relevant `citation_key` values
   MUST be recorded, not only the latest one.
5. If no appropriate external source exists for a structural helper concept,
   set `status: excluded` and record the reason in `Note`.
