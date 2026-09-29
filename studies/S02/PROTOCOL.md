# S02 — Frozen inventory-planning evaluation

Frozen before model fitting, tuning or holdout scoring. This bounded study forecasts **28-day unit-sales totals per product/store** for a replenishment-cycle decision. It is not an entry on the M5 daily-forecast leaderboard. Recorded sales are not latent demand.

## Cohort, timing and access

Use the four official M5 files and SHA-256 values in config.json. The organizer's distribution omits the Kaggle `id`/`d` convenience fields: join on item_id/store_id, derive source day number from the consecutive calendar beginning 2011-01-29, and verify all joins. The train file ends d_1941; the separate evaluation file covers d_1942–d_1969. No raw files are redistributed.

Select three item IDs per department by ascending SHA-256 of the ID, from products priced in all ten stores by the last completed week before the tuning origin. Keep all ten stores: 21 products, 210 series. Selection uses identifiers and prior availability only, never final sales. This is a bounded subset, not a claim about all 30,490 M5 series.

A forecast origin is the close of the indicated source day. Features include only sales through that day and prices from fully completed earlier weeks. Do not use future prices, promotion outcomes, or revised macro data. Calendar predictors are deterministic month/day-of-week and horizon season, not undocumented future event announcements. Each training example's full 28-day outcome must end on/before its model's training cutoff. Fit all preprocessing within permitted data. Product/store IDs describe this fixed known assortment; this is not a cold-start evaluation.

## Model development and evaluation

Training origins are every seven days in the preceding 730 days, with at least 365 days of history and 28 days of observed subsequent outcome. The fixed comparisons are (1) repeating last week's sales for four weeks, (2) repeating the last 28-day sales total, and (3) global histogram gradient-boosted 0.1/0.5/0.9 quantile models. Compare 7 versus 15 leaves at one tuning origin d_1689 (2015-09-13); select mean normalized pinball loss across all three quantiles, with grid order breaking ties. Use 120 boosting iterations, learning rate .05, L2=1, no early-stopping random split and the fixed seed. Do not tune again using later outcomes.

Out-of-time calibration origins are weekly d_1717–d_1829 (17 origins), with each 28-day outcome fully observed by d_1857. They supply forecast residual distributions and their cross-series rank dependence. Final, non-overlapping target windows follow d_1857, d_1885, d_1913 and d_1941; the final target ends June 19, 2016. Refit on eligible past outcomes at each origin, without changing model settings. Later rolling origins may learn earlier realized outcomes; no future observation enters an earlier forecast.

Baselines use the empirical signed errors of their separate calibration forecasts. The quantile challenger uses its predicted marginal quantiles and historical calibration residual ranks (a Schaake-style rank shuffle). Use 256 seeded joint draws sampled as whole calibration-origin vectors, preserving cross-series ordering; piecewise interpolation extends tails linearly and clips below zero. The 17 overlapping calibration windows are a small dependent support, not 256 independent historical samples. Do not claim exact distributional calibration.

Every scenario is aggregated from bottom-level series to store, category and total, guaranteeing accounting consistency per draw. Aggregate quantiles are computed from those aggregate scenarios; do not sum marginal quantiles and call that an aggregate quantile. Point forecasts sum bottom-level medians. A shuffle-independence ablation resamples ranks independently across series to show the sensitivity of aggregate intervals to dependence assumptions.

## Metrics, uncertainty and diagnostics

Primary: weighted scaled absolute error of 28-day totals, averaged across the four final origins. Scale each series by the square root of the mean squared differences between past, non-overlapping 28-day sales totals (floor one unit). Weights use prior 28-day sales times last-known eligible price, normalized within each level/origin. A completely zero-weight assortment uses equal weights; a zero-weight diagnostic subgroup uses its unweighted mean. This is explicitly a cycle-total metric, not the competition's daily WRMSSE.

Also report weighted scaled pinball loss, empirical 80% interval coverage and interval width by bottom/store/category/total. Pinball scaling uses past mean absolute consecutive-cycle change (floor one unit). Show all origins, category/store failure groups, zero-sale prevalence and information-timing/price-join diagnostics. Intervals for bottom-level policy/model differences use 500 paired item-cluster bootstrap draws; keep all stores and forecast origins together for each sampled item. They quantify item-sampling uncertainty conditional on these stores, dates and fitted models, not uncertainty across future economic regimes.

## Explicit inventory replay

Re-use observed daily sales as *scenario demand* over a single 28-day replenishment cycle. This is not a reconstruction of real stockouts. Make one order at the origin; it arrives before demand on day L+1 for L in {0,3,7}. Initial stock is the ceiling of historical daily mean times L, capped by storage. Storage is 0.5/1/2 times the previous 28-day sales (ceil, minimum one). Reserve space for the entire order at decision time: order <= storage minus initial stock. No backorders or additional orders; unmet scenario demand is lost.

Each forecast policy uses a quantile at p/(p+28h), with assumed lost-sale penalty p in {1,5} dollars/unit and holding h in {.01,.05} dollars/unit/day, interpolated from its joint marginal scenarios. Order up to that forecast target minus initial stock, subject to the same storage rule. An additional conventional policy orders to the prior 28-day mean total. No ordering/purchase cost, spoilage or actual retailer margin is observed.

Measure scenario holding cost, lost units, unit fill rate and total assumed cost. The hindsight comparator chooses the exact integer one-time order minimizing the same cost under identical initial stock, arrival and space constraints; implement/test the convex discrete search against brute force. Regret is a simulator comparison, not realized savings. Holding and lost-sale costs, lead time and storage are explicit sensitivity axes. These controls do not alter measured holdout forecast quality.

## Publication boundaries

Publish model comparisons, permitted aggregate forecast tables, coverage/failure diagnostics, scenario accounting, data/code versions and source citations. Do not publish raw sales/price files or claim causal stockout reductions. Preserve adverse/inconclusive results. Independent technical review is pending.
