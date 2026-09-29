# S57 — Turning severe-injury narratives into a prevention taxonomy

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A construction safety team needs a consistent view of recurring hazard mechanisms across incident reports. Test whether structured text extraction can organize reported incidents accurately enough to support expert review and training priorities.

## Proposed data

[OSHA Severe Injury Reports — construction subset](https://www.osha.gov/severe-injury-reports) — U.S. Occupational Safety and Health Administration. Actual files, release and publication rights require inspection before evaluation.

## Research design

Filter the OSHA records to the documented construction industry codes and eligible jurisdiction/time coverage. Build a prespecified mechanism/activity taxonomy. Compare keyword and TF-IDF baselines with a structured language-model classifier; retain supporting text spans and an abstention option for ambiguous cases.

## Theory

Measurement theory treats the taxonomy as an operational definition that requires validation. Selective classification trades coverage for lower error among accepted labels. Observed report counts reflect exposure and reporting processes as well as hazard, so they are not automatically injury rates.

## Evaluation design

Create a de-identified, independently adjudicated evaluation sample with clear labeling rules; report agreement, class-specific precision/recall and error-versus-review-volume curves. Use later periods for drift checks. Without expert labels, treat the model as an unvalidated organizing aid.

## Intended interaction

Visitors filter activity, hazard and time period. A mechanism matrix and evidence-linked examples show reported patterns; a confidence slider reveals how many records require expert review instead of automatic classification.

## Limits

Coverage excludes important jurisdictions and the severe-injury report system is not a complete fatality census. Counts lack matching worker-hour denominators; do not rank employers by safety or claim a prevention intervention reduced injuries.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
