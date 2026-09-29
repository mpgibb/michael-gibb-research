# S34 — Electricity reserve planning from probabilistic load forecasts

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A utility planning team must balance excess reserve against costly demand shortfalls. Ask whether calibrated upper-tail demand forecasts produce more reliable reserve decisions than a fixed margin above a point forecast.

## Proposed data

[EIA-930 Hourly Electric Grid Monitor](https://www.eia.gov/electricity/gridmonitor/about) — U.S. Energy Information Administration. Actual files, release and publication rights require inspection before evaluation.

## Research design

Forecast hourly balancing-authority demand at a precisely defined issue time using lagged load, calendar information and only legitimately available inputs. Compare seasonal models and quantile boosting; benchmark against published demand forecasts only when their issue time aligns with the task. Weather forecasts are an optional, separately sourced extension.

## Theory

Conditional quantiles connect directly to asymmetric shortage costs. A chance constraint sets reserve to keep modeled shortfall probability below a target. Correlated hourly errors and data revisions affect aggregate risk; point-forecast improvements do not automatically reduce shortage risk.

## Evaluation design

Use rolling seasonal holdouts and an extreme-demand stress period. Report quantile loss, interval coverage, upper-tail exceedances and modeled reserve/shortfall cost relative to fixed margins. Record data vintages; label revised-data backtests when original releases are unavailable.

## Intended interaction

Visitors set an authority, target shortfall probability and hypothetical reserve/shortage costs. A 24-hour fan chart and risk-cost frontier show the reserve implication and where historical outcomes exceeded the band.

## Limits

Demand-only reserve scenarios omit generator outages and full network/security constraints. They are not an operational dispatch plan; do not use realized future weather or mismatched official-forecast timing.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
