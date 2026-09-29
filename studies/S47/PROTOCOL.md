# S47 frozen service-friction evaluation

Freeze protocol and source before model fitting. Decision: compare three-month churn forecasts and quantify how heavily conclusions depend on complaint/usage and derived status/value fields. No automated customer action, causal retention estimate or individual service recommendation is made.

## Units, timing and partitions

Use the official audited CSV and documented first-nine-month features / month-twelve target. There are no dates or actual IDs; do not invent a temporal test. Retain every row, with repeated primary-feature profiles grouped together as documented in DATA.md. Exact row order provides only reproducible within-file indexing. Canonical profile hashes use the ten primary features, excluding target, Status, Customer Value and redundant Age; they remain the same for all feature variants.

A fixed five-fold StratifiedGroupKFold with shuffle and seed 470929 assigns fold zero to untouched final evaluation, fold one to probability calibration and folds two–four to model development. Every identical core profile stays in one fold, including contradictory-label groups. Publish actual rows/profiles/events and imbalance; do not claim a verified individual split. The final labels are used only for the frozen evaluation, not tuning, calibration or subgroup selection.

## Models and nested selection

Primary variants: `core` uses the ten audited primary fields; `no_friction` additionally omits Call Failure and Complains. Sensitivities `with_status`, `with_value`, `with_both` add the named uncertain derived fields to core. Do not treat sensitivity performance as proof of prospective availability or profit.

Comparators: constant development prevalence; complaint/low-usage cell rule (Complains × Seconds of Use below the training median), shrunk by 20 pseudo-observations toward development prevalence; ridge logistic core baseline; nonlinear additive logistic regression; histogram gradient boosting. No nonexistent recency variable is used. Additive and boosting comparisons execute all five variants; the constant, simple rule and linear model accompany core.

Numeric features: failures, tenure, charge band, seconds, call/SMS frequency, distinct called numbers; add Customer Value only where specified. Log1p numeric inputs for linear/additive models; StandardScaler learned within training. Additive uses cubic B-splines with five uniformly spaced knots in transformed training ranges, no extrapolation outside training boundaries (constant), no interactions. Age Group, Tariff and optional Status use training-fitted one-hot categories. Linear model uses the same transformed numerics without splines. Ridge C in {0.1,1,10}; no class weighting. Histogram boosting uses encoded categorical columns and raw numeric values, 150 iterations, .05 learning rate, L2=1, min leaf20, no early stopping; seven versus fifteen leaves. Missingness is absent and is not introduced artificially.

For additive/boosting core, report honest three-fold outer development validation; each outer training fold selects its setting using three inner stratified group folds on log loss. Final family/variant settings use three-fold grouped cross-validation over all development. The core nested estimate is a development diagnostic, not the untouched result. Fixed candidate order resolves ties. Every transformation fits inside its fold.

Fit selected models on development only. Apply a logistic probability calibration map (logit raw probability → label, ridge C=1) learned solely from the reserved calibration partition, separately per model/variant. Report raw and calibrated final metrics so calibration harm is visible. No final-threshold fitting. The constant/rule remain their explicit uncalibrated references.

## Evaluation, policy capacity and uncertainty

Primary comparison: calibrated final log loss, core boosting minus core additive, with 1,000 paired primary-profile cluster bootstrap draws and 95% percentile interval. Report Brier, average precision, ROC-AUC, prevalence and observed/expected churn totals. Report ten equal-count probability calibration bins, with bootstrap profile intervals for observed rate; these are descriptive and small-bin intervals can be unstable.

Saved capacity table covers 0/5/10/15/20/25/30/40/50/75/100% of final rows. Let k=floor(n×capacity); rank by calibrated risk. Ties use deterministic row key independent of outcome. Report selected rows, observed churn found, missed churn, non-churn contacts, precision and recall. No churn is called prevented. Report 95% profile-bootstrap recall intervals at each saved capacity, recomputing ranking in each resample. Sampling copies remain clustered but ranking treats each row in the sampled empirical population.

Report core group results for age group and tariff only where at least 30 rows and five churn/non-churn events; suppress insufficient groups, retaining them in totals. These are predictive error descriptions, not causal/fairness certification. Reweight core final metrics by reciprocal within-profile multiplicity so each profile has total weight one, as a duplication-sensitivity estimand; do not claim those weights identify actual customers.

## Associations and stability

Fit the selected core additive model to 100 profile-bootstrap development samples, retaining its chosen regularization, knots fitted in each resample and the original calibration map. For each bootstrap compute average model-risk contrasts over original development rows: Complains 1 minus 0, and each numeric feature's development 75th minus 25th percentile while holding the other fields at their observed values. Report full-fit effects, 2.5/97.5 percentiles and positive-sign fraction. These are model behavior and extrapolation-sensitive associations; correlated predictors mean they are not interventions or independent contributions. Fixed reference values and development rows never use final labels. Publish the complaint and call-failure contrasts prominently, not only effects with favorable signs.

A causal diagram separates latent service quality, engagement, usage, complaints and later churn. Shared causes and reverse pathways are unresolved. Turning a complaint flag from one to zero in a prediction model is not a valid estimate of fixing the complaint.

## Proposed randomized service-recovery experiment

The interaction outlines a prospective trial, without claiming it ran: pre-register eligibility before treatment; randomize eligible customers 1:1 within pre-treatment risk strata; usual service versus a specified additional recovery offer; intention-to-treat three-month churn; track complaint resolution and adverse/contact outcomes; keep persistent IDs and prevent cross-arm contamination; report uncertainty and total delivery costs.

Planning-only calculator: assumed control churn 5–40%, assumed absolute reduction 1–10 percentage points (must remain below baseline), two-sided alpha .05, power .80, equal independent groups. Required per-arm n is ceiling((z_.975 sqrt(2 pbar(1−pbar)) + z_.8 sqrt(p0(1−p0)+p1(1−p1)))²/(p0−p1)²), p1=p0−delta. Default p0=.15, delta=.03. Total is 2n. This normal approximation excludes attrition, clustering, multiplicity and noncompliance; recalculate for an actual trial. Historical ranking accuracy does not supply treatment effect or justify assumed reduction.

## Limitations and artifacts

Small, single-company sample with undisclosed collection year; unknown field timing beyond publisher statement; no verified IDs; ambiguous repeated rows; status/value definition; representative age categories; small contract segment; no prospective external validation or treatment assignment. Intervals condition on fitted models, whereas effect stability alone refits development. No independent technical review is claimed. Publish source/config, aggregate JSON, report/figures and saved interactive tables; no raw rows, profile hashes or individual predictions in the public artifact.
