# S05 — How fragile is multi-touch attribution?

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A growth team wants to understand how campaign-credit rules change with attribution windows and incomplete journeys. Study whether sequence-aware conversion forecasts improve prediction and whether channel/touch credit is stable enough to inform further experiments.

## Proposed data

[Criteo Attribution Modeling for Bidding](https://ailab.criteo.com/criteo-attribution-modeling-bidding-dataset/) — Criteo AI Lab. Actual files, release and publication rights require inspection before evaluation.

## Research design

Reconstruct eligible user journeys from timestamped impressions and clicks. Compare last-touch and time-decay summaries with a discrete-time conversion-hazard model and a compact sequence model. Apply the same observation and conversion windows across methods; use only available anonymized touch identifiers.

## Theory

Survival analysis handles time until conversion and right censoring. Markov-removal or Shapley-style attribution distributes a model's predicted value across observed inputs; it does not identify the causal effect of removing an advertising channel.

## Evaluation design

Use chronological cutoffs, a gap for delayed conversions and user-grouped sensitivity checks. Report log loss, calibration, time-to-conversion error where identifiable, and credit-rank stability under window changes, touch deletion and identity fragmentation. Compare to a no-history baseline.

## Intended interaction

An attribution laboratory lets visitors change the lookback window and attribution method. A journey diagram and credit waterfall update alongside held-out predictive performance and a credit-stability chart. A separate panel suggests which disagreements warrant randomized incrementality tests.

## Limits

Thirty days of observational, anonymized advertising records do not reveal causal channel lift. Do not convert attribution credit into verified incremental ROAS or invent absent spend fields.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
