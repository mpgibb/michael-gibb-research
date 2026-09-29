# S28 — Sales-contact prioritization before the call begins

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A sales operations manager has a limited outbound-contact budget. Determine whether calibrated subscription-response models improve the concentration of successful contacts relative to simple recency and prior-contact rules.

## Proposed data

[Bank Marketing](https://archive.ics.uci.edu/dataset/222/bank+marketing) — UCI / Portuguese bank study authors. Actual files, release and publication rights require inspection before evaluation.

## Research design

Use the time-ordered Bank Marketing variant and define the prediction point immediately before contact. Exclude call duration and other unavailable post-contact information. Compare regularized logistic regression, an interpretable additive model and gradient boosting; audit campaign-history availability.

## Theory

Probability calibration translates model scores into expected response counts. Under constant contact costs and equal response value, ordering by response probability maximizes expected observed responses within a fixed capacity. Causal incremental sales require a different estimand and a contact/no-contact design.

## Evaluation design

Use chronological blocks with nested tuning and compare to random selection and simple business rules. Report log loss, calibration, precision at contact capacity and performance across campaign periods. Repeat evaluation without economically sensitive or weakly justified features.

## Intended interaction

Visitors adjust agent capacity, contact cost and assumed response value. A gains curve shows holdout subscriptions captured; an economic panel displays hypothetical break-even thresholds and makes the observed-contact population explicit.

## Limits

Only observed campaign contacts are labeled. The study does not prove incremental benefit from contacting a person or support claims about uncontacted prospects; call duration must never be used to inflate pre-call accuracy.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
