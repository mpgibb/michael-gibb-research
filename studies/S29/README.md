# S29 — Mortgage application outcomes across markets and lenders

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A lending strategy and model-risk team wants to understand geographic variation in application outcomes and which differences remain after measured application characteristics are considered.

## Proposed data

[HMDA mortgage application data](https://www.consumerfinance.gov/data-research/hmda/) — CFPB / FFIEC. Actual files, release and publication rights require inspection before evaluation.

## Research design

Create comparable HMDA cohorts by year, loan purpose, product and application disposition. Keep withdrawals and incomplete files distinct from denials. Use multilevel logistic models and standardized outcome comparisons; audit privacy-modified, censored and missing fields before constructing covariates.

## Theory

Partial pooling stabilizes lender and geographic estimates. Standardization compares populations under a common distribution of observed characteristics. Selection into application and omitted underwriting variables mean adjusted group differences remain descriptive rather than identified discrimination effects.

## Evaluation design

Hold out later years and selected lenders/regions. Compare raw versus standardized differences with uncertainty, calibration and sensitivity to covariate sets. Avoid ranking tiny cells; evaluate missingness patterns and changes in reporting definitions.

## Intended interaction

A market explorer filters Chicago-area or national geographies, loan purpose and year. It shows application flows, raw/adjusted outcome differences and confidence intervals; an assumptions panel lets visitors see how the adjustment set affects conclusions.

## Limits

HMDA is not a loan-performance panel and does not contain every underwriting factor. This is an audit and research demonstration, not a legal finding of discrimination or a deployable credit-decision engine.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
