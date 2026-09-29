# S25 — Daily activity patterns and the limits of wellness segmentation

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A wellness analytics team wants to understand whether daily activity rhythms reveal useful population segments beyond total movement. Study how pattern estimates change with wear-time quality and demographic composition.

## Proposed data

[NHANES Physical Activity Monitor](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/PAXMIN_G.htm) — CDC / NCHS. Actual files, release and publication rights require inspection before evaluation.

## Research design

Build participant-level daily curves from NHANES monitor summaries using documented MIMS units, wear/sleep flags and quality checks. Fit functional principal components and a small, stable clustering model. Link same-cycle public demographics and selected examination/laboratory measures by participant ID only as explicitly documented companion files.

## Theory

Functional data analysis models a day's activity as a curve, preserving timing. Survey weights support population-level descriptions; missing wear time can distort both total activity and apparent rhythm. Associations with contemporaneous health measurements are cross-sectional, not evidence that changing activity causes better health.

## Evaluation design

Compare rhythm-based segments against total-activity bins. Assess within-person day-to-day reliability, weighted cluster stability and sensitivity to valid-day thresholds. Hold participants together and test transfer between survey cycles; report weighted uncertainty and sample exclusions.

## Intended interaction

Visitors select population groups, valid-wear rules and a segmentation method. A 24-hour activity ribbon and cluster-comparison plot reveal how inclusion rules change conclusions; linked health summaries appear only as labeled associations.

## Limits

Use thresholds appropriate to MIMS, not legacy accelerometer-count cutoffs. These data do not measure gym retention or validate personalized wellness advice; linked health endpoints require compatible survey weights and eligibility.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
