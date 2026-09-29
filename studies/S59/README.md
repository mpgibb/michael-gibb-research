# S59 — Complaint triage with evidence and a human-review threshold

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A customer-operations team needs consistent routing of complaints while recognizing uncertain or emerging issues. Compare a simple text classifier with an evidence-grounded language-model workflow under a fixed human-review budget.

## Proposed data

[Consumer Complaint Database](https://www.consumerfinance.gov/data-research/consumer-complaints/) — Consumer Financial Protection Bureau. Actual files, release and publication rights require inspection before evaluation.

## Research design

Use eligible public CFPB narratives and harmonized product/issue labels. Predict intake categories from narrative text only; exclude recorded outcome and routing fields from inputs. Add structured issue extraction with cited spans and an abstention rule. Treat historical category labels as imperfect supervision and document publication selection.

## Theory

Selective prediction balances automatic coverage against error. Hierarchical classification reflects related complaint categories; concept drift changes vocabulary and taxonomy over time. Evidence attribution tests whether an explanation is supported by the source, which is different from whether the routing label is correct.

## Evaluation design

Hold out later periods and a company-transfer slice. Compare TF-IDF/logistic and language-model approaches using macro-F1, rare-issue recall, calibration, coverage-risk curves, latency and cost. Audit factual support on an independently reviewed sample; separate weak-label accuracy from adjudicated quality.

## Intended interaction

Visitors inspect approved/redacted sample complaints and choose a review threshold. The demo shows proposed category, supporting spans, uncertainty and human escalation, alongside measured quality/cost tradeoffs and an emerging-theme timeline.

## Limits

Complaints are selected reports, not verified facts or a customer-base denominator. Do not infer company misconduct or rank complaint rates without exposure; no live customer data or automated external action is needed.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
