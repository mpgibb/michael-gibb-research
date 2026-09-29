# S43 — Chicago-area property valuation with honest geographic uncertainty

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A real-estate analytics team must distinguish predictable property value from uncertainty caused by sparse local comparables. Test whether flexible spatial models improve sale-price estimates without hiding neighborhood-level error.

## Proposed data

[Cook County Assessor parcel sales and characteristics](https://datacatalog.cookcountyil.gov/stories/s/Assessor-2025-Open-Data-Refresh/gzdr-q7c4/) — Cook County Assessor's Office. Actual files, release and publication rights require inspection before evaluation.

## Research design

Join valid Cook County sales to property characteristics using parcel identifiers and information available before sale. Audit non-market transactions, repeat sales and assessment timing. Compare a hedonic regression with boosted/spatial models; calibrate prediction intervals on separate data.

## Theory

Hedonic models explain value through property attributes, while spatial dependence captures location effects. Partial pooling stabilizes sparse areas. Conformal-style intervals need explicit calibration assumptions; spatial and temporal dependence mean empirical local coverage must be examined rather than assumed.

## Evaluation design

Use forward sale-date holdouts, spatial blocks and a parcel-unseen stress test. Report median absolute percentage error, log-price error and interval coverage by geography/value tier. Compare to local comparable-sale medians and a carefully timed assessment baseline only if eligible.

## Intended interaction

A Chicago-area map lets visitors choose an aggregate neighborhood, property profile and confidence level. It shows the price distribution, comparable evidence, interval width and local holdout performance rather than a falsely precise single valuation.

## Limits

This is research on historical sales, not an appraisal. Avoid buyer/seller details, future assessments and unsupported extrapolation to unusual properties; a model interval is not a guarantee of a sale price.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
