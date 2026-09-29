# S15 — Remaining useful life with decisions that acknowledge uncertainty

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A fleet planner must choose when to replace an asset when failure timing is uncertain. Test whether calibrated remaining-life distributions improve a simulated replacement policy relative to point estimates.

## Proposed data

[C-MAPSS turbofan degradation](https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/) — NASA. Actual files, release and publication rights require inspection before evaluation.

## Research design

Use engine-level C-MAPSS train/test partitions and preserve operating-condition subsets. Compare an engineered degradation-index baseline, boosted quantile regression and one sequence model. Make remaining-life label capping and sensor normalization explicit, including ablations.

## Theory

Reliability theory treats failure time as a random variable; conditional remaining life changes as new measurements arrive. Asymmetric loss reflects the different costs of early replacement and unexpected failure. Prediction intervals may be calibrated empirically, but dependent degradation sequences require more care than exchangeable conformal examples.

## Evaluation design

Report engine-level RUL error, the benchmark's asymmetric score and interval coverage by operating condition and life stage. Test an unseen-condition subset. Simulate replacement using only sequentially available measurements and compare fixed-age, point-estimate and uncertainty-aware rules.

## Intended interaction

Visitors move through an engine's sensor history, choose risk tolerance and set hypothetical replacement/failure costs. The remaining-life distribution and simulated replacement recommendation update with the evidence available at that cycle.

## Limits

C-MAPSS is simulator-generated. Both asset behavior and the policy economics must be labeled as simulation; no real fleet savings or safety validation are established.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
