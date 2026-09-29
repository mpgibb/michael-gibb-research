# S40 — Hotel cancellation risk and the cost of overbooking

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A hotel revenue manager must balance empty rooms against the cost of accommodating guests elsewhere. Test whether booking-level cancellation probabilities improve a simulated overbooking policy compared with uniform cancellation assumptions.

## Proposed data

[Hotel Booking Demand datasets](https://pmc.ncbi.nlm.nih.gov/articles/PMC6297060/) — Antonio, de Almeida and Nunes / Data in Brief. Actual files, release and publication rights require inspection before evaluation.

## Research design

Define a booking-time prediction point and audit whether each field was available then. Exclude final reservation status/date, later booking changes and other post-outcome fields. Compare calibrated logistic/additive models with boosting; aggregate predicted cancellations across arrival dates with dependence sensitivity.

## Theory

Revenue management treats uncertain show-up demand as a capacity decision. Asymmetric loss balances unused inventory against displacement penalties. Shared arrival-date shocks make independent booking outcomes an imperfect assumption; calibration matters when probabilities are summed.

## Evaluation design

Use time-based arrival holdouts and a hotel-transfer stress test. Report cancellation calibration, log loss and arrival-date prediction error. Compare fixed-rule and model-based overbooking in a simulator with explicit room capacity, room-night logic, rates and displacement costs.

## Intended interaction

Visitors set assumed capacity, displacement penalty and risk tolerance. A booking-arrival distribution, modeled revenue frontier and displaced-guest risk update together, with an observed-versus-assumed data legend.

## Limits

Two hotels do not establish universal performance. Original booking-time versions of some fields may be unavailable; label that limitation. Capacity and counterfactual overbooking revenue are simulated, not measured business improvement.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
