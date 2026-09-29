# S07 — Subscription renewal risk with actionable lead time

Status: blocked; source prerequisite pending as of September 29, 2026. Official source dictionary and reuse terms inspected. The download requires an authenticated Kaggle account and acceptance of KKBox competition rules. Data ingestion and all model fitting remain unrun.

Next action: Complete authorized source access, then inspect the official label generator, expiry alignment and mature-label calendar. Do not substitute an unofficial mirror or redistribute member records. See [DATA.md](DATA.md).

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
