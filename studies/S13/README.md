# S13 — Reliable quality screening with many sensors and few failures

Status: evaluated. Run `S13-608719b7-eea568ba` finds weak later-month screening performance: at 20% capacity, boosting identifies 4 of 22 failures and sparse logistic identifies 3. The primary comparison is inconclusive. See [REPORT.md](REPORT.md).

## Decision

A manufacturing quality leader must identify high-risk units without flooding inspection capacity. Test whether a stable, compact sensor model can match a more complex classifier while controlling missed failures.

## Inspected data

[SECOM](https://archive.ics.uci.edu/dataset/179/secom) — UCI / manufacturing-process data donor. The actual files contain 590 sensors and 104 failures. CC BY 4.0 attribution and timing limitations are recorded in [DATA.md](DATA.md).

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

Run `uv sync --frozen`, then `RESEARCH_DATA_DIR=/absolute/path/to/data uv run python -W error studies/S13/study.py`. Run `uv run python scripts/report_s13.py` to rebuild the report and figures. Only aggregate results are published.
