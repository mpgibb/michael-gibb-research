# S03 — When does a customer become worth winning back?

Status: planned. No analysis has been run and no finding is claimed.

## Decision

An e-commerce team needs to distinguish temporarily inactive buyers from customers unlikely to return. Estimate future transaction counts and revenue distributions to support the timing and prioritization of win-back campaigns.

## Proposed data

[Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii) — UCI / original retailer data donor. Actual files, release and publication rights require inspection before evaluation.

## Research design

Clean cancellations, returns and missing identifiers under documented rules. Fit BG/NBD purchase-frequency models and a Gamma-Gamma spend model on eligible positive purchases; compare with a flexible count/spend model when assumptions fail. Use successive purchase-history cutoffs and future observation windows.

## Theory

BG/NBD combines heterogeneous purchase rates with an unobserved dropout process. Gamma-Gamma pools transaction values across customers and assumes an appropriate separation of spend and purchase frequency. A posterior probability of activity is model-based uncertainty, not an observed churn label.

## Evaluation design

Compare against simple recency rules and RFM segments. Evaluate held-out transaction-count error, aggregate revenue bias, calibration by recency/frequency cohort and interval coverage. Test whether frequency and spend independence is plausible; publish the challenger if it performs better.

## Intended interaction

A customer-cohort explorer accepts recency, frequency, purchase horizon and assumed contact cost. It plots the expected purchase distribution, probability of future purchasing and hypothetical campaign break-even response, rather than claiming a known win-back effect.

## Limits

The data contain no randomized win-back intervention. Long-term value extrapolation is assumption-sensitive and concerns an older single retailer; do not present revenue as profit.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
