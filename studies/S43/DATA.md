# S43 — Source and timing audit

- [Assessor public-data overview](https://datacatalog.cookcountyil.gov/stories/s/Assessor-2025-Open-Data-Refresh/gzdr-q7c4/)
- [Official model source and public input links](https://github.com/ccao-data/model-res-avm#Getting-Data)
- [Pinned 2024 assessment input](https://ccao-data-public-us-east-1.s3.amazonaws.com/models/inputs/res/2024/run_id=2024-03-17-stupefied-maya/assessment_data.parquet):309,845,333 bytes; SHA-256 in config. Last-Modified April10,2024; meta_year2023. Unlike a current characteristics extract, this snapshot demonstrably predates all included sales.
- [Parcel Sales](https://datacatalog.cookcountyil.gov/d/wvhk-k5uv): monthly projected CSV downloads May2024–December2025; 132,773 rows, no duplicate row IDs or PIN/document pairs, 18,783 repeated document numbers largely reflecting multi-parcel transfers. The source reports lagged sale ingestion and periodic corrections. Metadata last updated September15,2026; downloaded September29,2026. Query URLs, selected fields, dates, counts and every checksum are frozen in config.
- [Publisher extraction documentation](https://github.com/ccao-data/wiki/blob/master/SOPs/Open-Data.md) identifies unique sale documents only after excluding multi-parcel transactions. Buyer and seller names are excluded from the API projection.
- [Residential assessment convention](https://rpie.cookcountyassessor.com/how-residential-property-valued-0): assessed values represent10% of estimated market value. Only the prior-year board value in the pre-sale snapshot is used as a supplementary benchmark.

The publisher's SQL explains the legacy sale flags and a backward-looking same-price/365-day duplicate check. Inspection found no missing projected sale fields. All joins are validated at parcel grain after restricting the characteristics snapshot to single-family, single-card, single-land-line, non-prorated records. The published analysis does not make every recorded sale an arm's-length transaction by assumption.

The [County terms](https://www.cookcountyil.gov/terms-use) provide data without accuracy/completeness warranties and disclaim endorsement. No separate Creative Commons license appears in the sales metadata, so none is invented. This project cites the sources and publishes original analysis and small aggregate findings, not the source records or County graphics. Public availability does not erase source limitations.

Re-downloads of the mutable sales API may differ; checksum mismatches stop execution. Use the exact cached files for bitwise replication. Raw source data, join keys, addresses, precise property locations and individual model predictions stay outside Git and deployment. Aggregate coordinates describe township cohorts only.
