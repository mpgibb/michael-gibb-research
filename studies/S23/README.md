# S23 — Baseball strategy as a risk-sensitive decision problem

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A baseball strategy analyst wants to quantify when a stolen-base attempt or other base-running choice is worth the risk. Estimate the break-even success probability under different base-out states and scoring environments.

## Proposed data

[Retrosheet play-by-play](https://www.retrosheet.org/eventfile.htm) — Retrosheet. Actual files, release and publication rights require inspection before evaluation.

## Research design

Parse Retrosheet events into validated base-out transitions and inning runs. Estimate era-specific run-expectancy tables with shrinkage for sparse states. For a stolen-base decision, compare expected runs after success, failure and no attempt using documented transition assumptions.

## Theory

An absorbing Markov reward process links state transitions to expected remaining runs. Expected utility gives a break-even action threshold; risk-sensitive extensions examine the distribution of runs rather than the mean alone. Counterfactual transitions require assumptions about what would happen after each action.

## Evaluation design

Hold out seasons and check run-expectancy calibration and transition validity. Compare pooled and era-specific tables, bootstrap by game, and test rare-state sensitivity. Validate the transition engine with known game-state identities and explicitly distinguish predictive checks from causal policy evaluation.

## Intended interaction

Visitors choose runners, outs, era and an assumed steal-success probability. A decision curve shows the break-even point and uncertainty; a state diagram explains the possible outcomes in plain language.

## Limits

Managers select attempts non-randomly, and observed non-attempts are not randomized controls. Historical decision replay cannot by itself establish that a new strategy would cause more wins.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
