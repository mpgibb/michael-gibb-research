"""Build the report and aggregate figures from the saved evaluation."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'studies/S28'
r=json.loads((HERE/'results/result.json').read_text())
models={m['id']:m['label'] for m in r['models']}
metrics={(m['model'],m['name']):m for m in r['metrics']}
frontier=r['tables']['capacity_frontier']
selected=r['tables']['selected_model']
rows=['| Model | Log loss ↓ | Brier ↓ | AUROC ↑ | Responses at 20% | Precision (95% interval) |','|---|---:|---:|---:|---:|---:|']
for key,label in models.items():
 f=next(x for x in frontier if x['model']==key and x['capacity']==.2)
 rows.append(f"| {label} | {metrics[key,'log_loss']['estimate']:.4f} | {metrics[key,'brier']['estimate']:.4f} | {metrics[key,'auroc']['estimate']:.4f} | {f['responses']:,.1f} | {f['precision']:.1%} ({f['precision_interval']['lower']:.1%}–{f['precision_interval']['upper']:.1%}) |")
d=r['tables']['block_sensitivity'][0];s=r['samples']
report=f'''# S28 — Evaluation report

Run `{r['run_id']}` · analysis commit `{r['code_version']}` · {r['evaluated_on']}.

## Decision and executive finding

For limited contact capacity, keep a simple history-and-recency ranking as the benchmark before deploying a more complex response model. It identifies 934 recorded subscriptions among 1,647 selected contacts (56.7%), versus 843 (51.2%) for the logistic model chosen on earlier development records. Random allocation has an analytical expectation of 507.8 subscriptions at the same capacity.

The predeclared primary metric also favors the simple rule: logistic-minus-rule log loss is **{d['estimate']:.4f} natural-log units** (95% block-bootstrap interval **{d['lower']:.4f}–{d['upper']:.4f}**; lower loss is better). This is a negative finding for the proposed model upgrade. It does not show that contacting customers causes these subscriptions, and does not justify a production targeting rule without current validation and appropriate review.

## Evidence

{chr(10).join(rows)}

All model families are shown. The principal logistic family was chosen by development-fold log loss, before final holdout scoring. Expanded-feature boosting is a sensitivity analysis, not a second opportunity to select the final model. Random responses are expected, not observed selected counts. Ranking for the business rule uses its declared score; its proper-score metrics use separately calibrated probabilities.

![Saved capacity frontier](results/capacity-frontier.svg)

## Data and evaluation population

UCI Bank Marketing, bank-additional-full: {s['total']:,} source-ordered records, May 2008–November 2010. Development {s['train']:,} ({s['events']['train']:,} positive); calibration {s['calibration']:,} ({s['events']['calibration']:,} positive); final holdout {s['test']:,} ({s['events']['test']:,} positive). Outcome prevalence rises from {s['events']['train']/s['train']:.1%} in development to {s['events']['test']/s['test']:.1%} in evaluation. The file has no exact dates or stable customer IDs. A record is not necessarily an independent person.

There are 12 exact repeated rows, two held-out profiles matching earlier profiles when duration/outcome are omitted, and 570 held-out records whose month was unseen in development. Missing categorical values remain explicit unknown levels; default status is unknown in 8,597 records. Full missingness, category novelty and overlap sensitivity are in the JSON. No identity is inferred from matching anonymized fields.

## Failure analysis and sensitivity

![Chronological failure groups](results/period-diagnostics.svg)

Logistic log loss rises from 0.2725 in the first final-test quarter to 1.0836 in the fourth; the rule rises from 0.2803 to 0.8831. Final-quarter subscription prevalence is much higher than in model development. Earlier calibration does not protect against this shift. Subperiods are consecutive source-row groups, not claimed calendar quarters.

Changing bootstrap block size from 100 to 50 or 200 leaves the primary interval above zero. Dropping the two previously seen profiles does not reverse the main comparison. Adding demographics and loan/default attributes to boosting does not beat the simple rule on final log loss or at the specified 20% capacity. Such attributes are excluded from the primary ranking.

The 500-draw paired circular block bootstrap preserves short-range row dependence. Its intervals describe repeated sampling conditional on fitted models; they omit retraining uncertainty, cannot identify repeated customers, and do not measure causal effects. At a fixed capacity, bootstrap precision/capture resamples the frozen selected indicators; bootstrap selected counts may vary. It is not a confidence interval for the already observed finite-test count.

## Scenario interpretation

The interactive arithmetic is `assumed response value × observed selected subscriptions − assumed contact cost × selected contacts`. The supported inputs are $0–$1,000 assumed value and $0–$50 assumed cost, in hypothetical USD-equivalent units. These are not observed bank financials, profit, treatment effects or predicted future revenue. A scenario interval rescales the conditional precision interval at fixed selected count; it is not an interval for causal profit. Break-even value is assumed cost divided by observed response precision.

## Reproduction and boundaries

Run the commands in [README.md](README.md). [PROTOCOL.md](PROTOCOL.md) fixes splits, feature timing, candidate grids, selection and uncertainty. [DATA.md](DATA.md) records provenance and attribution. `results/result.json` contains all model scores, uncertainty, calibration bins, capacity points, period results, tuning scores and source/data hashes. This report and its SVG figures are regenerated by `scripts/report_s28.py`.

The NumPy correction changes two rounded supplementary outputs by 0.00000001; the primary estimates, counts and conclusion are unchanged. No evaluation design or grid was altered after viewing the holdout. Independent technical review is pending. The historical observed-contact cohort cannot establish causal gains, current bank performance, equal opportunity across groups or legal suitability of a targeting deployment.
'''
(HERE/'REPORT.md').write_text(report)
plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,'svg.hashsalt':'s28-evaluation','text.color':'#0A192F','axes.labelcolor':'#334155','axes.titlesize':13})
colors={'business_rule':'#925322','logistic':'#0A192F','boosting':'#64748b','random':'#a0aab5'}
fig,ax=plt.subplots(figsize=(8,4.6),layout='constrained')
for key,color in colors.items():
 points=[f for f in frontier if f['model']==key]
 ax.plot([p['capacity']*100 for p in points],[p['capture']*100 for p in points],label=models[key],color=color,marker='o',ms=3)
ax.set(xlabel='Contact capacity (% of final cohort)',ylabel='Captured recorded subscriptions (%)',title='Historical ranking performance — not incremental sales',xlim=(0,100),ylim=(0,100));ax.grid(alpha=.18);ax.legend(frameon=False,fontsize=9)
fig.savefig(HERE/'results/capacity-frontier.svg',metadata={'Date':None,'Creator':'Michael P. Gibb, Ph.D.'});plt.close(fig)
fig,ax=plt.subplots(figsize=(8,4.4),layout='constrained')
for key in ['business_rule','logistic']:
 points=[p for p in r['tables']['periods'] if p['model']==key]
 ax.plot([p['period'] for p in points],[p['log_loss'] for p in points],color=colors[key],label=models[key],marker='o')
ax.set(xlabel='Consecutive quarter of final source-row block',ylabel='Log loss (natural-log units; lower is better)',title='Probability forecasts deteriorate in later records',xticks=[1,2,3,4]);ax.grid(alpha=.18);ax.legend(frameon=False)
fig.savefig(HERE/'results/period-diagnostics.svg',metadata={'Date':None,'Creator':'Michael P. Gibb, Ph.D.'});plt.close(fig)
for path in HERE.glob('results/*.svg'):
    path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
print('Generated S28 report and two aggregate SVG figures.')
