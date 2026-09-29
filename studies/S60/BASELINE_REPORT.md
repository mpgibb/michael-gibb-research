# S60 — Publisher trajectory baseline

Status: baseline reanalysis complete; new controlled intervention trials remain unrun. Audit `S60-audit-7caac4d6`; source-analysis revision `7caac4d64c177ae9b1fb83faecfdab2f62230958`; original benchmark commit `59a200c6d575d595120f1cb70fea53cef0632f6b`.

## Executive interpretation

A service agent that succeeds on one attempt can still be unreliable across repeated attempts at the same task. In the publisher's first four retail repeats, the gpt-4o file label records 60.4% average one-run success but 38.3% success on all four repeats; the sonnet-35-new label records 70.7% and 53.0%. These historical labels do not identify exact model snapshots or a current product comparison.

| Publisher file label | Environment | Tasks × repeats | Pass^1 | Pass^4 | Pass^4 95% interval |
|---|---|---:|---:|---:|---:|
| gpt-4o | airline | 50 × 4 | 42.0% | 20.0% | 10.0%–30.0% |
| gpt-4o | retail | 115 × 4 | 60.4% | 38.3% | 28.7%–47.0% |
| sonnet-35-new | retail | 115 × 4 | 70.7% | 53.0% | 44.3%–61.7% |
| sonnet-35-new | airline | 50 × 4 | 45.5% | 20.0% | 8.0%–32.0% |

The task sets are matched within each environment, but user-simulator and model configurations are not fully recoverable from these files. Differences do not identify the benefit of the proposed validation intervention. Do not use the results as evidence of current customer satisfaction, labor savings or deployment readiness.

## Audit and uncertainty

All 1,980 recorded dialogs are retained: 660 with four repeats per task and 1,320 with eight. Fourteen rows lack secondary reward metadata and remain in the denominators with their recorded failed reward. Available secondary rewards have zero disagreements. Internal agreement is not independent database-state reconstruction. Some cost fields are missing, so total user/API cost and latency remain null.

Pass^k is the fraction of k-repeat subsets on which every attempt succeeds, computed per task and averaged across tasks: choose(successes,k)/choose(repeats,k). It is not pass@k or the probability of at least one success. The comparison table uses the first four repeats to match repeat counts; all-available-repeat sensitivity and paired model-label contrasts are in [publisher-baseline.json](results/publisher-baseline.json). Intervals resample 1,000 task clusters and condition on these dated recorded trials.

Repeated identical calls are counted descriptively, without claiming they were unnecessary. Calls to transfer_to_human_agents are reported separately; the original reward may count an expected escalation as success. New autonomous-completion trials will distinguish escalation from completion rather than silently changing historical benchmark rewards.

## Remaining controlled experiment

[PROTOCOL.md](PROTOCOL.md) freezes an outcome-independent final subset of 20 retail tasks, four repeats and two policies: basic tool calling versus syntactic/schema tool validation. No new trial has run. Provider access, exact model snapshots and an approved bounded budget are still required. The proposed 160 dialogs remain limited to the benchmark simulation and 30 steps each. Until then, intervention effects, total cost, latency and independent final-state outcomes remain unmeasured.

## Reproduce and attribution

Run `RESEARCH_DATA_DIR=/absolute/path/to/data uv run python -W error studies/S60/publisher_audit.py`, then `uv run python scripts/report_s60_baseline.py`. Four pinned SHA-256 checksums and the original benchmark revision are recorded in [config.json](config.json). Source: [Sierra Research, original tau-bench](https://github.com/sierra-research/tau-bench), MIT license, copyright (c) 2024 Sierra. Full raw trajectories remain external; no model API is called by this audit.
