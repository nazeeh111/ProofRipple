"""Outcome-blind policies and bounded AND/OR search over real set inclusions.

DNF/alpha normalization belongs to dataset cleaning, never to this proof search.
A budget unit is one visited goal state, not a Lean tactic step or proof size.
"""
from __future__ import annotations

from collections import Counter
import copy
from functools import lru_cache
import hashlib
import json
import math
import random
import time

from .mathlib import validate_context, validate_term
from .engine import context_hash

METHODS = ("learned", "learned_no_bonus", "learned_singleton", "structure_only", "random", "semantic",
           "graph", "proof_cost", "greedy_coverage", "branching_aware")
MAX_PIVOTS = 8
MAX_DEPTH = 32
OBLIGATION_DEPTH = 4
OBLIGATION_CAP = 128
SCORE_TIE_DIGITS = 12
GRAPH_CACHE_SIZE = 32


def var(index):
    return {"op": "var", "index": index}


def op(kind, left, right):
    return {"op": kind, "left": left, "right": right}


def syntax(term):
    return json.dumps(term, sort_keys=True, separators=(",", ":"))


def _local_term_keys():
    """Identity memo confined to one immutable-input search/graph operation.

    Retaining the object prevents identity reuse. Nothing is cached across a
    caller's later mutation, and every value is the original syntax() bytes.
    """
    memo = {}
    def key(term):
        entry = memo.get(id(term))
        if entry is None:
            entry = term, syntax(term)
            memo[id(term)] = entry
        return entry[1]
    return key


def term_size(term):
    return 1 if term["op"] == "var" else 1 + term_size(term["left"]) + term_size(term["right"])


def term_depth(term):
    return 0 if term["op"] == "var" else 1 + max(term_depth(term["left"]), term_depth(term["right"]))


def subterms(term):
    result = {syntax(term): term}
    if term["op"] != "var":
        result.update(subterms(term["left"]))
        result.update(subterms(term["right"]))
    return result


def proof(rule, source, target, children=(), **extra):
    return {"rule": rule, "source": source, "target": target, "children": list(children), **extra}


def proof_cost(witness):
    return 1 + sum(proof_cost(child) for child in witness.get("children", []))


def proof_rules(witness):
    result = Counter([witness["rule"]])
    for child in witness.get("children", []):
        result.update(proof_rules(child))
    return result


def nontrivial_and_nodes(witness):
    children = witness.get("children", [])
    return int(len(children) == 2 and all(proof_cost(child) > 1 for child in children)) + sum(nontrivial_and_nodes(child) for child in children)


def direct_proof(source, target):
    """Only exact syntactic registered leaves; no semantic equality test."""
    if source == target:
        return proof("refl", source, target)
    if source["op"] == "meet":
        for key, rule in (("left", "inf_left"), ("right", "inf_right")):
            if source[key] == target:
                return proof(rule, source, target)
    if target["op"] == "join":
        for key, rule in (("left", "sup_left"), ("right", "sup_right")):
            if target[key] == source:
                return proof(rule, source, target)
    if source["op"] == "meet" and source["right"]["op"] == "join":
        a, b, c = source["left"], source["right"]["left"], source["right"]["right"]
        if target == op("join", op("meet", a, b), op("meet", a, c)):
            return proof("seed", source, target)
    return None


def _pivot_menu(source, target, lemmas, intermediates, key_fn=syntax):
    menu = []
    for item in lemmas:
        if item["target"] == target:
            menu.append(item["source"])
        if item["source"] == source:
            menu.append(item["target"])
    if source["op"] == "meet" and source["right"]["op"] == "join":
        a, b, c = source["left"], source["right"]["left"], source["right"]["right"]
        menu.append(op("join", op("meet", a, b), op("meet", a, c)))
    if (target["op"] == "join" and target["left"]["op"] == "meet"
            and target["right"]["op"] == "meet" and target["left"]["left"] == target["right"]["left"]):
        menu.append(op("meet", target["left"]["left"], op("join", target["left"]["right"], target["right"]["right"])))
    if source["op"] == "meet":
        menu.extend([source["left"], source["right"]])
    if target["op"] == "join":
        menu.extend([target["left"], target["right"]])
    menu.extend(sorted(intermediates, key=lambda item: (term_size(item), key_fn(item))))
    seen = {key_fn(source), key_fn(target)}
    result = []
    for item in menu:
        try:
            validate_term(item)
        except ValueError:
            continue
        key = key_fn(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
            if len(result) == MAX_PIVOTS:
                break
    return result


def search(source, target, budget=8, lemmas=(), intermediates=()):
    validate_term(source)
    validate_term(target)
    if not isinstance(budget, int) or isinstance(budget, bool) or not 0 <= budget <= 256:
        raise ValueError("Mathlib search budget must be 0..256 goal-state visits")
    lemmas = sorted(lemmas, key=lambda item: item["id"])
    if len(intermediates) > 8:
        raise ValueError("At most eight frozen search intermediates are allowed")
    for term in intermediates:
        validate_term(term)
    term_key = _local_term_keys()
    known = {(term_key(item["source"]), term_key(item["target"])): item for item in lemmas}
    memo, active = {}, set()
    stats = {"expansions": 0, "applicable_rule_attempts": 0, "cache_hits": 0, "cycle_cuts": 0}

    def solve(left, right, depth):
        if stats["expansions"] >= budget:
            return None
        stats["expansions"] += 1
        key = term_key(left), term_key(right)
        if key in memo:
            stats["cache_hits"] += 1
            return memo[key]
        item = known.get(key)
        found = proof("lemma", left, right, lemma_id=item["id"]) if item else direct_proof(left, right)
        if found:
            memo[key] = found
            return found
        if key in active or depth >= MAX_DEPTH:
            stats["cycle_cuts"] += 1
            return None
        active.add(key)
        options = []
        if left["op"] == right["op"] and left["op"] in ("join", "meet"):
            options.append(("sup_mono" if left["op"] == "join" else "inf_mono",
                            (left["left"], right["left"]), (left["right"], right["right"])))
        if left["op"] == "join":
            options.append(("sup_le", (left["left"], right), (left["right"], right)))
        if right["op"] == "meet":
            options.append(("le_inf", (left, right["left"]), (left, right["right"])))
        options.extend(("trans", (left, middle), (middle, right))
                       for middle in _pivot_menu(left, right, lemmas, intermediates, term_key))
        for rule, first, second in options:
            if stats["expansions"] >= budget:
                break
            stats["applicable_rule_attempts"] += 1
            a = solve(*first, depth + 1)
            if a is not None:
                b = solve(*second, depth + 1)
                if b is not None:
                    found = proof(rule, left, right, [a, b])
                    memo[key] = found
                    active.remove(key)
                    return found
        active.remove(key)
        return None

    witness = solve(source, target, 0)
    return {"solved": witness is not None, **stats, "proof": witness,
            "proof_nodes": proof_cost(witness) if witness else None,
            "nontrivial_and_nodes": nontrivial_and_nodes(witness) if witness else 0}


def _build_obligation_graph(source, target, intermediates=()):
    """A capped raw AND/OR menu; matching is syntactic, never entailment."""
    queue = [(source, target, 0)]
    seen, nodes, terms = set(), {}, {}
    visits = 0
    term_key = _local_term_keys()
    while queue and len(nodes) < OBLIGATION_CAP:
        left, right, depth = queue.pop(0)
        visits += 1
        key = term_key(left), term_key(right)
        if key in seen:
            continue
        seen.add(key)
        terms[key] = (left, right)
        nodes[key] = []
        if depth >= OBLIGATION_DEPTH:
            continue
        options = []
        if left["op"] == right["op"] and left["op"] in ("join", "meet"):
            options.append(("sup_mono" if left["op"] == "join" else "inf_mono", (left["left"], right["left"]), (left["right"], right["right"])))
        if left["op"] == "join":
            options.append(("sup_le", (left["left"], right), (left["right"], right)))
        if right["op"] == "meet":
            options.append(("le_inf", (left, right["left"]), (left, right["right"])))
        options.extend(("trans", (left, middle), (middle, right)) for middle in _pivot_menu(left, right, [], intermediates, term_key))
        for rule, a, b in options:
            first, second = (term_key(a[0]), term_key(a[1])), (term_key(b[0]), term_key(b[1]))
            terms[first], terms[second] = a, b
            nodes[key].append((rule, first, second))
            queue.extend([(a[0], a[1], depth + 1), (b[0], b[1], depth + 1)])
    return {"root": (term_key(source), term_key(target)), "nodes": nodes, "terms": terms, "visits": visits}


@lru_cache(maxsize=GRAPH_CACHE_SIZE)
def _cached_obligation_graph(source_key, target_key, intermediate_keys):
    graph = _build_obligation_graph(json.loads(source_key), json.loads(target_key),
                                    [json.loads(key) for key in intermediate_keys])
    graph["_direct_pairs"] = {key for key, pair in graph["terms"].items() if direct_proof(*pair)}
    graph["_frontier_priors"] = {key: 2 + min(8, (term_size(pair[0]) + term_size(pair[1]))/32)
                                 for key, pair in graph["terms"].items()}
    return graph


def obligation_graph(source, target, intermediates=()):
    # Independent copies prevent any selector/caller from altering cached data.
    before = _cached_obligation_graph.cache_info()
    graph = copy.deepcopy(_cached_obligation_graph(syntax(source), syntax(target), tuple(map(syntax, intermediates))))
    graph["construction_cache_hit"] = _cached_obligation_graph.cache_info().hits > before.hits
    return graph


def obligation_inventory(source, target):
    graph = obligation_graph(source, target)
    return set(graph["nodes"]), graph["visits"]


def demand_graphs(context):
    return [obligation_graph(goal["source"], goal["target"], context.get("intermediates", [])) for goal in context["goals"]]


def demand_inventory(context):
    graphs = demand_graphs(context)
    return [set(graph["nodes"]) for graph in graphs], sum(graph["visits"] for graph in graphs)


def _estimate(graph, supplied, costs, stats):
    cache = {}
    direct = graph["_direct_pairs"]
    priors = graph["_frontier_priors"]
    def visit(key, active):
        stats["heuristic_node_evaluations"] += 1
        if key in cache:
            return cache[key]
        if key in supplied or key in direct:
            return 1.0
        prior = costs.get(key, priors[key])
        if key in active or not graph["nodes"].get(key):
            return prior
        options = [1 + visit(a, active | {key}) + visit(b, active | {key}) for _, a, b in graph["nodes"][key]]
        value = min([*options, costs[key]] if key in costs else options)
        cache[key] = value
        return value
    stats["heuristic_estimate_calls"] += 1
    return visit(graph["root"], set())


def _descendants(graph, key):
    seen, pending = set(), [key]
    while pending:
        node = pending.pop()
        if node in seen:
            continue
        seen.add(node)
        pending.extend(child for _, a, b in graph["nodes"].get(node, []) for child in (a, b))
    return seen


def _tokens(source, target):
    mapping, tokens = {}, []
    def walk(term, prefix):
        kind = term["op"]
        if kind == "var":
            mapping.setdefault(term["index"], len(mapping))
            tokens.append(prefix + "v" + str(mapping[term["index"]]))
        else:
            tokens.append(prefix + kind)
            walk(term["left"], prefix + "l")
            walk(term["right"], prefix + "r")
    walk(source, "s:")
    walk(target, "t:")
    return Counter(tokens)


def select(context, candidates, goals, k=3, method="greedy_coverage", model=None, budget=8, random_seed=0):
    if method not in METHODS:
        raise ValueError("Unsupported Mathlib ranking method")
    if not isinstance(k, int) or isinstance(k, bool) or not 0 <= k <= 16:
        raise ValueError("Mathlib lemma selection cap must be 0..16")
    started = time.perf_counter()
    cache_before = _cached_obligation_graph.cache_info()
    graphs = demand_graphs({**context, "goals": goals})
    cache_after = _cached_obligation_graph.cache_info()
    demands = [set(graph["nodes"]) for graph in graphs]
    visits = sum(graph["visits"] for graph in graphs)
    covers = {item["id"]: {i for i, inventory in enumerate(demands)
                           if (syntax(item["source"]), syntax(item["target"])) in inventory} for item in candidates}
    rng = random.Random(random_seed)
    goal_terms = Counter()
    for goal in goals:
        goal_terms.update(_tokens(goal["source"], goal["target"]))
    ranked = copy.deepcopy(candidates)
    stats = {"heuristic_estimate_calls": 0, "heuristic_node_evaluations": 0,
             "candidate_feature_calls": 0, "conditional_feature_calls": 0, "model_prediction_calls": 0}
    costs = {(syntax(item["source"]), syntax(item["target"])): proof_cost(item.get("proof_ast", item["proof"])) for item in candidates}
    baseline_estimates = [_estimate(graph, set(), costs, stats) for graph in graphs] if method in ("graph", "greedy_coverage", "branching_aware") else []
    for item in ranked:
        item.update(uncertainty=0.0, score=0.0)
        cost = proof_cost(item.get("proof_ast", item["proof"]))
        if method in ("learned", "learned_no_bonus", "learned_singleton", "structure_only"):
            if model is None:
                raise ValueError("Mathlib learned selection requires a frozen training model")
            from .mathlib_model import features, predict
            vector = features(context, item, goals, budget, model["history"], demands, graphs=graphs)
            stats["candidate_feature_calls"] += 1
            stats["model_prediction_calls"] += 1
            mean, spread = predict(model, vector, structure_only=method == "structure_only", singleton=method == "learned_singleton")
            item.update(features=vector, uncertainty=spread,
                        score=mean + (0 if method == "learned_no_bonus" else 0.35) * spread)
        elif method == "random":
            item["score"] = rng.random()
        elif method == "proof_cost":
            item["score"] = -cost
        elif method == "semantic":
            tokens = _tokens(item["source"], item["target"])
            item["score"] = sum(value * goal_terms[key] for key, value in tokens.items()) / max(1, math.sqrt(sum(v*v for v in tokens.values()) * sum(v*v for v in goal_terms.values())))
        else:
            supplied = {(syntax(item["source"]), syntax(item["target"]))}
            after = [_estimate(graph, supplied, costs, stats) for graph in graphs]
            item["score"] = sum((old-new)/max(1, budget) + int(new <= budget)-int(old <= budget)
                                for old, new in zip(baseline_estimates, after))/max(1, len(goals))
        item["score_base"] = item["score"]
    chosen, pending, supplied, trace = [], ranked[:], set(), []
    current_estimates = baseline_estimates
    while pending and len(chosen) < min(k, len(ranked)):
        chosen_coverage = [supplied | graph["_direct_pairs"]
                           for graph in graphs] if method == "branching_aware" else []
        def score(item):
            value = item["score_base"]
            if method in ("learned", "learned_no_bonus", "structure_only"):
                from .mathlib_model import condition_features, predict
                vector = condition_features(item["features"], item, goals, demands, graphs, chosen)
                stats["conditional_feature_calls"] += 1
                stats["model_prediction_calls"] += 1
                mean, spread = predict(model, vector, structure_only=method == "structure_only")
                value = mean + (0 if method == "learned_no_bonus" else 0.35) * spread
                item.update(features=vector, uncertainty=spread, score=value,
                            score_prefix_ids=[prior["id"] for prior in chosen])
            if method in ("greedy_coverage", "branching_aware"):
                key = syntax(item["source"]), syntax(item["target"])
                after = [_estimate(graph, supplied | {key}, costs, stats) for graph in graphs]
                value = sum((old-new)/max(1, budget) + int(new <= budget)-int(old <= budget)
                            for old, new in zip(current_estimates, after))/max(1, len(goals))
                if method == "branching_aware":
                    completed = 0
                    for graph, before in zip(graphs, chosen_coverage):
                        following = before | {key}
                        for parent, alternatives in graph["nodes"].items():
                            if parent in following:
                                continue
                            completed += sum(a in following and b in following and not(a in before and b in before)
                                             for _, a, b in alternatives)
                    value += completed/max(1, len(goals))
            elif method in ("learned", "learned_no_bonus", "learned_singleton", "structure_only") and chosen:
                overlap = max(len(covers[item["id"]] & covers[c["id"]]) / max(1, len(covers[item["id"]] | covers[c["id"]])) for c in chosen)
                value -= 0.02 * overlap
            item.update(score=value, score_stage=len(chosen), score_portfolio=[prior["id"] for prior in chosen])
            return round(value, SCORE_TIE_DIGITS), item["id"]
        best = max(pending, key=score)
        trace.append({"round": len(chosen), "portfolio_before": [prior["id"] for prior in chosen],
                      "chosen_id": best["id"], "selected_at_score": best["score"],
                      "score_tie_key": round(best["score"], SCORE_TIE_DIGITS)})
        pending.remove(best)
        chosen.append(best)
        supplied.add((syntax(best["source"]), syntax(best["target"])))
        if method in ("greedy_coverage", "branching_aware"):
            current_estimates = [_estimate(graph, supplied, costs, stats) for graph in graphs]
    by_id = {item["id"]: item for item in ranked}
    for item in candidates:
        item.update({key: value for key, value in by_id[item["id"]].items()
                     if key in ("features", "score", "uncertainty", "score_stage", "score_portfolio")})
    return chosen, {"obligation_visits": visits, **stats, "obligation_cap_per_goal": OBLIGATION_CAP,
                    "obligation_build_visits": sum(graph["visits"] for graph in graphs if not graph["construction_cache_hit"]),
                    "graph_primitive_preprocess_pairs": sum(len(graph["terms"]) for graph in graphs if not graph["construction_cache_hit"]),
                    "graph_cache_hits": cache_after.hits-cache_before.hits,
                    "graph_cache_misses": cache_after.misses-cache_before.misses,
                    "graph_cache_capacity": GRAPH_CACHE_SIZE,
                    "obligation_depth": OBLIGATION_DEPTH, "selection_trace": trace,
                    "selection_elapsed_seconds": time.perf_counter() - started}


def discover(context, model=None, k=3, search_budget=8, method="greedy_coverage", random_seed=0):
    validate_context(context)
    candidates = copy.deepcopy(context["candidates"])
    for item in candidates:
        item.update(proof_ast=copy.deepcopy(item["proof"]), status="proposed", axioms=None)
    selected, selection_cost = select(context, candidates, context["goals"], k, method, model, search_budget, random_seed)
    outcomes = []
    for goal in context["goals"]:
        base = search(goal["source"], goal["target"], search_budget, intermediates=context.get("intermediates", []))
        aug = search(goal["source"], goal["target"], search_budget, selected, context.get("intermediates", []))
        outcomes.append({**goal, "baseline": base, "augmented": aug})
    baseline = sum(goal["baseline"]["solved"] for goal in outcomes)
    augmented = sum(goal["augmented"]["solved"] for goal in outcomes)
    return {"schema_version": 1, "context": copy.deepcopy(context), "domain": context["domain"],
            "context_sha256": context_hash(context),
            "candidates": candidates, "selected": [item["id"] for item in selected], "goals": outcomes,
            "budget": {"selected_lemmas": k, "search_expansions": search_budget,
                       "unit": "visited raw-syntax goal state, including failed branches/cache/cycle visits", "max_transitivity_pivots": MAX_PIVOTS},
            "selection_cost": selection_cost,
            "ranking_model": {"kind": model.get("kind") if model else None, "method": method},
            "verification": {"status": "not_run"},
            "metrics": {"method": method, "goal_count": len(outcomes), "candidate_count": len(candidates),
                        "baseline_solved": baseline, "augmented_solved": augmented, "marginal_solved": augmented - baseline,
                        "newly_solved": sum(not g["baseline"]["solved"] and g["augmented"]["solved"] for g in outcomes),
                        "regressed": sum(g["baseline"]["solved"] and not g["augmented"]["solved"] for g in outcomes)},
            "timeline": [{"stage": "IMPORT", "detail": "Pinned Mathlib distributivity schema; data-only Set Nat terms."},
                         {"stage": "EXPLORE", "detail": f"{len(candidates)} non-equivalent inclusions; no world-novelty claim."},
                         {"stage": "PROVE", "detail": "Search witnesses await independent Mathlib kernel checks."}]}
