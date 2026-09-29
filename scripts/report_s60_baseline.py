"""Document the scope and measured reliability of pinned publisher trajectories."""
from pathlib import Path
import json
p=Path(__file__).resolve().parents[1]/'studies/S60';r=json.loads((p/'results/publisher-baseline.json').read_text())
rows=['| Publisher file label | Environment | Tasks × repeats | Pass^1 | Pass^4 | Pass^4 95% interval |','|---|---|---:|---:|---:|---:|']
for f in r['files']:
 m={x['k']:x for x in f['metrics'] if x['repeat_subset']=='first_four'};a=f['audit'];rows.append(f"| {f['publisher_model_label']} | {f['environment']} | {a['tasks']} × 4 | {m[1]['estimate']:.1%} | {m[4]['estimate']:.1%} | {m[4]['lower']:.1%}–{m[4]['upper']:.1%} |")
(p/'BASELINE_REPORT.md').write_text(f'''# S60 — Publisher trajectory baseline

Status: baseline reanalysis complete; new controlled intervention trials remain unrun. Audit `{r['run_id']}`; source-analysis revision `{r['code_version']}`; original benchmark commit `{r['benchmark_commit']}`.

## Executive interpretation

A service agent that succeeds on one attempt can still be unreliable across repeated attempts at the same task. In the publisher's first four retail repeats, the gpt-4o file label records 60.4% average one-run success but 38.3% success on all four repeats; the sonnet-35-new label records 70.7% and 53.0%. These historical labels do not identify exact model snapshots or a current product comparison.

{chr(10).join(rows)}

The task sets are matched within each environment, but user-simulator and model configurations are not fully recoverable from these files. Differences do not identify the benefit of the proposed validation intervention. Do not use the results as evidence of current customer satisfaction, labor savings or deployment readiness.

## Audit and uncertainty

All 1,980 recorded dialogs are retained: 660 with four repeats per task and 1,320 with eight. Fourteen rows lack secondary reward metadata and remain in the denominators with their recorded failed reward. Available secondary rewards have zero disagreements. Internal agreement is not independent database-state reconstruction. Some cost fields are missing, so total user/API cost and latency remain null.

Pass^k is the fraction of k-repeat subsets on which every attempt succeeds, computed per task and averaged across tasks: choose(successes,k)/choose(repeats,k). It is not pass@k or the probability of at least one success. The comparison table uses the first four repeats to match repeat counts; all-available-repeat sensitivity and paired model-label contrasts are in [publisher-baseline.json](results/publisher-baseline.json). Intervals resample 1,000 task clusters and condition on these dated recorded trials.

Repeated identical calls are counted descriptively, without claiming they were unnecessary. Calls to transfer_to_human_agents are reported separately; the original reward may count an expected escalation as success. New autonomous-completion trials will distinguish escalation from completion rather than silently changing historical benchmark rewards.

## Offline validation intervention

The frozen schema validator was exercised against the pinned source tool definitions and all 14,285 recorded tool calls. All 10,360 retail calls pass schema validation. Three airline calls fail required-argument or enum checks. These are retrospective syntax findings only: rejecting a call does not establish successful recovery or better completion. The validation function checks JSON, duplicate keys, tool names, required fields, types, enums and unsupported arguments without invoking any tool. See [schema-audit.json](results/schema-audit.json). This implements the intervention but does not replace repeated controlled trials.

## Remaining controlled experiment

[PROTOCOL.md](PROTOCOL.md) freezes an outcome-independent final subset of 20 retail tasks, four repeats and two policies: basic tool calling versus syntactic/schema tool validation. No new trial has run. Provider access, exact model snapshots and an approved bounded budget are still required. The proposed 160 dialogs remain limited to the benchmark simulation and 30 steps each. Until then, intervention effects, total cost, latency and independent final-state outcomes remain unmeasured.

## Reproduce and attribution

Run `RESEARCH_DATA_DIR=/absolute/path/to/data uv run python -W error studies/S60/publisher_audit.py`, then `uv run python scripts/report_s60_baseline.py`. Four pinned SHA-256 checksums and the original benchmark revision are recorded in [config.json](config.json). Source: [Sierra Research, original tau-bench](https://github.com/sierra-research/tau-bench), MIT license, copyright (c) 2024 Sierra. Full raw trajectories remain external; no model API is called by this audit.
''')
print('S60 baseline report exported.')
