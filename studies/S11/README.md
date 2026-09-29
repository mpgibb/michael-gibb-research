# S11 — Delivery promises and early exception prioritization

Status: planned. No analysis has been run and no finding is claimed.

## Decision

An e-commerce operations team needs to identify orders likely to miss their delivery promise early enough to respond. Estimate both lateness probability and a delivery-time distribution at order approval.

## Proposed data

[Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) — Olist. Actual files, release and publication rights require inspection before evaluation.

## Research design

Join orders, items, seller information and coarse origin/destination geography with explicit grain checks. Use only fields available at approval; compare quantile boosting with a censoring-aware time-to-delivery model. Separate cancellation from delivery rather than treating undelivered orders as on-time.

## Theory

Quantile prediction represents asymmetric delivery risk. Survival or competing-event models distinguish delivery from unresolved/canceled orders when timestamps support it. Decision theory converts calibrated risk into a service queue under a chosen cost of late versus unnecessary alerts.

## Evaluation design

Use chronological order holdouts and seller-held-out checks. Compare against the promised date and historical lane medians. Report interval coverage, late-order precision/recall at queue capacity and regional calibration; treat later reviews as outcomes, never predictors.

## Intended interaction

A service-queue dashboard lets visitors choose order horizon, alert capacity and cost assumptions. It shows a coarse lane map, promise-versus-prediction bands and observed late orders captured at each threshold.

## Limits

The data do not show the causal effect of proactive contact or expedited shipping. Respect the dataset's noncommercial/share-alike terms and avoid publishing raw customer records.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
