# S31 frozen evaluation protocol

Frozen before any model fitting. Scope: historical French motor expected claim cost, not individual eligibility, a rate filing, a current price recommendation or causal risk factors.

## Population, target and allocation

Retain all 677,991 policies and 26,444 positive claim rows. Join at unique policy grain after aggregating severity; validate claim counts and retain repeated claim amounts and exposure above one year. Unit: policy. Primary target: uncapped aggregate claim euros divided by recorded policy-years. Frequency is claims/policy-year; conditional severity is euros/claim. The frequency×severity mean models event-weighted severity; it does not assume every claim or policy has an identical severity distribution.

SHA-256 of the fixed salt plus textual policy ID allocates the first unsigned 64-bit integer divided by 2^64: below .6 development, [.6,.8) validation, [.8,1) final. Claims from a policy stay together. IDs and split are not predictors. There is no invented time holdout or claim that policy IDs identify independent drivers. Final data are used once after settings are selected; audit totals are not tuning evidence.

## Models and selection

1. Training portfolio mean loss/exposure, with mean frequency and claim-weighted mean severity, is the constant reference.
2. Interpretable Poisson log-link frequency plus Gamma log-link severity. Fit frequency to count/exposure with exposure weights: equivalent to a Poisson count model with log-exposure offset. Fit severity to policy loss/claim count on claimants with claim-count weights: equivalent parameter estimation to repeated claim-level outcomes sharing the same predictors. Report count dispersion to diagnose Poisson mean/variance mismatch; no Poisson sampling intervals are claimed.
3. Direct log-link Tweedie regression of loss/exposure, exposure-weighted, fixed power 1.5. It predicts pure premium only; no invented frequency/severity decomposition.
4. Histogram gradient boosting with Poisson frequency and Gamma severity, same targets/weights. Fixed 150 iterations, learning rate .05, L2=1, 7 or 15 leaves, minimum frequency leaf 200 and severity leaf 50, no early stopping. Training-only ordinal encodings identify categorical columns; unseen categories become missing.

Regression features: cubic B-splines (5 training-quantile knots, linear extrapolation, no bias) of driver/vehicle age; standardized log BonusMalus and log1p Density; full one-hot Area, VehPower, VehBrand, VehGas and Region, unseen levels ignored. All bases/scales/categories fit inside training. For boosting use the two ages, log BonusMalus, log1p Density and the same categorical features, no splines. No outcomes, IDs or exposure enter features. Poisson/Gamma/Tweedie L2 candidates are .0001 and .01; Poisson and Gamma share the chosen alpha. Deterministic candidate order breaks ties. Max regression iterations 300, tolerance 1e-7; numerical nonconvergence stops the run.

Select each family's setting by **validation uncapped exposure-weighted Tweedie deviance at power 1.5**. Refit selected families on development+validation. Do not recalibrate on final data. Primary comparison: final boosting minus frequency-severity GLM deviance; negative favors boosting. Report all models regardless of result.

## Evidence and sensitivities

Report primary deviance, exposure-weighted mean absolute pure-premium error, predicted/observed total loss, observed and predicted pure premium, frequency and event-weighted severity where defined. Paired policy bootstrap, 500 draws with replacement and fixed seed, yields 95% percentile intervals including the primary difference. These condition on fitted models and the empirical loss tail, not sampling independent years or capturing unobserved catastrophes.

Calibration: ten approximately equal-count predicted-risk groups per model. Segment diagnostics: all portfolio, source Region and Area, plus driver age under 25, 25–39, 40–59 and 60+; show only segments with at least 500 final policies. Record policies, claims, exposure, observed/predicted loss and predicted/observed ratio with 250 policy-bootstrap intervals. This is descriptive calibration, not a fairness certification. Do not expose individual records or sparse risk cells.

Tail sensitivity: cap each source claim at **€50,000**, then aggregate to policy. Refit all final families with their uncapped development-selected settings; do not retune. Evaluate against capped outcomes separately. This changes the target, is not an actual contract limit or winsorization silently applied to the primary analysis. Report tail concentration and largest-claim sensitivity of observed portfolio loss without tuning on them.

Geographic stress: reserve all Ile-de-France policies, chosen from predictor coverage before fitting. Independently select GLM and boosting on non-reserved development/validation policies, refit on all non-reserved training+validation, then evaluate only the reserved region. Non-reserved final policies remain unused for stress fitting. Omit Region as a predictor in **both** geographic-stress models to avoid equating an unseen encoded region with a known one. Report paired 500-draw policy-bootstrap difference. A separate-region result does not establish future-time transfer.

## Interaction and limits

Saved model/segment/uncapped-versus-capped results drive the explorer. Hypothetical expense loading ranges 0–50%; illustrative gross premium = estimated pure premium/(1−loading). These are assumptions, excluding profit, taxes, capital, regulation and reinsurance. Slider changes do not rerun models or estimate delivered savings. Uncertainty in future tail losses and dependence can exceed empirical bootstrap intervals. Historical characteristics and settled amounts cannot establish prospective fairness, causality, claim development or a current insurance price. Independent technical review remains pending.
