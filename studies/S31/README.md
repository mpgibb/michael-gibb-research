# S31 — Insurance pricing: interpretable structure versus nonlinear accuracy

Status: evaluated public-data study. Run `S31-02c309de-1e141502`. Independent technical review is pending.

On 136,271 held-out policies, boosting does not establish a clear full-loss deviance advantage over interpretable frequency–severity regression: difference −0.531 (95% interval −1.626 to +0.811). Observed loss is €147.76 per policy-year; boosting predicts €138.35. Capped-target and geographic-stress gains remain separate findings. See [the executive summary and full report](REPORT.md).

## Decision

An insurance analytics team needs accurate expected-loss estimates that remain understandable across policy segments. Test whether a nonlinear model improves frequency-severity predictions while preserving portfolio and segment calibration.

## Proposed data

[freMTPL2 frequency and severity](https://dutangc.github.io/CASdatasets/reference/freMTPL.html) — CASdatasets / actuarial research contributors. Archived CASdatasets 1.2-0 is verified; actual files, reconciliation and reuse details are in DATA.md.

## Research design

Audit policy exposure and claim counts, aggregate severity by policy before joining, and explain inconsistencies. Compare an exposure-offset Poisson/negative-binomial frequency model plus Gamma severity model with Tweedie and boosted challengers. Keep claim-level observations from the same policy together.

## Theory

Expected aggregate loss combines claim frequency and conditional severity under stated dependence assumptions. The log-exposure offset accounts for unequal time at risk. Tweedie compound models accommodate zero claims and continuous positive loss; actuarial calibration checks whether predicted totals match experience.

## Evaluation design

Use policy-held-out development/test sets and geographic stress tests where feasible. Report exposure-weighted deviance, total predicted/observed loss, segment calibration and tail sensitivity. Compare uncapped and transparently capped severity analyses; do not claim a time split without reliable policy dates.

## Intended interaction

An actuarial model explorer switches model class and portfolio segment. It decomposes expected loss into frequency and severity and displays calibration, uncertainty and hypothetical expense-loading effects separately.

## Limits

Historical French motor data do not validate a current insurance rate filing. Pure premium is expected insured loss, not the final customer price; regulatory and deployment questions are outside the benchmark.

Run `uv sync --frozen`, then `uv run python -W error studies/S31/study.py`. Raw files and private predictions use RESEARCH_DATA_DIR or the external user cache. PROTOCOL.md freezes targets, splits, settings and uncertainty before fitting. [Aggregate results](results/result.json) and report figures come from the executed evaluation.
