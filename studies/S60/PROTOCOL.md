# S60 — Agent-reliability evaluation protocol

Pin original tau-bench commit `59a200c6d575d595120f1cb70fea53cef0632f6b`. The publisher says these task versions are outdated; later benchmark fixes are not silently substituted. All tools operate only on the benchmark's simulated databases. Preserve the source's MIT notice and scientific model identifiers.

## Available fallback: publisher-trajectory audit

Independently recalculate reliability from the four versioned historical trajectory files. This is a reanalysis of publisher runs, not new trials or an intervention experiment. Treat file labels as publisher model labels; do not invent a dated model snapshot, common simulator configuration or latency absent from the files.

Validate unique task/trial keys, binary rewards, task coverage, repeated-trial counts, recorded reward-component agreement and tool-message accounting. Compute pass^k = choose(successful repeats,k)/choose(total repeats,k), averaged over tasks, for k=1,2,3,4. It measures all-k success, not at-least-one success. Show all available repeats and a separate first-four-repeat comparison so unequal repeat counts stay visible. Preserve task-level clustering with 1,000 bootstrap draws; paired model differences use the same tasks, but are not matched random-seed causal effects.

Report benchmark reward, repeated identical tool-call counts, escalations and recorded user-simulator cost when present. Total agent+simulator cost and latency stay null where missing. A recorded success is not a newly verified final-state reconstruction. Raw transcripts remain outside publication; share only aggregate audit tables and a citation to the original source.

## Required new controlled comparison

Development uses retail dev tasks 0, 1, 2. Final tasks are the 20 smallest SHA-256 hashes of `S60-retail-test-{task_id}` among the 115 official retail test task indices, independent of outcomes. Run 4 repeats per task per policy:160 final dialogs, plus bounded development checks. Each starts with a fresh simulated database. Preserve final task IDs before any new trial; no task substitution after failures.

Compare baseline native tool calling with exactly one intervention: validate function name, JSON syntax, required arguments, types, enums and unsupported arguments against the tool schema before invoking the simulated tool. Return a structured validation error within the same step limit; do not execute invalid arguments. Do not add hidden policy instructions, privileged target actions, independent human labels or unvalidated semantic claims.

Both conditions use the same dated agent and user-simulator model versions, temperature, step/token bounds and task schedule. Record seeds if the selected provider supports them; matching requested seeds does not guarantee identical stochastic trajectories. Provider/model snapshots and a hard total cost limit must be fixed before execution. No credentials are stored in the repository. Exhausting the budget leaves missing trials explicitly incomplete; it does not turn them into successful or observed failures.

Primary: paired difference in autonomous final-goal success across held-out tasks. Preserve the original database-state/output reward separately; an escalation is not autonomous completion even if the benchmark rewards it. Report pass^1 through pass^4, escalation, schema errors, repeated identical lookups, measured latency and complete measured API costs with task-clustered uncertainty. Required output-string tests and database hashes follow the pinned evaluator. General policy adherence or unnecessary-action judgments require an explicit adjudication protocol; automated schema checks are not independent human review.

The interaction must show only actual saved trajectories/results, model versions, tool events, verified final-state outcomes and the observed reliability/cost comparison. Historical publisher audits alone cannot satisfy the intervention claim. No unrestricted inference is placed in the public website.
