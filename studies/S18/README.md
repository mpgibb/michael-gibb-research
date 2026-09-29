# S18 — Medicare service concentration and regional market coverage

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A healthcare strategy team needs to understand service mix and dependence on a small number of providers. Identify regional concentrations and changing specialty/service patterns that merit a closer market assessment.

## Proposed data

[Medicare Physician & Other Practitioners](https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners) — CMS. Actual files, release and publication rights require inspection before evaluation.

## Research design

Construct provider-service-year panels from the public CMS aggregates. Harmonize procedure codes and geographic definitions; distinguish provider location from beneficiary residence. Use service-mix factorization or clustering plus multilevel trend models. Add compatible Medicare enrollment denominators only as an explicitly sourced extension.

## Theory

Concentration measures summarize how observed service volume is distributed across providers. Matrix factorization reveals recurring service portfolios; shrinkage stabilizes small-area trends. Ecological inference warns against translating aggregate utilization into individual access or clinical quality.

## Evaluation design

Test cluster stability across years and alternative volume definitions. Compare trend forecasts against last-year values, using later years as holdouts. Report suppression-related missingness and sensitivity to geographic boundaries and provider identifiers.

## Intended interaction

A service-market map lets visitors select procedure family, year and geographic scale. It shows observed volume, provider concentration, service-mix comparisons and forecast bands; denominator-dependent rates remain unavailable until compatible enrollment data are added.

## Limits

Original Medicare Part B is only part of the market. Provider location does not prove patient access, service volume is not clinical quality, and concentration alone does not establish market power.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
