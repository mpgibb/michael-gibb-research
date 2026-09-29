"""Render the spatial valuation result without introducing new estimates."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parents[1]/'studies/S43';r=json.loads((HERE/'results/result.json').read_text());t=r['tables'];d=t['primary_difference'];names={x['id']:x['label'] for x in r['models']}
rows=['| Model | Median percentage error | 95% interval | Log-price RMSE | Median absolute error |','|---|---:|---:|---:|---:|']
for name,label in names.items():
 m={x['name']:x for x in r['metrics'] if x['model']==name};p=m['median_ape_pct'];rows.append(f"| {label} | {p['estimate']:.2f}% | {p['lower']:.2f}–{p['upper']:.2f}% | {m['log_rmse']['estimate']:.3f} | ${m['median_absolute_error_USD']['estimate']:,.0f} |")
local=sorted([x for x in t['diagnostics'] if x['model']=='spatial_boosting' and x['grouping']=='meta_township_name'],key=lambda x:x['coverage_90'])
failure=['| Township | Final sales | Median percentage error | 90% interval coverage |','|---|---:|---:|---:|']+[f"| {x['group']} | {x['sales']:,} | {x['median_ape_pct']:.1f}% | {x['coverage_90']:.1%} |" for x in local[:5]]
(HERE/'REPORT.md').write_text(f'''# S43 — Chicago-area property valuation with honest geographic uncertainty

Run `{r['run_id']}` · analysis commit `{r['code_version']}` · {r['evaluated_on']}.

## Decision and executive summary

Do not choose a property-value model by its countywide score alone. On **24,551 later sale records**, spatial boosting has **17.29% median percentage error**, compared with **17.50%** for a regularized hedonic model. The primary paired difference is **{d['estimate']:.2f} percentage points** (95% interval **{d['lower']:.2f} to +{d['upper']:.2f}**). This does not establish a clear advantage over the simpler regression.

Location matters: removing location from the boosted model raises error to **26.48%**. But flexible location features do not solve local uncertainty. The nominal 90% intervals cover **89.8%** countywide yet only **70.1%** in the historical Hyde Park township cohort. That township is an assessment geography, not the smaller neighborhood commonly called Hyde Park. A near-target county average is not a reliable assurance for every local market.

A leader should require local interval audits and a route for cases outside the studied property scope. The site shows historical cohort distributions and measured local errors; it does not offer a current appraisal, an individual tax-appeal recommendation or an exact price quote.

## Evidence

{chr(10).join(rows)}

The final cohort contains 23,898 parcels in 331 spatial cells. The 500 paired .03-degree spatial-cluster bootstrap draws keep every repeat sale from a parcel together. Both principal models tend to underpredict: median predicted-to-observed ratios are about 0.93. Dollar error is virtually identical for the two models. All intervals condition on the fitted models and this historical sample.

![Accuracy and uncertainty comparison](results/model-comparison.svg)

## Data and information timing

The characteristics snapshot was last modified April 10, 2024 and describes 2023 property records. Every included sale occurs later, from May 2024 onward. Development has 16,519 May–October sales; validation has 4,327 November–December sales. Final fitting uses 20,846 May–December 2024 sales. January–March 2025 supplies 5,828 distinct calibration parcels. Final evaluation uses April–December 2025 sales. No closing date or later property update enters a predictor.

The original snapshot has 1,098,988 card rows; single-family, single-card, single-land-line and non-prorated restrictions yield 878,069 unique parcels. The sales source contains 132,773 records. Publisher multi-parcel/deed/duplicate/low-price flags exclude 34,637; 45,918 remaining sales do not match the eligible snapshot. Predetermined price/area bounds remove 953 more. The result artifact preserves each sequential exclusion, zero missing projected sale fields and full join checks.

Sales are drawn from a September 2026 corrected extract. Historical ingestion timestamps are unavailable, so chronological sale dates do not prove the same records were available in real time. Features are demonstrably pre-sale; label availability is a separate limitation. Buyer/seller names were never requested in the projected sales download. Raw addresses, PINs and precise property coordinates remain outside publication.

## Geographic uncertainty

{chr(10).join(failure)}

These are diagnostic groups, not newly selected primary hypotheses. Cells with fewer than 30 sales are withheld. Nominal 80%,90%,95% bands use a separate finite-sample log-residual calibration order statistic. Temporal drift, spatial dependence and repeated parcels violate simple exchangeability assumptions, so empirical local coverage remains visible rather than a guaranteed probability for a particular house.

![Geographic coverage](results/local-coverage.svg)

Countywide median 90% interval width is about $384,244 for spatial boosting. This is a wide band around heterogeneous historical sale predictions. The explorer's median lower/upper bounds summarize individual bands; they are not confidence bounds for the township's mean or median value.

## Stress tests and assessment benchmark

The spatial transfer check reserves 60 final grid cells and removes all fitting, tuning and calibration rows from those cells. On 5,064 final sales, spatial boosting has 18.68% median percentage error and 88.9% interval coverage, versus 19.24% and 86.6% for the hedonic comparator. This uses a separately tuned non-reserved development cohort and remains a supplementary comparison.

The previously unseen-parcel slice contains 22,938 sale records: no parcel appeared in fitting or calibration. Spatial boosting error is 16.46% and 90% coverage 90.8%. That slice has a different population from the primary cohort; it does not substitute for the main result after seeing performance.

The frozen prior-year board assessment, multiplied by 10 under the residential assessment convention, is available for 24,498 final sales; 53 are missing/nonpositive. It has 35.09% median percentage error on that available-case subset. Older assessed values are not ground truth or current appraisals, and this result is not an assessment-office performance review.

## Method, reproducibility and attribution

The simple comparator pools training neighborhood medians with township/global fallbacks. The hedonic model uses Ridge(alpha=10) with training-only numeric imputation/scaling and categorical encoding. The spatial challenger selects 31 versus 15 leaves using validation only; 250 iterations, learning rate .05 and L2=10 are fixed. A physical-only ablation removes coordinates and township. See [PROTOCOL.md](PROTOCOL.md), [DATA.md](DATA.md), [README.md](README.md) and [result.json](results/result.json).

Source: Cook County Assessor's Office, [public input files](https://github.com/ccao-data/model-res-avm#Getting-Data) and [Parcel Sales](https://datacatalog.cookcountyil.gov/d/wvhk-k5uv). The [County terms](https://www.cookcountyil.gov/terms-use) disclaim accuracy/completeness warranties and endorsement; no separate Creative Commons license is invented. No County graphics or raw records are redistributed. Source hashes, queries and versions are preserved. Independent technical review remains pending.

Recreate the figures and report with `uv run python scripts/report_s43.py`. The analysis uses a fixed historical snapshot; updated API records can fail checksum verification and must not silently replace the pinned input.
''')
plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,'svg.hashsalt':'s43-property','text.color':'#0a192f','axes.labelcolor':'#334155'})
fig,ax=plt.subplots(figsize=(8,4.3),layout='constrained')
for i,(name,label) in enumerate(names.items()):
 m=next(x for x in r['metrics'] if x['model']==name and x['name']=='median_ape_pct');ax.errorbar(m['estimate'],i,xerr=[[m['estimate']-m['lower']],[m['upper']-m['estimate']]],fmt='o',capsize=4,color='#925322' if name=='spatial_boosting' else '#0a192f')
ax.set_yticks(range(len(names)),names.values());ax.set(xlabel='Median absolute percentage error (%)',title='No clear gain over the hedonic comparator');ax.grid(axis='x',alpha=.15);fig.savefig(HERE/'results/model-comparison.svg',metadata={'Date':None,'Creator':'Michael P. Gibb, Ph.D.'});plt.close(fig)
fig,ax=plt.subplots(figsize=(8,7),layout='constrained');points=local;ax.barh([x['group'] for x in points],[100*x['coverage_90'] for x in points],color=['#925322' if x['coverage_90']<.85 else '#64748b' for x in points]);ax.axvline(90,color='#0a192f',linestyle='--');ax.set(xlabel='Observed coverage of nominal 90% prediction intervals (%)',title='Countywide coverage hides local gaps',xlim=(0,100));ax.tick_params(axis='y',labelsize=8);fig.savefig(HERE/'results/local-coverage.svg',metadata={'Date':None,'Creator':'Michael P. Gibb, Ph.D.'});plt.close(fig)
for p in HERE.glob('results/*.svg'):p.write_text('\n'.join(x.rstrip() for x in p.read_text().splitlines())+'\n')
print('S43 report and figures exported.')
