# S30 — Credit-risk decisions when calibration matters more than a leaderboard

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A risk analytics leader must understand how probability errors affect a hypothetical review policy. Compare interpretable and flexible default models under asymmetric error costs and limited manual-review capacity.

## Proposed data

[Default of Credit Card Clients](https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients) — UCI / original Taiwan study authors. Actual files, release and publication rights require inspection before evaluation.

## Research design

Use the available repayment, bill and payment history to predict the provided next-month default outcome. Fit logistic and monotone/additive baselines plus boosted trees. Reserve an untouched customer-level test set, calibrate on separate validation data and document feature timing.

## Theory

Expected-loss decisions depend on calibrated probabilities and assumed loss given default, not classification accuracy alone. Proper scoring rules evaluate probability quality. Threshold optimization is conditional on costs, population prevalence and the intervention's meaning.

## Evaluation design

Use nested development folds and the fixed test set; do not invent a temporal holdout absent multiple cohorts. Report Brier score, log loss, calibration by risk band, PR performance and decision-cost sensitivity. Analyze subgroup errors without making automatic individual lending decisions.

## Intended interaction

Visitors set a manual-review budget and hypothetical error costs. Calibration plots, observed test defaults captured and a modeled loss frontier show when the preferred model or threshold changes.

## Limits

This is an older Taiwan cohort with no prospective U.S. validation. Default prediction is not fraud detection; assumed exposure and losses must be separated from observed labels and no actual lending policy is validated.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
