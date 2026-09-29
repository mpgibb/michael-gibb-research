"""Render service-friction evidence, diagnostics and an explicit trial plan."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];HERE=ROOT/'studies/S47';r=json.loads((HERE/'results/result.json').read_text());t=r['tables'];d=t['primary_difference'];labels={x['id']:x['label'].split(' · ')[0] for x in r['models']}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none','svg.hashsalt':r['run_id'],'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(8,4.5))
for name,color in [('core/service_rule','#64748b'),('core/additive','#0a192f'),('core/boosting','#925322')]:
 rows=[x for x in t['capacity'] if x['model']==name];ax.plot([100*x['capacity'] for x in rows],[100*x['recall'] for x in rows],marker='o',label=labels[name],color=color)
ax.set(xlabel='Service queue capacity (% of final source rows)',ylabel='Observed churn captured (%)',title='Ranking identifies risk; it does not measure retention benefit',xlim=(0,100),ylim=(0,105));ax.grid(alpha=.15);ax.legend();fig.tight_layout();fig.savefig(HERE/'results/telecom-capacity.svg',metadata={'Creator':'Michael P. Gibb, Ph.D.','Date':None});plt.close(fig)
fig,ax=plt.subplots(figsize=(8,5.3))
for i,x in enumerate(t['effects']):ax.errorbar(100*x['risk_difference'],i,xerr=[[100*(x['risk_difference']-x['lower'])],[100*(x['upper']-x['risk_difference'])]],fmt='o',color='#925322',capsize=3)
ax.axvline(0,color='#64748b',linestyle='--');ax.set(yticks=range(len(t['effects'])),yticklabels=[x['feature'] for x in t['effects']],xlabel='Model-risk contrast (percentage points); 95% stability interval',title='Associations depend on what is held fixed');ax.grid(axis='x',alpha=.15);fig.tight_layout();fig.savefig(HERE/'results/telecom-associations.svg',metadata={'Creator':'Michael P. Gibb, Ph.D.','Date':None});plt.close(fig)
def metric(name,key):return next(x for x in r['metrics'] if x['model']==name and x['name']==key)
main=[]
for name in ['core/prevalence','core/service_rule','core/linear','core/additive','core/boosting']:
 x=metric(name,'log_loss');a=metric(name,'average_precision');c=next(x for x in t['capacity'] if x['model']==name and x['capacity']==.2);main.append(f"| {labels[name]} | {x['estimate']:.4f} ({x['lower']:.4f}–{x['upper']:.4f}) | {a['estimate']:.4f} | {c['churn_found']} / 94 | {100*c['recall_lower']:.1f}–{100*c['recall_upper']:.1f}% |")
variant='\n'.join(f"| {x['variant']} | {metric(x['variant']+'/boosting','log_loss')['estimate']:.4f} | {x['estimate']:+.4f} | {x['lower']:+.4f} to {x['upper']:+.4f} |" for x in t['variant_comparisons'])
effects='\n'.join(f"| {x['feature']} | {x['low_value']:g} → {x['high_value']:g} | {100*x['risk_difference']:+.1f} | {100*x['lower']:+.1f} to {100*x['upper']:+.1f} | {100*x['positive_fraction']:.0f}% |" for x in t['effects'])
raw='\n'.join(f"| {labels[x['model']]} | {x['log_loss']:.4f} | {metric(x['model'],'log_loss')['estimate']:.4f} | {x['predicted_observed_churn_ratio']:.3f} | {metric(x['model'],'predicted_observed_churn_ratio')['estimate']:.3f} |" for x in t['raw_probability_metrics'] if x['model'].startswith('core/'))
(HERE/'REPORT.md').write_text(f'''# S47 — Service-friction signals and a three-month churn planning window

Run `{r['run_id']}` · analysis `{r['code_version']}` · {r['evaluated_on']}.

## Decision and executive summary

A telecom service leader wants an early-warning queue that identifies customers at risk before deciding how to help them. In this small historical sample, **boosting improves forecast quality over additive regression even after excluding the uncertain status and calculated-value fields**. Final calibrated log loss is **0.0981 versus 0.1576**; lower is better. The paired difference is **{d['estimate']:.4f}**, with 95% profile-bootstrap interval **{d['lower']:.4f} to {d['upper']:.4f}**. This is predictive error, not a retention gain.

At 20% capacity, the service queue contains **124 of 624 final records**. Boosting identifies **90 of 94 observed churn outcomes** (95.7% recall, 95% interval 89.9–100.0%), versus **85** for additive regression and **57** for the complaint/low-usage rule. The boosted queue also contains **34 records that did not churn**, and misses **4 that did**. None of the 90 outcomes is claimed prevented.

Retain the service-friction fields for further prospective testing: dropping complaints and call failures worsens boosted log loss by **0.0511** (95% interval **0.0255–0.0774**). Adding Status or calculated Customer Value does not establish a clear further improvement. A larger score is not permission to use an inadequately timed field operationally.

Before using these rankings in a live service program, validate field timing and record identity on a later cohort, then randomize an actual recovery intervention. The file has **no customer ID or dates**, includes repeated and contradictory profiles, and comes from one company with an unspecified collection year. The documented planning gap cannot become a genuine out-of-time validation without additional data.

## Primary evidence and service capacity

The final partition contains **624 rows, 561 distinct primary-feature profiles and 94 churn labels** (15.1%). Identical primary profiles stay together in every partition and cross-validation fold. Rows are not represented as verified independent customers.

| Model | Log loss (95% interval) | Average precision | Churn in 124 contacts | Recall 95% interval |
|---|---:|---:|---:|---:|
{chr(10).join(main)}

![Observed churn captured at service capacity](results/telecom-capacity.svg)

The default boosted queue has 72.6% precision. Average precision is 0.949 (95% interval 0.906–0.974) versus additive 0.862 (0.792–0.923); chance prevalence is 0.151. The primary log-loss comparison is prespecified. Precision/recall are budget-specific descriptive outcomes, not estimated effects of making contact. Capacity ties use an outcome-independent hash of original row index. The prevalence reference uses that deterministic tie order; it is not a learned ranking.

## Feature sensitivity and probability calibration

Every variant keeps the same profile partitions and independently selects its model setting within development. Calibration always uses the separate calibration partition. Derived-field comparisons are sensitivities, not a revised primary model selected from the final result.

| Boosted feature variant | Log loss | Difference from core | 95% paired interval |
|---|---:|---:|---:|
{variant}

`core` has ten documented fields, excluding Status, Customer Value and redundant Age. `no_friction` additionally removes Complains and Call Failure. The other variants add Status, Customer Value or both. Value is calculated with an unspecified operational formula and is not verified profit. The publisher describes all predictors as first-nine-month summaries, but no source timestamps independently verify that assertion.

Probability recalibration is also an empirical choice with visible tradeoffs:

| Core model | Raw log loss | Calibrated log loss | Raw predicted/observed churn | Calibrated ratio |
|---|---:|---:|---:|---:|
{raw}

The boosted calibrated model predicts 1.104 times observed churn (95% interval 1.016–1.204), despite its strong ranking and lower log loss. Calibration raises total predicted events relative to the raw model. It slightly worsens additive log loss. These outcomes remain visible; no final-label recalibration or post-hoc replacement is performed. Ten equal-count probability bins are exported with profile-bootstrap uncertainty for their observed event rates.

Equal-profile weights change the estimand from rows to profiles. Boosted log loss is 0.0868 versus additive 0.1425 under those weights, preserving the ordering. This does not resolve whether repeated rows are duplicate customers. Age-group 1, age-group 5 and contractual-tariff final summaries are suppressed because they fail the prespecified 30-row/five-events-per-class rule; they remain in portfolio totals. Suppression is not evidence of subgroup parity.

## Service-friction associations and stability

The additive model provides controlled descriptions of **model behavior**, not causal effects. For a complaint, compare the predicted risk after setting Complains to one versus zero over the same development rows. For numeric fields, compare the development 75th versus 25th percentile while holding other fields fixed. Bootstrap intervals refit 100 profile-resampled development models at the selected setting, retaining the original calibration map.

| Feature | Low → high reference | Model-risk difference (pp) | 95% stability interval (pp) | Positive sign |
|---|---|---:|---:|---:|
{effects}

![Model association stability](results/telecom-associations.svg)

The complaint contrast is **+36.7 percentage points** (28.5–45.3), and the call-failure contrast is **+12.2 points** (6.8–17.3). Both are positive in all 100 refits. Increasing seconds while holding call count and other correlated measures fixed yields a positive contrast, whereas increasing call count yields a negative one. This is a warning about conditional interpretation and unusual feature combinations, not advice to increase calls or reduce call duration.

A possible causal structure illustrates the unresolved distinctions; arrows are hypotheses, not identified effects:

```mermaid
flowchart LR
 Q[Latent service quality] --> F[Recorded call failures]
 F --> C[Complaint flag]
 Q --> Y[Later churn]
 E[Latent engagement and alternatives] --> C
 E --> U[Observed usage]
 E --> Y
 R[Proposed randomized recovery offer] -. effect to measure .-> Y
```

Complaints can reveal service problems or a customer's pre-existing disengagement. Changing the complaint field in a model cannot estimate the benefit of resolving the underlying problem. No independently reviewed causal labels or intervention outcomes are invented.

## A prospective service-recovery experiment

The study does **not** run a campaign. The proposed next test would pre-register eligibility using pre-contact information, then randomize eligible customers 1:1 within risk strata to usual service or a specified additional recovery offer. Estimate intention-to-treat churn at three months, with persistent identities, safeguards against contamination, complete follow-up, uncertainty, contact/adverse outcomes and delivery-cost accounting. Complaint resolution is a secondary process measure, not a substitute for the churn endpoint.

A planning-only scenario assumes **15% control churn and a three-percentage-point reduction to 12%**, two-sided alpha .05, power .80, equal independent groups. The normal approximation needs **2,036 participants per arm, 4,072 total**. That exceeds this benchmark's entire sample and is not an experiment already run. Control rates 5–40% and reductions 1–10 points are user assumptions; infeasible reductions at or above baseline are rejected. Attrition, clustering, noncompliance and multiplicity require additional planning and are excluded here.

The formula is recorded in [PROTOCOL.md](PROTOCOL.md) and all saved grid values match the independent [statsmodels two-proportion sample-size implementation](https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.samplesize_proportions_2indep_onetail.html). It ignores the negligible far tail in the usual two-sided approximation. Neither a high-risk score nor a stable complaint association determines the assumed treatment effect.

## Data and estimation

[UCI Iranian Churn](https://archive.ics.uci.edu/dataset/563/iranian+churn+dataset), donated 2020, [doi:10.24432/C5JW3Z](https://doi.org/10.24432/C5JW3Z), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The official file contains 3,150 rows, 495 churn outcomes and no missing cells. The source describes first-nine-month predictor summaries and end-of-month-twelve churn; no calendar dates are supplied. Original aggregates and analysis are published with attribution, without endorsement or raw records.

There are 300 exact repeated full rows and 324 repetitions of the ten-field primary profile. Twenty-two profile groups have contradictory labels (83 rows); the largest group has 12 rows. No actual ID exists. Age is exactly mapped from five age groups to the representative values 15,25,30,45,55; it is not continuous observed age. Seven charge values equal ten despite a 0–9 dictionary range. Both issues are retained and documented rather than silently corrected. The contractual source cohort has only six churn outcomes.

A fixed grouped stratified five-way partition assigns 1,897 development rows/1,700 profiles/302 churn labels; 629 calibration rows/565 profiles/99 churn; and the untouched 624-row final partition. Three-fold outer development validation nests three-fold selection for core additive and boosting; all final variants select within development only. All variants choose C=10 for additive regression and fifteen leaves for boosting; core linear C=10. Exact nested scores and candidate losses remain in the artifact.

Log1p numeric inputs and training-fitted cubic splines/standardization provide additive structure; categorical features are one-hot encoded. Boosting uses raw numeric and encoded categorical values. No class weights or final-outcome thresholds are fitted. Learned models receive a reserved logistic calibration map; explicit rule/prevalence references retain their defined probabilities. Model-risk plots refer to the core additive fit, independent of the selected capacity scenario.

## Limits and reproduction

Small single-company cohort; no prospectively verified availability or later-time validation; no confirmed identities; residual dependence beyond identical profiles; correlated predictors; sparse subgroups; no intervention or profit measurement. Bootstrap intervals condition on fitted predictions and the observed sample. The effect stability analysis refits development but is still not a causal confidence interval. Independent technical review is pending.

Run `uv sync --frozen`, `uv run python -W error studies/S47/study.py`, then `uv run python scripts/report_s47.py`. [DATA.md](DATA.md), [PROTOCOL.md](PROTOCOL.md), pinned checksums and [results/result.json](results/result.json) record accounting, model selection, uncertainty and all scenarios. Set `RESEARCH_DATA_DIR` outside the checkout. Raw rows and verification predictions stay private.
''')
for path in (HERE/'results').glob('*.svg'):path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
print('Generated S47 report and figures from',r['run_id'])
