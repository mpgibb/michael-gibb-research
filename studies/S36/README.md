# S36 — Peak-demand prediction across heterogeneous electricity customers

Status: planned. No analysis has been run and no finding is claimed.

## Decision

An energy analytics team needs reliable peak forecasts across many customers with different load shapes. Test whether a shared model transfers useful information without sacrificing performance on unusual customers.

## Proposed data

[ElectricityLoadDiagrams20112014](https://archive.ics.uci.edu/dataset/321/electricityloaddiagrams20112014) — UCI / original data donor. Actual files, release and publication rights require inspection before evaluation.

## Research design

Build timezone-aware quarter-hourly series with explicit missing-value, zero and daylight-saving rules. Compare seasonal naive forecasts, local statistical models and a global quantile model. Cluster load shapes only within training data and evaluate whether cluster-aware models improve peak forecasting.

## Theory

Global forecasting pools information across related series, reducing estimation variance; excessive pooling can create negative transfer. Extreme-load errors matter more for capacity planning than average error. Hierarchical or clustered shrinkage mediates between a single universal model and isolated customer models.

## Evaluation design

Use rolling time holdouts plus customer-held-out transfer tests. Report scaled error, peak-window quantile loss, interval coverage and worst-decile customer performance. Compare aggregate forecasts and sensitivity to DST handling and newly active customers.

## Intended interaction

Visitors select a load-shape cohort, horizon and risk percentile. Customer and aggregate fan charts show how model choice changes peak estimates, with an optional assumed-capacity line highlighting historical exceedances.

## Limits

Customer identities and interventions are largely unknown. This benchmark cannot estimate causal tariff response or infer demographic explanations; capacity lines and operating costs are scenarios unless separately supplied.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
