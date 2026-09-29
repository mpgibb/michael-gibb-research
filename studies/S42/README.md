# S42 — Tourism capacity planning across seasons and regions

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A tourism or hospitality strategy team needs to distinguish recurring seasonality from lasting changes in demand mix. Forecast accommodation nights and identify regions or visitor segments with the greatest planning uncertainty.

## Proposed data

[Eurostat tourism accommodation statistics](https://ec.europa.eu/eurostat/web/tourism/) — Eurostat. Actual files, release and publication rights require inspection before evaluation.

## Research design

Select comparable Eurostat monthly nights/arrivals series at a supported geographic level, separating resident and nonresident demand where available. Harmonize coverage and reporting breaks. Compare seasonal baselines, dynamic regression and globally pooled probabilistic forecasts with consistent totals.

## Theory

Seasonal decomposition separates recurring patterns from trend; hierarchical forecasting respects geographic and visitor-segment aggregation. Structural breaks and varying reporting coverage limit transportability. Capacity planning translates forecast distributions into conditional resource scenarios.

## Evaluation design

Use rolling forecast origins across normal and disrupted periods. Report scaled error, quantile loss, interval coverage and peak-season bias by region. Compare simple seasonal recovery assumptions with fitted models; include missing-series and definition-change sensitivity.

## Intended interaction

Visitors choose a region, visitor segment and planning horizon. A seasonal heatmap and fan chart display uncertainty; an optional capacity slider shows modeled utilization under a transparent assumed accommodation capacity.

## Limits

Aggregate nights are not individual bookings or a hotel's revenue. Match the geography and frequency actually available; do not infer property-level occupancy or staffing needs from incompatible regional totals.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
