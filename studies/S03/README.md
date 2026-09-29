# S03 — When does a customer become worth winning back?

Status: evaluated. Run `S03-2f7d21cd-572e3627` compares 14,388 final customer-window forecasts across 5,155 customers. BG/NBD beats hurdle boosting on primary 90-day count deviance: 0.990 versus 1.072, paired difference +0.082 (95% interval 0.068–0.096). Seasonal calibration still shifts substantially; no win-back effect is measured.

[Executive summary and evaluation report](REPORT.md) · [Aggregate results](results/result.json) · [Interactive case study](https://michaelpgibb.com/research/s03-when-does-a-customer-become-worth-winning-back)

## Decision

An e-commerce team needs to distinguish temporarily inactive buyers from customers unlikely to return. Estimate future transaction counts and revenue distributions to support the timing and prioritization of win-back campaigns.

## Proposed data

[Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii) — UCI / original retailer data donor. Official workbook and CC BY 4.0 attribution are documented in [DATA.md](DATA.md).

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

## Reproduce

Install the locked environment with `uv sync --frozen`, set `RESEARCH_DATA_DIR` to a private data directory, then run `uv run python -W error studies/S03/study.py`. Commit the protocol and analysis source before running; provenance rejects modified analysis files. [PROTOCOL.md](PROTOCOL.md) records timing, model selection, intervals and the prespecified accounting sensitivity. No raw records or customer-level predictions belong in the public repository.
