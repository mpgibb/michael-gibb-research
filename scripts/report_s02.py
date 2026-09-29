"""Export the inventory evaluation narrative and figures from saved aggregates."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parents[1]/'studies/S02'
r=json.loads((HERE/'results/result.json').read_text());t=r['tables'];names={x['id']:x['label'] for x in r['models']};names['conventional_mean']='Conventional prior-cycle target'
m={(x['model'],x['name']):x for x in r['metrics']};d=t['primary_difference']
improvement=1-m['quantile_boosting','weighted_scaled_error_28d']['estimate']/m['seasonal_28','weighted_scaled_error_28d']['estimate']
rows=['| Model | Cycle error ↓ (95% interval) | Scaled pinball ↓ | 80% band coverage |','|---|---:|---:|---:|']
for name in names:
 if name=='conventional_mean':continue
 score=m[name,'weighted_scaled_error_28d'];rows.append(f"| {names[name]} | {score['estimate']:.4f} ({score['lower']:.4f}–{score['upper']:.4f}) | {m[name,'scaled_pinball']['estimate']:.4f} | {m[name,'coverage_80']['estimate']:.1%} |")
scenario=[x for x in t['inventory_scenarios'] if x['scenario_id']=='L3-H0.01-P1-K1'];q=next(x for x in scenario if x['model']=='quantile_boosting');b=next(x for x in scenario if x['model']=='conventional_mean')
inv=['| Policy | Assumed cost | Lost scenario units | Cost minus conventional (95% interval) |','|---|---:|---:|---:|']
for x in scenario:
 ci=x['cost_difference_interval'];inv.append(f"| {names[x['model']]} | ${x['assumed_cost']:,.2f} | {x['lost_units']:,.0f} | ${x['cost_difference_vs_conventional']:,.2f} (${ci['lower']:,.2f} to ${ci['upper']:,.2f}) |")
report=f'''# S02 — Inventory forecasting evaluation

Run `{r['run_id']}` · analysis commit `{r['code_version']}` · {r['evaluated_on']}.

## Decision and executive summary

A replenishment planner needs both an accurate sales forecast and an explicit service/cost tradeoff. On 210 product/store series across four final 28-day windows, global quantile boosting reduces the primary cycle forecast error by **{improvement:.1%}** against repeating the previous cycle. The challenger-minus-baseline difference is **{d['estimate']:.4f}** (95% item-cluster interval **{d['lower']:.4f} to {d['upper']:.4f}**). Lower is better. This supports further operational validation, not a promise of realized savings.

In the default replay—three-day lead time, $0.01 holding per unit/day, $1 per lost unit, storage equal to prior-cycle sales—the challenger costs **${q['assumed_cost']:,.2f} versus ${b['assumed_cost']:,.2f}** under the assumed costs. It nevertheless loses **{q['lost_units']:,.0f} versus {b['lost_units']:,.0f} scenario units**. Lower cost and better service are different objectives. Recorded sales are not unconstrained demand, and actual inventory, margins and costs are unavailable.

## Measured forecast evidence

{chr(10).join(rows)}

The 840 final product/store cycles contain 30,600 recorded unit sales. This is a fixed 21-item assortment spanning all ten stores and seven departments, selected using identifiers and pre-tuning price availability. Results do not describe all 30,490 source series. The cycle-total metric differs from the competition's daily WRMSSE. Revenue weights and scale denominators use only eligible prior observations.

![Forecast error at each held-out origin](results/forecast-errors.svg)

The 80% forecast bands cover 88.3% of final bottom-level cycles for the challenger; that aggregate number does not imply calibrated coverage for each store or future period. Store/category/total tables, all four origins, subgroup failures and dependence ablations remain in the result JSON. Aggregate scenarios sum exactly; marginal quantiles are not additive. The 17 overlapping calibration windows provide limited support for uncertainty and cross-series dependence.

## Explicit inventory scenario

{chr(10).join(inv)}

The same initial stock, one-order constraint, arrival date and capacity apply to every policy and to the exact hindsight comparator. Hindsight cost is ${q['hindsight_cost']:,.2f} in this default setting; the challenger regret is ${q['regret']:,.2f}. This is a constrained simulator comparison, not an achievable observed retailer saving. All 36 prespecified combinations of lead time, holding, lost-sale penalty and storage remain visible. Boosting has lower assumed total cost than the conventional target in all 36 tested settings; that finite sensitivity grid is not a universal guarantee.

![Capacity, service and assumed cost](results/scenario-frontier.svg)

## Method and uncertainty

Two leaf-count settings are compared only at d_1689. The selected {t['selected_leaves']}-leaf quantile models use lagged sales, deterministic calendar fields, known item/store categories and completed-week prices. Models refit on eligible past examples at every forecast origin. Training labels must finish before each origin. The 17 intermediate calibration origins precede all final windows. The final four 28-day windows are non-overlapping; later rolling fits may learn earlier realized outcomes without changing settings.

Whole residual-rank vectors construct joint quantile scenarios. An independent-rank ablation illustrates sensitivity of aggregate intervals to dependence. The 256 draws do not constitute 256 independent observed histories. Paired resampling of 21 item clusters retains each item's ten stores and four dates. These intervals are conditional on the fixed stores, dates and fitted models. They do not establish population representativeness or capture future economic-regime uncertainty.

There are no observed stock levels or stockout flags. No purchase cost, ordering fee, spoilage or real margin is assumed known. The service/cost decision is an explicitly hypothetical replay of observed sales. Source dates, sums and prices are not evidence of deployment outcomes. Independent technical review is pending.

## Reproduction

[DATA.md](DATA.md) records exact organizer downloads and checksums; raw files stay outside the repository. [PROTOCOL.md](PROTOCOL.md) fixes the split and evaluation before fitting. Run the commands in [README.md](README.md). The result contains versioned metrics and aggregate tables; `scripts/report_s02.py` exports this report and figures. The external verification artifact retains final predictions for arithmetic checks without publishing individual series histories.
'''
(HERE/'REPORT.md').write_text(report)
plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,'svg.hashsalt':'s02-inventory','text.color':'#0a192f','axes.labelcolor':'#334155'})
colors={'seasonal_7':'#64748b','seasonal_28':'#925322','quantile_boosting':'#0a192f','conventional_mean':'#a0aab5'}
fig,ax=plt.subplots(figsize=(8,4.5),layout='constrained')
for name in list(names)[:3]:
 points=[x for x in t['metrics_by_origin_level'] if x['level']=='bottom' and x['model']==name]
 ax.plot(range(1,5),[x['weighted_scaled_error_28d'] for x in points],marker='o',color=colors[name],label=names[name])
ax.set(xticks=[1,2,3,4],xlabel='Final 28-day window (chronological)',ylabel='Weighted scaled cycle error · lower is better',title='Quantile boosting improves the bounded forecast comparison');ax.grid(alpha=.15);ax.legend(frameon=False)
fig.savefig(HERE/'results/forecast-errors.svg',metadata={'Date':None,'Creator':'Michael P. Gibb, Ph.D.'});plt.close(fig)
fig,ax=plt.subplots(figsize=(8,4.5),layout='constrained')
for name in names:
 points=sorted([x for x in t['inventory_scenarios'] if x['model']==name and x['lead_days']==3 and x['holding_per_unit_day']==.01 and x['lost_sale_penalty']==1],key=lambda x:x['storage_multiplier'])
 ax.plot([100*(1-x['lost_units']/30600) for x in points],[x['assumed_cost'] for x in points],marker='o',color=colors[name],label=names[name])
ax.set(xlabel='Scenario unit fill rate (%)',ylabel='Assumed cost (USD)',title='Three capacity settings · 3-day lead, $0.01 holding, $1 lost unit');ax.grid(alpha=.15);ax.legend(frameon=False,fontsize=9)
fig.savefig(HERE/'results/scenario-frontier.svg',metadata={'Date':None,'Creator':'Michael P. Gibb, Ph.D.'});plt.close(fig)
for p in HERE.glob('results/*.svg'):p.write_text('\n'.join(x.rstrip() for x in p.read_text().splitlines())+'\n')
print('S02 report and two figures exported from saved results.')
