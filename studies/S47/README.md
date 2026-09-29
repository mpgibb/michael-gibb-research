# S47 — Service-friction signals and a three-month churn planning window

Status: evaluated. Run `S47-a0ada992-696c3a18` compares 624 final records, 561 profiles and 94 churn labels. Core boosting log loss is 0.0981 versus additive 0.1576; paired difference −0.0595 (95% interval −0.0826 to −0.0347). At 124-record capacity it identifies 90 observed churn outcomes. No retention benefit is measured.

[Executive summary and report](REPORT.md) · [Aggregate results](results/result.json) · [Interactive case study](https://michaelpgibb.com/research/s47-service-friction-signals-and-a-three-month-churn-planning-window)

## Decision

A telecom service leader wants to understand whether call failures, complaints and usage patterns identify customers at risk before departure. Test stable, interpretable signals and the limits of translating them into an intervention plan.

## Proposed data

[Iranian Churn](https://archive.ics.uci.edu/dataset/563/iranian+churn+dataset) — UCI / original telecom study authors. Actual fields, attribution and checksum are documented in [DATA.md](DATA.md).

## Research design

Respect the dataset's first-nine-month feature period and end-of-month-12 churn label. Compare regularized logistic/additive models with boosting. Audit status and calculated customer-value fields for circular or late information and report ablations excluding them; avoid treating row order as calendar time.

## Theory

Additive models expose nonlinear associations without requiring a black-box explanation layer. Partial dependence or accumulated local effects summarize model behavior, not causal effects. A causal diagram makes competing explanations for complaints, usage decline and churn explicit.

## Evaluation design

Use nested stratified development and a fixed customer test. Report PR performance, calibration, recall at service capacity and bootstrap stability of feature effects. Compare a simple complaints/recency-style rule with the learned models and assess dependence on derived fields.

## Intended interaction

Visitors choose a service-capacity threshold and toggle feature families. Risk calibration and service-friction association plots update; a separate panel designs the randomized service-recovery experiment needed to estimate actual retention benefit.

## Limits

A small single-company sample cannot establish that fixing call failures causes retention. There are no repeated time cohorts for a genuine out-of-time validation; inferred customer value is not verified profit.

## Reproduce

Set `RESEARCH_DATA_DIR` to a private directory, run `uv sync --frozen`, then `uv run python -W error studies/S47/study.py`. Analysis source must be committed and clean. [PROTOCOL.md](PROTOCOL.md) records grouped development, calibration, final testing, feature sensitivities and the unrun experiment-planning scenario.
