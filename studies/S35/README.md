# S35 — Demand response: shifting peak load or moving the problem?

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A utility wants to know whether time-varying prices reduce peak usage or merely shift it into adjacent periods. Estimate heterogeneous load changes and rebound patterns under the London tariff trial's documented assignment process.

## Proposed data

[Low Carbon London SmartMeter data](https://data.london.gov.uk/dataset/smartmeter-energy-consumption-data-in-london-households-vqm0d) — UK Power Networks / London Datastore. Actual files, release and publication rights require inspection before evaluation.

## Research design

Join household half-hourly consumption with the supplied 2013 price-signal calendar. Audit recruitment, group assignment and pre-period comparability before selecting the estimand. Use randomized assignment analysis only if verified; otherwise use household/time panel models and difference-in-differences with explicit identifying assumptions.

## Theory

Intertemporal substitution predicts that customers can move consumption between periods. Difference-in-differences requires credible parallel trends and absence of competing group-specific changes; randomized assignment supports intention-to-treat effects only under the documented design. Rebound affects net energy and peak-reduction conclusions.

## Evaluation design

Predefine event windows, peak and adjacent-period outcomes. Compare with flat-tariff households, inspect pre-trends/placebo windows, cluster uncertainty by household and price event as appropriate, and assess heterogeneous effects using held-out households.

## Intended interaction

Visitors choose a price event, household segment and time window. An event-study curve shows observed/estimated consumption changes and rebound; a separate scenario panel explores hypothetical event frequency without claiming an observed new tariff effect.

## Limits

A tariff-group label alone does not establish random assignment. If design documentation is insufficient, publish adjusted associations and sensitivity analyses rather than causal savings claims.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
