# S41 — Short-term rental positioning without invented occupancy

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A hospitality market analyst wants to understand which listing features and neighborhoods are associated with asking-price differences. Build a reliable comparison tool that distinguishes a listing's advertised position from actual booking performance.

## Proposed data

[Inside Airbnb](https://insideairbnb.com/get-the-data/) — Inside Airbnb project. Actual files, release and publication rights require inspection before evaluation.

## Research design

Choose a city and reproducible snapshot set; normalize currency, minimum-stay rules and listing types. Fit a spatial hedonic model and a quantile-boosting challenger to advertised nightly prices. Group repeated listings across splits and use coarse location features with spatial-block validation.

## Theory

Hedonic pricing decomposes observed price differences into associations with attributes. Spatial dependence makes neighboring listings less independent; quantile models reveal market segments hidden by average-price estimates. Selection into listing and strategic pricing prevent causal amenity valuations.

## Evaluation design

Compare neighborhood/type medians with model predictions on later snapshots and held-out spatial blocks. Report absolute/log-price error, interval coverage and stability after outlier filtering. Audit calendar availability as a separate recorded field rather than converting it into observed occupancy.

## Intended interaction

Visitors choose neighborhood, property type and supported amenities. A comparable-listings distribution and asking-price band show where a profile sits in the market; assumptions and snapshot date remain visible.

## Limits

Unavailable calendar nights may be booked or blocked. Do not claim measured occupancy, annual rental yield or causal revenue gains from amenities; location and host details should remain appropriately aggregated.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
