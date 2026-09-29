# S01 — Customer value and promotion concentration

Status: blocked as of September 29, 2026. The publisher source page and download terms have been inspected; authorized terms acceptance and clarification of aggregate publication rights remain prerequisites. No data or model results are claimed.

Next action: complete the official access form after terms authorization, then inspect the delivered documentation, actual provenance and permitted use. The current publisher describes Source Files as representations inspired by real-world data; an uninspected download must not be presented as raw observed household records.

## Decision

A retail marketing director must decide which customer segments deserve limited campaign capacity. Test whether forward-looking customer value identifies future high-value households better than recent spending alone, while detecting dependence on discounts.

## Proposed data

[dunnhumby — The Complete Journey](https://www.dunnhumby.com/source-files/) — dunnhumby. Actual files, release and publication rights require inspection before evaluation.

## Research design

Create household-month snapshots from transactions, baskets and available promotion records. Predict next-quarter purchasing and net sales using only prior history. Model transaction frequency and basket value separately; compare a hierarchical count/spend model with gradient boosting. Track discounted and full-price purchasing as separate outcomes.

## Theory

Customer lifetime value is discounted expected future contribution, not historical revenue. Partial pooling stabilizes estimates for sparse households; a two-part model separates purchase incidence from conditional value. Apply assumed margins only in an explicitly labeled scenario layer.

## Evaluation design

Use rolling quarterly holdouts and household-clustered uncertainty. Compare against recency-frequency-monetary scoring and last-quarter sales. Report forecast error, calibration by value decile, top-budget value capture, and sensitivity to returns and discount accounting.

## Intended interaction

A campaign planner lets visitors set contact capacity, assumed contribution margin and segment. It displays observed holdout sales captured, uncertainty, discount dependence and hypothetical contribution. A household-cohort drilldown explains why a segment ranks highly.

## Limits

The frequent-shopper panel is selective. Promotion exposure is observational: the project cannot establish incremental sales caused by a coupon or prove retention ROI.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
