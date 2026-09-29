# S17 — Emergency-department waiting-time inequality and uncertainty

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A healthcare operations leader wants to know which visit groups experience the longest waits and how stable those patterns are. Estimate adjusted waiting-time distributions, not just a systemwide average.

## Proposed data

[NHAMCS emergency department public-use files](https://www.cdc.gov/nchs/nhamcs/about/) — CDC / NCHS. Actual files, release and publication rights require inspection before evaluation.

## Research design

Select NHAMCS emergency-department years with comparable waiting-time, arrival and triage fields after codebook review. Use survey-weighted distributional or quantile models and a long-wait indicator model. Audit missing, capped and special-code values and distinguish visits that were never seen where identifiable.

## Theory

Quantile modeling reveals tail behavior hidden by averages. Standardization compares groups under a common measured case mix; design-based variance respects the sampled-visit structure. Adjustment does not remove unmeasured operational differences or identify causal effects.

## Evaluation design

Compare weighted empirical quantiles with adjusted estimates and leave-year-out predictions. Report uncertainty, effective sample sizes, weighted calibration and sensitivity to missing waits. Suppress unreliable fine-grained cells instead of producing precise-looking rankings.

## Intended interaction

A visit-mix explorer allows selection of triage group, arrival category and year. It displays median/tail waits, uncertainty bands and standardized comparisons. Any staffing scenario is a separate illustrative queue model with user-supplied arrival and service assumptions.

## Limits

NHAMCS is a sampled visit survey ending in 2022, not a complete hospital arrival/service log. It cannot directly calibrate a particular hospital's queue or prove staffing changes reduce waits.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
