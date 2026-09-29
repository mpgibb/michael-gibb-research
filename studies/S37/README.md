# S37 — Early warning of airline disruption across an airport network

Status: planned. No analysis has been run and no finding is claimed.

## Decision

An airline operations team must prioritize flights for early disruption review. Test whether recent network conditions add useful warning of severe arrival delays or cancellations beyond schedule and seasonal patterns.

## Proposed data

[Airline On-Time Performance](https://www.transtats.bts.gov/ONTIME/Index.aspx) — Bureau of Transportation Statistics. Actual files, release and publication rights require inspection before evaluation.

## Research design

Define a fixed pre-departure prediction cutoff and create schedule, airport-congestion and lagged completed-flight features. Compare calibrated boosting with a simpler logistic model and a network-aware challenger. Use aircraft rotation features only where the assignment is knowable at the cutoff; exclude the target flight's realized delay causes.

## Theory

Network dependence allows disruptions to propagate through shared airports and resources. Temporal feature availability determines whether a forecast is actionable. Calibrated probabilities support queue prioritization, while causal effects of changing a schedule require an explicit operational model.

## Evaluation design

Use rolling month/season holdouts and airport-transfer tests. Report rare-event precision-recall, calibration, warning lead time and severe disruptions captured at a fixed review capacity. Separate cancellation from conditional delay severity and audit publication/schedule revision timing.

## Intended interaction

An airport-network timeline lets visitors choose a cutoff, airport and review budget. It shows observed holdout outcomes, risk concentration and model comparison; any rerouting or delay-propagation intervention is a separately labeled simulation.

## Limits

Retrospective BTS records may not reconstruct every live schedule or aircraft assignment. Do not present hindsight features as real-time knowledge or simulated schedule changes as proven delay reduction.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
