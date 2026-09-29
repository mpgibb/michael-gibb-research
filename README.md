# Decision-science research program

Research by Michael P. Gibb, Ph.D. Public portfolio: [michaelpgibb.com/research](https://michaelpgibb.com/research).

The catalog accounts for 60 study designs across 20 industries. **S28 and S02 have executed public-data evaluations. The other 58 have no completed findings.** The four earlier synthetic demonstrations are separate projects and do not count toward this program.

## Evaluated research

- [S02 — Inventory planning](studies/S02): a 210-series M5 forecast comparison and explicit inventory replay. Better measured sales forecasts reduce assumed cost in the tested scenarios, but service and cost are different objectives; no realized savings are claimed.

- [S28 — Sales contact prioritization](studies/S28): a chronological UCI Bank Marketing evaluation. A simple history-and-recency rule has lower final-period log loss than the logistic model selected during development. This is response prediction among previously observed contacts, not proof that calling causes additional subscriptions.

## Reproduction

Install Python 3.11.16 and [uv](https://docs.astral.sh/uv/). Dependencies are locked in `uv.lock`.

```sh
uv sync --frozen
uv run python -W error -m unittest discover -s tests -v
uv run python -m research_program.validate
uv run python -W error studies/S28/study.py
uv run python scripts/report_s28.py
```

Data downloads use the publisher's HTTPS endpoint with fixed SHA-256 checks. Raw files and individual predictions stay outside this repository, under `~/.cache/michael-gibb-research` by default. Set `RESEARCH_DATA_DIR` to another external directory if desired. Only source and aggregate results are published. Training runs locally; the website reads static artifacts and does not train or call paid services.

Code provenance records the committed analysis source and locked environment. Reproduction requires a committed, clean analysis source. Platform numerical libraries can cause small floating-point differences; compare estimates within a justified tolerance rather than assuming byte-identical output across platforms. The report is generated from the result artifact.

## Program structure and states

`catalog/studies.json` separates execution (`planned`, `data_ready`, `baseline_complete`, `evaluated`, `blocked`) from publication (`unpublished`, `draft`, `published`, `withheld`). Study folders document the decision, proposed design and boundaries. A planned folder is not evidence of an executed analysis.

Evaluated folders add a frozen protocol, ingestion and feature code, data documentation, executable comparison, diagnostics, report and schema-validated result. Each result records sample counts, target and timing, model specifications, uncertainty, limitations, data hashes and source version. Published records require those artifacts and actual code/case-study links. Drafts have no public case-study route.

## Sources and reuse

Data access and licensing are specific to each study. Follow its `DATA.md` and the original publisher's terms. S28 derives aggregate results from UCI Bank Marketing (Moro, Rita & Cortez, 2014), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), [doi:10.24432/C5K306](https://doi.org/10.24432/C5K306). No broad reuse license is granted for the authored source in this repository. Third-party rights remain with their owners.

Independent technical review remains pending. These studies are portfolio research, not verified employer/client outcomes or deployment recommendations.
