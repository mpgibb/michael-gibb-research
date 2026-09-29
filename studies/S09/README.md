# S09 — Developer ecosystem health beyond star counts

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A developer-platform or open-source program leader needs to distinguish brief attention from durable participation. Predict repeat contribution and contributor concentration from early public activity patterns.

## Proposed data

[GH Archive](https://www.gharchive.org/) — GH Archive project. Actual files, release and publication rights require inspection before evaluation.

## Research design

Construct repository and contributor cohorts from documented public event types. Define a qualifying contribution and a future return window in advance; exclude obvious automation in a sensitivity analysis. Model time to the next qualifying contribution with survival models and repository-level partial pooling.

## Theory

Survival analysis handles contributors whose return has not yet been observed. Cohort analysis separates tenure from calendar effects; hierarchical estimates avoid overreacting to tiny repositories. Concentration metrics describe dependency on a small contributor base without pretending to measure employee productivity.

## Evaluation design

Train on earlier cohorts and evaluate later cohorts, with a repository-held-out stress test. Compare against stars, recent event count and simple recency. Report return-risk calibration, time-dependent prediction error and sensitivity to bot rules and archive coverage.

## Intended interaction

Visitors choose project age, community size and return horizon. Cohort-retention curves, a contribution-concentration plot and a forecast band show how activity quality differs from headline popularity.

## Limits

Public GitHub activity excludes private work and paid usage. It cannot establish software sales, organization-wide productivity or the causal effect of community initiatives.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
