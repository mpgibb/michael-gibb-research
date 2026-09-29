# S28 — Sales contact prioritization before the call begins

**Status: evaluated.** Public data; independent technical review pending.

## Decision and implication

Should a sales team replace a simple contact-history ranking with a more complex prediction model at limited capacity? On the final 8,238 chronological UCI Bank Marketing records, the simple rule identifies **934 subscriptions among 1,647 selected contacts**, compared with **843** for the logistic model selected during development. Its log loss is also better: 0.6349 versus 0.7171; the paired difference is 0.0822 (95% interval 0.0470–0.1177).

Keep the simpler benchmark until a replacement demonstrates current, decision-relevant improvement. These are historical responses among observed contacts, not additional subscriptions caused by calling, realized profit or a production deployment recommendation.

## Evidence and sources

- [Full evaluation report](REPORT.md): all prespecified models, capacity curves, failure periods, calibration and sensitivities.
- [Result artifact](results/result.json): run ID, source/data hashes, model definitions, counts, metrics and uncertainty.
- [Frozen protocol](PROTOCOL.md) and [configuration](config.json): chronological folds, pre-call features, selection and bootstrap.
- [Data and access](DATA.md): UCI release, licensing, field timing and missingness.
- [Executable study](study.py): checked ingestion, feature pipeline, baseline, additive/logistic/boosted comparisons and evaluation.

Data: [UCI Bank Marketing](https://archive.ics.uci.edu/dataset/222/bank+marketing), full bank-additional variant, 41,188 records from May 2008–November 2010. Moro, Rita & Cortez (2014), [doi:10.24432/C5K306](https://doi.org/10.24432/C5K306), CC BY 4.0. Exact call dates, person identifiers, treatment controls and observed financial outcomes are unavailable.

## Reproduce

From the repository root, using Python 3.11.16:

```sh
uv sync --frozen
uv run python -W error -m unittest discover -s tests -v
uv run python -W error studies/S28/study.py
uv run python scripts/report_s28.py
uv run python -m research_program.validate
```

The command downloads the fixed publisher archive into an external cache and verifies archive/CSV checksums. Set `RESEARCH_DATA_DIR` to another external directory if needed. Raw data and individual predictions are not published. Analysis source must be committed and clean for provenance capture. The result records the executed source version, which may precede documentation commits. Numerical results reproduce within floating-point tolerance across platform libraries.
