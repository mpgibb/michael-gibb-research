# S08 — Does relational learning justify its complexity?

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A product analytics leader must choose between engineered SQL features and relational machine learning. Ask whether learning across users, posts and interactions improves future engagement prediction enough to justify maintenance and serving complexity.

## Proposed data

[RelBench rel-stack](https://star-project.stanford.edu/relbench/) — Stanford / Kumo.AI; Stack Exchange source data. Actual files, release and publication rights require inspection before evaluation.

## Research design

Select a documented rel-stack engagement task and preserve its official prediction horizon and temporal splits. Compare a transparent SQL aggregation plus boosted-tree baseline with a heterogeneous graph model. Restrict every neighbor, edge and aggregate to information available at the task reference time.

## Theory

Relational inductive bias exploits dependencies across linked entities; message passing shares information through the database graph. This differs from treating each customer row as independent. Temporal causality in feature construction is essential even though the task itself is predictive.

## Evaluation design

Report the official benchmark metric plus probability calibration, resource usage and performance on users with sparse history. Ablate relation types and compare against identical-budget SQL baselines. Audit neighborhood timestamps to expose graph leakage.

## Intended interaction

A schema-to-prediction explorer lets visitors toggle relationship types and cold-start cohorts. It shows which historical tables contribute, the accuracy/compute tradeoff and aggregate engagement-risk distributions without exposing personal profiles.

## Limits

Q&A engagement is a product-usage proxy. It does not establish paid SaaS revenue, conversion or the causal effect of a customer-success action.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
