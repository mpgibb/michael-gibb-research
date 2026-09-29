"""Render the sensor-screening report from the evaluated aggregate artifact."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];HERE=ROOT/'studies/S13';r=json.loads((HERE/'results/result.json').read_text());t=r['tables'];d=t['primary_difference']
labels={m['id']:m['label'] for m in r['models']};short={'elastic_net':'Sparse logistic','pca_monitor':'PCA monitor','boosting':'Boosting','boosting_no_missing':'No missingness indicators'}
colors={'elastic_net':'#0a192f','pca_monitor':'#64748b','boosting':'#925322','boosting_no_missing':'#94a3b8'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none','svg.hashsalt':r['run_id'],'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(7.8,4.4))
for model in short:
 rows=[v for v in t['capacity'] if v['model']==model];ax.plot([100*v['capacity'] for v in rows],[v['detected_failures'] for v in rows],label=short[model],color=colors[model],marker='o',markersize=3)
ax.set(xlabel='Assumed share of final batch inspected (%)',ylabel='Observed failures identified (of 22)',title='More inspection is not proof of a useful ranking',ylim=(0,23),xlim=(0,100));ax.legend(frameon=False,fontsize=8);ax.grid(alpha=.15);fig.tight_layout();fig.savefig(HERE/'results/inspection-capacity.svg',metadata={'Creator':'Michael P. Gibb, Ph.D.','Date':None});plt.close(fig)
fig,ax=plt.subplots(figsize=(7.8,4.4));rows=t['sensor_stability'][:12][::-1];ax.barh([v['sensor'] for v in rows],[100*v['selection_frequency'] for v in rows],color='#925322');ax.set(xlabel='Selected in training-day bootstrap refits (%)',title='Selection frequency is not physical importance',xlim=(0,105));ax.grid(axis='x',alpha=.15);fig.tight_layout();fig.savefig(HERE/'results/sensor-stability.svg',metadata={'Creator':'Michael P. Gibb, Ph.D.','Date':None});plt.close(fig)
metricrows=[]
for model,label in labels.items():
 ap=next(v for v in r['metrics'] if v['model']==model and v['name']=='average_precision');ll=next(v for v in r['metrics'] if v['model']==model and v['name']=='log_loss');br=next(v for v in r['metrics'] if v['model']==model and v['name']=='brier');metricrows.append(f"| {label} | {ap['estimate']:.4f} | {ap['lower']:.4f}–{ap['upper']:.4f} | {ll['estimate']:.4f} | {br['estimate']:.4f} |")
caprows=[f"| {labels[v['model']]} | {v['inspections']} | {v['detected_failures']} | {v['missed_failures']} | {v['unnecessary_inspections']} |" for v in t['capacity'] if v['capacity']==.2]
j=np.mean([v['jaccard_to_final'] for v in t['stability_runs']]);mi=min(v['selected_sensors'] for v in t['stability_runs']);ma=max(v['selected_sensors'] for v in t['stability_runs'])
(HERE/'REPORT.md').write_text(f'''# S13 — Reliable quality screening with many sensors and few failures

Run `{r['run_id']}` · analysis `{r['code_version']}` · {r['evaluated_on']}.

## Decision and executive summary

Do not use this comparison to justify automatic release or reduced quality inspection. On 359 later production entities, the tested models provide weak ranking evidence. At 20% capacity (71 inspections), boosting identifies only 4 of 22 observed failures; sparse logistic identifies 3 and the PCA monitor 5. Most failures remain undetected under that assumed budget.

Boosting's average precision is 0.0626, versus 0.0765 for sparse logistic and a 0.0613 final failure prevalence. The primary paired difference is **{d['estimate']:.4f}** (95% day-cluster interval **{d['lower']:.4f} to {d['upper']:+.4f}**). No clear advantage is established. Average precision summarizes precision over recall thresholds; higher is better, but its numerical value depends on failure prevalence. It is not an accuracy percentage or the detection rate at 20% capacity.

The decision implication is to require prospective evidence and verified feature timing before operational use. The data contain anonymous sensors without acquisition timestamps. This is a historical screening comparison conditional on recorded measurements being available; it does not establish advance warning, root causes, avoided failures or savings.

## Final evidence

| Model | Average precision | 95% interval | Log loss | Brier score |
|---|---:|---:|---:|---:|
{chr(10).join(metricrows)}

A constant training-prevalence probability has lower final log loss and Brier score than the fitted sensor models. Probability calibration therefore does not support treating their scores as dependable failure probabilities. The result artifact includes five equal-count calibration groups and day-specific diagnostics.

| Model at 20% capacity | Inspections | Detected failures | Missed failures | Inspected passes |
|---|---:|---:|---:|---:|
{chr(10).join(caprows)}

![Inspection capacity and missed failures](results/inspection-capacity.svg)

These are exact counts from one historical holdout, not expected counts in a new plant. Capacity ranks the complete October batch, not a daily production schedule. Inspecting all units recovers all known labels by construction; it is not a measured process improvement.

## Data, timing and selection

SECOM contains 1,567 production entities and 104 failed tests from July 19–October 17, 2008. The official documentation lists 591 features; the actual numeric file has 590 sensor columns. The separate label file aligns row-for-row and contains quoted test timestamps. Source audit: 41,951 missing cells, 116 constant columns, 104 exact duplicate columns, no exact duplicate full sensor rows and 33 timestamp ties.

July–August supplies 618 development rows and 65 failures. September supplies 590 validation rows and 17 failures. October supplies the untouched final 359 rows and 22 failures. Separate family settings are selected by September log loss; final fitting uses 1,208 July–September rows and 82 failures. The chosen settings are elastic-net C=.1, PCA five components, and boosting seven leaves. September boosting average precision was 0.2519; that performance did not persist in October. No tuning uses final outcomes.

All filtering, clipping, imputation, duplicate removal, scaling and missingness-indicator selection are fitted inside the permitted training period. No timestamp enters a predictor. Reporting delay, wafer/lot grouping and the acquisition time of each measurement are not available, so calendar order alone cannot reconstruct a prospective deployment.

## Sparse-sensor stability and missingness

The final processor retains 444 original sensors and 502 transformed variables. Sparse logistic retains 79 nonzero coefficients representing 78 sensors. Across 30 training-day bootstrap refits, {mi}–{ma} sensors are selected, with mean Jaccard overlap **{100*j:.1f}%** against the final selected set. This substantial variability is a warning against interpreting a single selected list as a durable engineering diagnosis.

![Anonymous sensor selection frequency](results/sensor-stability.svg)

Sensor_060 is selected in every resample, but the source supplies no physical identity or intervention evidence. Selection frequency describes this estimator and dataset, not a causal fault. The explorer can change its display threshold without refitting any model.

Removing missingness indicators from the selected boosting configuration leaves average precision near 0.0632 and finds only two failures at 20% capacity. This is a fixed sensitivity analysis, not a separate model search. Forty-eight final entities have more than 5% of sensors missing and no observed failures; that slice cannot establish failure-detection quality.

## Uncertainty and limitations

The primary uncertainty uses 1,000 paired calendar-day cluster draws; all contain both outcomes. Only 17 final days and 22 failures are available. A two-day circular-block sensitivity gives {t['block_sensitivity']['lower']:.4f} to {t['block_sensitivity']['upper']:+.4f}, also inconclusive. Intervals condition on the fitted models and recorded period; hidden production batches and future drift remain unresolved. Sensor stability uses a separate 30-resample training procedure.

A development-only optimizer check corrected the degenerate all-zero coefficient case to its analytical training-prevalence intercept. This correction was committed before final results were inspected; it did not change the chosen C=.1 model. No failure labels or held-out metrics were changed. The protocol and tests record that numerical safeguard.

This short, historical, anonymous dataset is not evidence for a modern manufacturing deployment. No human engineering diagnosis or independent technical review is claimed; independent review remains pending.

## Reproduce and cite

Run `uv sync --frozen`, `uv run python -W error studies/S13/study.py`, then `uv run python scripts/report_s13.py`. [PROTOCOL.md](PROTOCOL.md), [DATA.md](DATA.md) and [results/result.json](results/result.json) contain the frozen design, hashes, all model comparisons and aggregate diagnostics. Individual measurements and predictions remain outside publication.

McCann, M. & Johnston, A. (2008). [SECOM](https://archive.ics.uci.edu/dataset/179/secom), UCI Machine Learning Repository, [doi:10.24432/C54305](https://doi.org/10.24432/C54305). Source data: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). This study transforms the source into original aggregate analyses; no publisher endorsement is implied.
''')
for path in (HERE/'results').glob('*.svg'):
 path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
print('Generated S13 report and two figures from',r['run_id'])
