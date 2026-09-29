# S46 — Balancing retention and expansion in a telecom contact queue

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A telecom commercial team must allocate limited contact capacity across churn risk, product appetite and upsell likelihood. Test whether a shared predictive representation improves the three outcomes and clarifies tradeoffs between objectives.

## Proposed data

[Orange KDD Cup 2009](https://www.kdd.org/kdd-cup/view/kdd-cup-2009/Data) — Orange / ACM SIGKDD. Actual files, release and publication rights require inspection before evaluation.

## Research design

Use the documented Orange KDD Cup targets and a manageable feature subset before scaling. Compare three independent regularized/boosted models with a shared multi-task representation. Audit missingness and anonymized features; calibrate each target separately and retain the official held-out protocol where labels are available.

## Theory

Multi-task learning can borrow signal across related outcomes but may cause negative transfer. Constrained optimization combines calibrated probabilities with explicit objective weights and contact limits. Outcome likelihood is not the incremental effect of offering a particular product or retention incentive.

## Evaluation design

Use nested development splits and an untouched customer test; do not invent timestamps. Report target-specific PR metrics, calibration, multi-task gains/losses and capacity-specific outcome capture. Test sensitivity to missing features and assumed value weights.

## Intended interaction

Visitors divide a hypothetical contact budget between retention and expansion objectives. A frontier shows tradeoffs in observed target capture, alongside calibration and the assumptions behind any modeled economic value.

## Limits

Anonymous benchmark features limit business explanation. These labels do not identify causal offer response, actual revenue or a production-ready next-best-action policy; synthetic value assumptions must be clearly labeled.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
