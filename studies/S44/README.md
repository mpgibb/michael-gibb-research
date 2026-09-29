# S44 — Housing-market forecasts that acknowledge revisions and turning points

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A property strategy team needs to compare regional rent and home-value trajectories without treating estimated indices as executable investment returns. Test whether pooled models detect changing momentum better than simple trend extrapolation.

## Proposed data

[Zillow Research housing data](https://www.zillow.com/research/data/) — Zillow Research. Actual files, release and publication rights require inspection before evaluation.

## Research design

Select stable ZHVI/ZORI regional series with documented methodology and available vintages. Compare local trend/seasonal models with a dynamic-factor or pooled forecasting model. Use lagged regional indicators from the same release; introduce outside macro series only with explicit as-of publication alignment.

## Theory

Dynamic-factor models share common market movements while allowing local deviations. Regime changes challenge stable trend extrapolation. Real-time forecasting is about information available at the issue date; revised historical values can produce optimistic backtests.

## Evaluation design

Use rolling 3-, 6- and 12-month horizons. Report scaled error, directional accuracy, interval coverage and performance around turning points. Compare original-vintage and latest-revised backtests where possible; otherwise label the exercise a revised-data retrospective forecast.

## Intended interaction

Visitors choose regions, forecast origin and horizon. Indexed trajectories and fan charts reveal dispersion; a vintage toggle, where supported, shows how revisions alter the apparent historical forecast quality.

## Limits

Regional indices are modeled aggregates, not individual asset returns, rental cash flows or buy/sell recommendations. Historical revision awareness does not remove uncertainty about future structural changes.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
