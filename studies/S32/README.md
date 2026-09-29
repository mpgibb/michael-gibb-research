# S32 — Flood claims and the risk of geographic concentration

Status: planned. No analysis has been run and no finding is claimed.

## Decision

An insurer or resilience planner needs to understand tail payments and correlated geographic exposure. Estimate how claim-severity conclusions change when major flood events, coverage limits and portfolio composition are considered.

## Proposed data

[OpenFEMA NFIP Redacted Claims](https://www.fema.gov/openfema-data-page/fima-nfip-redacted-claims-v2) — FEMA. Actual files, release and publication rights require inspection before evaluation.

## Research design

Clean NFIP claim payments and dated event/geography information. Analyze severity conditional on a reported claim using hierarchical models and carefully diagnosed tail models. For incidence or expected loss per insured exposure, explicitly add compatible redacted policy data and define earned-exposure denominators first.

## Theory

Extreme-value methods model the tail above a chosen threshold; event clustering violates independent-claim assumptions. Frequency and severity are different processes. Portfolio stress tests require a stated exposure mix and event-dependence model, not simply a map of claim counts.

## Evaluation design

Hold out entire major events or event-years and geographic groups. Compare empirical severity and lognormal/Gamma baselines with tail models. Report tail quantile calibration, threshold sensitivity and event-bootstrap uncertainty; flag unsupported extrapolation beyond observed experience.

## Intended interaction

Visitors choose geography, historical event and a hypothetical exposure concentration. A severity exceedance curve and scenario-loss map update, with claims-only views clearly separated from exposure-normalized views.

## Limits

Claims alone cannot establish flood probability or claim incidence. Redacted geography, evolving limits and nominal payment amounts complicate comparisons; modeled return periods or portfolio losses need explicit additional assumptions.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
