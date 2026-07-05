# HiTOP DZPG Minimal Data Set — v1 (V10dzp)

Status: **draft** (tree not yet populated)

## What this is

A factorization is a specific, versioned composition of stable HiTOP base
concepts from the shared core ontology (`ontology/hitop.rdf`), expressed as
a recursive hierarchy tree. This factorization tracks the DZPG "Psychische
Gesundheit Basiserfassung" minimal data set composition (see
`docs/hitop_base_vocabulary.md` and `docs/mapping-und-harmonisierung.md`
for related manifestation-level tooling used by this data set).

This directory was previously a standalone repository (`hitop-dzpg-mds`)
and has been consolidated into `hitop-ontology`. See
[`docs/factorizations.md`](../../../docs/factorizations.md) for why
factorizations live here, how versioning works, and how to add a new
version.

## Contents

| File | Purpose |
| --- | --- |
| [`V10dzp_hierarchy.yaml`](V10dzp_hierarchy.yaml) | Provenance and the ontology version this factorization will be resolved against; `hierarchy` is `null` until the tree is curated |

## Status

`hierarchy` is `null`. Populating it and moving `meta.status` from `draft`
to `active` in `V10dzp_hierarchy.yaml` is tracked as follow-up work.
