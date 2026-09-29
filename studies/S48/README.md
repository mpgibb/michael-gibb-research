# S48 — Urban telecom activity and resilient capacity scenarios

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A network planning team wants to locate predictable activity peaks and unusual surges. Test whether spatial models improve short-horizon cell-grid activity forecasts and identify where a hypothetical capacity budget would be most exposed.

## Proposed data

[Telecom Italia Milan activity](https://doi.org/10.7910/DVN/EGZHFV) — Telecom Italia / original Scientific Data authors. Actual files, release and publication rights require inspection before evaluation.

## Research design

Build time-aligned Milan grid series for the released activity measures. Compare seasonal baselines, spatially pooled models and a graph-temporal challenger. Define adjacency from the documented grid and preserve separate activity types; treat normalization and missing intervals explicitly.

## Theory

Spatiotemporal dependence allows neighboring regions to share predictive information. Graph regularization encodes geographic proximity, while anomaly detection separates forecast residuals from ordinary daily seasonality. Resource allocation requires a mapping from activity proxies to capacity that the dataset does not supply.

## Evaluation design

Use blocked future-day/week holdouts and selected spatial blocks. Report scaled error, peak-period quantile loss and false alerts under a defined threshold. Test the short observation period's sensitivity to unusual days and compare any allocation policies only under common simulated assumptions.

## Intended interaction

Visitors replay a time window, choose a model and set a hypothetical capacity level. A grid heatmap displays forecast bands, observed residuals and scenario overload exposure, with a clear activity-unit legend.

## Limits

Normalized grid activity is not subscriber count, bytes, tower load or dropped-call experience. The short historical period cannot validate a physical network expansion plan or annual seasonality.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
