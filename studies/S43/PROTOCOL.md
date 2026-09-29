# S43 — Frozen property-valuation protocol

Decision: judge whether a flexible location-aware model improves historical single-family sale-price estimates over local medians and a regularized hedonic model, while exposing geographic uncertainty. This is research, not an appraisal, lending decision, current property quote or observed business return.

## Inspected source and eligible unit

Use the Cook County Assessor's public 2024 final-run assessment input, `2024-03-17-stupefied-maya`, whose S3 Last-Modified is April 10, 2024. The file describes 2023 characteristics and contains 1,098,988 improvement/card rows, not unique parcels. Pin SHA-256 `86877d098101ca0c6ec4e77b9b0f5d5e3200e2b3fca6fe2c1a92e9044b3e9a9b`. Keep only modeling group SF, card1, non-multicard, non-multiland and non-prorated parcels. The inspected filtered snapshot contains 878,069 unique parcels. No card-level sale price is counted multiple times.

Join to the public Parcel Sales dataset `wvhk-k5uv`, monthly May2024–December2025 extracts (132,773 source sale rows). The characteristics file predates every included sale. Zero-pad PINs to 14 digits and validate many-sales-to-one-parcel joins. Drop multi-parcel sales and the publisher's explicit same-price-within-365-days, ≤$10,000 and excluded-deed flags. The publisher's duplicate-price filter looks backward. These rules cannot certify every transaction is arm's length. Any remaining duplicated document number is excluded as a group, not arbitrarily counted twice.

Before fitting, restrict target prices to $50,000–$3,000,000, building area to 500–10,000 square feet and land to 500–200,000 square feet; require finite valid Cook County-area coordinates (latitude41–43, longitude−89–−87). These are declared scope exclusions, not test-error trimming. Record all exclusions and missingness. Retain repeat-sale parcels with cluster-aware inference and a separate unseen-parcel stress view. Buyer/seller names, street addresses, raw PINs and precise individual coordinates are never published.

## Feature availability and calendar split

Predict from the fixed April2024 snapshot: building/land area, age, beds/rooms/baths, fireplaces, residential type, construction/roof/basement/air/garage attributes, township, latitude and longitude. Neighborhood identifies the simple local-median comparator and regularized hedonic geographic effects. Exclude later sale date/price, new assessments, buyer/seller fields, census demographics, income, tax-payment and exemption data, later renovation fields, recent-sale target aggregates and all post-snapshot updates. Snapshot age remains fixed; no knowledge of closing date is used as a feature.

Development: May–October2024 sales. Validation: November–December2024. Freeze selected settings, refit on May–December2024. Calibration: January–March2025, one last chronological record per calibration parcel. Final test: April–December2025. No fitting or tuning uses calibration/test sale prices. All snapshot predictors predate every split. Sale-record ingestion timestamps and original historical vintages are unavailable; this is a retrospective sale-date evaluation, not a proven real-time deployment replay. Current corrected sale records and selection can differ from what was known on a past reporting date.

## Models and comparison

Baseline: median training log sale price by snapshot neighborhood with ≥20 sales, otherwise township with ≥30, otherwise overall. Hedonic: Ridge(alpha=10, solver=lsqr) log-price regression with training-median numeric imputation and scaling, log1p areas, and training-only one-hot physical/geographic categories. Ridge shrinkage regularizes sparse neighborhood effects. Challenger: histogram gradient boosting on log price, 250 iterations, learning rate .05, L2=10, native training-mapped categories; compare 15 and31 leaves using validation median absolute percentage error. Native categories exclude high-cardinality neighborhood; coordinates and township provide spatial predictors. Early stopping is disabled. All models exponentiate log predictions; no final-outcome bias correction.

Ablation: refit the chosen challenger without coordinates or township. Assessment benchmark: prior-year board assessed value from the frozen snapshot ×10, matching the publisher's residential 10% assessment convention. Report it only on positive, available values; do not impute missing assessments or equate tax assessments with appraisal ground truth.

Primary: selected challenger minus hedonic median absolute percentage error, in percentage points, on the full final cohort. Also report log-price RMSE, median absolute dollar error and price ratio. Use500 paired spatial-grid-cluster bootstrap draws at .03° latitude/longitude bins, preserving all parcel repeats in each cell. Intervals condition on fitted models and this geographic/time sample; they do not prove future exchangeability.

## Intervals and stress tests

For each model, compute absolute calibration log residuals and the finite-sample order statistic ceil((n+1)×coverage) for nominal80%,90%,95% intervals. Exponentiate predicted log price ±radius. Empirical temporal, township, building-size and value-tier coverage is reported rather than asserting distribution-free guarantees under drift/dependence. No confidence level is selected by final coverage.

A spatial transfer stress test reserves cells with SHA256(`S43-`+cell_id) modulo5=0. Tune the same two challenger settings using only non-reserved development and validation cells. Refit hedonic and that stress-selected challenger with all fitting rows in reserved cells removed; calibrate using non-reserved cells only; evaluate reserved-cell final sales. A separate unseen-parcel slice excludes every final PIN that appears in fitting or calibration. These are named distinct estimands; neither replaces the primary final cohort after seeing outcomes.

Report local error/coverage for groups of at least30 sales, with cohort counts and aggregate centroids. Values above the calibration/training range are not silently clipped into plausible prices. Preserve poor local coverage. The interactive map will select aggregate township and building-size profiles, supported models and coverage levels; it reads saved historical price/interval distributions and local diagnostics, not an address-level valuation API. Include local training-comparable count and all-cohort fallback. Property profiles are groups of observed sales, not an arbitrary hypothetical home.

## Publication

Attribute Cook County Assessor's Office public data, both source versions and County terms. No endorsement or accuracy warranty is implied. Raw records remain external; share only aggregate derived findings, code, diagnostics and the 20-file checksum manifest. Do not copy County graphics. Independent technical review remains pending.
