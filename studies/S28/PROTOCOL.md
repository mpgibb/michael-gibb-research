# S28 evaluation protocol

Frozen before tuning or evaluation. The corresponding Git revision records this design and the executable analysis. No existing four-study simulation supplies evidence for this study.

## Decision and estimand

Rank already observed campaign contacts immediately before the call, at fixed capacity. The target is the recorded binary term-deposit subscription outcome, not the causal effect of calling. The source does not provide a fixed subsequent follow-up horizon or stable customer IDs. A record is a contact/example, not a proven independent person. Population: contacts in one historical Portuguese bank campaign, May 2008–November 2010.

## Data and information cutoff

Use the 41,188-row `bank-additional-full.csv`, explicitly ordered by date by its publisher, with the SHA-256 in config.json. Preserve source row order. Do not invent dates from month/day-of-week or treat the random 10% sample as chronological. Exclude duration universally. Exclude all five economic indicators because their release vintages at the call time cannot be established from these files. For campaign history subtract one from `campaign` because its definition includes the current call. Map `pdays=999` to a never-contacted indicator and missing elapsed days, not 999 actual elapsed days. Retain `unknown` categorical levels. Fit imputers, scaling, categories and spline knots on each allowed training prefix only.

Primary inputs are contact channel, month, weekday, earlier current-campaign call count, previous-campaign count, previous outcome, elapsed prior days and prior-contact indicator. A separately labeled sensitivity adds age, job, marital status, education, default, housing-loan and personal-loan indicators. Those attributes are not in the primary operational ranking. No model uses response labels or future records as features.

## Chronological design and comparisons

Define integer boundaries by floor(n × fraction). Development: first 70%; probability calibration: next 10%; untouched final evaluation: last 20%. Two expanding development folds train on first 40%/55% and validate on the next 15% respectively. Choose each model's configuration by mean fold log loss, with declared grid order resolving ties. The principal comparison is the model family with minimum development log loss versus the business rule; also report every prespecified family to prevent test-driven selection.

Models: regularized logistic regression, additive cubic splines plus logistic regression (five knots, additive numeric effects), and histogram gradient boosting (200 iterations, learning rate .05, L2=1, 7/15 leaves, no random early-stopping split). Logistic/spline C is .1/1. Fit on development only, then calibrate logits with a sigmoid fitted on the separate calibration block. The random-allocation baseline uses the calibration prevalence. The simple rule prioritizes previous campaign success, then prior-contact status, then recency and fewer previous current-campaign calls, with sigmoid probability calibration for proper scoring metrics. Ties keep source order. Capacity rounding uses floor(n × capacity).

## Outcomes and uncertainty

Primary metric: log loss (natural-log units) on the untouched final chronological block. Decision metric: precision and captured subscriptions at 20% capacity. Also report Brier score, AUROC, average precision, calibration bins, the 5–100% capacity frontier, and four consecutive final-evaluation subperiods. Random-allocation response count is its analytical expectation, not an observed intervention.

Use 500 paired circular moving-block bootstrap draws of 100 ordered test records for metric/decision intervals and the primary log-loss difference. Repeat the primary comparison with block lengths 50/200. Preserve adjacent records within blocks; intervals are conditional on fitted models and this observed campaign, do not include retraining uncertainty and cannot remove dependence from unknown repeated customers. Show both finite-test counts and conditional uncertainty; do not claim a population causal interval. The richer-feature challenger uses the frozen boosting complexity and the identical splits/calibration. Inspect cross-boundary exact duplicate rows as a sensitivity; do not automatically treat identical anonymized profiles as duplicate people.

## Economics and publication

Any value/cost control is an explicit scenario: value × held-out subscriptions in selected contacts − cost × selected contacts. It is not measured profit, incremental sales or a rerun of accuracy. Report the break-even assumed value per response and the selected cohort size. No raw contact records, model binaries or private local paths are published. Publish aggregate data, source citations, checksums, calibrated model comparisons, failure periods and negative findings. Independent technical review is pending.
