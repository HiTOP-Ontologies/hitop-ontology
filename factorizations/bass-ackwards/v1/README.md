# Bass-Ackwards Structure — v1 (V10bak)

Status: **active**

## What this is

A factorization is a specific, versioned composition of stable HiTOP base
concepts from the shared core ontology (`ontology/hitop.rdf`), expressed as
a recursive hierarchy tree. This factorization tracks a HiTOP factor
structure derived via the bass-ackwards method (hierarchical cross-level
factor comparison), based on [Kerber et al. (2024), Translational
Psychiatry](https://doi.org/10.1038/s41398-024-03046-z).

This directory was previously a standalone repository
(`hitop-bassackwards`) and has been consolidated into `hitop-ontology`. See
[`docs/factorizations.md`](../../../docs/factorizations.md) for why
factorizations live here, how versioning works, and how to add a new
version.

## Contents

| File | Purpose |
| --- | --- |
| [`V10bak_hierarchy.yaml`](V10bak_hierarchy.yaml) | Reviewed hierarchy, provenance, and the referenced ontology version |
| `V10bak_factorization.rdf`, `.ttl`, `.owl` | Generated factorization ontology; regenerate from YAML |
| `V10bak_diagram.json` | Generated diagram data |

## Status

`meta.status` is `active`. The populated hierarchy has been manually reviewed
and passed schema, structural, core-code, local-identity, bridge, and generation
checks. Partial mappings and bridges are retained in the generated artifacts.
