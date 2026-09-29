# S49 — Personalization beyond popularity: accuracy, diversity and cold start

Status: planned. No analysis has been run and no finding is claimed.

## Decision

A media product team wants useful recommendations without showing everyone the same popular titles. Test how much ranking quality must be traded for catalog coverage, diversity and performance on users with little observed history.

## Proposed data

[MovieLens 32M](https://grouplens.org/datasets/movielens/32m/) — University of Minnesota GroupLens. Actual files, release and publication rights require inspection before evaluation.

## Research design

Create global chronological train/validation/test periods from MovieLens ratings. Compare popularity and neighborhood baselines with matrix factorization and a diversity-aware reranker. Define relevance from observed ratings and document candidate construction; use short-history cohorts based only on information available at the cutoff.

## Theory

Low-rank factorization represents latent user-item preferences. Multiobjective ranking balances estimated relevance with diversity or popularity exposure. Ratings are missing non-randomly: an unrated movie is not a known dislike, and ranking metrics depend strongly on the evaluation candidate set.

## Evaluation design

Report NDCG/Recall under a fixed documented protocol, rating error where appropriate, catalog coverage, novelty and user-history subgroup results. Compare full eligible-catalog and sampled-candidate sensitivity where computationally feasible; keep future interactions out of popularity statistics.

## Intended interaction

Visitors select an illustrative preference profile and diversity weight. Recommendation lists, relevance/diversity frontiers and cold-start performance update using precomputed rankings, with clear explanations of observed versus inferred preference.

## Limits

Offline ratings do not demonstrate watch time, subscription retention or causal engagement lift. Respect MovieLens's research-use terms; the publisher requires permission for commercial use, so public demo contents must be checked before release.

There is no runnable study or result artifact yet. The catalog records the next verified stage.
