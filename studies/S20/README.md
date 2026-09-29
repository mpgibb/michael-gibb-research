# S20 — Trial completion risk from information available at registration

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A clinical-development operations team must anticipate prolonged or unsuccessful trial execution. Study whether registration-time design and enrollment characteristics predict completion timing and early termination.

## Proposed data

[ClinicalTrials.gov study records](https://clinicaltrials.gov/data-api/api) — NIH / National Library of Medicine. Actual files, release and publication rights require inspection before evaluation.

## Research design

Define a cohort by registration period and study type. Reconstruct fields as recorded at registration using accessible record history or dated snapshots; do not use later actual enrollment or revised completion dates as baseline predictors. Fit competing-event models for completion and termination, retaining ongoing trials as censored.

## Theory

Competing-risks analysis recognizes that termination prevents the intended completion event. Survival likelihoods handle incomplete follow-up; informative reporting delays and amendments can bias both event times and predictors. This is an operations forecast, not an efficacy comparison.

## Evaluation design

Use later registration cohorts as holdouts, allowing adequate follow-up. Compare simple phase/design strata with regularized survival models. Report horizon-specific calibration, censoring-adjusted Brier scores, event counts and sensitivity to status-reporting lag.

## Intended interaction

Visitors choose a trial-design profile and follow-up horizon. Cumulative completion/termination curves and uncertainty bands appear beside a record-history timeline explaining what was known when.

## Limits

Current registry records alone cannot support a leakage-free registration-time forecast. If history cannot be recovered, deliver a retrospective association study and label it accordingly; registry completion is not scientific success.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
