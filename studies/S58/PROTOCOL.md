# S58 — Frozen workflow-delay protocol

Decision: prioritize applications whose next recorded business disposition is likely to be slow. Target the first subsequent application status among A_Pending, A_Denied and A_Cancelled. This explicitly defined status endpoint is not loan disbursement or completion of every later work-item event. Do not equate employee activity timestamps with service time or inefficiency.

## Data grain and timing

Use BPI Challenge 2017, published by Boudewijn van Dongen / Eindhoven University of Technology, DOI 10.4121/uuid:5f3067df-f10b-45da-b98b-86ae4c7a310b. Pin the original XES gzip SHA-256 `183c5e5189282779c811c78c33ff936351b3dd201165d612211fc220936f8249`. There are 31,509 application traces and 1,202,267 events. The observed UTC endpoint is 2017-02-01T14:11:03.499Z, matching the publisher's local 15:11 cutoff.

Keep applications as the split/uncertainty unit. Offers and all event prefixes stay within their enclosing application. Retain workflow lifecycle transitions as distinct events; do not conflate start/suspend/resume/complete. Check chronological order, same-time ties, repeated event IDs, offer references and observed application endpoints. Identifiers and resources stay external and never enter predictors or public tables.

Create event prefixes of length 5,10 and20 only while the application has not reached the target disposition. A prefix uses the first k source events; sort by timestamp with source order breaking ties if needed. Features use only those events: application age, gaps, latest application stage, latest event/lifecycle, cumulative activity/lifecycle counts and offers created so far. No future total event count, final offer acceptance, later credit scores or future application attributes enter features. Omit initial financial/demographic attributes: this is a workflow-delay model, not a credit or lending decision.

## Fixed cohorts and survival endpoint

Development: applications opened January–August 2016, prefixes observed before September 1; administrative follow-up ends the start of October 1 UTC. Validation: applications opened September 2016, prefixes observed before October 1; follow-up ends at the start of November 1 UTC. Tune after validation outcomes mature. For final fitting, use applications opened January–September with prefixes before November 1 and follow-up through November 30. Final holdout: applications opened December 2016 with prefixes observed before January 1, 2017. Observe outcomes through the file endpoint. October/November applications are not used for final testing.

These entry cutoffs provide each final prefix at least 30 days of follow-up. Report entries excluded because the prefix was not yet observed or disposition already occurred. Cases without a target status remain administratively censored; never treat their final event as completion.

Predict restricted remaining time over 30 days. Discretize an event at elapsed ceil(days), minimum1; survival beyond 30 days contributes 30 to the restricted target. An administratively censored partial day contributes only completed risk intervals. The restricted expectation is sum of survival probabilities at days 0–29. Final prefixes have complete 30-day ascertainment, so absolute error and Brier scores do not require extrapolating unobserved outcomes. The model still uses censored development cases through their observed risk intervals.

## Baselines, challenger and selection

Baseline 1: pooled discrete Kaplan–Meier remaining survival. Baseline 2: Kaplan–Meier conditioned on latest application stage and prefix-age band (<1,1–7,>7 days), with a pooled fallback for fewer than 50 training prefixes. These baselines forecast restricted mean remaining days; stage medians are reported descriptively where identified, not substituted as missing-tail means.

Challenger: discrete-time histogram gradient-boosted hazard model with native categorical fields and day 1–30 as a feature. Use 120 iterations, .05 learning rate, L2=10, no random early-stopping split, and compare 7 versus15 leaves using validation restricted-time MAE. Fit category mappings only on eligible training prefixes; unknown categories become missing. Each application's prefixes collectively receive weight 1; expand each prefix into observed person-day risk intervals using that prefix weight. Fix settings after validation and refit once on the eligible final-training cohort.

Primary: application-weighted restricted-remaining-time MAE, challenger minus stage/age baseline. Also report 14-day completion Brier score, mean forecast/observed restricted days, and late-case capture at capacities 10%,20%,30%,50% and100%. Rank by predicted probability of remaining unresolved after 14 days; actual late outcome is observed at 14 days. Model selection and capacity are not tuned on the final holdout.

Use 500 paired application-cluster bootstrap draws, keeping all prefixes from an application together. Report conditional 95% intervals, all prefix lengths, latest-stage groups, calibration bins, censoring and cohort attrition. Sensitivity: remove detailed activity-count history and refit the selected model using age/current stage/day alone. Preserve negative results. Intervals omit retraining and future regime uncertainty; the single institution is not a representative labor-productivity sample.

## Workflow map and explicit capacity scenario

From final prefixes, show common consecutive application-stage transitions and observed elapsed event gaps, retaining a count and median/p90 per edge. These are elapsed times, not measured active service. Describe self-loops and repeat validation/incomplete stages without attributing blame. A stage/prefix selector changes the corresponding saved evidence and cohort counts.

Capacity controls use a transparent proportional scenario: restricted days × ((1−addressable share)+addressable share/capacity multiplier), with assumed addressable share 0–1 and capacity multiplier 0.5–2.0. No queue-arrival/service mechanism is observed well enough to identify a causal staffing effect. This scenario is arithmetic under assumptions, not a fitted intervention, savings estimate or changed prediction score. Show baseline and implied days side by side and support reset.

## Publication

Raw trace IDs, resource IDs, offer records and individual financial fields stay outside Git and deployment. Aggregate research must cite van Dongen (2017), BPI Challenge 2017, Eindhoven University of Technology, the DOI and 4TU.ResearchData. The dataset uses 4TU General Terms of Use (2016), including noncommercial reuse, source citation and notification of bibliographic publication details. Prepare that notification and resolve its authorized submission before marking the public case published. Independent technical review is pending.
