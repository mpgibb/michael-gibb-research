# S26 — Wearable activity recognition that generalizes to a new person

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A wearable-product team must balance activity-recognition quality with the burden of additional sensors. Determine which sensor combination maintains useful recognition on people the model has never seen.

## Proposed data

[PAMAP2 Physical Activity Monitoring](https://archive.ics.uci.edu/dataset/231/pamap2+physical+activity+monitoring) — UCI / original study researchers. Actual files, release and publication rights require inspection before evaluation.

## Research design

Segment PAMAP2 streams with documented overlap and label-transition rules. Compare handcrafted features plus a tree model with a compact temporal convolutional network. Run sensor-location and heart-rate ablations, keeping every window from a participant inside the same outer validation fold.

## Theory

Temporal representation learning captures movement dynamics; domain generalization asks whether learned patterns transfer across people. Correlated windows can inflate apparent sample size. A multiobjective design balances recognition performance, uncertainty and measured inference requirements.

## Evaluation design

Use nested leave-one-participant-out validation. Report macro-F1, class-specific confusion, transition-period errors, calibration and per-participant results. Compare sensor subsets under the same protocol and measure latency/model size on stated hardware.

## Intended interaction

Visitors switch sensor locations on or off and replay an activity sequence. Predicted activity, confidence and a confusion matrix update; a performance-versus-device-complexity frontier shows the tradeoff.

## Limits

Nine participants provide limited evidence about real-world users. Measured inference cost does not directly establish battery life, and the model is an activity benchmark rather than a validated medical monitor.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
