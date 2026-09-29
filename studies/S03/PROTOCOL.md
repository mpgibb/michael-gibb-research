# S03 frozen customer-return evaluation

Freeze before fitting. Decision: assess purchase forecasts and campaign break-even assumptions for already observed customers. No observed churn labels or randomized win-back effect are available. No lifetime-value extrapolation or targeted contact is performed.

## Accounting, cohort and time

Follow DATA.md: exact complete-row deduplication, identified positive-price/quantity noncancelled lines, one purchase occasion per customer/calendar day. All calculations use source timestamps; cutoff c includes history strictly before c and outcomes in [c,c+h). Eligible customers first purchased by c−30 days. The first observed purchase defines model time zero; it is not proven acquisition. No future customer enters an earlier cohort.

Development cutoffs March 1, June 1 and September 1, 2010. Validation cutoff December 1, 2010. Final rolling cutoffs March 1, June 1 and September 1, 2011. Forecast horizons 30, 60 and 90 days; all are completely observed. The three primary 90-day final windows do not overlap. Households/customers recur across windows, so uncertainty resamples **customer IDs with all their final windows together**, not independent rows.

At each cutoff define repeat frequency x=purchase days−1, t_x=last−first purchase day, T=cutoff−first day and inactivity=cutoff−last day; model time is weeks. Record mean spend on repeat purchase days separately from the acquisition-like first day. Additional as-of features: count and gross spend in the last 30/90 days, lifetime observed count/spend, average purchase-day spend, age, inactivity, x, t_x and known calendar month. No net future spend, country, ID or future label is a feature.

## Baselines and principal models

- Recent-90-day rule: purchase-day count × h/90; expected spending multiplies that by the past-90-day average (fallback to observed lifetime mean). Purchase probability uses 1−exp(−expected count), explicitly a Poisson approximation.
- RFM cohort rule: inactivity 0–30, 31–90, >90 days crossed with prior purchase-day count 1, 2–5, 6+. Learn horizon-specific future counts, purchase probabilities and event-weighted spend from completed historical development snapshots, shrunk toward portfolio means (20 pseudo-customers; 10 pseudo-events for spend). It is a descriptive benchmark, not a calibrated causal segment.
- BG/NBD repeat-purchase model with Gamma-Gamma repeat-spend model. Fit population parameters to history available at each cutoff, by multi-start maximum likelihood; no future labels tune these parameters. Optimize positive log parameters with declared bounds, record convergence and boundary hits. Gamma-Gamma uses repeat purchasers with positive repeat mean spend, q>1 for a finite population mean; one-time buyers use its population mean. Test Pearson/Spearman association of repeat frequency and mean repeat spend as a diagnostic of the independence assumption.
- Flexible challenger: a histogram binary-purchase classifier multiplied by one plus a Poisson excess-count model fitted among future purchasers; Gamma conditional purchase-day spend regression uses positive future counts and count weights. This hurdle construction keeps expected count and purchase probability coherent. Numerical features above plus horizon. Fixed 150 iterations, learning rate .05, L2=1, minimum leaf 30, no early stopping; choose seven versus fifteen leaves. Poisson/Gamma fits estimate means, without assuming final conditional variances are Poisson/Gamma.

Select the challenger setting only on **90-day count Poisson deviance** in a deterministic half of December 2010 validation customers (SHA-256 `S03-validation:`+ID, first byte <128 for selection; the rest for interval calibration). Candidate order breaks ties. Only histories whose entire horizon ends at or before a forecast cutoff can train the supervised models. After selection, freeze complexity; at each final cutoff refit with the completed historical snapshots (including earlier final windows once observable). Validation-calibration rows remain excluded from supervised fitting. This is prespecified rolling-origin updating, never retrospective tuning on the current future window.

## Probabilities, distributions and interval checks

BG/NBD's alive probability is latent-model probability and is never scored as observed churn. Report the distinct probability of at least one purchase in h days against actual future purchasing. For zero repeat purchases, basic BG/NBD fixes alive probability at one; clearly expose that limitation.

Compute BG/NBD expected purchases by a positive Gauss–Jacobi integral over the conditional-alive beta dropout distribution, retaining the combined integrand so it remains finite when a≤1. Use 64 nodes and test against a 128-node calculation and independent simulation. Posterior-alive transaction rate is Gamma(r+x, rate α+T); dropout probability is Beta(a,b+x). Simulated future counts are min(Poisson(λh), Geometric(p)) when alive, otherwise zero. Draw 2,000 predictive replicates/customer with fixed seeds. Gamma-Gamma conditional rate is Gamma(q+p*x, rate γ+x*mean_repeat_spend); given N future purchases, total positive spend is Gamma(p*N, that rate), zero when N=0. Frequency/spend independence is an explicit assumption. Report 90% equal-tail count and spend interval coverage/width; intervals condition on estimated population parameters.

The challenger receives horizon-specific 90% empirical residual bands calibrated on the reserved half of December validation customers: |y−prediction|/sqrt(prediction+1) for count, |spend−prediction|/max(prediction,1) for revenue. Use the finite-sample ceil((n+1)*.9) order statistic. Lower limits truncate at zero; count limits round outward. Refitting, temporal dependence and seasonality mean no exchangeability guarantee is asserted. Report actual later coverage rather than labeling nominal intervals dependable.

## Evaluation and sensitivities

Primary: 90-day Poisson deviance difference, challenger minus BG/NBD, pooled across final customer-cutoff rows. Predicted means floor at 1e-8 only for log scoring. Report count MAE, future-purchase Brier/log loss, mean prediction/observed count, positive-spend MAE and predicted/observed gross-spend ratio, horizon/window/recency-frequency calibration and 90% interval coverage. Use 1,000 paired customer-cluster bootstrap draws and 95% percentile intervals for main metrics/difference. This conditions on fitted models and three historical windows, not independent seasons or future shocks.

Show return sensitivity by scoring the same gross-spend forecasts against separately recorded signed net spend. It is a target mismatch diagnostic, not a model claimed to predict negative revenue. Refit the frozen comparisons under the multiset-union accounting sensitivity, without retuning model complexity, to assess exact-line deduplication. Preserve all actual large purchases in the primary analysis. Report tail concentration without removing a disappointing held-out result.

## Cohort explorer and economic assumptions

Selectors choose saved final horizon (30/60/90), inactivity band and observed purchase-frequency band, with all-cohort options. Show mean predicted counts, probability of any purchase, latent BG/NBD alive probability, predictive count distribution (0,1,2,3,4,5+), actual purchasing, spend and interval coverage; fewer than 50 observations yield an explicit unavailable state. No individual-customer inference endpoint is exposed. Counts are customer-cutoff observations; unique-customer counts remain visible.

Assumed contact cost £0–£5 and contribution margin 10–50% produce a break-even **incremental purchase probability** = cost/(margin×predicted spend per purchase day). This assumes one incremental purchase occasion and omits displacement, channel costs and treatment heterogeneity. Do not subtract ordinary predicted purchase probability from that requirement or call it campaign ROI. No measured win-back lift exists. Reset controls return the whole cohort, 90 days, £1 and 30%.

## Method references and limitations

Fader, Hardie & Lee, [BG/NBD derivation](https://brucehardie.com/notes/039/) (2019); Schumacher, Fader & Hardie, [expectation derivation corrections](https://www.brucehardie.com/notes/041/) (2022); Fader & Hardie, [Gamma-Gamma monetary model](https://www.brucehardie.com/notes/025/) (2013). The method notes are cited, not redistributed. The combined-integrand implementation avoids incorrectly separating divergent expectations at a≤1.

Wholesale buyers, incomplete IDs, unknown acquisition dates, same-day aggregation, giftware seasonality, cancellations and older single-retailer coverage limit transportability. Purchase inactivity is not observed permanent churn. Revenue is not profit. Forecast distributions and economic scenarios do not prove intervention value. Independent technical review is pending.
