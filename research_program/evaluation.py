"""Metrics and uncertainty helpers with explicit observation units."""
from __future__ import annotations

import numpy as np
from sklearn.metrics import average_precision_score, brier_score_loss, log_loss, roc_auc_score


def binary_metrics(y, probability) -> dict:
    y, probability = np.asarray(y), np.clip(np.asarray(probability), 1e-6, 1-1e-6)
    if len(y) != len(probability) or not set(np.unique(y)) <= {0, 1}:
        raise ValueError('Invalid binary evaluation cohort')
    return {'log_loss': log_loss(y, probability, labels=[0, 1]), 'brier': brier_score_loss(y, probability), 'auroc': roc_auc_score(y, probability), 'average_precision': average_precision_score(y, probability)}


def ranked_selection(score, fraction: float) -> np.ndarray:
    score = np.asarray(score)
    if not 0 <= fraction <= 1 or not np.isfinite(score).all():
        raise ValueError('Invalid capacity or scores')
    count = int(np.floor(len(score) * fraction))
    selected = np.zeros(len(score), dtype=bool)
    selected[np.argsort(-score, kind='stable')[:count]] = True
    return selected


def calibration_bins(y, probability, bins=10) -> list:
    y, probability = np.asarray(y), np.asarray(probability)
    groups = np.minimum((probability * bins).astype(int), bins-1)
    return [{'bin': b, 'n': int((groups == b).sum()), 'prediction': float(probability[groups == b].mean()), 'observed': float(y[groups == b].mean())} for b in range(bins) if (groups == b).any()]


def circular_block_indices(n: int, block: int, repetitions: int, seed: int):
    if n < 1 or block < 1 or block > n:
        raise ValueError('Invalid block length')
    rng = np.random.default_rng(seed)
    for _ in range(repetitions):
        starts = rng.integers(0, n, int(np.ceil(n / block)))
        yield ((starts[:, None] + np.arange(block)) % n).reshape(-1)[:n]


def interval(values, confidence=.95):
    lower, upper = np.quantile(values, [(1-confidence)/2, 1-(1-confidence)/2])
    return {'lower': float(lower), 'upper': float(upper), 'confidence': confidence}


def pass_power(successes: int, trials: int, k: int) -> float:
    """Unbiased pass^k estimator: all k sampled trials must succeed."""
    from math import comb
    if not 0 <= successes <= trials or not 1 <= k <= trials:
        raise ValueError('Invalid repeat counts')
    return comb(successes, k) / comb(trials, k) if successes >= k else 0.0
