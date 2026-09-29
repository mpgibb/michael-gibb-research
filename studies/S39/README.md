# S39 — Chicago transit planning through structural demand changes

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A transit planning team needs a forecast that adapts when commuting patterns change. Test whether regime-aware models improve daily bus and rail boarding forecasts over a stable seasonal baseline.

## Proposed data

[CTA Daily Boarding Totals](https://data.cityofchicago.org/Transportation/CTA-Ridership-Daily-Boarding-Totals/6iiy-9s97) — Chicago Transit Authority / City of Chicago. Actual files, release and publication rights require inspection before evaluation.

## Research design

Use CTA's system-level daily bus, rail and total boarding series. Build calendar/day-type features and compare seasonal naive, dynamic regression and state-space models with change detection. Fit change points using training data only; evaluate known disruption periods as stress tests.

## Theory

State-space models allow trend and seasonal components to evolve. Structural breaks violate assumptions of stable historical relationships. Coherent aggregation keeps bus-plus-rail forecasts consistent with system totals; uncertainty should widen when a regime changes.

## Evaluation design

Use rolling 7- and 28-day forecast origins spanning stable and changing demand periods. Report scaled error, interval coverage and recovery after shifts. Compare expanding versus recent-window training and evaluate weekday/weekend performance separately.

## Intended interaction

Visitors choose a historical forecast date, horizon and adaptation speed. A Chicago-branded timeline reveals the forecast available then, subsequent actual boardings and hypothetical daily capacity thresholds.

## Limits

This specific dataset contains daily system totals, not station-hour demand or individual trips. Capacity scenarios cannot justify train-by-train staffing or prove service changes caused ridership growth without additional data.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
