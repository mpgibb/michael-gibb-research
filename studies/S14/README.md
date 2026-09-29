# S14 — Maintenance warnings without an alarm flood

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A maintenance team needs warnings early enough to schedule work, with few false alarms. Compare interpretable vibration change detection against an unsupervised anomaly model across independent bearing experiments.

## Proposed data

[IMS Bearings](https://data.nasa.gov/dataset/ims-bearings) — University of Cincinnati IMS / NASA. Actual files, release and publication rights require inspection before evaluation.

## Research design

Extract spectral-band energy, envelope features and robust distribution summaries from vibration windows. Define an early-run reference period explicitly rather than assuming verified healthy labels. Compare robust control charts/change-point methods with a compact anomaly detector and enforce an alarm-persistence rule.

## Theory

Statistical process control detects departures from a reference distribution. Change-point models distinguish sustained regime shifts from transient noise; sequential thresholds trade detection delay against average false-alarm frequency. Overlapping windows are dependent measurements, not independent test subjects.

## Evaluation design

Keep complete experiments or bearings together and show leave-run-out results wherever the small number of runs allows. Report time before documented failure, false alarms per operating hour and sensitivity to window length. Bootstrap by run only when meaningful; emphasize per-run results over spurious narrow intervals.

## Intended interaction

A signal replay lets visitors vary alarm threshold and required persistence. It overlays warnings on a vibration timeline and compares warning lead time with false-alert burden for each experiment.

## Limits

A few laboratory failures cannot establish fleet-wide reliability. The onset of degradation is not fully labeled; maintenance savings and the effect of a repair policy require explicit simulation or prospective data.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
