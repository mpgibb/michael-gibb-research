# S55 — Permit-process duration and project planning risk

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A construction planning team needs realistic administrative lead times before committing downstream resources. Estimate the distribution of time from a documented filing milestone to a documented permit milestone and identify where uncertainty is greatest.

## Proposed data

[NYC DOB applications and permits](https://www.nyc.gov/site/buildings/dob/building-applications-permits.page) — NYC Department of Buildings. Actual files, release and publication rights require inspection before evaluation.

## Research design

Choose a consistent DOB system and application cohort with reliable milestone dates. Separate application, job and permit identifiers, amendments and withdrawals. Fit hierarchical accelerated-failure-time or survival models using information known at the starting milestone; retain unresolved applications as censored where follow-up is observable.

## Theory

Survival models account for incomplete administrative processes; multistate reasoning distinguishes approval, withdrawal and resubmission when histories permit. Partial pooling stabilizes estimates for sparse project categories. Administrative elapsed time is different from physical construction duration.

## Evaluation design

Hold out later filing cohorts and compare with category-level historical medians. Report horizon-specific calibration, censoring-adjusted error and interval coverage. Audit missing dates, system migrations and whether the apparent endpoint is original issuance or a later revision.

## Intended interaction

Visitors select project category, borough and planning horizon. Completion-probability curves and percentile lead times show uncertainty; a scenario schedule propagates the assumed administrative start delay into an illustrative downstream plan.

## Limits

Permit dates do not identify construction completion, total project cost or the causal effect of an expediting service. If milestone history is unavailable, narrow the question to the reliably observed administrative interval.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
