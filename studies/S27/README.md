# S27 — When more wellness sensors do not mean more evidence

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A digital-wellness research team must decide whether combining sleep, activity and cardiac features is promising enough to justify a larger study. Test a deliberately small model of next-morning self-reported affect.

## Proposed data

[MMASH](https://physionet.org/content/mmash/1.0.0/) — PhysioNet / original study researchers. Actual files, release and publication rights require inspection before evaluation.

## Research design

Use MMASH's short monitoring period and prespecify only a few interpretable features observed before the morning questionnaire. Compare prior affect and a mean-only baseline with strongly regularized models adding sleep/activity or heart-rate-variability summaries. Keep the outcome timing and signal-quality exclusions explicit.

## Theory

Bayesian shrinkage reduces overfitting when participant count is tiny. Measurement-error reasoning distinguishes noisy sensor estimates from psychological constructs. Repeated readings within a participant do not create independent people, and exploratory associations need replication.

## Evaluation design

Use participant-held-out prediction with training-fold preprocessing; report absolute error, interval width and sensitivity to individual participants and priors. Compare modality additions one at a time. Publish an inconclusive or negative result if extra sensors do not improve held-out prediction.

## Intended interaction

A modality toggle shows how adding sensors changes predictions, uncertainty and model stability. A leave-one-participant-out view reveals whether an apparent result depends on a single volunteer.

## Limits

The study contains 22 healthy young adult men monitored for roughly one day. It cannot support longitudinal recovery forecasting, broad consumer claims or clinical diagnosis; wide uncertainty is a central finding to communicate.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
