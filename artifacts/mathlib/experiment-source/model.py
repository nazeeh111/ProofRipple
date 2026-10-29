"""A small bootstrap ridge ensemble, trained on measured search usefulness.

The uncertainty is ensemble disagreement, not a calibrated probability or a
guarantee. Training uses no language model, network service, or GPU.
"""
from __future__ import annotations

import math
import random

from .engine import FEATURE_NAMES, generate_candidates, search


def _solve(matrix, vector):
    """Partial-pivot Gaussian elimination for the tiny positive-definite system."""
    n = len(vector)
    work = [list(row) + [value] for row, value in zip(matrix, vector)]
    for column in range(n):
        pivot = max(range(column, n), key=lambda row: abs(work[row][column]))
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        if abs(scale) < 1e-12:
            raise ValueError("Singular training system")
        work[column] = [value / scale for value in work[column]]
        for row in range(n):
            if row == column:
                continue
            factor = work[row][column]
            work[row] = [a - factor * b for a, b in zip(work[row], work[column])]
    return [row[-1] for row in work]


def _ridge(rows, targets, indices, alpha):
    dimension = len(rows[0])
    matrix = [[0.0] * dimension for _ in range(dimension)]
    vector = [0.0] * dimension
    for i in indices:
        row, target = rows[i], targets[i]
        for a in range(dimension):
            vector[a] += row[a] * target
            for b in range(dimension):
                matrix[a][b] += row[a] * row[b]
    for a in range(dimension):
        matrix[a][a] += alpha if a else 1e-6
    return _solve(matrix, vector)


def train_model(contexts, search_budget=8, members=7, seed=2026, alpha=4.0):
    """Labels are marginal goal-solve fractions, including zero and regressions.

    Bootstrap samples whole training contexts rather than rows, to avoid
    pretending correlated candidates are independent uncertainty evidence.
    """
    raw, targets, context_rows = [], [], []
    for context in contexts:
        goals = context.get("goals", [])
        baseline = [search(context, g["source"], g["target"], search_budget)["solved"] for g in goals]
        indices = []
        for candidate in generate_candidates(context, goals):
            augmented = [search(context, g["source"], g["target"], search_budget, [candidate])["solved"] for g in goals]
            target = sum(int(a) - int(b) for a, b in zip(augmented, baseline)) / max(1, len(goals))
            indices.append(len(raw))
            raw.append(candidate["features"])
            targets.append(target)
        if indices:
            context_rows.append(indices)
    if not raw or not context_rows:
        raise ValueError("No training candidates")
    dimension = len(FEATURE_NAMES)
    means = [sum(row[i] for row in raw) / len(raw) for i in range(dimension)]
    scales = [max(1e-6, math.sqrt(sum((row[i] - means[i]) ** 2 for row in raw) / len(raw))) for i in range(dimension)]
    rows = [[1.0] + [(v - mean) / scale for v, mean, scale in zip(row, means, scales)] for row in raw]
    rng = random.Random(seed)
    weights = []
    for _ in range(members):
        bootstrap = [index for _ in context_rows for index in rng.choice(context_rows)]
        weights.append(_ridge(rows, targets, bootstrap, alpha))
    return {"schema_version": 1, "kind": "context-bootstrap-ridge", "feature_names": FEATURE_NAMES,
            "means": means, "scales": scales, "weights": weights,
            "exploration": 0.35, "redundancy_penalty": 0.02,
            "training": {"context_ids": [c["id"] for c in contexts], "examples": len(raw),
                         "contexts": len(context_rows), "search_budget": search_budget,
                         "seed": seed, "alpha": alpha, "members": members,
                         "positive_labels": sum(y > 0 for y in targets), "negative_labels": sum(y < 0 for y in targets),
                         "zero_labels": sum(y == 0 for y in targets),
                         "label": "one-lemma marginal downstream solve fraction"},
            "limitations": "Synthetic implication graphs only. Disagreement is not calibrated confidence. No claim of new mathematics or superiority on Mathlib."}


def predict(model, features):
    if model.get("feature_names") != FEATURE_NAMES or len(features) != len(FEATURE_NAMES):
        raise ValueError("Model feature contract does not match this engine")
    row = [1.0] + [(v - mean) / scale for v, mean, scale in zip(features, model["means"], model["scales"])]
    predictions = [sum(a * b for a, b in zip(weights, row)) for weights in model["weights"]]
    if not predictions:
        raise ValueError("Empty model ensemble")
    mean = sum(predictions) / len(predictions)
    deviation = math.sqrt(sum((p - mean) ** 2 for p in predictions) / len(predictions))
    return mean, deviation


_DEFAULT = None


def default_model():
    global _DEFAULT
    if _DEFAULT is None:
        # Same frozen training contexts as the benchmark; never trained on the
        # user's context or test outcomes. Bundled training is CPU deterministic.
        from .benchmark import make_context
        _DEFAULT = train_model([make_context(seed, "train") for seed in range(1000, 1016)])
    return _DEFAULT
