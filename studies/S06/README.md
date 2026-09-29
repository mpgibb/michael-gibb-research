# S06 — The accuracy–latency frontier in ad prediction

Status: planned. No analysis has been run and no finding is claimed.

## Decision

An advertising platform must score high-volume traffic within a serving budget. Determine which model delivers the best calibrated click predictions per unit of memory, latency and training cost.

## Proposed data

[Criteo 1TB Click Logs](https://ailab.criteo.com/download-criteo-1tb-click-logs-dataset/) — Criteo AI Lab. Actual files, release and publication rights require inspection before evaluation.

## Research design

Use a documented chronological subset first, then a larger scale tier. Compare hashed logistic regression, a factorization machine and one nonlinear interaction model. Keep feature transformations identical where possible; handle unseen categories and changing feature frequencies explicitly.

## Theory

Logistic loss is a proper scoring rule for probability estimation. Factorization machines approximate sparse pairwise interactions through low-rank representations. Pareto optimization recognizes that no single model necessarily dominates accuracy, memory footprint and serving latency.

## Evaluation design

Hold out later daily files. Measure log loss, precision-recall performance, calibration, peak memory, throughput and p50/p95 latency under a fixed hardware and batch-size protocol. Compare sample-size scaling and ablate interaction features; include cold-start and drift slices.

## Intended interaction

Visitors set a latency ceiling and memory limit, then select model and data scale. A Pareto plot filters feasible models; calibration curves and benchmark cards show measured hardware, model size and reproducible run identifiers.

## Limits

Click labels do not measure incremental sales or advertising profit. Report measured benchmark compute costs separately from extrapolated production costs; do not download or train on the full terabyte by default.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
