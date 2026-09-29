# S60 — Can an AI service agent complete the task reliably?

Status: publisher-trajectory baseline complete; controlled intervention trials remain unrun. Audit `S60-audit-7caac4d6` retains 1,980 dialogs and explicitly records missing metadata. See [BASELINE_REPORT.md](BASELINE_REPORT.md).

## Decision

An enterprise AI leader must choose an agent design based on reliable task completion, policy adherence and cost. Test whether explicit state tracking, tool validation and escalation improve repeated task success over a basic tool-calling agent.

## Proposed data

[tau-bench](https://github.com/sierra-research/tau-bench) — Sierra Research. Actual files, release and publication rights require inspection before evaluation.

## Research design

Pin the original tau-bench repository, environment, task split, model versions and user-simulator configuration. Compare a baseline agent with one intervention at a time: structured task state, validated tool arguments, policy checks or escalation. Run repeated trials on identical task sets; isolate all tools in the benchmark's simulated environment.

## Theory

Sequential decision-making compounds errors across tool calls. State machines and invariants constrain invalid transitions; selective automation trades completion coverage against escalation. The benchmark's pass^k measures consistency across repeated trials, unlike pass@k, which rewards at least one success.

## Evaluation design

Reserve tasks for final evaluation and use matched trial seeds where possible. Report goal-state success, pass^k, policy violations, unnecessary tool calls, escalation, latency and cost with task-clustered uncertainty. Validate final database state rather than relying only on an LLM judge's impression.

## Intended interaction

A task replay compares baseline and improved agents step by step. Visitors toggle a validated intervention and view tool events, policy checks, final-state differences and a measured reliability/cost frontier; default to precomputed runs.

## Limits

Simulated customer-service tasks do not establish real customer satisfaction or labor savings. Escalation is not autonomous completion; pin benchmark versions and distinguish synthetic stress tasks from the official evaluation.

There is no runnable study or result artifact yet. The catalog records the next verified stage.

## Reproduce the baseline

Run `uv sync --frozen`, then `RESEARCH_DATA_DIR=/absolute/path/to/data uv run python -W error studies/S60/publisher_audit.py` and `uv run python scripts/report_s60_baseline.py`. This calls no model API. [PROTOCOL.md](PROTOCOL.md) records the separate, still-unrun intervention experiment; exact model versions, access and a bounded approved budget are required.
