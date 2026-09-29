# S43 — Chicago-area property valuation with honest geographic uncertainty

Status: evaluated. Run `S43-a92f1ea2-98e410fd` evaluates 24,551 later sales using a fixed pre-sale characteristics snapshot. Spatial boosting does not establish a clear gain over regularized hedonic regression, and countywide interval coverage hides substantial local gaps. See [REPORT.md](REPORT.md).

## Decision

A real-estate analytics team must distinguish predictable property value from uncertainty caused by sparse local comparables. Test whether flexible spatial models improve sale-price estimates without hiding neighborhood-level error.

## Inspected data

[Cook County Assessor parcel sales and characteristics](https://datacatalog.cookcountyil.gov/stories/s/Assessor-2025-Open-Data-Refresh/gzdr-q7c4/) — Cook County Assessor's Office. The April 2024 characteristic snapshot predates every included sale. [DATA.md](DATA.md) records source conditions, join grain and frozen checksums.

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

## Reproduce

Run `uv sync --frozen`, then `RESEARCH_DATA_DIR=/absolute/path/to/data uv run python -W error studies/S43/study.py` and `uv run python scripts/report_s43.py`. The mutable source API must match the pinned monthly checksums. Raw data remain external. [PROTOCOL.md](PROTOCOL.md) describes the calendar, spatial and parcel stress tests.
