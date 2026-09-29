# S10 — Delivery sequencing that combines optimization and driver experience

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A last-mile operator needs feasible routes that balance travel efficiency with practical delivery order. Test whether learning from historical high-quality routes improves a constraint-based routing baseline.

## Proposed data

[Amazon Last Mile Routing Research Challenge](https://registry.opendata.aws/amazon-last-mile-challenges/) — Amazon / MIT Center for Transportation and Logistics. Actual files, release and publication rights require inspection before evaluation.

## Research design

Use the provided travel-time matrix, stop/package features and documented constraints. Compare nearest-neighbor and classical local-search baselines with learned sequence preferences inside a constrained routing solver. Preserve an untouched route-level benchmark split and use station holdouts as a transfer test where feasible.

## Theory

Vehicle routing is combinatorial optimization under feasibility constraints. Learning-to-rank or inverse-optimization ideas encode preferences implicit in expert sequences; imitation and physical travel minimization are different objectives and should be reported separately.

## Evaluation design

Use the official sequence-quality metric, constraint-violation counts, supplied travel-time totals and computation time. Ablate learned preferences and test travel-time perturbations. Show when a shorter route deviates from expert order rather than treating historical behavior as a globally optimal solution.

## Intended interaction

A route replay allows selection of a benchmark route and method. Visitors vary the preference/travel tradeoff or a labeled travel-time shock; the stop sequence, feasibility warnings and benchmark scores update together.

## Limits

Locations are obfuscated and route labels do not measure realized wage or fuel savings. Show geographic displays as schematic when appropriate and keep cost conversions explicitly assumed.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
