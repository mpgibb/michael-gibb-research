# Data and access

Source: [UCI Bank Marketing](https://archive.ics.uci.edu/dataset/222/bank+marketing), specifically the full **bank-additional** variant, not the older 45,211-row file or random 10% extract.

Citation: Moro, S., Rita, P., & Cortez, P. (2014). Bank Marketing [Dataset]. UCI Machine Learning Repository. [doi:10.24432/C5K306](https://doi.org/10.24432/C5K306). Method paper: Moro, Cortez & Rita, *A Data-Driven Approach to Predict the Success of Bank Telemarketing*, Decision Support Systems, [doi:10.1016/j.dss.2014.03.001](https://doi.org/10.1016/j.dss.2014.03.001).

UCI lists Creative Commons Attribution 4.0. Attribute the creators and UCI when reusing derived outputs. The archive contains a specific dictionary whose missing-value description takes precedence over the website's summary: `unknown` represents missing categorical information. No raw data is included in this repository. Ingestion retrieves the publisher archive over HTTPS, checks both archive and CSV hashes, and extracts only the intended CSV into an external cache.

The study preserves row order, documented as chronological from May 2008 to November 2010. The public file has month and weekday but no exact call date, year field or customer identifier. It cannot establish person-disjoint splits or exact calendar boundaries. All split descriptions therefore use source row numbers. Loan/default and demographic attributes are confined to a sensitivity analysis. Economic indicator vintages are unavailable and those columns are excluded. `duration` is always excluded. `campaign-1`, `previous`, `poutcome` and `pdays` are used under their documented pre-current-call history definitions. The original `campaign` field is never passed to a model.

The analysis reports schema/missingness/duplicate audits, category novelty, split counts and event totals in `results/result.json`. Matching anonymized rows are not proven duplicate customers and are retained, with a held-out exact-profile overlap sensitivity. Derived aggregate tables do not identify customers.
