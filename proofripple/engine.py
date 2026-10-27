"""Consequence exploration for a deliberately small, explicit implication calculus.

Search success is a witness, not a formal proof. Only the separate Lean adapter
may promote a result to ``kernel_verified``.
"""
from __future__ import annotations

from collections import defaultdict, deque
import copy
import hashlib
import json
import math
import random
import re

FEATURE_NAMES = [
    "proof_length", "source_indegree", "source_outdegree", "target_indegree",
    "target_outdegree", "ancestors", "descendants", "goal_source_match",
    "goal_target_match", "goal_coverage", "mean_saving", "seed_fraction",
]
METHODS = ("learned", "random", "semantic", "graph", "proof_cost")
_IDENT = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


def validate_context(context: dict) -> dict:
    """Validate a supported manifest without executing any supplied source code."""
    if not isinstance(context, dict):
        raise ValueError("Context must be a JSON object")
    nodes = context.get("nodes", [])
    edges = context.get("edges", [])
    if not isinstance(nodes, list) or not 2 <= len(nodes) <= 128:
        raise ValueError("A context needs 2 to 128 nodes")
    if not isinstance(edges, list) or len(edges) > 2048:
        raise ValueError("Too many edges or invalid edge list")
    ids = [n.get("id", "") for n in nodes if isinstance(n, dict)]
    if len(ids) != len(nodes) or len(set(ids)) != len(ids):
        raise ValueError("Node identifiers must be unique")
    all_ids = list(ids)
    edge_map = {}
    for edge in edges:
        if not isinstance(edge, dict):
            raise ValueError("Each edge must be an object")
        eid = edge.get("id", "")
        if eid in edge_map:
            raise ValueError("Edge identifiers must be unique")
        if edge.get("source") not in ids or edge.get("target") not in ids:
            raise ValueError("An edge refers to an unknown node")
        if edge["source"] == edge["target"]:
            raise ValueError("Primitive self implications are unsupported")
        edge_map[eid] = edge
        all_ids.append(eid)
    seed = context.get("seed", {})
    if not isinstance(seed, dict):
        raise ValueError("Seed must be an object")
    all_ids.append(seed.get("id", ""))
    if any(not isinstance(i, str) or len(i) > 24 or not _IDENT.fullmatch(i) for i in all_ids):
        raise ValueError("Identifiers must be short ASCII Lean identifiers")
    if len(set(all_ids)) != len(all_ids):
        raise ValueError("Nodes, edges and seed need distinct identifiers")
    path = seed.get("path")
    if not isinstance(path, list) or not 1 <= len(path) <= 128:
        raise ValueError("Seed needs a bounded primitive-edge witness")
    at = seed.get("source")
    if at not in ids or seed.get("target") not in ids:
        raise ValueError("Unknown seed endpoint")
    for eid in path:
        edge = edge_map.get(eid)
        if edge is None or edge["source"] != at:
            raise ValueError("Seed witness is not a composable primitive path")
        at = edge["target"]
    if at != seed["target"] or seed["source"] == at:
        raise ValueError("Seed witness has the wrong endpoint")
    validate_goals(context, context.get("goals", []))
    return context


def validate_goals(context, goals):
    if not isinstance(goals, list) or len(goals) > 128:
        raise ValueError("Goals must be a list with at most 128 entries")
    node_ids = {node["id"] for node in context["nodes"]}
    for goal in goals:
        if not isinstance(goal, dict) or goal.get("source") not in node_ids or goal.get("target") not in node_ids:
            raise ValueError("Every goal must refer to known node identifiers")
    return goals


def context_hash(context: dict) -> str:
    return hashlib.sha256(json.dumps(context, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _adjacency(context, lemmas=(), include_seed=True):
    edges = list(context["edges"]) + ([context["seed"]] if include_seed else []) + list(lemmas)
    adjacency = defaultdict(list)
    for edge in edges:
        adjacency[edge["source"]].append(edge)
    # All policies use the same deterministic traversal ordering.
    for values in adjacency.values():
        values.sort(key=lambda e: (e["target"], e["id"]))
    return adjacency


def search(context, source, target, budget=8, lemmas=()):
    """Breadth-first proof search; one budget unit is one dequeued proposition.

    Every inspected adjacency list counts once, even when it is empty. Success
    may be found while inspecting a list; queue insertion is never a free
    theorem-solving oracle. A false result means only bounded search failure.
    """
    node_ids = {node["id"] for node in context["nodes"]}
    if source not in node_ids or target not in node_ids:
        raise ValueError("Unknown search endpoint")
    if not isinstance(budget, int) or isinstance(budget, bool) or budget < 0:
        raise ValueError("Search budget must be a nonnegative integer")
    if source == target:
        return {"solved": True, "expansions": 0, "path": []}
    adjacency = _adjacency(context, lemmas)
    queue = deque([(source, [])])
    seen = {source}
    expansions = 0
    while queue and expansions < budget:
        node, path = queue.popleft()
        expansions += 1
        for edge in adjacency[node]:
            following = path + [edge["id"]]
            if edge["target"] == target:
                return {"solved": True, "expansions": expansions, "path": following}
            if edge["target"] not in seen:
                seen.add(edge["target"])
                queue.append((edge["target"], following))
    return {"solved": False, "expansions": expansions, "path": []}


def _all_paths(context, include_seed=True):
    adjacency = _adjacency(context, include_seed=include_seed)
    output = {}
    for node in context["nodes"]:
        start = node["id"]
        paths = {start: []}
        queue = deque([start])
        while queue:
            at = queue.popleft()
            for edge in adjacency[at]:
                if edge["target"] not in paths:
                    paths[edge["target"]] = paths[at] + [edge["id"]]
                    queue.append(edge["target"])
        output[start] = paths
    return output


def candidate_features(context, candidate, goals=(), paths=None):
    paths = paths or _all_paths(context)
    source, target = candidate["source"], candidate["target"]
    nodes = len(context["nodes"])
    indegree = defaultdict(int)
    outdegree = defaultdict(int)
    for edge in context["edges"]:
        indegree[edge["target"]] += 1
        outdegree[edge["source"]] += 1
    coverage, saving = 0, 0
    for goal in goals:
        a, b = goal["source"], goal["target"]
        if source in paths[a] and b in paths[target] and b in paths[a]:
            coverage += 1
            saving += max(0, len(paths[a][b]) - len(paths[a][source]) - 1 - len(paths[target][b]))
    denominator = max(1, len(goals))
    primitive_length = sum(len(context["seed"]["path"]) if e == context["seed"]["id"] else 1 for e in candidate["path"])
    return [
        primitive_length / max(1, nodes), indegree[source] / nodes,
        outdegree[source] / nodes, indegree[target] / nodes,
        outdegree[target] / nodes,
        sum(source in p for p in paths.values()) / nodes,
        len(paths[target]) / nodes,
        sum(g["source"] == source for g in goals) / denominator,
        sum(g["target"] == target for g in goals) / denominator,
        coverage / denominator, saving / denominator,
        len(context["seed"]["path"]) / primitive_length,
    ]


def generate_candidates(context, goals=None, max_candidates=256):
    validate_context(context)
    goals = context.get("goals", []) if goals is None else goals
    validate_goals(context, goals)
    if not isinstance(max_candidates, int) or not 1 <= max_candidates <= 1024:
        raise ValueError("Candidate limit must be between 1 and 1024")
    paths = _all_paths(context, include_seed=False)
    feature_paths = _all_paths(context)
    seed = context["seed"]
    existing = {(e["source"], e["target"]) for e in context["edges"] + [seed]}
    # Directly supplying the evaluation theorem would be a misleading shortcut.
    held_out = {(g["source"], g["target"]) for g in goals}
    candidates = []
    used_ids = {e["id"] for e in context["edges"] + [seed]} | set(paths)
    for source in sorted(paths):
        if seed["source"] not in paths[source]:
            continue
        for target in sorted(paths[seed["target"]]):
            witness = paths[source][seed["source"]] + [seed["id"]] + paths[seed["target"]][target]
            if (source, target) in existing | held_out or source == target or len(witness) > 6:
                continue
            # Cyclic manifests are accepted, but cyclic witness paths are not.
            lookup = {e["id"]: e for e in context["edges"] + [seed]}
            visited = {source}
            simple = True
            for eid in witness:
                nxt = lookup[eid]["target"]
                if nxt in visited:
                    simple = False
                    break
                visited.add(nxt)
            if not simple:
                continue
            base_id = "ripple_" + source + "_" + target
            cid, suffix = base_id, 0
            while cid in used_ids:
                suffix += 1
                cid = f"{base_id}_{suffix}"
            used_ids.add(cid)
            candidate = {"id": cid, "source": source, "target": target, "path": witness,
                         "status": "proposed", "score": 0.0, "uncertainty": 0.0,
                         "dependencies": witness, "axioms": None,
                         "explanation": f"Compose {len(witness)} implication steps through {seed['id']}. This is a consequence relative to the manifest, not a claim of new mathematics."}
            candidate["features"] = candidate_features(context, candidate, goals, feature_paths)
            candidates.append(candidate)
    if context.get("domain") == "list-capacity":
        from .natural import filter_redundant_candidates
        candidates = filter_redundant_candidates(context, candidates, goals)
    candidates.sort(key=lambda c: (len(c["path"]), c["id"]))
    return candidates[:max_candidates]


def _tokens(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def select_candidates(context, candidates, goals, k=3, method="learned", model=None, seed=0):
    if method not in METHODS:
        raise ValueError(f"Unknown ranking method: {method}")
    if not isinstance(k, int) or isinstance(k, bool) or k < 0:
        raise ValueError("Selection budget must be a nonnegative integer")
    if method == "learned" and model is not None and model.get("kind") == "natural-list-capacity-context-bootstrap-ridge-v1":
        from .natural_model import select_natural
        return select_natural(context, candidates, goals, k=k, model=model)
    validate_goals(context, goals)
    ranked = copy.deepcopy(candidates)
    rng = random.Random(seed)
    labels = {n["id"]: n.get("label", n["id"]) for n in context["nodes"]}
    goal_tokens = _tokens(" ".join(labels[g["source"]] + " " + labels[g["target"]] for g in goals))
    if method == "learned" and model is None:
        from .model import default_model
        model = default_model()
    feature_paths = _all_paths(context)
    for candidate in ranked:
        features = candidate_features(context, candidate, goals, feature_paths)
        candidate["features"] = features
        if method == "learned":
            from .model import predict
            mean, uncertainty = predict(model, features)
            candidate["score"] = mean + model.get("exploration", 0.35) * uncertainty
            candidate["uncertainty"] = uncertainty
        elif method == "random":
            candidate["score"] = rng.random()
        elif method == "semantic":
            terms = _tokens(labels[candidate["source"]] + " " + labels[candidate["target"]])
            candidate["score"] = len(terms & goal_tokens) / math.sqrt(max(1, len(terms) * len(goal_tokens)))
        elif method == "graph":
            # Strong goal-aware structural route-saving heuristic.
            candidate["score"] = features[10] + 0.2 * features[9]
        else:
            candidate["score"] = -features[0]
    chosen = []
    pending = ranked[:]
    while pending and len(chosen) < min(k, len(ranked)):
        def adjusted(candidate):
            penalty = 0.0
            if method == "learned" and chosen:
                witness = set(candidate["path"])
                penalty = max(len(witness & set(c["path"])) / max(1, len(witness | set(c["path"]))) for c in chosen)
                penalty *= model.get("redundancy_penalty", 0.02)
            return (candidate["score"] - penalty, candidate["id"])
        best = max(pending, key=adjusted)
        chosen.append(best)
        pending.remove(best)
    scores = {c["id"]: c for c in ranked}
    for candidate in candidates:
        candidate.update({key: scores[candidate["id"]][key] for key in ("features", "score", "uncertainty")})
    return chosen


def discover(context, model=None, k=3, search_budget=8, goals=None, method="learned", random_seed=0):
    validate_context(context)
    goals = goals if goals is not None else context.get("goals", [])
    validate_goals(context, goals)
    candidates = generate_candidates(context, goals)
    selected = select_candidates(context, candidates, goals, k, method, model, random_seed)
    outcomes = []
    for index, goal in enumerate(goals):
        outcomes.append({"id": goal.get("id", f"goal_{index}"), "source": goal["source"], "target": goal["target"],
                         "baseline": search(context, goal["source"], goal["target"], search_budget),
                         "augmented": search(context, goal["source"], goal["target"], search_budget, selected)})
    baseline = sum(g["baseline"]["solved"] for g in outcomes)
    augmented = sum(g["augmented"]["solved"] for g in outcomes)
    return {"schema_version": 1, "context": copy.deepcopy(context), "context_sha256": context_hash(context),
            "seed": copy.deepcopy(context["seed"]), "candidates": candidates, "selected": [c["id"] for c in selected],
            "ranking_model": {"kind": model.get("kind"), "training": copy.deepcopy(model.get("training")),
                              "model_sha256": hashlib.sha256(json.dumps(model, sort_keys=True).encode()).hexdigest()} if model else None,
            "goals": outcomes, "budget": {"selected_lemmas": k, "search_expansions_per_goal": search_budget,
            "candidate_limit": 256, "candidate_generation_max_path_edges": 6},
            "verification": {"status": "unavailable", "toolchain": None, "source_sha256": None, "log": "Lean has not been run.", "axioms": None},
            "metrics": {"candidate_count": len(candidates), "goal_count": len(outcomes), "baseline_solved": baseline,
                        "augmented_solved": augmented, "marginal_solved": augmented - baseline, "method": method,
                        "newly_solved": sum(not g["baseline"]["solved"] and g["augmented"]["solved"] for g in outcomes),
                        "regressed": sum(g["baseline"]["solved"] and not g["augmented"]["solved"] for g in outcomes)},
            "timeline": [{"stage": "IMPORT", "detail": "Validated frozen implication manifest"},
                         {"stage": "UNDERSTAND", "detail": "Indexed explicit implication hypotheses"},
                         {"stage": "EXPLORE", "detail": f"Enumerated {len(candidates)} distinct seed-dependent candidates"},
                         {"stage": "EVALUATE", "detail": f"Compared {len(outcomes)} bounded downstream searches; formal verification pending"}]}
