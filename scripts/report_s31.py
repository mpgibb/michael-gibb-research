"""Render the actuarial report and figures from the executed result artifact."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]; HERE=ROOT/'studies/S31'
r=json.loads((HERE/'results/result.json').read_text());t=r['tables'];u=t['scenarios']['uncapped'];c=t['scenarios']['capped'];g=t['geographic_stress'];d=u['primary_difference']
labels={m['id']:m['label'] for m in r['models']};short={'constant':'Portfolio mean','glm':'Poisson–Gamma','tweedie':'Direct Tweedie','boosting':'Boosted model'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none','svg.hashsalt':r['run_id'],'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(7.8,4.4))
rows=[x for x in u['metrics'] if x['name']=='tweedie_deviance']
for i,x in enumerate(rows):
 ax.errorbar(x['estimate'],i,xerr=[[x['estimate']-x['lower']],[x['upper']-x['estimate']]],fmt='o',color='#925322' if x['model']=='boosting' else '#0a192f',capsize=4)
ax.set(yticks=range(len(rows)),yticklabels=[short[x['model']] for x in rows],xlabel='Exposure-weighted Tweedie deviance (power 1.5; lower is better)',title='Full-loss accuracy does not establish a clear model upgrade');ax.grid(axis='x',alpha=.15);fig.tight_layout();fig.savefig(HERE/'results/insurance-accuracy.svg',metadata={'Creator':'Michael P. Gibb, Ph.D.','Date':None});plt.close(fig)
fig,ax=plt.subplots(figsize=(7.8,4.4));rows=[x for x in u['segments'] if x['model']=='boosting' and x['grouping']=='driver_age']
for i,x in enumerate(rows):ax.errorbar(x['predicted_observed_loss_ratio'],i,xerr=[[x['predicted_observed_loss_ratio']-x['ratio_lower']],[x['ratio_upper']-x['predicted_observed_loss_ratio']]],fmt='o',color='#925322',capsize=4)
ax.axvline(1,color='#64748b',linestyle='--');ax.set(yticks=range(len(rows)),yticklabels=[x['group'] for x in rows],xlabel='Predicted / observed total loss; 95% policy bootstrap interval',title='Portfolio calibration can hide segment differences');ax.grid(axis='x',alpha=.15);fig.tight_layout();fig.savefig(HERE/'results/insurance-segments.svg',metadata={'Creator':'Michael P. Gibb, Ph.D.','Date':None});plt.close(fig)
table=[]
for name,label in labels.items():
 x=next(x for x in u['metrics'] if x['model']==name and x['name']=='tweedie_deviance');p=next(x for x in u['segments'] if x['model']==name and x['grouping']=='portfolio')
 table.append(f"| {label} | {x['estimate']:.3f} | {x['lower']:.3f}–{x['upper']:.3f} | €{p['predicted_pure_premium']:.2f} | {p['predicted_observed_loss_ratio']:.3f} |")
stress='\n'.join(f"| {labels[x['model']]} | {x['estimate']:.3f} | {next(v['estimate'] for v in g['metrics'] if v['model']==x['model'] and v['name']=='predicted_observed_loss_ratio'):.3f} |" for x in g['metrics'] if x['name']=='tweedie_deviance')
(HERE/'REPORT.md').write_text(f'''# S31 — Insurance pricing: interpretable structure versus nonlinear accuracy

Run `{r['run_id']}` · analysis `{r['code_version']}` · {r['evaluated_on']}.

## Decision and executive summary

An insurance analytics leader needs an expected-loss model that improves decisions and remains calibrated across the portfolio. This evaluation **does not establish a clear full-loss accuracy advantage** for the boosted challenger over interpretable frequency–severity regression. On {r['samples']['test']:,} held-out policies and {r['samples']['test_claims']:,} claims, the primary deviance is 77.894 versus 78.424. The paired difference is **{d['estimate']:.3f}**, with 95% interval **{d['lower']:.3f} to {d['upper']:+.3f}**. Lower is better; this is a prediction-error measure, not a percentage saving.

The full-loss portfolio records **€147.76 per policy-year**. Boosting predicts **€138.35**, about 6.4% below that recorded average; the interpretable model predicts **€158.74**, about 7.4% above it. Uncertainty includes exact calibration for both models. An expense loading cannot repair a biased or unstable expected-loss estimate.

Keep the interpretable comparator and require tail and segment evidence before replacement. The largest 1% of source claims account for 38.0% of recorded loss. Better performance after limiting claim size does not establish dependable full-tail pricing. These are historical model comparisons, not current quotes, regulatory filings or realized savings.

## Evidence from the untouched policy holdout

| Model | Tweedie deviance | 95% interval | Estimated €/policy-year | Predicted / observed total loss |
|---|---:|---:|---:|---:|
{chr(10).join(table)}

![Final full-loss model comparison](results/insurance-accuracy.svg)

Deviance uses fixed power 1.5 and exposure weights. It compares mean predictions while respecting unequal exposure. The result includes exposure-weighted absolute error, portfolio calibration, ten risk-group calibration tables and frequency/severity decomposition. Direct Tweedie estimates pure premium directly and has no fitted frequency/severity components. The constant training-portfolio reference is also reported, rather than omitted after comparison with fitted models.

Boosting predicts 7.33 claims per 100 policy-years and €1,886.53 per predicted claim, versus 7.52 observed claims and €1,965.01 observed average severity. Cohort-level predicted severity is weighted by predicted event frequency so the decomposition exactly reconstructs expected total loss. It is not an unweighted average of policy severities.

## Segments, tail sensitivity and geographic transfer

![Driver-age loss calibration](results/insurance-segments.svg)

For the 60+ driver cohort, boosting's predicted/observed full-loss ratio is 0.721 (95% interval 0.546–1.005), based on 22,637 final policies and 887 claims. Area F has ratio 0.604 (0.315–1.311) on 3,628 policies and 150 claims. These descriptive slices show wide uncertainty; they are neither causal effects nor a fairness certification. Region, Area and age cohorts require at least 500 final policies. Small suppressed regions remain in portfolio totals.

The separately fitted **€50,000 per-claim sensitivity** has final boosting deviance 71.304 versus 72.025 for the interpretable model, difference **{c['primary_difference']['estimate']:.3f}** (95% interval **{c['primary_difference']['lower']:.3f} to {c['primary_difference']['upper']:.3f}**). It uses settings selected on uncapped development outcomes, without retuning. Capped observed loss is €130.75 per policy-year; boosting predicts €123.93. This is a different target, not an actual policy limit or evidence that large claims disappear.

All **69,789 Ile-de-France policies** and 2,591 claims are reserved for a separate geographic stress test. Both models omit Region and train on 485,915 non-reserved development/validation policies. Their settings are selected only on non-reserved development/validation; no reserved-region outcomes enter fitting or selection.

| Geographic-stress model | Tweedie deviance | Predicted / observed loss |
|---|---:|---:|
{stress}

The stress-test difference is **{g['primary_difference']['estimate']:.3f}** (95% interval **{g['primary_difference']['lower']:.3f} to {g['primary_difference']['upper']:.3f}**), favoring boosting. Nevertheless, boosting overpredicts reserved-region loss by 19.1% (95% ratio interval 1.045–1.374). A better relative score does not mean absolute calibration. This is a different population and model specification, not a substitute for the primary test or future-time evidence.

## Data audit and estimation

The archived CASdatasets 1.2-0 files contain 677,991 policies and 26,444 claims, approximately 2011–2013. Exposure totals 358,482.835463 policy-years; nominal claim loss totals €59,909,216.50. Every claim matches a policy and every policy's severity-row count equals ClaimNb. There are no missing fields. Keep all 235 repeated severity rows because identical settlement amounts can be distinct claims. Keep 1,224 exposures above one year, up to 2.01. The maximum claim is €4,075,400.56; 88 claims exceed €50,000 and together account for €17,917,329.27. The single largest claim is 6.8% of source loss.

The salted SHA-256 policy split supplies 405,817 development policies, 135,903 validation policies and 136,271 final policies. Final fitting uses 541,720 development/validation policies. ID factor labels, not internal R factor codes, join the files and determine allocation. No reliable policy dates exist; no temporal validation is claimed. Source risk-field timing and ultimate claim maturity remain unverified.

Poisson frequency uses count/exposure with exposure weights, equivalent to a count likelihood with log-exposure offset. Gamma severity uses policy-average claim amount with claim-count weights, equivalent parameter estimation to repeated claim rows with shared predictors. Cubic age splines, transformed density/bonus-malus and one-hot risk categories are fitted in permitted training data. Direct Tweedie uses the same feature structure. Boosting uses numerical ages/transforms and categorical splits. All models exclude ID, claims, loss and exposure as predictors.

Validation selects alpha .0001 for both regression families and seven leaves for boosting. The frozen alternative settings remain in the tuning table. No final calibration or additional hyperparameter search is performed. Mean squared Pearson count residuals are 1.778 for Poisson regression and 1.741 for boosting, indicating residual overdispersion relative to the Poisson variance assumption. Mean estimation and empirical policy bootstrap are used; no Poisson claim-count prediction intervals are claimed.

## Uncertainty, interaction and limits

The primary and geographic comparisons use 500 paired policy bootstrap draws; each segment uses 250 draws. Different Monte Carlo samples can yield slightly different portfolio-ratio intervals in the metrics and segment tables. They estimate uncertainty conditional on fitted models and the empirical tail. Repeated policyholders, common shocks, claim development, future inflation and unseen catastrophes are not resolved. There is no independent temporal replication.

The website explorer switches saved model, cohort and full/capped outcomes. A separate assumed expense loading, 0–50%, calculates pure premium/(1−loading). The default full-loss boosted estimate at 20% loading is €172.93 per policy-year. Loading is not estimated from data, and profit, taxes, capital, reinsurance and regulatory constraints are omitted. Controls never refit models or change held-out accuracy.

Independent technical review is pending. No individual insurance decisions are taken. Historical French claims do not validate a current rate filing, fairness assessment or causal explanation.

## Reproduce and cite

Run `uv sync --frozen`, `uv run python -W error studies/S31/study.py`, then `uv run python scripts/report_s31.py`. [PROTOCOL.md](PROTOCOL.md), [DATA.md](DATA.md) and [results/result.json](results/result.json) record the frozen design, exact archived inputs, checksums and all aggregate comparisons. Source policy data and individual predictions remain outside publication.

Dutang, C.; Charpentier, A.; Gallic, E. [Insurance dataset](https://doi.org/10.57745/P0KHAG), Recherche Data Gouv, version 1.1, July 12, 2024; CASdatasets 1.2-0, file [doi:10.57745/ULR0ZA](https://doi.org/10.57745/ULR0ZA). [Publisher dictionary](https://dutangc.github.io/CASdatasets/reference/freMTPL.html). Dataset metadata: Etalab Open Licence 2.0. Package code: GPL >=2. This study publishes original analysis and aggregates with source attribution; no publisher endorsement is implied.
''')
for path in (HERE/'results').glob('*.svg'):path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
print('Generated S31 report and two figures from',r['run_id'])
