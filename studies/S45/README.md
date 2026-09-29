# S45 — Transparent screening of property redevelopment opportunities

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A real-estate strategy team needs a defensible way to prioritize parcels for further diligence. Build a transparent screening framework that weighs current use, building characteristics and simple utilization proxies under multiple business preferences.

## Proposed data

[PLUTO / MapPLUTO](https://data.cityofnewyork.us/City-Government/Primary-Land-Use-Tax-Lot-Output-PLUTO-/64uk-42ks) — NYC Department of City Planning. Actual files, release and publication rights require inspection before evaluation.

## Research design

Use PLUTO tax-lot geometry, land use, building age/area and documented zoning-related fields. Validate units and implausible records. Derive a clearly approximate unused-floor-area indicator only where compatible fields permit; use multi-criteria ranking and robust optimization rather than training on an invented redevelopment-profit label.

## Theory

Multi-criteria decision analysis makes preference weights explicit. Pareto dominance identifies parcels that are unattractive across all chosen criteria; robust ranking tests whether priorities survive uncertain inputs and weights. A feasibility proxy is not a legal entitlement or causal outcome.

## Evaluation design

Compare simple size/age filters with the multi-criteria shortlist. Report rank stability under weight/input perturbations, missing-data sensitivity and independent spot checks against source attributes. If outcome data are later added, define a separate temporal validation study.

## Intended interaction

Visitors choose geography, parcel type and criterion weights. A map, Pareto plot and explanation card show why a parcel category rises or falls in the shortlist; all proxy assumptions remain visible.

## Limits

PLUTO is an inventory, not transaction-return or tenant-demand data. Simple floor-area calculations do not certify buildability; project economics, entitlements and parcel-specific constraints require additional evidence.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
