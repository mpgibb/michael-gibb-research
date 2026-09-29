# S12 — Regional freight resilience under capacity shocks

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A supply-chain planning leader must understand dependence on particular corridors, modes and regions. Identify where a disruption concentrates exposure and compare hypothetical diversification plans.

## Proposed data

[Freight Analysis Framework](https://www.bts.gov/faf) — BTS / FHWA. Actual files, release and publication rights require inspection before evaluation.

## Research design

Build a commodity-specific origin-destination flow network from a pinned FAF release. Distinguish estimated base-year flows from projections. Formulate an interregional transportation problem with explicitly assumed modal capacities, transfer penalties and demand scenarios; add physical infrastructure data only as a separately documented extension.

## Theory

Network flow conservation links regional supply and demand. Robust optimization minimizes losses across a defined uncertainty set; CVaR emphasizes severe modeled scenarios. This produces conditional planning recommendations rather than predictions of an unobserved real disruption.

## Evaluation design

Compare current shares, proportional diversion and optimized diversification under the same scenarios. Verify conservation and feasibility; report unserved tonnage, concentration and scenario cost. Test rank stability across releases and commodity definitions; validate projections against later observations only where comparable vintages exist.

## Intended interaction

Visitors select a commodity, affected region and capacity reduction. An OD flow map and resilience frontier show where modeled freight shifts and which constraints bind, with every assumed capacity/cost visible.

## Limits

FAF is an estimated aggregate flow system, not shipment traces or a physical road network. Capacity, rerouting feasibility and costs cannot be inferred from tonnage alone.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
