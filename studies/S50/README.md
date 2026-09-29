# S50 — News recommendation when freshness and relevance compete

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A news product team needs to surface relevant articles as interests and the news cycle change. Test whether content-aware user-history models improve ranking, especially for newly encountered articles, without excessively narrowing topic exposure.

## Proposed data

[MIND — Microsoft News Dataset](https://msnews.github.io/) — Microsoft Research. Actual files, release and publication rights require inspection before evaluation.

## Research design

Use MIND's impression candidates, observed clicks and preceding user histories. Compare popularity/content-similarity baselines with a news-encoder and user-history model. Preserve supplied temporal boundaries and evaluate only candidates available in each impression; begin with MIND-small before scaling.

## Theory

Representation learning transfers semantic information to articles with little interaction history. Sequential preference models account for recency, while diversity-aware reranking trades relevance against topic concentration. Clicks are conditioned on the logging system's exposure; missing propensities prevent automatically unbiased off-policy evaluation.

## Evaluation design

Measure impression-level NDCG, MRR and calibration plus cold-article performance and topic coverage. Compare history lengths and diversity penalties, using user-clustered uncertainty where appropriate. Do not equate a non-click on an exposed candidate with dislike of every unexposed article.

## Intended interaction

Visitors change history length and diversity weight for an illustrative news reader. A ranked slate, topic distribution and held-out performance frontier show how editorial/product preferences alter recommendations.

## Limits

The benchmark cannot establish live CTR lift, reader welfare or subscriber revenue. Use only licensed text fields and approved display content; do not imply unrestricted redistribution of full news articles.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
