# S13 — Frozen chronological quality-screening protocol

Frozen before fitting. Decision: how much historical batch inspection capacity is needed to detect observed failed entities, and whether sparse sensor scoring remains competitive with nonlinear scoring. Population: the 1,567 SECOM production entities recorded July 19–October 17, 2008. Unit: one source row; no batch/wafer identifiers are available. Target: publisher label +1 (failure), with −1 a pass.

The 590 anonymous sensor measurements have no individual acquisition timestamps. Their availability before the quality test is not independently established. This is a retrospective screening comparison conditional on having those measurements at the screening point, not a validated early-warning system. Missingness can encode test procedure; report a no-missingness-indicator ablation. Test-point timestamps order evaluation and do not enter the model. No claim of warning lead time, modern deployment performance, root cause or savings is permitted.

## Calendar and selection

July–August: 618 development rows, 65 failures. September: 590 validation rows, 17 failures. October 1–17: untouched 359-row final cohort, 22 failures. These calendar boundaries follow the inspected coverage, not tuned model results. Source row order is preserved within timestamp ties. All repeated timestamps stay within their calendar month. Label reporting delay is unknown; this is a retrospective calendar split rather than historical availability replay.

Select settings separately within each family by September log loss; break exact ties by smaller setting. Refit each selected family on all 1,208 July–September rows (82 failures). Do not tune on October. No additional probability calibration is fitted: 17 validation failures cannot support broad tuning plus a credible independent calibration split. Show raw probability calibration and proper scores explicitly.

Primary comparison: October average precision, boosting minus elastic-net logistic regression. The PCA monitor is a decision-relevant alternative baseline. Higher average precision is better. Supplementary ROC AUC, log loss, Brier score, recall/precision/counts at 20% and the full frozen inspection-capacity grid are reported without selecting the final model from those scores. Ranking ties use original source row order; no outcome-dependent tie breaking. Capacity means selecting the highest scored units in the complete final batch, not a prospective daily scheduling policy. At zero capacity precision is null.

## Training-only processing and fixed models

For each fit independently, retain sensors with no more than 50% missing values, observed standard deviation above 1e-8 and dominant observed value proportion below 99.5%. Remove exact duplicate retained columns after training-median imputation, retaining the first source column. Winsorize to training 1st/99th percentiles, impute training medians and standardize from training data. Add missingness indicators only when training missingness prevalence is between 0.5% and 99.5%, and remove transformed zero-variance columns. Never learn masks, medians, limits or scale from validation/final data.

- Elastic-net logistic regression: l1 ratio .8; C in .01, .1, 1; SAGA, maximum 20,000 iterations, tolerance 1e-4; no class reweighting or oversampling. Report convergence and selected signal counts.
- PCA process monitor: fit 5 or 15 components on development passes only. Two scores are log(1+Hotelling-like T²) and log(1+mean squared reconstruction error). Standardize these using development rows, then fit L2 logistic(C=1) to the development labels. No missingness indicators enter PCA.
- Histogram gradient boosting: 100 iterations, learning rate .05, L2=5, minimum leaf 30, 3 or 7 leaves, no automatic early stopping. Compare selected configuration without missingness indicators as a fixed ablation.
- The July–September failure prevalence is a descriptive constant-probability benchmark for proper scores, not an operational ranking comparator.

## Dependence, uncertainty and stability

Use 1,000 paired bootstrap draws of October calendar-day clusters for 95% percentile intervals; keep all entities from a sampled day together. Skip and count draws without both outcomes. Report a circular two-day block sensitivity for the primary difference. These intervals condition on fitted models and the observed October period; 17 days and 22 failures support limited precision. No claim that rows or sensors are independent.

Fit the selected elastic-net specification on 30 July–September day-cluster bootstrap resamples, including complete preprocessing each time. Report per-sensor selection frequency, availability frequency, signal type, total selected sensors and Jaccard overlap with the final fit. A selected sensor is one with absolute coefficient above 1e-6 in its measurement or missingness indicator. Stability is descriptive, not causal attribution or formal false-selection control.

Report missingness, constant/duplicate sensors, timestamp ties, monthly prevalence, all partitions, feature dimensionality, tuning scores, five equal-count calibration groups, final day/coarse-missingness diagnostics, full capacity counts and independent result reconstruction. Export only aggregate evidence and anonymous sensor indices, never row-level sensor records or predictions. Preserve CC BY 4.0 attribution and source checksums.
