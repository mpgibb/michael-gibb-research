# S02 — Inventory planning with coherent demand uncertainty

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A merchandise planner must balance excess inventory against missed sales across stores and categories. Ask whether coherent probabilistic forecasts produce more reliable replenishment decisions than independent point forecasts.

## Proposed data

[M5 Walmart sales](https://github.com/Mcompetitions/M5-methods) — M5 competition organizers / Walmart. Actual files, release and publication rights require inspection before evaluation.

## Research design

Forecast 28-day product-store sales from lagged sales, calendar information and prices known at the forecast origin. Compare seasonal baselines and global gradient-boosted quantile models. Enforce consistency across store/category totals and evaluate multiple historical origins.

## Theory

Hierarchical forecasting respects aggregation identities. The newsvendor rule chooses a demand quantile based on the ratio of underage to total underage-plus-overage cost. Scenario optimization extends this rule to budget and storage constraints; forecast accuracy and decision quality are separate objectives.

## Evaluation design

Report weighted scaled error, quantile loss and interval coverage by aggregation level. Compare simple order-up-to policies against forecast-driven policies in an explicit inventory simulator. Sweep lead times, holding costs and lost-sales assumptions; report regret against a hindsight benchmark only inside that simulator.

## Intended interaction

Visitors adjust lead time, shortage cost and storage budget. Linked charts show forecast bands, the recommended inventory allocation and a simulated service-level/cost frontier, with observed-sales replay separated from assumed latent-demand scenarios.

## Limits

Recorded sales are not unconstrained demand. True stock availability and economic costs are missing; stockout reduction and dollar savings must remain simulation results.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
