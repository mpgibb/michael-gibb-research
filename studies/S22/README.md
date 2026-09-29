# S22 — Pitcher development signals that survive the next season

Status: blocked; source prerequisite pending as of September 29, 2026. Official field documentation inspected. The general MLB terms do not establish the required automated-ingestion and public-reuse permission for this research publication. No dataset has been downloaded or model fitted.

Next action: Obtain applicable publisher permission or a legitimately licensed source covering the intended study before ingestion and publication. Preserve the pitch-level, season-forward design. See [DATA.md](DATA.md).

## Decision

A player-development group needs to distinguish durable pitch quality from small-sample outcomes. Test whether pitch characteristics and context improve forecasts of future swing-and-miss and contact quality beyond recent results.

## Proposed data

[Statcast / Baseball Savant](https://baseballsavant.mlb.com/csv-docs) — Major League Baseball. Actual files, release and publication rights require inspection before evaluation.

## Research design

Create pitcher/pitch-type season histories from Statcast with explicit tracking-era and field-availability checks. Model swing, miss and contact outcomes in stages, using count, handedness and pitch characteristics available at the relevant stage. Pool sparse pitcher/pitch-type estimates hierarchically and forecast a later season.

## Theory

Partial pooling reduces overreaction to small samples; multistage probability models respect the sequence from pitch to swing to contact. Measurement drift can change apparent skill. Changes in modeled pitch mix are conditional scenarios, not identified effects of coaching intervention.

## Evaluation design

Use season-forward holdouts and pitcher-level uncertainty. Compare with prior-season rates and league/pitch-type averages. Report calibration, log loss for binary outcomes, contact-quality error and rank stability across pitch-count thresholds and tracking eras.

## Intended interaction

A pitcher-development explorer varies the minimum sample and supported pitch-mix weights. It shows posterior skill distributions, next-season holdout performance and conditional pitch-mix scenarios; uncertainty expands for sparse or unsupported combinations.

## Limits

Observed pitch selection depends on opponent and situation. The study cannot prove that changing pitch mix improves performance, and outcome-stage variables must not leak into pre-pitch forecasts.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
