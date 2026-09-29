# S04 — Incremental advertising under a fixed contact budget

Status: corrected data inspected and evaluation protocol frozen. No evaluated finding is claimed.

## Decision

A marketing leader wants to reach people whose behavior changes because of advertising. Test whether treatment-effect targeting outperforms response-probability targeting at the same contact capacity.

## Proposed data

[Criteo Uplift](https://ailab.criteo.com/criteo-uplift-prediction-dataset/) — Criteo AI Lab. Actual files, release and publication rights require inspection before evaluation.

## Research design

Pin Criteo's corrected uplift release and audit assignment, sampling and eligible features. Estimate conditional treatment effects with a cross-fitted doubly robust learner and an honest causal forest. Use assigned treatment for intention-to-treat analysis; exclude realized exposure as a post-treatment predictor.

## Theory

Potential outcomes define the effect as E[Y(1)-Y(0)|X]. Random assignment supports identification within the documented benchmark design; overlap and sampling mechanisms still matter. Policy evaluation must use outcomes on untouched data, not the sum of the model's own selected uplift predictions.

## Evaluation design

Reserve an independent evaluation split. Compare random allocation, treat-all/treat-none and response targeting using treatment-control policy contrasts or doubly robust policy value, with confidence intervals and uplift calibration. Show budget-specific uncertainty rather than AUROC alone.

## Intended interaction

A budget slider updates the targeting frontier, estimated incremental conversions and uncertainty. Users compare response versus uplift targeting and optionally add an assumed conversion value and contact cost to inspect hypothetical net value.

## Limits

The original release had leakage; privacy subsampling prevents recovery of original advertiser economics. Confirm identification for the chosen release and label all effects as benchmark-population estimates, never advertiser ROI.

## Reproduce

Run `uv sync --frozen`, then `RESEARCH_DATA_DIR=/absolute/path/to/data uv run python -W error studies/S04/study.py`. The pinned publisher download and all individual records stay in the external S04 cache. See [DATA.md](DATA.md) for access and sampling limits, and [PROTOCOL.md](PROTOCOL.md) for the fixed comparisons. A result is published only after execution and checks.
