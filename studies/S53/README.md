# S53 — Crop-rotation forecasting without spatial leakage

Status: planned. No analysis has been run and no finding is claimed.

## Decision

An agricultural planning team wants to anticipate regional crop-mix changes and identify where transitions are difficult to forecast. Test whether multi-year rotation history improves next-year crop classification and aggregate acreage estimates.

## Proposed data

[USDA Cropland Data Layer](https://www.nass.usda.gov/Research_and_Science/Cropland/Release/) — USDA National Agricultural Statistics Service. Actual files, release and publication rights require inspection before evaluation.

## Research design

Use past-year Cropland Data Layers to predict the next year's crop class on a fixed, compatible grid. Compare persistence and transition-matrix baselines with a spatial-temporal classifier. Harmonize changing resolution, class definitions and alignment; never use the target-year crop map as an input feature.

## Theory

Markov transition models express dependence on prior crop states; longer histories can capture rotation patterns. Spatial autocorrelation makes neighboring pixels pseudo-replicates. Classification error in the source maps propagates into apparent transition rates and acreage uncertainty.

## Evaluation design

Hold out future years and large geographic blocks, not random adjacent pixels. Report class-balanced accuracy, transition-specific confusion and county-level acreage error, with uncertainty clustered spatially. Test sensitivity to map resolution and documented label accuracy.

## Intended interaction

A map time slider compares last-year crop, predicted next-year crop and later observed map labels. Visitors adjust the history length and spatial holdout, revealing rotation uncertainty and aggregate acreage consequences.

## Limits

CDL labels are themselves remotely sensed estimates, not perfect field ground truth. This study does not estimate farm profit, yield or the causal benefit of crop rotation; nominal pixel count overstates independent evidence.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
