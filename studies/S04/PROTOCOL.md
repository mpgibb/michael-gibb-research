# S04 — Frozen advertising targeting protocol

Frozen before model fitting or policy scoring. The decision is which released-benchmark records to target under limited capacity. Primary endpoint: the file's binary conversion label. Features are f0–f11 only; treatment is assigned eligibility, while visit, conversion and realized exposure are excluded from predictors. No campaign timestamp, user ID, original economics or actual experimental-stratum ID is supplied.

## Source, bounded cohort and split

Use corrected Criteo v2.1, SHA-256 `2716e1bf0fd157a93b5bf86924d9088419dfbac2022c6cd90030220634f616dc`, 13,979,592 rows. Read the publisher's correction and privacy-sampling caveat. The released sample is non-uniformly subsampled; the original advertiser effect and ROI are not identified. Causal interpretation within the released benchmark additionally requires consistency, overlap and exchangeability after that sampling. Results are benchmark treatment contrasts under those assumptions, not recovered experimental effects for an advertiser.

Hash the 12-feature profile with pandas 2.3.3's stable hash. Keep `hash % 70 < 10` (1,995,142 rows). Define split bucket `(hash // 70) % 100`: 0–59 development, 60–79 validation, 80–99 untouched evaluation. Identical anonymized profiles stay in one partition; matching profiles are not asserted to be the same person. There are 231,375 repeated-profile rows in the bounded cohort. Use all validation and test records; for fitting use development profiles with `(hash // 7000) % 2 == 0`, an outcome-independent approximately half-sized training sample. This is a bounded benchmark, not full-source performance.

No temporal ordering is invented. Audit missingness, exact profiles, treatment overlap, outcome counts, exposure/assignment cells, standardized feature differences and propensity distributions. No preprocessing sees validation/test outcomes. Store individual records and predictions externally; publish only aggregates.

## Models and development

Nuisance models: arm-specific histogram boosting regression for binary conditional means (7 leaves, 120 iterations, .05 learning rate, L2=10; predictions clipped to [0.000001,0.999999]); propensity is standardized L2 logistic regression C=1, max_iter=500, clipped [0.05,0.95]. Use three folds defined by `(hash // 14000) % 3` so profiles remain together. Cross-fitted pseudo-outcome is m1−m0 + T(Y−m1)/e − (1−T)(Y−m0)/(1−e).

Principal comparisons: (1) a doubly robust learner regresses the cross-fitted pseudo-outcome on f0–f11 with histogram boosting (7 leaves,120 iterations,.05), comparing L2=10 versus100; (2) EconML CausalForestDML with honest trees and three profile-separated nuisance folds, 128 trees, depth 10, max_samples .45, two worker threads, min leaf 100 versus500. Its outcome nuisance uses pooled boosting including assignment only through residualization; propensity uses the same logistic pipeline. Forest internal inference is disabled: policy intervals come from independent held-out outcomes, not predicted effects. Fixed seed in config; no parameter search outside these four candidates.

Fit final evaluation nuisance functions only on development. Response targeting ranks the treatment-arm conditional conversion prediction. Random targeting is an analytical expected capacity fraction; treat-none and treat-all are explicit endpoints. At 20% validation capacity choose the advanced candidate with the largest independent doubly robust policy contrast; ties follow declared candidate order. Retain all candidates in final reporting. No retraining on validation, and no setting changes after final scores.

## Independent policy evaluation

Capacity fractions: 0, .01, .05, .10, .20, .30, .50, .75 and1. Sort scores stably, selecting floor(fraction×N) rows. The primary contrast is the selected advanced policy minus response targeting at 20%, measured as incremental benchmark conversions per 10,000 eligible records relative to no targeting. A policy's independent score is mean(selection × held-out doubly robust pseudo-outcome). Expected random allocation uses its fractional selection probability, not a fabricated observed random count. Treat-all and none provide the full/no targeting endpoints. Never evaluate a policy by summing its own predicted effects.

Compute paired 95% normal intervals using profile-cluster influence sums, with a finite-cluster correction. The independent sampling assumption is between anonymized profiles; no campaign IDs exist to adjust campaign dependence. Intervals condition on fitted functions and frozen rankings and do not include training uncertainty or multiplicity across the exploratory frontier. Primary comparison is prespecified at20%. Show estimates even when negative or inconclusive.

Report all candidate frontiers, arm/event counts, global benchmark contrast, predicted-effect decile calibration against independent scores, treatment overlap and propensity balance. Deciles use score ranks without outcomes. Sensitivities: replace propensity by development treatment prevalence in the same held-out score, use an unadjusted inverse-propensity contrast, and keep only the first evaluation row per profile. Preserve all discrepancies. No demographic/fairness claims can be made from anonymized f0–f11.

## Economic interaction and publication

Controls use saved capacity tables and optionally assumed conversion value $0–$1,000 and contact cost $0–$10. Net scenario per10,000 eligible records = independent incremental benchmark conversions × assumed value − selected fraction ×10,000×assumed contact cost. It is neither original advertiser ROI nor observed profit. Values do not change measured research evidence.

Cite Diemert, Betlei, Renaudin & Amini (2018), A Large Scale Benchmark for Uplift Modeling, and the corrected publisher release. Data terms: CC BY-NC-SA4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/. Do not redistribute raw records, trained binaries or copied publisher prose. Derived aggregate research tables retain attribution and the same notice; original code is separate. Independent technical review is pending.
