# S52 — Crop-yield uncertainty for procurement planning

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A food procurement team needs to anticipate regional supply variability before harvest. Test whether spatially pooled yield forecasts improve uncertainty estimates and hypothetical sourcing allocations over trend-only planning.

## Proposed data

[USDA NASS Quick Stats](https://data.nass.usda.gov/Quick_Stats/) — USDA National Agricultural Statistics Service. Actual files, release and publication rights require inspection before evaluation.

## Research design

Select one major crop and comparable NASS county/state yield series. Define a pre-harvest forecast issue date and use only information published by then. Start with historical trend and lagged yield; treat dated NOAA weather and available acreage estimates as separately documented enhancements, not assumed fields in Quick Stats.

## Theory

Hierarchical spatial models share information across similar regions while permitting local trends. Yield and harvested acreage jointly determine production, so yield forecasting alone is not supply forecasting. Stochastic procurement allocates across regional scenarios under explicit demand, price and sourcing assumptions.

## Evaluation design

Use year-forward and region-held-out tests. Compare trend, historical-average and pooled models using yield error, interval coverage and adverse-year performance. Audit suppressed/revised estimates. Evaluate procurement regret only in a simulator whose prices, capacity and demand are clearly specified.

## Intended interaction

Visitors select crop, region, forecast date and sourcing concentration. A yield-risk map and uncertainty fan show the forecast; a separate allocation panel tests hypothetical procurement diversification.

## Limits

Public aggregate estimates are not farm-level treatment data. Do not use final acreage, realized future weather or revised releases as if available before harvest, or claim causal effects of agronomic practices.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
