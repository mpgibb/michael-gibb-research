"""Render advertising policy evidence directly from the saved run."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parents[1]/'studies/S04';r=json.loads((HERE/'results/result.json').read_text());t=r['tables'];d=t['primary_difference'];selected=t['selected_model'];names={m['id']:m['label'] for m in r['models']};metrics={m['model']:m for m in r['metrics']}
rows=['| Policy at 20% capacity | Benchmark conversions per 10,000 | 95% interval |','|---|---:|---:|']
for k,label in names.items():
 x=metrics[k];rows.append(f"| {label}{' · selected in validation' if k==selected else ''} | {x['estimate']:.2f} | {x['lower']:.2f} to {x['upper']:.2f} |")
sens=['| Selected policy sensitivity | Selected share | Contrast per 10,000 | 95% interval |','|---|---:|---:|---:|']
for x in t['sensitivity']:
 if x['model']==selected:sens.append(f"| {x['analysis']} | {x['selected_fraction']:.1%} | {x['estimate']:.2f} | {x['lower']:.2f} to {x['upper']:.2f} |")
report=f'''# S04 — Advertising incrementality evaluation

Run `{r['run_id']}` · analysis commit `{r['code_version']}` · {r['evaluated_on']}.

## Decision and executive summary

Do not replace response targeting solely because a method is designed to estimate uplift. At the prespecified 20% capacity, the honest causal forest selected on validation estimates **{metrics[selected]['estimate']:.2f} incremental benchmark conversions per 10,000 eligible records**, versus **{metrics['response']['estimate']:.2f}** for response targeting. The paired difference is **{d['estimate']:.2f}**, with a 95% interval of **{d['lower']:.2f} to {d['upper']:.2f}**. This test does not demonstrate an advantage for the uplift upgrade, and it does not prove exact equality.

Both targeted policies outperform expected random allocation in point estimates, but the main decision is whether the more complex targeting system improves on the existing alternative. Validate a change in a current randomized setting with known costs, rather than presenting this benchmark as advertiser ROI.

## Evidence

{chr(10).join(rows)}

All four advanced candidates remain visible. Selection used validation only; the selected forest has minimum leaf size 500. Final evaluation contains 398,506 records, 352,598 distinct feature profiles and 1,243 conversions. There are 60,018 control records with 127 conversions and 338,488 treatment-assigned records with 1,116 conversions. Labels are rare, especially in control, so capacity-specific contrasts are uncertain.

![Independent capacity comparison](results/policy-frontier.svg)

Treat-none is the zero endpoint. Treat-all estimates {t['all_vs_none']['estimate']:.2f} benchmark conversions per 10,000 relative to none (95% interval {t['all_vs_none']['lower']:.2f}–{t['all_vs_none']['upper']:.2f}). Random allocation is an analytical expected policy; its selected count and event counts are expected, not observed random draws. Policies are scored using independent final outcomes, not the sum of their own predicted effects.

## Source and assignment audit

The corrected v2.1 source has 13,979,592 rows and twelve features f0–f11. An outcome-independent hash sample keeps 1,995,142 records. Matching profiles cannot cross split boundaries. Model fitting uses 596,910 development records; validation uses 399,506. Additional development rows are excluded by a fixed profile-hash rule to bound fitting cost. No chronological split or independent person identifiers are invented.

Treatment propensity in final records ranges from {t['propensity']['min']:.3f} to {t['propensity']['max']:.3f}; no score hits the [.05,.95] clipping boundary. Assignment-prediction AUROC is {t['propensity']['assignment_auroc']:.3f}. Near-chance discrimination is a balance diagnostic, not proof that privacy sampling preserved causal exchangeability. Realized exposure and both outcome fields are excluded from predictors.

The publisher non-uniformly subsampled data for privacy. Causal interpretation requires assumptions within that released benchmark, and original advertiser incrementality/economics cannot be recovered. No actual campaign cost, future market effect or fairness conclusion is observed.

## Sensitivity and calibration

{chr(10).join(sens)}

The one-record-per-profile sensitivity retains the frozen policy selections; the resulting selected share changes and is shown explicitly. It changes the evaluation population and is not a same-capacity comparison. Complete decile effect calibration, feature balance and all model sensitivities are in the result JSON.

![Selected-model effect calibration](results/effect-calibration.svg)

Confidence intervals use profile-cluster influence sums and a finite-cluster correction. They condition on fitted models and rankings, do not adjust for unknown campaign dependence, and are not simultaneous guarantees across the plotted capacities. The primary paired comparison was fixed at 20% before final scoring. Sampling bias and causal-identification uncertainty are outside these statistical intervals.

## Economic scenarios

The web controls multiply independent benchmark conversions per 10,000 by an assumed value ($0–$1,000) and subtract selected fraction×10,000×assumed contact cost ($0–$10). The displayed interval rescales the held-out contrast interval under fixed assumed prices. It is not profit, advertiser ROI or a new experiment. Moving controls does not change measured policy evidence.

## Reproduction and attribution

See [README.md](README.md), [PROTOCOL.md](PROTOCOL.md) and [DATA.md](DATA.md). The result records the source checksum, exact code version, locked package versions, cross-fitting counts, tuning scores and all comparison tables. Individual records/predictions remain external. Independent technical review is pending.

Source: Diemert, E., Betlei, A., Renaudin, C. & Amini, M.-R. (2018), *A Large Scale Benchmark for Uplift Modeling*, AdKDD/TargetAd Workshop. [Corrected Criteo dataset](https://ailab.criteo.com/criteo-uplift-prediction-dataset/). Derived aggregate research tables: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/), with no warranty. Original analysis code is separate; raw data are not redistributed.
'''
(HERE/'REPORT.md').write_text(report)
plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,'svg.hashsalt':'s04-policy','text.color':'#0a192f','axes.labelcolor':'#334155'})
fig,ax=plt.subplots(figsize=(8,4.6),layout='constrained')
for name,color in [(selected,'#925322'),('response','#0a192f'),('random','#64748b')]:
 points=[x for x in t['capacity_frontier'] if x['model']==name];cap=[100*x['capacity'] for x in points]
 ax.plot(cap,[x['estimate'] for x in points],marker='o',ms=3,label=names[name],color=color)
 if name==selected:ax.fill_between(cap,[x['lower'] for x in points],[x['upper'] for x in points],color=color,alpha=.14)
ax.set(xlabel='Targeting capacity (% of final benchmark cohort)',ylabel='Incremental benchmark conversions per 10,000',title='No demonstrated uplift advantage over response targeting');ax.axhline(0,color='#cbd5e1');ax.grid(alpha=.15);ax.legend(frameon=False,fontsize=9)
fig.savefig(HERE/'results/policy-frontier.svg',metadata={'Date':None,'Creator':'Michael P. Gibb, Ph.D.'});plt.close(fig)
points=[x for x in t['effect_calibration'] if x['model']==selected];fig,ax=plt.subplots(figsize=(8,4.5),layout='constrained')
ax.errorbar([x['predicted_effect_per_10000'] for x in points],[x['estimate'] for x in points],yerr=[[x['estimate']-x['lower'] for x in points],[x['upper']-x['estimate'] for x in points]],fmt='o',color='#925322',capsize=3)
limits=[min(0,min(x['lower'] for x in points)),max(x['upper'] for x in points)];ax.plot(limits,limits,'--',color='#64748b');ax.set(xlabel='Mean predicted effect per 10,000 (decile)',ylabel='Independent benchmark contrast per 10,000',title='Effect calibration · selected honest forest');ax.grid(alpha=.15)
fig.savefig(HERE/'results/effect-calibration.svg',metadata={'Date':None,'Creator':'Michael P. Gibb, Ph.D.'});plt.close(fig)
for p in HERE.glob('results/*.svg'):p.write_text('\n'.join(x.rstrip() for x in p.read_text().splitlines())+'\n')
print('S04 report and figures exported.')
