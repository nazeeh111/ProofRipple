"""Compact ridge ensembles for measured Mathlib-registry consequence utility.

Conventional feature hashing/regression, not a new learning algorithm. Training
uses only frozen training contexts and successful training proof motifs.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import math
import random

from .mathlib import validate_context
from .mathlib_search import (
    _tokens, demand_graphs, demand_inventory, direct_proof, nontrivial_and_nodes, proof_cost, proof_rules,
    search, subterms, syntax, term_depth, term_size,
)
from .model import _ridge
from .engine import context_hash

STRUCTURE_NAMES = ["source_nodes", "target_nodes", "source_depth", "target_depth",
                   "proof_nodes", "seed_calls", "binary_nodes", "nontrivial_and_nodes",
                   "goal_demand_coverage", "demand_pair_frequency", "source_subterm_hits",
                   "target_subterm_hits", "mean_goal_term_nodes", "search_budget",
                   "proof_nodes_per_budget", "variable_count"]
BASE_FEATURE_NAMES = STRUCTURE_NAMES + [f"symbolic_hash_{i:02d}" for i in range(16)] + [
    "history_mean_rule_frequency", "history_max_rule_frequency", "history_transition_frequency", "history_unseen_rule_fraction"]
CONDITIONAL_NAMES = ["selected_count", "selected_exact_obligation_fraction", "candidate_new_obligation_fraction",
                     "candidate_already_supplied", "new_exact_and_complement_fraction", "candidate_selected_common_goal_fraction",
                     "selected_mean_proof_cost", "candidate_selected_rule_overlap"]
FEATURE_NAMES = BASE_FEATURE_NAMES + CONDITIONAL_NAMES
PARTNER_SIZES = (0, 1, 2, 3, 4)
RULE_CONSTANTS = {"seed": "inf_sup_left", "refl": "le_rfl", "inf_left": "inf_le_left",
                  "inf_right": "inf_le_right", "sup_left": "le_sup_left", "sup_right": "le_sup_right",
                  "sup_le": "sup_le", "le_inf": "le_inf", "sup_mono": "sup_le_sup",
                  "inf_mono": "inf_le_inf", "trans": "le_trans"}


def _rules(witness):
    names = [RULE_CONSTANTS[witness["rule"]]]
    pairs = []
    for child in witness.get("children", []):
        child_names, child_pairs = _rules(child)
        names.extend(child_names)
        pairs.append(names[0] + ">" + child_names[0])
        pairs.extend(child_pairs)
    return names, pairs


def _history(contexts, budgets):
    rules, transitions = Counter(), Counter()
    seen = set()
    successes = 0
    for context in contexts:
        for goal in context["goals"]:
            for budget in budgets:
                result = search(goal["source"], goal["target"], budget, intermediates=context.get("intermediates", []))
                if not result["solved"]:
                    continue
                successes += 1
                key = (context["id"], syntax(goal["source"]), syntax(goal["target"]),
                       json.dumps(result["proof"], sort_keys=True, separators=(",", ":")))
                if key in seen:
                    continue
                seen.add(key)
                names, pairs = _rules(result["proof"])
                rules.update(names)
                transitions.update(pairs)
    return {"source": "Unique successful frozen training baseline proof ASTs; deduplicated across budget profiles before counting",
            "rule_counts": dict(sorted(rules.items())), "transition_counts": dict(sorted(transitions.items())),
            "rule_occurrences": sum(rules.values()), "transition_occurrences": sum(transitions.values()),
            "unique_proofs": len(seen), "successful_profile_queries_before_dedup": successes,
            "budgets": list(budgets), "interpretation": "Generated training proof use of actual registered Mathlib constants; not Mathlib chronology or human citation counts."}


def condition_features(base, candidate, goals, demands, graphs, selected=()):
    keys = {(syntax(item["source"]), syntax(item["target"])) for item in selected}
    key = syntax(candidate["source"]), syntax(candidate["target"])
    total = max(1, sum(len(inventory) for inventory in demands))
    complementary = groups = 0
    for graph in graphs:
        direct = graph.get("_direct_pairs")
        if direct is None:
            direct = {pair for pair, terms in graph["terms"].items() if direct_proof(*terms)}
            graph["_direct_pairs"] = direct
        before = keys | direct
        after = before | {key}
        for parent, options in graph["nodes"].items():
            if parent in after:
                continue
            for _, a, b in options:
                groups += 1
                complementary += a in after and b in after and not(a in before and b in before)
    rules = set(proof_rules(candidate.get("proof_ast", candidate["proof"])))
    prior_rules = set().union(*(set(proof_rules(item.get("proof_ast", item["proof"]))) for item in selected)) if selected else set()
    conditional = [len(selected)/5, sum(len(keys & inventory) for inventory in demands)/total,
                   sum(key in inventory and key not in keys for inventory in demands)/max(1, len(goals)),
                   float(key in keys), complementary/max(1, groups),
                   sum(key in inventory and bool(keys & inventory) for inventory in demands)/max(1, len(goals)),
                   sum(proof_cost(item.get("proof_ast", item["proof"])) for item in selected)/(64*max(1, len(selected))),
                   len(rules & prior_rules)/max(1, len(rules | prior_rules))]
    return list(base[:len(BASE_FEATURE_NAMES)]) + conditional


def features(context, candidate, goals, budget, history, demands=None, selected=(), graphs=None):
    graphs = graphs if graphs is not None else demand_graphs({**context, "goals": goals})
    demands = demands if demands is not None else [set(graph["nodes"]) for graph in graphs]
    source, target = candidate["source"], candidate["target"]
    witness = candidate.get("proof_ast", candidate["proof"])
    rules = proof_rules(witness)
    key = syntax(source), syntax(target)
    matching = sum(key in inventory for inventory in demands)
    denominator = max(1, len(goals))
    source_key, target_key = key
    goal_subterms = [set(subterms(goal["source"])) | set(subterms(goal["target"])) for goal in goals]
    atoms = {node["index"] for node in [*subterms(source).values(), *subterms(target).values()] if node["op"] == "var"}
    vector = [term_size(source)/127, term_size(target)/127, term_depth(source)/12, term_depth(target)/12,
              proof_cost(witness)/64, rules["seed"]/8, sum(value for name, value in rules.items() if name in ("sup_le", "le_inf", "sup_mono", "inf_mono", "trans"))/32,
              nontrivial_and_nodes(witness)/16, matching/denominator,
              matching/max(1, sum(len(inventory) for inventory in demands)),
              sum(source_key in terms for terms in goal_subterms)/denominator,
              sum(target_key in terms for terms in goal_subterms)/denominator,
              sum(term_size(goal["source"])+term_size(goal["target"]) for goal in goals)/(254*denominator),
              budget/12, proof_cost(witness)/(budget+1), len(atoms)/6]
    embedding = [0.0] * 16
    for token, count in _tokens(source, target).items():
        digest = hashlib.sha256(token.encode()).digest()
        embedding[int.from_bytes(digest[:8], "big") % 16] += count * (1 if digest[8] & 1 else -1)
    norm = math.sqrt(sum(value*value for value in embedding))
    vector.extend(value/norm if norm else 0.0 for value in embedding)
    names, pairs = _rules(witness)
    frequencies = [history.get("rule_counts", {}).get(name, 0)/max(1, history.get("rule_occurrences", 0)) for name in names]
    transitions = [history.get("transition_counts", {}).get(pair, 0)/max(1, history.get("transition_occurrences", 0)) for pair in pairs]
    vector.extend([sum(frequencies)/max(1, len(frequencies)), max(frequencies, default=0.0),
                   sum(transitions)/max(1, len(transitions)),
                   sum(name not in history.get("rule_counts", {}) for name in names)/max(1, len(names))])
    return condition_features(vector, candidate, goals, demands, graphs, selected)


def partner_portfolios(context, candidate, seed=2027):
    others = sorted((item for item in context["candidates"] if item["id"] != candidate["id"]), key=lambda item: item["id"])
    used, result = set(), []
    for requested in PARTNER_SIZES:
        count = min(requested, len(others))
        salt = f"{seed}/{context['id']}/{candidate['id']}/{requested}"
        rng = random.Random(int.from_bytes(hashlib.sha256(salt.encode()).digest()[:8], "big"))
        portfolio = sorted(rng.sample(others, count), key=lambda item: item["id"])
        key = tuple(item["id"] for item in portfolio)
        if key not in used:
            used.add(key)
            result.append(portfolio)
    return result


def _fit(raw, targets, context_rows, indices, members, seed, alpha):
    values = [[row[i] for i in indices] for row in raw]
    eligible = sorted({index for rows in context_rows for index in rows})
    means = [sum(values[row][i] for row in eligible)/len(eligible) for i in range(len(indices))]
    scales = [max(1e-6, math.sqrt(sum((values[row][i]-means[i])**2 for row in eligible)/len(eligible))) for i in range(len(indices))]
    rows = [[1.0] + [(value-mean)/scale for value, mean, scale in zip(row, means, scales)] for row in values]
    rng = random.Random(seed)
    weights = []
    for _ in range(members):
        bootstrap = [index for _ in context_rows for index in rng.choice(context_rows)]
        weights.append(_ridge(rows, targets, bootstrap, alpha))
    return {"indices": indices, "means": means, "scales": scales, "weights": weights}


def train_mathlib_model(contexts, budgets=(4, 8, 12), members=7, seed=2027, alpha=4.0, label_sink=None):
    contexts = list(contexts)
    if not contexts or any(context.get("metadata", {}).get("split") != "train" for context in contexts):
        raise ValueError("Mathlib model requires explicitly frozen training contexts only")
    identifiers = [context.get("id") for context in contexts]
    if (any(not isinstance(identifier, str) or identifier.startswith(("test_", "validation_")) for identifier in identifiers)
            or len(set(identifiers)) != len(identifiers)):
        raise ValueError("Training context identifiers must be distinct and must not identify a held-out split")
    for context in contexts:
        validate_context(context)
    history = _history(contexts, budgets)
    raw, targets, context_rows, labels, singleton_indices = [], [], [], [], []
    search_queries = baseline_cache_hits = 0
    for context in contexts:
        rows = []
        graphs = demand_graphs(context)
        demands = [set(graph["nodes"]) for graph in graphs]
        baseline_cache = {}
        for budget in budgets:
            for candidate in context["candidates"]:
                base_features = features(context, candidate, context["goals"], budget, history, demands, graphs=graphs)
                for prefix in partner_portfolios(context, candidate, seed):
                    prefix_ids = tuple(item["id"] for item in prefix)
                    cache_key = budget, prefix_ids
                    if cache_key not in baseline_cache:
                        baseline_cache[cache_key] = [search(goal["source"], goal["target"], budget, prefix, context.get("intermediates", []))["solved"] for goal in context["goals"]]
                        search_queries += len(context["goals"])
                    else:
                        baseline_cache_hits += 1
                    baseline = baseline_cache[cache_key]
                    augmented = [search(goal["source"], goal["target"], budget, [*prefix, candidate], context.get("intermediates", []))["solved"] for goal in context["goals"]]
                    search_queries += len(context["goals"])
                    target = sum(int(a)-int(b) for a, b in zip(augmented, baseline))/max(1, len(baseline))
                    rows.append(len(raw))
                    if not prefix:
                        singleton_indices.append(len(raw))
                    raw.append(condition_features(base_features, candidate, context["goals"], demands, graphs, prefix))
                    targets.append(target)
                    labels.append({"context_id": context["id"], "candidate_id": candidate["id"], "budget": budget,
                                   "prefix_ids": list(prefix_ids), "marginal_solve_fraction": target})
        if rows:
            context_rows.append(rows)
    if not raw:
        raise ValueError("No Mathlib training candidates")
    singleton_set = set(singleton_indices)
    singleton_rows = [[index for index in rows if index in singleton_set] for rows in context_rows]
    singleton_rows = [rows for rows in singleton_rows if rows]
    structure_indices = [*range(len(STRUCTURE_NAMES)), *range(len(BASE_FEATURE_NAMES), len(FEATURE_NAMES))]
    if label_sink is not None:
        label_sink.extend(labels)
    return {"schema_version": 1, "kind": "mathlib-set-lattice-ridge-v1", "feature_names": FEATURE_NAMES,
            "ensembles": {"full": _fit(raw, targets, context_rows, list(range(len(FEATURE_NAMES))), members, seed, alpha),
                          "structure": _fit(raw, targets, context_rows, structure_indices, members, seed, alpha),
                          "singleton": _fit(raw, targets, singleton_rows, list(range(len(FEATURE_NAMES))), members, seed, alpha)},
            "history": history, "exploration": 0.35, "diversity_penalty": 0.02,
            "training": {"context_ids": [context["id"] for context in contexts],
                         "context_sha256": [context_hash(context) for context in contexts],
                         "examples": len(raw), "contexts": len(context_rows), "budgets": list(budgets),
                         "members": members, "seed": seed, "alpha": alpha, "partner_sizes": list(PARTNER_SIZES),
                         "singleton_examples": len(singleton_indices), "actual_label_search_queries": search_queries,
                         "training_prefix_baseline_cache_hits": baseline_cache_hits,
                         "positive_labels": sum(value>0 for value in targets), "zero_labels": sum(value==0 for value in targets),
                         "negative_labels": sum(value<0 for value in targets),
                         "target": "Portfolio-conditioned marginal solve fraction U(S+c)-U(S), at B4/8/12 with fixed seeded prefix sizes0..4; no test outcomes or utility-adaptive partners",
                         "labels_sha256": hashlib.sha256(json.dumps(labels, sort_keys=True).encode()).hexdigest()},
            "limitations": ["Standard ridge/bootstrap/feature hashing, not a new ML algorithm.",
                            "Immediate marginal labels still need not anticipate future AND completion from an empty prefix.",
                            "Ensemble spread is not calibrated uncertainty.",
                            "Proof motif history is generated training use, not mathematical library chronology."]}


def predict(model, vector, structure_only=False, singleton=False):
    if model.get("kind") != "mathlib-set-lattice-ridge-v1" or model.get("feature_names") != FEATURE_NAMES:
        raise ValueError("Incompatible Mathlib usefulness model")
    ensemble = model["ensembles"]["singleton" if singleton else "structure" if structure_only else "full"]
    row = [1.0] + [(vector[index]-mean)/scale for index, mean, scale in zip(ensemble["indices"], ensemble["means"], ensemble["scales"])]
    estimates = [sum(a*b for a, b in zip(weights, row)) for weights in ensemble["weights"]]
    mean = sum(estimates)/len(estimates)
    return mean, math.sqrt(sum((value-mean)**2 for value in estimates)/len(estimates))
