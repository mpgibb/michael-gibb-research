# S19 — Compound selection when laboratory tests are expensive

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A discovery team must choose which compounds to test next under a limited assay budget. Evaluate whether uncertainty-aware selection finds active compounds more efficiently than random screening or choosing the largest predicted activity.

## Proposed data

[ChEMBL](https://www.ebi.ac.uk/chembl/) — EMBL-EBI. Actual files, release and publication rights require inspection before evaluation.

## Research design

Choose a well-populated ChEMBL target and a compatible endpoint. Harmonize units, assay types and duplicate compound measurements before defining the label. Compare molecular-fingerprint models with one graph-based challenger. Run retrospective active-learning rounds by revealing withheld assay labels only after a selection.

## Theory

Chemical structure provides an inductive bias for activity prediction. Bayesian/ensemble uncertainty supports an exploration-versus-exploitation tradeoff. Active learning selects informative measurements; it must distinguish epistemic model uncertainty from noisy or incompatible assays.

## Evaluation design

Use scaffold-separated and, when feasible, publication-time holdouts. Compare random, greedy and uncertainty/diversity acquisition under identical label budgets. Report hit rate, enrichment, calibration and chemical diversity; repeat acquisition trials with multiple seeds.

## Intended interaction

A screening-budget slider replays retrospective selection rounds. A chemical-space plot highlights selected compounds, uncertainty and known held-out outcomes, while a discovery curve compares acquisition strategies.

## Limits

This is retrospective selection within a measured compound pool. It does not establish clinical efficacy, safety, prospective laboratory hit rates or discovery of a new drug.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
