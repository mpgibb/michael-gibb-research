"""Export workflow evidence from the recorded survival evaluation."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parents[1]/'studies/S58'
r=json.loads((HERE/'results/result.json').read_text());t=r['tables'];d=t['primary_difference'];names={m['id']:m['label'] for m in r['models']};metric={(m['model'],m['name']):m for m in r['metrics']}
rows=['| Model | Restricted-time MAE (days) | 95% interval | 14-day Brier score | 80% band coverage |','|---|---:|---:|---:|---:|']
for name,label in names.items():
 m=metric[name,'restricted_mae_days'];b=metric[name,'brier_14'];c=metric[name,'coverage_80']
 rows.append(f"| {label} | {m['estimate']:.3f} | {m['lower']:.3f}–{m['upper']:.3f} | {b['estimate']:.4f} | {c['estimate']:.1%} |")
transitions=['| Recorded stage transition | Observations | Median elapsed days | 90th percentile |','|---|---:|---:|---:|']
for x in t['workflow_transitions']:transitions.append(f"| {x['from']} → {x['to']} | {x['observations']:,} | {x['median_elapsed_days']:.3f} | {x['p90_elapsed_days']:.3f} |")
report=f'''# S58 — Where business workflows accumulate delay

Run `{r['run_id']}` · analysis commit `{r['code_version']}` · {r['evaluated_on']}.

## Decision and executive summary

Detailed workflow history improves delay forecasts only modestly over knowing an application's current stage and age. On 2,365 December applications, the selected survival model reduces average absolute forecasting error from **8.72 to 8.58 days**. The paired difference is **{d['estimate']:.3f} days** (95% interval **{d['lower']:.3f} to {d['upper']:.3f}**): about **1.6%**, or **3.3 hours less forecasting error**. This does not mean applications finished 3.3 hours faster.

An operations leader should use this as evidence for a bounded prioritization pilot, with a simple stage/age benchmark retained. At the twentieth event and 20% review capacity, the detailed model identifies 218 of 623 applications that remain unresolved after 14 days; the stage/age baseline identifies 215. The three-case point difference does not demonstrate that reviewing those applications will accelerate them.

The longest commonly observed stage gap is from A_Complete to A_Validating: a median 6.86 elapsed days across 266 observed transitions. That is a place to investigate process handoffs, not evidence of employee inefficiency or measured active service time. Operational staffing effects require an intervention or better arrival/service data.

## Evidence

{chr(10).join(rows)}

The primary paired comparison is fixed in the protocol. Intervals use 500 application-cluster bootstrap draws, retaining related prefixes together. The reduced-history hazard model has a slightly better 14-day Brier score than the full-history model; the extra history does not dominate every metric. Nominal 80% bands cover 88.5% for the selected model, so their conservative coverage should not be called exact calibration.

![Error comparison](results/remaining-time-error.svg)

All times are discrete remaining days capped at 30, ending at the first recorded A_Pending, A_Denied or A_Cancelled application status. This is not disbursement, final trace completion or an unrestricted-duration estimate. There are 6,247 eligible event prefixes across 2,365 final applications, including 183 prefixes with no observed endpoint before administrative follow-up ends. Every final prefix nevertheless has a complete 30-day horizon, so restricted-time error does not impute an unobserved tail.

## Data and timing

BPI Challenge 2017 contains 31,509 applications and 1,202,267 events. Related offers stay with their enclosing application. The audit finds no cross-application offer-reference conflicts, unordered traces or duplicated event IDs within an application. Lifecycle transitions remain distinct. Initial financial attributes, resource identities, application IDs and future statuses are excluded from predictors.

Applications opened January–August form development, September supplies validation, and December is the untouched final arrival cohort. Final training uses January–September applications with prefixes before November and outcomes through November 30. Prefix entry cutoffs ensure 30-day final follow-up. October/November applications do not enter final evaluation. Detailed eligibility counts, calendar cutoffs and source checksums appear in the artifact and [PROTOCOL.md](PROTOCOL.md).

Each application's available prefixes share total weight one. Stage/prefix diagnostic subsets retain those weights; they are not necessarily equal-weight cross-sections. Late-case capture uses one fixed-length prefix per application, so its counts are distinct applications. Diagnostic cells with fewer than 30 prefixes are withheld.

## Method and sensitivity

Two survival baselines are pooled Kaplan–Meier and current-stage/age-band Kaplan–Meier, with a pooled fallback for small training groups. The principal comparison is a discrete-time boosted hazard model, selected between 7 and 15 leaves using validation MAE only. The selected 15-leaf model and age/stage-only ablation are fitted once on final training. All preprocessing category mappings are training-only. Censored partial days contribute only complete observed risk intervals.

![Late-case prioritization](results/late-case-capture.svg)

Per-model probability calibration bins, stage/prefix errors, band coverage and all capacity points are retained in the JSON. Intervals condition on fitted models, one institution and one test month; they exclude refitting, future regime uncertainty and simultaneous comparisons across all sliders.

## Workflow and capacity scenarios

{chr(10).join(transitions)}

{t['transition_scope']} Early prefixes do not show every later loop. Neither the map nor the forecast identifies causally removable waiting time.

The interactive capacity scenario is explicit arithmetic: `remaining days × ((1 − addressable share) + addressable share / capacity multiplier)`. Addressable share (0–100%) and capacity multiplier (0.5–2.0) are assumed. At the default zero addressable share, the scenario equals the saved forecast. The calculation is not a queueing model, promised improvement, measured savings or changed prediction accuracy. Scenario outputs can exceed 30 days when assumed capacity falls; that extrapolation has no fitted survival interpretation.

## Reproduce and source

See [README.md](README.md), [DATA.md](DATA.md), [PROTOCOL.md](PROTOCOL.md) and [result.json](results/result.json). Figures and this report derive from the saved result using `uv run python scripts/report_s58.py`. Raw records and individual predictions stay outside the repository. Numerical verification is separate from independent human technical review, which remains pending.

van Dongen, B. (2017): *BPI Challenge 2017*. Eindhoven University of Technology / 4TU.ResearchData. [Dataset DOI](https://doi.org/10.4121/uuid:5f3067df-f10b-45da-b98b-86ae4c7a310b). Reuse is subject to the dataset's [4TU General Terms of Use (2016)](https://ndownloader.figshare.com/files/24080255), including noncommercial use, source citation and bibliographic publication notification. No source records are redistributed.
'''
(HERE/'REPORT.md').write_text(report)
plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,'svg.hashsalt':'s58-workflow','text.color':'#0a192f','axes.labelcolor':'#334155'})
fig,ax=plt.subplots(figsize=(8,4.3),layout='constrained')
for i,(name,label) in enumerate(names.items()):
 m=metric[name,'restricted_mae_days'];ax.errorbar(m['estimate'],i,xerr=[[m['estimate']-m['lower']],[m['upper']-m['estimate']]],fmt='o',capsize=4,color='#925322' if name=='hazard_boosting' else '#0a192f')
ax.set_yticks(range(len(names)),names.values());ax.set(xlabel='Restricted remaining-time MAE (days; lower is better)',title='Detailed history produces a small forecasting gain');ax.grid(axis='x',alpha=.15)
fig.savefig(HERE/'results/remaining-time-error.svg',metadata={'Date':None,'Creator':'Michael P. Gibb, Ph.D.'});plt.close(fig)
fig,ax=plt.subplots(figsize=(8,4.4),layout='constrained')
for name,color in [('stage_age_km','#0a192f'),('hazard_boosting','#925322'),('pooled_km','#64748b')]:
 points=[x for x in t['late_frontier'] if x['model']==name and x['prefix']==20];cap=[100*x['capacity'] for x in points]
 ax.plot(cap,[100*x['capture'] for x in points],marker='o',label=names[name],color=color)
 if name=='hazard_boosting':ax.fill_between(cap,[100*x['capture_interval']['lower'] for x in points],[100*x['capture_interval']['upper'] for x in points],color=color,alpha=.14)
ax.set(xlabel='Review capacity (% of applications at event 20)',ylabel='Share of late applications identified (%)',title='Prioritization is predictive, not a review intervention');ax.legend(frameon=False,fontsize=9);ax.grid(alpha=.15)
fig.savefig(HERE/'results/late-case-capture.svg',metadata={'Date':None,'Creator':'Michael P. Gibb, Ph.D.'});plt.close(fig)
for p in HERE.glob('results/*.svg'):p.write_text('\n'.join(x.rstrip() for x in p.read_text().splitlines())+'\n')
print('S58 report and figures exported.')
