# S07 — Subscription renewal risk with actionable lead time

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A subscription business needs enough advance warning to act on likely non-renewals. Test how much predictive value comes from usage deterioration versus payment/renewal history at realistic intervention cutoffs.

## Proposed data

[KKBox Churn Prediction Challenge](https://www.kaggle.com/competitions/kkbox-churn-prediction-challenge/data) — KKBOX / WSDM / Kaggle. Actual files, release and publication rights require inspection before evaluation.

## Research design

Build member snapshots before expected subscription expiry and reproduce the official churn definition. Compare an elastic-net logistic baseline with gradient boosting and, where complete renewal episodes permit, a discrete-time hazard model. Exclude transactions or usage recorded after each prediction cutoff.

## Theory

A hazard models conditional non-renewal risk among subscriptions still at risk. Temporal landmarking aligns the available information with the intervention date. Expected-loss ranking combines risk and an explicitly assumed economic exposure, but risk alone does not identify persuadable customers.

## Evaluation design

Use month-based holdouts with label-maturation gaps. Report log loss, calibration, precision/recall at fixed contact capacity and performance by tenure and plan. Compare several warning horizons and remove payment/usage feature families in ablations.

## Intended interaction

A retention-capacity slider and warning-horizon selector show how many eventual non-renewals the model identifies in the holdout. Users inspect cohort calibration and a sensitivity surface for assumed intervention success and contribution margin.

## Limits

KKBox is a consumer music service, not a B2B account-revenue dataset. Saved subscribers and retention ROI require an intervention experiment; observed churn prediction cannot establish them.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
