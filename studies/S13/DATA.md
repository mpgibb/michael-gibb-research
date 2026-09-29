# S13 — Inspected SECOM source

McCann, M. & Johnston, A. (2008). **SECOM** [Dataset]. UCI Machine Learning Repository. [doi:10.24432/C54305](https://doi.org/10.24432/C54305). [Publisher documentation](https://archive.ics.uci.edu/dataset/179/secom). [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); this study transforms the measurements into aggregate evaluation results and original analytical figures. No publisher endorsement is implied.

The official 1,964,989-byte ZIP was downloaded September 29, 2026. Its SHA-256 and the two input-file hashes are fixed in config.json. The documentation describes 591 features; the actual numeric file contains **590 sensor columns**. Labels and quoted test timestamps are in a separate, row-aligned file. Do not create a phantom sensor or silently misparse the quoted timestamp.

There are 1,567 rows, 104 failures (+1), 1,463 passes (−1), and 41,951 missing sensor cells. Every numeric column has at least one observed value. There are 116 globally constant columns, 104 exact duplicate columns (including constant signals), 28 columns more than half missing, no exact duplicate complete sensor rows and 33 repeated test timestamps. Audit statistics describe the source; removal decisions are relearned inside every training fit.

Timestamps are already ordered from July 19 through October 17, 2008. Monthly failure/total counts are July 14/63, August 51/555, September 17/590 and October 22/359. The shift in observed prevalence is substantial. No lot, wafer, production-line or sensor acquisition timestamp is supplied; day clustering is only an observable proxy for dependence. Fields cannot identify physical root causes or independently verify pre-test availability. See PROTOCOL.md for the restricted retrospective estimand.

Reproduction downloads the original ZIP through UCI with a 10 MB bound and fails if hashes, dimensions, labels or ordering differ. Raw files and individual predictions stay outside Git and deployment under RESEARCH_DATA_DIR/S13.
