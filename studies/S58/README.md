# S58 — Where business workflows accumulate delay

Status: planned. No analysis has been run and no finding is claimed.

## Decision

An operations leader needs to know which process paths predict long completion times and where limited review capacity might help. Study bottlenecks and remaining-time uncertainty in a real loan-application workflow.

## Proposed data

[BPI Challenge 2017](https://figshare.com/articles/dataset/BPI_Challenge_2017/12696884) — 4TU.ResearchData / contributing financial institution. Actual files, release and publication rights require inspection before evaluation.

## Research design

Parse BPI 2017 events with application/offer relationships and lifecycle semantics intact. Discover common paths and loops, then predict remaining completion time from event prefixes using an interpretable baseline and a sequence/survival challenger. Keep all related offers and prefixes within the same application split.

## Theory

Process mining represents workflow structure; survival models handle unfinished cases and varying process age. Queueing theory distinguishes arrival load, service capacity and waiting, but event-to-event elapsed time does not automatically identify active service time. Simulation requires explicit assumptions for unobserved service mechanisms.

## Evaluation design

Use later application cohorts with appropriate censoring. Compare prefix-age and current-stage medians with learned forecasts; report remaining-time error, calibration and late-case capture at review capacity. Check discovered paths against logs and evaluate staffing scenarios separately from observed prediction quality.

## Intended interaction

Visitors click a workflow stage, choose a case-prefix length and vary a hypothetical capacity bottleneck. A process map shows observed elapsed times, forecast uncertainty and separately labeled simulated completion changes.

## Limits

Observed delays do not prove employee inefficiency or the causal effect of automation. Missing service-time/resource detail limits staffing simulation; business savings cannot be inferred from elapsed time alone.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
