# S24 — Roster allocation under aging and performance uncertainty

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A roster planner must allocate a fixed budget across players with uncertain future production. Test whether modeling aging, playing time and downside risk changes a roster relative to ranking last season's statistics.

## Proposed data

[Lahman Baseball Database](https://sabr.org/lahman-database/) — SABR / Sean Lahman and contributors. Actual files, release and publication rights require inspection before evaluation.

## Research design

Build historical player-season panels with era normalization and a prespecified offensive run-value formula. Forecast playing time and offensive production jointly using hierarchical age curves and flexible challengers. Optimize a simplified roster under position and budget constraints, using documented salary-covered seasons or clearly synthetic costs.

## Theory

Aging curves require separating within-player change from cohort and survivor selection. Bayesian partial pooling stabilizes sparse careers. Portfolio optimization combines expected production with correlated downside scenarios and concentration constraints rather than treating every forecast as certain.

## Evaluation design

Use season-forward holdouts and compare against last-season production and age-neutral forecasts. Report production error, interval coverage and roster-performance distributions in historical replay. Stress retirement/selection assumptions and salary coverage; keep hindsight-optimal comparisons confined to the simulation.

## Intended interaction

A roster builder exposes budget, positional requirements and downside tolerance. An efficient frontier and alternative roster cards show projected production, uncertainty and where the allocation changes as assumptions change.

## Limits

Lahman is not a complete current payroll or scouting database. A simplified offensive roster omits defense, injuries and contractual constraints unless explicitly added; it cannot establish current front-office value.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
