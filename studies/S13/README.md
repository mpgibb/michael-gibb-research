# S13 — Reliable quality screening with many sensors and few failures

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A manufacturing quality leader must identify high-risk units without flooding inspection capacity. Test whether a stable, compact sensor model can match a more complex classifier while controlling missed failures.

## Proposed data

[SECOM](https://archive.ics.uci.edu/dataset/179/secom) — UCI / manufacturing-process data donor. Actual files, release and publication rights require inspection before evaluation.

## Research design

Audit SECOM timestamps, missingness and duplicated/near-constant measurements. Compare elastic-net logistic regression, a PCA-based process-monitoring baseline and boosted trees. Fit imputation, scaling and feature selection entirely within training folds; include missingness indicators only when available before inspection.

## Theory

Regularization controls variance when predictors outnumber useful failure observations. Latent-factor methods model correlated process variation; stability selection asks whether selected signals persist under resampling. Cost-sensitive decision theory separates failure detection from the chosen inspection threshold.

## Evaluation design

Use time-ordered evaluation where timestamp coverage supports it, otherwise nested stratified validation with the limitation stated. Report precision-recall performance, recall at fixed inspection capacity, calibration and feature-selection stability. Quantify wide uncertainty due to the small failure count.

## Intended interaction

An inspection-budget slider updates missed-failure and unnecessary-inspection counts on held-out data. Visitors compare a sparse model with a complex one and inspect sensor-selection stability across resamples.

## Limits

Anonymous sensors prevent engineering root-cause claims. A correlated measurement is not a proven process fault, and this small historical sample does not validate deployment in a modern plant.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
