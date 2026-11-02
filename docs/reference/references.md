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

Each entry was verified against its DOI registry (Crossref or DataCite) or,
for the working model, the publisher page:

| citation_key | Full reference | DOI/URL | Coverage |
| --- | --- | --- | --- |
| `kotov2017` | Kotov R, Krueger RF, Watson D, Achenbach TM, Althoff RR, Bagby RM, et al. The Hierarchical Taxonomy of Psychopathology (HiTOP): a dimensional alternative to traditional nosologies. J Abnorm Psychol. 2017;126(4):454-77. | https://doi.org/10.1037/abn0000258 | Founding description of the complete HiTOP model and its hierarchical levels. |
| `kotov2020` | Kotov R, Jonas KG, Carpenter WT, Dretsch MN, Eaton NR, Forbes MK, et al. Validity and utility of Hierarchical Taxonomy of Psychopathology (HiTOP): I. Psychosis superspectrum. World Psychiatry. 2020;19(2):151-72. | https://doi.org/10.1002/wps.20730 | Psychosis superspectrum (thought disorder and detachment spectra); source of factorization `V10749`. |
| `krueger2021` | Krueger RF, Hobbs KA, Conway CC, Dick DM, Dretsch MN, Eaton NR, et al. Validity and utility of Hierarchical Taxonomy of Psychopathology (HiTOP): II. Externalizing superspectrum. World Psychiatry. 2021;20(2):171-93. | https://doi.org/10.1002/wps.20844 | Externalizing superspectrum (disinhibited and antagonistic externalizing); source of factorization `V108kx`. |
| `watson2022` | Watson D, Levin-Aspenson HF, Waszczuk MA, Conway CC, Dalgleish T, Dretsch MN, et al. Validity and utility of Hierarchical Taxonomy of Psychopathology (HiTOP): III. Emotional dysfunction superspectrum. World Psychiatry. 2022;21(1):26-54. | https://doi.org/10.1002/wps.20943 | Emotional dysfunction superspectrum (internalizing, somatoform, eating pathology, sexual problems, mania); source of factorization `V106mv`. |
| `kerber2024` | Kerber A, Ehrenthal JC, Zimmermann J, Remmers C, Nolte T, Wendt LP, et al. Examining the role of personality functioning in a hierarchical taxonomy of psychopathology using two years of ambulatory assessed data. Transl Psychiatry. 2024;14(1):340. | https://doi.org/10.1038/s41398-024-03046-z | Empirical bass-ackwards structure; source of factorization `V10bak`. |
| `woelke2025` | Woelke M, Foerstner BR, Rapp MA, Böttger SJ, Heinen-Stach D, Tschorn M. DZPG Minimum Data Set (MDS) [Internet]. OSF; 2025 [updated 2025 Oct 21; cited 2026 Nov 2]. | https://doi.org/10.17605/OSF.IO/EC9HS | DZPG Minimum Data Set; source of factorization `V10dzp`. |
| `hitop_wm` | HiTOP Consortium. Current model [Internet]. Hierarchical Taxonomy of Psychopathology; [cited 2026 Oct 23]. | https://www.hitop-system.org/current-model | Current HiTOP working model; source of factorization `V1052k` and of most core labels. |

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
| `0004KV` | Version |  |  | Structural schema class (factorization version), not a domain-specific HiTOP concept | excluded |  |  |
| `C001qy` | Conversion | hitop_wm, kotov2017 |  | Identity in: working-model; partial overlap only in: emotional-dysfunction ("Neurological") | draft |  |  |
| `C00217` | Somatization | hitop_wm, kotov2017, woelke2025 |  | Identity in: working-model, dzpg-mds | draft |  |  |
| `C0033z` | Malaise | hitop_wm, kotov2017, watson2022 |  | Identity in: working-model, emotional-dysfunction | draft |  |  |
| `C00416` | Head Pain | hitop_wm, kotov2017 |  | Identity in: working-model | draft |  |  |
| `C005Sv` | Gastrointestinal | hitop_wm, kotov2017, watson2022 |  | Identity in: working-model, emotional-dysfunction | draft |  |  |
| `C006MD` | Cognitive | hitop_wm, kotov2017 |  | Identity in: working-model | draft |  |  |
| `C00JTU` | Interactive anxiety | hitop_wm, kotov2017, watson2022, kerber2024, woelke2025 |  | Identity in: working-model, emotional-dysfunction, bass-ackwards, dzpg-mds | draft |  |  |
| `C00KL0` | Performance anxiety | hitop_wm, kotov2017, watson2022, kerber2024, woelke2025 |  | Identity in: working-model, emotional-dysfunction, bass-ackwards, dzpg-mds | draft |  |  |
| `C00LqY` | Public places | hitop_wm, kotov2017, watson2022, kerber2024, woelke2025 |  | Identity in: working-model, emotional-dysfunction, bass-ackwards, dzpg-mds | draft |  |  |
| `C00Mpl` | Enclosed spaces | hitop_wm, kotov2017, watson2022, kerber2024, woelke2025 |  | Identity in: working-model, emotional-dysfunction, bass-ackwards, dzpg-mds | draft |  |  |
| `C00N4I` | Animal phobia | hitop_wm, kotov2017, watson2022, kerber2024 |  | Identity in: working-model, emotional-dysfunction, bass-ackwards | draft |  |  |
| `C00OuR` | Situational phobia | hitop_wm, kotov2017, watson2022, kerber2024 |  | Identity in: working-model, emotional-dysfunction, bass-ackwards | draft |  |  |
| `C00Pjp` | Blood-injection-injury | hitop_wm, kotov2017, watson2022, kerber2024 |  | Identity in: working-model, emotional-dysfunction, bass-ackwards | draft |  |  |
| `C00Q1t` | Physiological panic | hitop_wm, kotov2017, watson2022, kerber2024, woelke2025 |  | Identity in: working-model, emotional-dysfunction, bass-ackwards, dzpg-mds; partial overlap only in: emotional-dysfunction ("Cardiopulmonary"), emotional-dysfunction ("Physiological anxiety") | draft |  |  |
| `C00RGy` | Psychological panic | hitop_wm, kotov2017, watson2022, kerber2024, woelke2025 |  | Identity in: working-model, emotional-dysfunction, bass-ackwards, dzpg-mds; partial overlap only in: emotional-dysfunction ("Anxiety sensitivity") | draft |  |  |
| `C00S9m` | Cleaning | hitop_wm, kotov2017, watson2022 |  | Identity in: working-model, emotional-dysfunction | draft |  |  |
| `C00TgL` | Rituals | hitop_wm, kotov2017, watson2022 |  | Identity in: working-model, emotional-dysfunction | draft |  |  |
| `C00Urw` | Checking | hitop_wm, kotov2017, watson2022 |  | Identity in: working-model, emotional-dysfunction | draft |  |  |
| `C00VHv` | Dysphoria | hitop_wm, kotov2017, watson2022, kerber2024, woelke2025 |  | Identity in: working-model, emotional-dysfunction, bass-ackwards, dzpg-mds | draft |  |  |
| `C00WJc` | Lassitude | hitop_wm, kotov2017, kerber2024, woelke2025 |  | Identity in: working-model, bass-ackwards, dzpg-mds | draft |  |  |
| `C00XyI` | Anhedonia (Component) | hitop_wm, kotov2017, kerber2024 |  | Identity in: working-model, bass-ackwards | draft |  |  |
| `C00Y8j` | Insomnia | hitop_wm, kotov2017, watson2022, kerber2024 |  | Identity in: working-model, emotional-dysfunction, bass-ackwards | draft |  |  |
| `C00ZyP` | Suicidality | hitop_wm, kotov2017, watson2022 |  | Identity in: working-model, emotional-dysfunction | draft |  |  |
| `C00aMF` | Agitation | hitop_wm, kotov2017 |  | Identity in: working-model | draft |  |  |
| `C00bEx` | Retardation | hitop_wm, kotov2017 |  | Identity in: working-model | draft |  |  |
| `C00cSn` | Appetite loss | hitop_wm, kotov2017, woelke2025 |  | Identity in: working-model, dzpg-mds | draft |  |  |
| `C00dc1` | Appetite gain | hitop_wm, kotov2017 |  | Identity in: working-model | draft |  |  |
| `C00e0L` | (low) Wellbeing | hitop_wm, kotov2017 |  | Identity in: working-model; partial overlap only in: dzpg-mds ("Low self esteem") | draft |  |  |
| `C00fKQ` | Generalized anxiety disorder symptoms | hitop_wm, kotov2017, kerber2024, woelke2025 |  | Identity in: working-model, bass-ackwards, dzpg-mds | draft |  |  |
| `C00gvD` | Re-experiencing | hitop_wm, kotov2017 |  | Identity in: working-model | draft |  |  |
| `C00hPJ` | Avoidance | hitop_wm, kotov2017, woelke2025 |  | Identity in: working-model, dzpg-mds | draft |  |  |
| `C00iAh` | Hyperarousal | hitop_wm, kotov2017, woelke2025 |  | Identity in: working-model, dzpg-mds | draft |  |  |
| `C00jw5` | Numbing | hitop_wm, kotov2017 |  | Identity in: working-model | draft |  |  |
| `C00kEN` | Dissociation | hitop_wm, kotov2017, kotov2020, woelke2025 |  | Identity in: working-model, psychosis, dzpg-mds | draft |  |  |
| `C00l5y` | Irritability | hitop_wm, kotov2017, watson2022, woelke2025 |  | Identity in: working-model, emotional-dysfunction, dzpg-mds | draft |  |  |
| `C00mpe` | Pure obsessions | hitop_wm, kotov2017, watson2022, kerber2024 |  | Identity in: working-model, emotional-dysfunction, bass-ackwards; partial overlap only in: dzpg-mds ("OCD") | draft |  |  |
| `C00nyb` | Euphoric activation | hitop_wm, kotov2017, watson2022 |  | Identity in: working-model, emotional-dysfunction | draft |  |  |
| `C00oKM` | Hyperactive cognition | hitop_wm, kotov2017, watson2022 |  | Identity in: working-model, emotional-dysfunction | draft |  |  |
| `C00pnZ` | Reckless overconfidence | hitop_wm, kotov2017, watson2022 |  | Identity in: working-model, emotional-dysfunction | draft |  |  |
| `C00qSD` | Psychotic | hitop_wm, kotov2017, kotov2020, woelke2025 |  | Identity in: working-model, psychosis, dzpg-mds | draft |  |  |
| `C00rnS` | Disorganized | hitop_wm, kotov2017, kotov2020 |  | Identity in: working-model, psychosis | draft |  |  |
| `C00sWr` | Inexpressivity | hitop_wm, kotov2017, kotov2020 |  | Identity in: working-model, psychosis | draft |  |  |
| `C00tUQ` | Avolition | hitop_wm, kotov2017, kotov2020 |  | Identity in: working-model, psychosis | draft |  |  |
| `C01DAb` | Alcohol use | hitop_wm, kotov2017, krueger2021, kerber2024, woelke2025 |  | Identity in: working-model, externalizing, bass-ackwards, dzpg-mds | draft |  |  |
| `C01Elz` | Alcohol problems | hitop_wm, kotov2017, krueger2021 |  | Identity in: working-model, externalizing | draft |  |  |
| `C01FDy` | Marijuana use | hitop_wm, kotov2017, krueger2021, kerber2024 |  | Identity in: working-model, externalizing, bass-ackwards | draft |  |  |
| `C01GEY` | Marijuana problems | hitop_wm, kotov2017, krueger2021 |  | Identity in: working-model, externalizing | draft |  |  |
| `C01HGq` | Drug use | hitop_wm, kotov2017, krueger2021, kerber2024, woelke2025 |  | Identity in: working-model, externalizing, bass-ackwards, dzpg-mds; partial overlap only in: dzpg-mds ("Smoking") | draft |  |  |
| `C01Ip4` | Drug problems | hitop_wm, kotov2017, krueger2021, woelke2025 |  | Identity in: working-model, externalizing, dzpg-mds | draft |  |  |
| `C01JH8` | Physical aggression | hitop_wm, kotov2017, krueger2021, woelke2025 |  | Identity in: working-model, externalizing, dzpg-mds | draft |  |  |
| `C01KXo` | Destructive aggression | hitop_wm, kotov2017, krueger2021, woelke2025 |  | Identity in: working-model, externalizing, dzpg-mds | draft |  |  |
| `C01LSp` | Relational aggression | hitop_wm, kotov2017, krueger2021, woelke2025 |  | Identity in: working-model, externalizing, dzpg-mds | draft |  |  |
| `C01MjB` | Fraud | hitop_wm, kotov2017, krueger2021 |  | Identity in: working-model, externalizing | draft |  |  |
| `C01i7x` | Pain | watson2022 |  | Identity in: emotional-dysfunction | draft |  |  |
| `C01jKN` | Fatigue | watson2022 |  | Identity in: emotional-dysfunction | draft |  |  |
| `C01kKJ` | Behavioral avoidance | watson2022 |  | Identity in: emotional-dysfunction | draft |  |  |
| `C01l9M` | Body dissatisfaction | watson2022 |  | Identity in: emotional-dysfunction; partial overlap only in: bass-ackwards ("ED Thoughts") | draft |  |  |
| `C01mPz` | Binge eating | watson2022 |  | Identity in: emotional-dysfunction; partial overlap only in: bass-ackwards ("ED Bulimic"), dzpg-mds ("ED Bulimic") | draft |  |  |
| `C01nVp` | Cognitive restraint | watson2022 |  | Identity in: emotional-dysfunction | draft |  |  |
| `C01oMk` | Purging | watson2022 |  | Identity in: emotional-dysfunction | draft |  |  |
| `C01pc6` | Excessive exercise | watson2022 |  | Identity in: emotional-dysfunction | draft |  |  |
| `C01qTa` | Restricting | watson2022 |  | Identity in: emotional-dysfunction; partial overlap only in: bass-ackwards ("ED Anorectic"), dzpg-mds ("ED Anorectic") | draft |  |  |
| `C01rfi` | Muscle building | watson2022 |  | Identity in: emotional-dysfunction | draft |  |  |
| `C01s9T` | Negative attitudes toward obesity | watson2022 |  | Identity in: emotional-dysfunction | draft |  |  |
| `C01tAk` | Low sexual desire | watson2022 |  | Identity in: emotional-dysfunction | draft |  |  |
| `C01ueZ` | Difficulties with arousal | watson2022 |  | Identity in: emotional-dysfunction | draft |  |  |
| `C01vT5` | Low orgasmic function | watson2022 |  | Identity in: emotional-dysfunction | draft |  |  |
| `C01wSl` | Sex-related distress | watson2022 |  | Identity in: emotional-dysfunction | draft |  |  |
| `C01xzj` | Decreased need for sleep | watson2022 |  | Identity in: emotional-dysfunction | draft |  |  |
| `C01yno` | Health/Illness anxiety | watson2022 |  | Identity in: emotional-dysfunction | draft |  |  |
| `C01zXz` | Hyperactivity | krueger2021 |  | Identity in: externalizing | draft |  |  |
| `C020XA` | Disorganization | krueger2021 |  | Identity in: externalizing | draft |  |  |
| `F001Hw` | General Factor of Psychopathology | hitop_wm, kotov2017, kerber2024, woelke2025 |  | Identity in: working-model, bass-ackwards, dzpg-mds | draft |  |  |
| `O002sP` | Tier |  |  | Structural schema class (tier vocabulary), not a domain-specific HiTOP concept | excluded |  |  |
| `P001Y2` | Somatoform | hitop_wm, kotov2017, watson2022, kerber2024 |  | Identity in: working-model, emotional-dysfunction, bass-ackwards | draft |  |  |
| `P002nf` | Internalizing | hitop_wm, kotov2017, watson2022, kerber2024, woelke2025 |  | Identity in: working-model, emotional-dysfunction, bass-ackwards, dzpg-mds; partial overlap only in: emotional-dysfunction ("Negative emotionality") | draft |  |  |
| `P003SL` | Thought Disorder | hitop_wm, kotov2017, kotov2020, kerber2024, woelke2025 |  | Identity in: working-model, psychosis, bass-ackwards, dzpg-mds | draft |  |  |
| `P004R1` | Detachment | hitop_wm, kotov2017, kotov2020, kerber2024, woelke2025 |  | Identity in: working-model, psychosis, bass-ackwards, dzpg-mds | draft |  |  |
| `P005xY` | Disinhibited Externalizing | hitop_wm, kotov2017, krueger2021, kerber2024, woelke2025 |  | Identity in: working-model, externalizing, bass-ackwards, dzpg-mds | draft |  |  |
| `P006gM` | Antagonistic Externalizing | hitop_wm, kotov2017, krueger2021, kerber2024, woelke2025 |  | Identity in: working-model, externalizing, bass-ackwards, dzpg-mds | draft |  |  |
| `S0013h` | Externalizing | hitop_wm, kotov2017, krueger2021 |  | Identity in: working-model, externalizing | draft |  |  |
| `S002SE` | Emotional dysfunction | watson2022 |  | Identity in: emotional-dysfunction | draft |  |  |
| `S003TB` | Psychosis | kotov2020 |  | Identity in: psychosis | draft |  |  |
| `T007eM` | Anxiousness | hitop_wm, kotov2017, watson2022, woelke2025 |  | Identity in: working-model, emotional-dysfunction, dzpg-mds | draft |  |  |
| `T008mD` | Emotional lability | hitop_wm, kotov2017, watson2022, woelke2025 |  | Identity in: working-model, emotional-dysfunction, dzpg-mds | draft |  |  |
| `T0094I` | Hostility | hitop_wm, kotov2017, krueger2021, woelke2025 |  | Identity in: working-model, externalizing, dzpg-mds | draft |  |  |
| `T00A0Z` | Perseveration | hitop_wm, kotov2017 |  | Identity in: working-model | draft |  |  |
| `T00BXK` | (low) Restricted affectivity | hitop_wm, kotov2017 |  | Identity in: working-model; partial overlap only in: dzpg-mds ("Restricted affectivity"), psychosis ("Emotional detachment") | draft |  |  |
| `T00Cgy` | Separation insecurity | hitop_wm, kotov2017, watson2022 |  | Identity in: working-model, emotional-dysfunction | draft |  |  |
| `T00D42` | Submissiveness | hitop_wm, kotov2017, watson2022 |  | Identity in: working-model, emotional-dysfunction | draft |  |  |
| `T00Eht` | Identity problems | hitop_wm, kotov2017, kerber2024, woelke2025 |  | Identity in: working-model, bass-ackwards, dzpg-mds | draft |  |  |
| `T00Fe0` | Negative relationships | hitop_wm, kotov2017, kerber2024, woelke2025 |  | Identity in: working-model, bass-ackwards, dzpg-mds | draft |  |  |
| `T00G3d` | Fragility | hitop_wm, kotov2017, kerber2024, woelke2025 |  | Identity in: working-model, bass-ackwards, dzpg-mds | draft |  |  |
| `T00HCy` | Ineptitude | hitop_wm, kotov2017, kerber2024 |  | Identity in: working-model, bass-ackwards | draft |  |  |
| `T00IAT` | (low) Invulnerability | hitop_wm, kotov2017, kerber2024 |  | Identity in: working-model, bass-ackwards | draft |  |  |
| `T00ua9` | Eccentricity | hitop_wm, kotov2017, kotov2020 |  | Identity in: working-model, psychosis | draft |  |  |
| `T00vjR` | Cognitive dysregulation | hitop_wm, kotov2017 |  | Identity in: working-model | draft |  |  |
| `T00wk6` | Unusual beliefs and experiences | hitop_wm, kotov2017, kotov2020, woelke2025 |  | Identity in: working-model, psychosis, dzpg-mds | draft |  |  |
| `T00xLn` | Fantasy proneness | hitop_wm, kotov2017, kotov2020 |  | Identity in: working-model, psychosis | draft |  |  |
| `T00yfU` | Depressivity | hitop_wm, kotov2017, watson2022 |  | Identity in: working-model, emotional-dysfunction | draft |  |  |
| `T00zDk` | Intimacy avoidance | hitop_wm, kotov2017, woelke2025 |  | Identity in: working-model, dzpg-mds; partial overlap only in: psychosis ("Romantic disinterest") | draft |  |  |
| `T010c6` | Suspiciousness | hitop_wm, kotov2017, krueger2021 |  | Identity in: working-model, externalizing | draft |  |  |
| `T011K6` | Withdrawal | hitop_wm, kotov2017, kotov2020, woelke2025 |  | Identity in: working-model, psychosis, dzpg-mds | draft |  |  |
| `T012QL` | Interpersonal passivity | hitop_wm, kotov2017 |  | Identity in: working-model | draft |  |  |
| `T013F1` | Disaffiliativeness | hitop_wm, kotov2017, woelke2025 |  | Identity in: working-model, dzpg-mds | draft |  |  |
| `T014BA` | (low) Attention seeking | hitop_wm, kotov2017 |  | Identity in: working-model | draft |  |  |
| `T015o8` | Problematic impulsivity | hitop_wm, kotov2017, krueger2021, woelke2025 |  | Identity in: working-model, externalizing, dzpg-mds | draft |  |  |
| `T016k0` | Irresponsibility | hitop_wm, kotov2017, krueger2021 |  | Identity in: working-model, externalizing | draft |  |  |
| `T0177S` | Theft | hitop_wm, kotov2017, krueger2021 |  | Identity in: working-model, externalizing | draft |  |  |
| `T018ir` | Distractibility | hitop_wm, kotov2017, krueger2021, woelke2025 |  | Identity in: working-model, externalizing, dzpg-mds; partial overlap only in: externalizing ("Inattention") | draft |  |  |
| `T019Cj` | Risk taking | hitop_wm, kotov2017, krueger2021, woelke2025 |  | Identity in: working-model, externalizing, dzpg-mds | draft |  |  |
| `T01A5i` | (low) Rigid perfectionism | hitop_wm, kotov2017 |  | Identity in: working-model; partial overlap only in: externalizing ("(Low) Perfectionism") | draft |  |  |
| `T01BfQ` | (low) Ruminative deliberation | hitop_wm, kotov2017 |  | Identity in: working-model | draft |  |  |
| `T01C1W` | (low) Workaholism | hitop_wm, kotov2017, krueger2021 |  | Identity in: working-model, externalizing | draft |  |  |
| `T01Neb` | Impatient urgency | hitop_wm, kotov2017 |  | Identity in: working-model | draft |  |  |
| `T01OY2` | (low) Planful control | hitop_wm, kotov2017 |  | Identity in: working-model | draft |  |  |
| `T01PMW` | (low) Dependability | hitop_wm, kotov2017 |  | Identity in: working-model | draft |  |  |
| `T01QNN` | Alienation | hitop_wm, kotov2017 |  | Identity in: working-model | draft |  |  |
| `T01RYG` | Boredom proneness | hitop_wm, kotov2017 |  | Identity in: working-model | draft |  |  |
| `T01SYW` | Blame externalization | hitop_wm, kotov2017 |  | Identity in: working-model | draft |  |  |
| `T01T3u` | (low) Honesty | hitop_wm, kotov2017 |  | Identity in: working-model | draft |  |  |
| `T01UGN` | Rebelliousness | hitop_wm, kotov2017 |  | Identity in: working-model | draft |  |  |
| `T01VXq` | (low) Empathy | hitop_wm, kotov2017 |  | Identity in: working-model | draft |  |  |
| `T01W1E` | Excitement seeking | hitop_wm, kotov2017, woelke2025 |  | Identity in: working-model, dzpg-mds | draft |  |  |
| `T01XQi` | Attention seeking | hitop_wm, kotov2017, krueger2021 |  | Identity in: working-model, externalizing | draft |  |  |
| `T01Y7w` | Callousness | hitop_wm, kotov2017, krueger2021 |  | Identity in: working-model, externalizing | draft |  |  |
| `T01Ziz` | Deceitfulness | hitop_wm, kotov2017, krueger2021, woelke2025 |  | Identity in: working-model, externalizing, dzpg-mds | draft |  |  |
| `T01a7u` | Grandiosity | hitop_wm, kotov2017, krueger2021, woelke2025 |  | Identity in: working-model, externalizing, dzpg-mds | draft |  |  |
| `T01bz7` | Manipulativeness | hitop_wm, kotov2017, krueger2021, woelke2025 |  | Identity in: working-model, externalizing, dzpg-mds | draft |  |  |
| `T01cX5` | Rudeness | hitop_wm, kotov2017, krueger2021 |  | Identity in: working-model, externalizing | draft |  |  |
| `T01d9I` | Egocentricity | hitop_wm, kotov2017 |  | Identity in: working-model | draft |  |  |
| `T01eG6` | Dominance | hitop_wm, kotov2017, krueger2021 |  | Identity in: working-model, externalizing | draft |  |  |
| `T01fc8` | Flirtatiousness | hitop_wm, kotov2017 |  | Identity in: working-model | draft |  |  |
| `T01gKP` | (low) Timorousness | hitop_wm, kotov2017 |  | Identity in: working-model | draft |  |  |
| `T01hQc` | Anhedonia (Trait) | hitop_wm, kotov2017, kotov2020, woelke2025 |  | Identity in: working-model, psychosis, dzpg-mds | draft |  |  |
| `T021iZ` | Perceptual dysregulation | hitop_wm, kotov2017, woelke2025 |  | Identity in: working-model, dzpg-mds | draft |  |  |
| `U0012Y` | Sexual Problems | hitop_wm, kotov2017, watson2022 |  | Identity in: working-model, emotional-dysfunction | draft |  |  |
| `U002SC` | Eating Pathology | hitop_wm, kotov2017, watson2022, kerber2024, woelke2025 |  | Identity in: working-model, emotional-dysfunction, bass-ackwards, dzpg-mds | draft |  |  |
| `U0036N` | Fear | hitop_wm, kotov2017, watson2022, kerber2024, woelke2025 |  | Identity in: working-model, emotional-dysfunction, bass-ackwards, dzpg-mds | draft |  |  |
| `U004dm` | Distress | hitop_wm, kotov2017, watson2022, kerber2024, woelke2025 |  | Identity in: working-model, emotional-dysfunction, bass-ackwards, dzpg-mds | draft |  |  |
| `U0050q` | Mania | hitop_wm, kotov2017, kotov2020, watson2022, kerber2024 |  | Identity in: working-model, psychosis, emotional-dysfunction, bass-ackwards | draft |  |  |
| `U0061L` | Harmful Substance Use | hitop_wm, kotov2017, krueger2021, woelke2025 |  | Identity in: working-model, externalizing, dzpg-mds | draft |  |  |
| `U007EJ` | Antisocial Behavior | hitop_wm, kotov2017, krueger2021, woelke2025 |  | Identity in: working-model, externalizing, dzpg-mds | draft |  |  |

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
