# S51 — Customer-review intelligence that anticipates emerging product issues

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A media merchandising or product team needs to detect recurring customer concerns before they dominate a category. Test whether prior-period review themes predict a later increase in negative-review share better than star-rating trends alone.

## Proposed data

[Amazon Reviews 2023 — media subsets](https://amazon-reviews-2023.github.io/) — UC San Diego McAuley Lab. Actual files, release and publication rights require inspection before evaluation.

## Research design

Choose a reproducible Books, Movies/TV or Digital Music subset. Extract a restrained theme taxonomy using interpretable topic models and a structured language-model challenger. Build item/category-period summaries from reviews already available; reserve later review periods for evaluation and group related products where identifiable.

## Theory

Latent-topic models summarize co-occurring language; measurement validation is needed before treating extracted themes as business concepts. Hierarchical binomial models shrink noisy negative-review rates. Review submission is a selected behavior, so review sentiment does not estimate satisfaction among all buyers.

## Evaluation design

Compare rating-only and theme-augmented temporal forecasts. Report calibration/error for later negative-review share, topic stability and extraction precision on an independently adjudicated sample. Without adjudication, label extraction quality as unverified and publish only benchmark-label performance.

## Intended interaction

A voice-of-customer explorer filters category, period and theme. It shows theme trajectories, future-period validation and approved short evidence snippets or verified paraphrases; an alert threshold controls the review queue.

## Limits

Reviews do not reveal complete sales, exposure or the causal effect of a product change. Avoid full-text redistribution and never treat an LLM's fluent theme explanation as independent evidence.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
