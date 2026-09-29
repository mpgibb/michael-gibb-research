# S38 — Fleet positioning under uncertain urban trip demand

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A mobility operator needs to place a limited fleet where upcoming trips are likely. Compare fixed, historically proportional and forecast-driven allocation under explicit travel and repositioning assumptions.

## Proposed data

[NYC TLC Trip Records](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) — NYC Taxi and Limousine Commission. Actual files, release and publication rights require inspection before evaluation.

## Research design

Choose one TLC vehicle category and consistent date range. Aggregate completed trips into zone-time demand and estimate travel-time distributions from eligible historical trips. Forecast next-period observed pickups using seasonal and spatially pooled models; feed scenarios into a min-cost-flow allocation model.

## Theory

Spatial forecasting shares information across related zones. Flow conservation and vehicle availability constrain feasible positioning; stochastic optimization trades shortage risk against relocation cost. Observed fulfilled trips are a censored proxy for underlying demand when service is scarce.

## Evaluation design

Hold out later weeks and demand-shift periods. Report zone-level scaled error, interval coverage and peak-zone performance. In a clearly specified simulator, compare unmet observed-request proxies, relocation distance and modeled cost across policies; vary travel-time and fleet-size assumptions.

## Intended interaction

Visitors set fleet size, relocation penalty and forecast horizon. A zone map animates proposed allocations while a frontier shows modeled coverage versus repositioning burden, with an uncertainty overlay.

## Limits

Completed trips omit unserved requests and empty-vehicle movements. Public monthly files also have publication lag. The project is a historical fleet-planning benchmark, not a validated live dispatch system.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
