"""Small usefulness model for the typed ``List Nat`` capacity domain.

This is standard feature hashing plus a context-bootstrap ridge ensemble, not a
new learning algorithm or a pretrained theorem embedding.  Its historical reuse
prior is measured from successful *training* search witnesses.  It makes no
claim to reproduce Mathlib's chronology or human mathematical usefulness.

Only operation syntax, graph structure, visible task endpoints and the frozen
training model enter selection.  Held-out search outcomes never enter features.
"""
from __future__ import annotations

from collections import Counter
import copy
import hashlib
import math
import random

from .engine import (
    FEATURE_NAMES, _all_paths, candidate_features, context_hash,
    generate_candidates, search, validate_context, validate_goals,
)
from .model import _ridge

EMBEDDING_DIMENSION = 16
HISTORY_FEATURE_NAMES = [
    "history_mean_dependency_frequency",
    "history_max_dependency_frequency",
    "history_mean_transition_frequency",
    "history_unseen_dependency_fraction",
]
NATURAL_FEATURE_NAMES = (
    ["structure_" + name for name in FEATURE_NAMES]
    + [f"symbolic_hash_{i:02d}" for i in range(EMBEDDING_DIMENSION)]
    + HISTORY_FEATURE_NAMES
)
_OPERATIONS = frozenset(("input", "filter", "map", "reverse", "take"))


def _expressions(context):
    """Read data-only ASTs; labels, identifiers and goal results are not tokens."""
    mapping = context.get("expressions", {})
    if not isinstance(mapping, dict):
        raise ValueError("Natural expression mapping must be an object")
    metadata = context.get("metadata", {})
    fallback = metadata.get("expressions", {}) if isinstance(metadata, dict) else {}
    if not isinstance(fallback, dict):
        fallback = {}
    result = {}
    for item in context["nodes"]:
        expression = item.get("expression", mapping.get(item["id"], fallback.get(item["id"])))
        if not isinstance(expression, dict) or expression.get("op") not in _OPERATIONS:
            raise ValueError("Each natural node needs a supported List Nat expression")
        result[item["id"]] = expression
    for expression in result.values():
        if expression["op"] != "input" and expression.get("input") not in result:
            raise ValueError("A natural expression has an unknown parent")
    return result


def _primitive_path(context, path):
    """Expand the seed once into its primitive proof dependencies."""
    primitive = {edge["id"]: edge for edge in context["edges"]}
    seed = context["seed"]
    expanded = []
    for identifier in path:
        dependencies = seed["path"] if identifier == seed["id"] else [identifier]
        for dependency in dependencies:
            if dependency not in primitive:
                raise ValueError("Natural model witness contains an unknown dependency")
            expanded.append(primitive[dependency])
    return expanded


def _dependency_signatures(context, path, expressions=None):
    expressions = expressions or _expressions(context)
    return [expressions[edge["source"]]["op"] + ">" + expressions[edge["target"]]["op"]
            for edge in _primitive_path(context, path)]


def _expression_syntax(expressions, identifier):
    """Canonical bounded operator chain, independent of proposition spelling."""
    chain, seen = [], set()
    while True:
        if identifier in seen:
            raise ValueError("Natural expression syntax must be acyclic")
        seen.add(identifier)
        expression = expressions[identifier]
        chain.append(expression["op"])
        if expression["op"] == "input":
            return list(reversed(chain))
        identifier = expression["input"]


def _symbolic_tokens(context, candidate, expressions=None):
    expressions = expressions or _expressions(context)
    source = _expression_syntax(expressions, candidate["source"])
    target = _expression_syntax(expressions, candidate["target"])
    signatures = _dependency_signatures(context, candidate["path"], expressions)
    # Tokens encode the actual typed statement family and compositional syntax,
    # but no random node names, scenario ids, labels or supplied outcome fields.
    tokens = ["type:List:Nat", "statement:length:le:capacity", "proof:implication:composition"]
    tokens += ["source:op:" + op for op in source]
    tokens += ["target:op:" + op for op in target]
    tokens += ["source:pair:" + a + ">" + b for a, b in zip(source, source[1:])]
    tokens += ["target:pair:" + a + ">" + b for a, b in zip(target, target[1:])]
    tokens += ["dependency:" + signature for signature in signatures]
    tokens += ["path:pair:" + a + "/" + b for a, b in zip(signatures, signatures[1:])]
    return tokens


def symbolic_embedding(context, candidate, dimension=EMBEDDING_DIMENSION):
    """Deterministic signed SHA-256 feature hash, normalized to unit length.

    Hash collisions are expected in this deliberately compact representation.
    The vector is symbolic syntax, not semantic understanding or a neural model.
    """
    if not isinstance(dimension, int) or isinstance(dimension, bool) or dimension <= 0:
        raise ValueError("Embedding dimension must be a positive integer")
    vector = [0.0] * dimension
    for token in _symbolic_tokens(context, candidate):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        bucket = int.from_bytes(digest[:8], "big") % dimension
        vector[bucket] += 1.0 if digest[8] & 1 else -1.0
    norm = math.sqrt(sum(value * value for value in vector))
    return [value / norm for value in vector] if norm else vector


def _training_history(contexts, search_budget):
    dependencies, transitions = Counter(), Counter()
    successful = 0
    for context in contexts:
        expressions = _expressions(context)
        for goal in context.get("goals", []):
            result = search(context, goal["source"], goal["target"], search_budget)
            if not result["solved"]:
                continue
            successful += 1
            signatures = _dependency_signatures(context, result["path"], expressions)
            dependencies.update(signatures)
            transitions.update(a + "/" + b for a, b in zip(signatures, signatures[1:]))
    return {
        "source": "successful frozen training baseline proof-search witnesses only",
        "signature_counts": dict(sorted(dependencies.items())),
        "transition_counts": dict(sorted(transitions.items())),
        "dependency_occurrences": sum(dependencies.values()),
        "transition_occurrences": sum(transitions.values()),
        "successful_training_goals": successful,
        "search_budget": search_budget,
        "interpretation": "Operator-motif reuse, not Mathlib history or human theorem citations.",
    }


def _history_features(context, candidate, history):
    signatures = _dependency_signatures(context, candidate["path"])
    counts = history.get("signature_counts", {})
    transition_counts = history.get("transition_counts", {})
    total = max(1, history.get("dependency_occurrences", 0))
    pair_total = max(1, history.get("transition_occurrences", 0))
    frequencies = [counts.get(signature, 0) / total for signature in signatures]
    pairs = [transition_counts.get(a + "/" + b, 0) / pair_total
             for a, b in zip(signatures, signatures[1:])]
    return [
        sum(frequencies) / max(1, len(frequencies)),
        max(frequencies, default=0.0),
        sum(pairs) / max(1, len(pairs)),
        sum(signature not in counts for signature in signatures) / max(1, len(signatures)),
    ]


def natural_features(context, candidate, goals=(), history=None, paths=None):
    """Structure + typed syntax hash + frozen training reuse (32 features)."""
    return (candidate_features(context, candidate, goals, paths)
            + symbolic_embedding(context, candidate)
            + _history_features(context, candidate, history or {}))


def train_natural_model(contexts, search_budget=8, members=7, seed=2026, alpha=4.0):
    """Train exclusively on the contexts supplied as the frozen training split.

    Callers retain split assignment; the returned exact context hashes allow a
    benchmark to reject overlap. Explicit ``split=test/validation`` metadata is
    rejected. Hyperparameters are fixed independently of held-out outcomes.
    """
    contexts = list(contexts)
    if not contexts:
        raise ValueError("Natural training needs frozen training contexts")
    if not isinstance(search_budget, int) or isinstance(search_budget, bool) or search_budget < 0:
        raise ValueError("Search budget must be a nonnegative integer")
    if not isinstance(members, int) or isinstance(members, bool) or members < 1:
        raise ValueError("Ensemble needs at least one member")
    if not isinstance(alpha, (int, float)) or not math.isfinite(alpha) or alpha <= 0:
        raise ValueError("Ridge regularization must be positive and finite")
    for context in contexts:
        validate_context(context)
        _expressions(context)
        split = context.get("split", context.get("metadata", {}).get("split") if isinstance(context.get("metadata"), dict) else None)
        if split in ("test", "validation"):
            raise ValueError("Held-out contexts cannot enter natural model training")
    hashes = [context_hash(context) for context in contexts]
    if len(set(hashes)) != len(hashes):
        raise ValueError("Training contexts must be distinct")
    history = _training_history(contexts, search_budget)
    raw, targets, context_rows = [], [], []
    for context in contexts:
        goals = context.get("goals", [])
        baseline = [search(context, goal["source"], goal["target"], search_budget)["solved"] for goal in goals]
        paths = _all_paths(context)
        indices = []
        for candidate in generate_candidates(context, goals):
            augmented = [search(context, goal["source"], goal["target"], search_budget, [candidate])["solved"] for goal in goals]
            target = sum(int(after) - int(before) for after, before in zip(augmented, baseline)) / max(1, len(goals))
            indices.append(len(raw))
            raw.append(natural_features(context, candidate, goals, history, paths))
            targets.append(target)
        if indices:
            context_rows.append(indices)
    if not raw:
        raise ValueError("No natural training candidates")
    dimension = len(NATURAL_FEATURE_NAMES)
    means = [sum(row[i] for row in raw) / len(raw) for i in range(dimension)]
    scales = [max(1e-6, math.sqrt(sum((row[i] - means[i]) ** 2 for row in raw) / len(raw))) for i in range(dimension)]
    rows = [[1.0] + [(value - mean) / scale for value, mean, scale in zip(row, means, scales)] for row in raw]
    rng = random.Random(seed)
    weights = []
    for _ in range(members):
        bootstrap = [index for _ in context_rows for index in rng.choice(context_rows)]
        weights.append(_ridge(rows, targets, bootstrap, alpha))
    return {
        "schema_version": 1,
        "kind": "natural-list-capacity-context-bootstrap-ridge-v1",
        "feature_names": NATURAL_FEATURE_NAMES,
        "means": means, "scales": scales, "weights": weights,
        "history": history,
        "exploration": 0.35, "redundancy_penalty": 0.02,
        "training": {
            "context_ids": [context["id"] for context in contexts],
            "context_sha256": hashes,
            "examples": len(raw), "contexts": len(context_rows),
            "search_budget": search_budget, "seed": seed,
            "alpha": alpha, "members": members,
            "positive_labels": sum(value > 0 for value in targets),
            "zero_labels": sum(value == 0 for value in targets),
            "negative_labels": sum(value < 0 for value in targets),
            "label": "one-lemma marginal bounded downstream solve fraction",
            "embedding": "16-dimensional normalized signed SHA-256 hash of typed operator syntax; not pretrained",
            "history": "operator motifs of successful frozen training baseline proof witnesses only",
        },
        "limitations": [
            "Typed List Nat capacity pipelines only; not arbitrary Lean or Mathlib.",
            "Conventional ridge regression and symbolic feature hashing, not a new ML algorithm.",
            "Historical reuse is generated training proof usage, not chronological mathematical library reuse.",
            "Ensemble disagreement is not calibrated epistemic uncertainty.",
            "No test outcome labels, held-out proof paths, neural embeddings or language model are used in selection.",
            "Kernel verification and natural-language fidelity are separate from this ranking estimate.",
        ],
    }


def predict_natural(model, features):
    if model.get("kind") != "natural-list-capacity-context-bootstrap-ridge-v1" or model.get("feature_names") != NATURAL_FEATURE_NAMES:
        raise ValueError("Natural model feature contract does not match")
    if len(features) != len(NATURAL_FEATURE_NAMES):
        raise ValueError("Natural feature vector has the wrong size")
    dimension = len(features)
    if len(model.get("means", [])) != dimension or len(model.get("scales", [])) != dimension:
        raise ValueError("Natural model normalization has the wrong size")
    if any(not math.isfinite(value) for value in features):
        raise ValueError("Natural features must be finite")
    if any(not math.isfinite(value) or value <= 0 for value in model["scales"]):
        raise ValueError("Natural model scales must be positive and finite")
    row = [1.0] + [(value - mean) / scale for value, mean, scale in zip(features, model["means"], model["scales"])]
    weights = model.get("weights", [])
    if not weights or any(len(member) != dimension + 1 or any(not math.isfinite(value) for value in member) for member in weights):
        raise ValueError("Invalid natural model ensemble")
    predictions = [sum(weight * value for weight, value in zip(member, row)) for member in weights]
    mean = sum(predictions) / len(predictions)
    spread = math.sqrt(sum((value - mean) ** 2 for value in predictions) / len(predictions))
    return mean, spread


def select_natural(context, candidates, goals, k=3, model=None):
    """Select with an explicit frozen model; never fit on the user's context."""
    if model is None:
        raise ValueError("Supply a frozen model from train_natural_model")
    if not isinstance(k, int) or isinstance(k, bool) or k < 0:
        raise ValueError("Selection budget must be a nonnegative integer")
    validate_context(context)
    validate_goals(context, goals)
    _expressions(context)
    ranked = copy.deepcopy(candidates)
    paths = _all_paths(context)
    for candidate in ranked:
        candidate["features"] = natural_features(context, candidate, goals, model.get("history", {}), paths)
        mean, spread = predict_natural(model, candidate["features"])
        candidate["score"] = mean + model.get("exploration", 0.35) * spread
        candidate["uncertainty"] = spread
    chosen, pending = [], ranked[:]
    while pending and len(chosen) < min(k, len(ranked)):
        def adjusted(candidate):
            witness = set(candidate["path"])
            similarity = max((len(witness & set(item["path"])) / max(1, len(witness | set(item["path"])))
                              for item in chosen), default=0.0)
            return candidate["score"] - model.get("redundancy_penalty", 0.02) * similarity, candidate["id"]
        best = max(pending, key=adjusted)
        chosen.append(best)
        pending.remove(best)
    by_id = {candidate["id"]: candidate for candidate in ranked}
    for candidate in candidates:
        candidate.update({key: by_id[candidate["id"]][key] for key in ("features", "score", "uncertainty")})
    return chosen
