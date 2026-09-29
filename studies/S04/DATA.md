# Corrected Criteo uplift benchmark

Source: [Criteo corrected uplift release](https://ailab.criteo.com/criteo-uplift-prediction-dataset/), v2.1. The official download is linked by the publisher and pinned in config.json. The compressed file is 311,422,618 bytes; SHA-256 `2716e1bf0fd157a93b5bf86924d9088419dfbac2022c6cd90030220634f616dc`.

The file has 13,979,592 numeric records, twelve anonymized features f0–f11, assigned treatment, conversion, visit and exposure. All inspected fields are present, with no missing numeric values. The published introductory description retains older counts; this study uses the actual corrected file schema. There are 40,774 conversions, 656,929 visits and 11,882,655 treatment-assigned rows. The publisher corrected leakage in an earlier version; that version is not used.

A row represents a released anonymous record. No exact date, campaign-stratum identifier or stable person ID is available. Matching feature profiles can describe different people; they are grouped conservatively for splitting and uncertainty. Exposure is realized after assignment and never enters predictors. Visit is an outcome, not a baseline feature.

Privacy-related non-uniform subsampling prevents recovery of original advertiser-level incrementality. Benchmark treatment contrasts require assumptions about assignment after sampling; balance diagnostics cannot prove exchangeability. No monetary fields or verified causal profit are observed.

Data attribution: Diemert, E., Betlei, A., Renaudin, C. & Amini, M.-R. (2018), *A Large Scale Benchmark for Uplift Modeling*, AdKDD/TargetAd Workshop. Criteo data terms: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). Data are provided without warranty. The study transforms released records into sampled, aggregate research comparisons; those aggregate tables retain this attribution and license notice. No raw records, full derived dataset or fitted model binary are redistributed. Original analysis code is separate from the licensed source data.
