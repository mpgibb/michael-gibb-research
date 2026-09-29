# S21 — Does molecular data add stable prognostic information?

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A translational research team must decide whether a complex molecular signature adds information beyond a simpler clinical baseline. Test this increment under rigorous leakage and batch-effect controls in one cancer cohort.

## Proposed data

[TCGA open-access data through GDC](https://gdc.cancer.gov/access-data/data-access-processes-and-tools) — National Cancer Institute. Actual files, release and publication rights require inspection before evaluation.

## Research design

Select only open TCGA clinical and processed molecular files with usable outcome definitions. Start with a clinical Cox model, add a prespecified pathway-level representation and compare with penalized multi-omic survival modeling. Perform normalization and feature selection inside training folds and keep all samples from a patient together.

## Theory

Penalized proportional-hazards models address high dimensionality while pathway aggregation reduces degrees of freedom. Right censoring requires survival-aware scoring. Batch effects can masquerade as biological signal; incremental predictive value must be assessed against a clinical-only baseline.

## Evaluation design

Use nested patient-level validation and a collection-site holdout if feasible. Report time-specific calibration, concordance, integrated Brier score and feature stability. Test proportional-hazards assumptions and clinical-variable missingness; identify external validation as a future requirement.

## Intended interaction

An evidence explorer compares clinical-only and molecular models by horizon and validation split. It shows incremental performance with uncertainty, pathway stability and batch/site sensitivity, without presenting an individual treatment recommendation.

## Limits

Retrospective prognostic association does not identify treatment benefit. Open TCGA cohorts do not establish clinical utility or readiness for patient care; controlled-access files are outside this project's scope.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
