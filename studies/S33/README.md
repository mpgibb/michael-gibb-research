# S33 — Longevity assumptions and long-horizon liability sensitivity

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A benefits or insurance planning team must understand how mortality assumptions affect a long-duration payment obligation. Quantify sensitivity to table choice, longevity improvement and discount rates without pretending the tables are individual training records.

## Proposed data

[Mortality and Other Rate Tables (MORT)](https://mort.soa.org/) — Society of Actuaries. Actual files, release and publication rights require inspection before evaluation.

## Research design

Select compatible SOA tables with clear population, vintage and select/ultimate or generational definitions. Convert death probabilities into survival curves and expected payment streams. Apply a clearly synthetic cohort of ages and benefits, then compare deterministic and explicitly assumed stochastic improvement scenarios.

## Theory

Life-contingent valuation discounts payments weighted by survival probabilities. Period and cohort mortality describe different objects. Sensitivity and scenario decomposition identify which assumptions drive liability variation; stochastic uncertainty is not estimable from a rate table alone.

## Evaluation design

Check survival monotonicity, probability identities and actuarial present values against hand-calculated cases. Compare suitable table vintages and run rate/improvement stress grids. Do not report predictive accuracy without separate death and exposure observations.

## Intended interaction

Visitors choose cohort age, table, discount rate and mortality-improvement assumption. Survival curves, expected payment timing and a liability sensitivity surface update; a decomposition attributes differences to table and financial assumptions.

## Limits

This is a transparent scenario engine using published rates and synthetic obligations. It is not a fitted individual mortality model, an audited reserve calculation or a validated forecast of future longevity.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
