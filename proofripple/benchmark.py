"""Reproducible graph-disjoint procedural benchmark with explicit limitations."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import random
import statistics
import time

from .engine import METHODS, context_hash, discover, generate_candidates, search, select_candidates
from .model import train_model


def make_context(seed, split="example", node_count=None):
    rng = random.Random(seed)
    count = node_count or rng.randrange(26, 45)
    # Permuted proposition names prevent an accidental numeric-name curriculum.
    order = list(range(count))
    rng.shuffle(order)
    names = [f"p{i}" for i in order]
    labels = ["finite", "bounded", "stable", "ordered", "positive", "invariant"]
    nodes = [{"id": name, "label": f"{rng.choice(labels)} invariant {i}"} for i, name in enumerate(names)]
    pairs = {(i, i + 1) for i in range(count - 1)}
    for i in range(count):
        for j in range(i + 2, min(count, i + 10)):
            if rng.random() < 0.10:
                pairs.add((i, j))
    edge_pairs = sorted(pairs)
    edges = [{"id": f"h{k}", "source": names[i], "target": names[j]} for k, (i, j) in enumerate(edge_pairs)]
    lookup = {(e["source"], e["target"]): e["id"] for e in edges}
    middle = rng.randrange(count // 3, 2 * count // 3)
    seed_path = [lookup[(names[middle], names[middle + 1])], lookup[(names[middle + 1], names[middle + 2])]]
    context = {"id": f"{split}_{seed}", "title": f"Frozen implication system {seed}",
               "description": "Procedural propositional implication DAG. Labels are synthetic; these are not Mathlib theorems.",
               "nodes": nodes, "edges": edges,
               "seed": {"id": "breakthrough", "source": names[middle], "target": names[middle + 2], "path": seed_path}}
    possible = [(i, j) for i in range(middle + 1) for j in range(middle + 3, count) if j - i >= 7]
    rng.shuffle(possible)
    goals = []
    for i, j in possible:
        # These goals are frozen before ranking; their proofs/labels are hidden
        # from the ranker. Endpoints are deliberately visible for task utility.
        goals.append({"id": f"goal_{len(goals)}", "source": names[i], "target": names[j]})
        if len(goals) >= 20:
            break
    context["goals"] = goals
    return context


def _interval(values, seed=2026):
    if not values:
        return [0.0, 0.0]
    rng = random.Random(seed)
    means = sorted(statistics.mean(rng.choices(values, k=len(values))) for _ in range(1000))
    return [means[24], means[974]]


def _candidate_labels(context, candidates, goals, budget):
    baseline = [search(context, g["source"], g["target"], budget)["solved"] for g in goals]
    labels = {}
    for c in candidates:
        values = [search(context, g["source"], g["target"], budget, [c])["solved"] for g in goals]
        labels[c["id"]] = sum(int(a) - int(b) for a, b in zip(values, baseline))
    return labels


def _ranking_quality(candidates, selected, labels):
    gains = [max(0, labels[c["id"]]) for c in selected]
    ideal = sorted([max(0, v) for v in labels.values()], reverse=True)[:len(selected)]
    dcg = sum(value / math.log2(i + 2) for i, value in enumerate(gains))
    idcg = sum(value / math.log2(i + 2) for i, value in enumerate(ideal))
    return {"ndcg_at_k": dcg / idcg if idcg else None,
            "positive_precision_at_k": sum(g > 0 for g in gains) / max(1, len(gains)),
            "oracle_positive_candidates": sum(v > 0 for v in labels.values())}


def run_benchmark(output_dir=None, quick=False):
    started = time.perf_counter()
    train_seeds = list(range(1000, 1008 if quick else 1016))
    validation_seeds = list(range(2000, 2003 if quick else 2006))
    test_seeds = list(range(3000, 3004 if quick else 3012))
    train = [make_context(s, "train") for s in train_seeds]
    validation = [make_context(s, "validation") for s in validation_seeds]
    test = [make_context(s, "test") for s in test_seeds]
    budget, k = 8, 3
    model = train_model(train, search_budget=budget)
    # Hyperparameters are fixed before test evaluation; validation is a sanity
    # report, not an unreported multiple-comparison tuning sweep.
    validation_runs = [discover(c, model, k, budget) for c in validation]
    records = []
    certification_runs = []
    for context in test:
        candidates = generate_candidates(context, context["goals"])
        oracle_labels = _candidate_labels(context, candidates, context["goals"], budget)
        for method in METHODS:
            repetitions = range(5) if method == "random" else range(1)
            for repetition in repetitions:
                tick = time.perf_counter()
                run = discover(context, model, k, budget, method=method, random_seed=4400 + repetition)
                ranking_seconds = time.perf_counter() - tick
                selected = [next(c for c in run["candidates"] if c["id"] == cid) for cid in run["selected"]]
                quality = _ranking_quality(candidates, selected, oracle_labels)
                record = {"context_id": context["id"], "context_sha256": context_hash(context), "method": method,
                          "repetition": repetition, **run["metrics"], **quality,
                          "baseline_expansions": sum(g["baseline"]["expansions"] for g in run["goals"]),
                          "augmented_expansions": sum(g["augmented"]["expansions"] for g in run["goals"]),
                          "selected": run["selected"],
                          "selected_primitive_proof_edges": sum(sum(len(context["seed"]["path"]) if eid == context["seed"]["id"] else 1 for eid in c["path"]) for c in selected),
                          "ranking_and_search_seconds": ranking_seconds}
                records.append(record)
                # Full concrete witnesses are retained for all policies. The
                # caller can batch-certify them with Lean independently.
                certification_runs.append(run)
    summary = {}
    for method in METHODS:
        per_context = []
        method_rows = [r for r in records if r["method"] == method]
        for cid in [c["id"] for c in test]:
            per_context.append(statistics.mean(r["marginal_solved"] for r in method_rows if r["context_id"] == cid))
        ndcg = [r["ndcg_at_k"] for r in method_rows if r["ndcg_at_k"] is not None]
        summary[method] = {"contexts": len(test), "goals_per_context": 20, "mean_baseline_solved": statistics.mean(r["baseline_solved"] for r in method_rows),
                           "mean_augmented_solved": statistics.mean(r["augmented_solved"] for r in method_rows),
                           "mean_marginal_solved": statistics.mean(per_context), "marginal_95pct_context_bootstrap": _interval(per_context),
                           "mean_newly_solved": statistics.mean(r["newly_solved"] for r in method_rows),
                           "mean_regressed": statistics.mean(r["regressed"] for r in method_rows),
                           "mean_ndcg_at_k": statistics.mean(ndcg) if ndcg else None,
                           "mean_positive_precision_at_k": statistics.mean(r["positive_precision_at_k"] for r in method_rows),
                           "mean_augmented_expansions": statistics.mean(r["augmented_expansions"] for r in method_rows)}
    report = {"schema_version": 1, "benchmark": "proofripple-implication-dag-v1", "quick": quick,
              "protocol": {"train_seeds": train_seeds, "validation_seeds": validation_seeds, "test_seeds": test_seeds,
                           "selection_budget": k, "search_expansions_per_goal": budget,
                           "candidate_limit": 256, "max_candidate_path_edges": 6,
                           "random_repetitions": 5, "model_seed": 2026,
                           "endpoint_visibility": "Task endpoints visible to all rankers; test outcomes withheld. Transductive task-conditioned selection.",
                           "leakage_controls": ["Disjoint graph seeds and context hashes", "No held-out goal endpoint pair is offered as a candidate", "All methods receive identical candidates and budgets", "Model labels use training-context search outcomes only", "All candidates must traverse the verified seed; primitive graph contains no candidate declarations"],
                           "budget_accounting": "Equal selected theorem count and per-goal BFS expansion cap. Primitive proof-edge counts and search expansions reported separately. Model training and candidate enumeration are offline/common costs; no equal wall-time claim.",
                           "verification": "Search witnesses only until independently certified by Lean. No search timeout implies mathematical necessity."},
              "model_training": model["training"],
              "validation": {"contexts": len(validation), "marginal_solved": [r["metrics"]["marginal_solved"] for r in validation_runs]},
              "contexts": [{"id": c["id"], "sha256": context_hash(c), "split": split} for split, contexts in (("train", train), ("validation", validation), ("test", test)) for c in contexts],
              "summary": summary, "records": records,
              "elapsed_seconds": time.perf_counter() - started,
              "limitations": ["Procedural propositional implication graphs, not natural mathematical research or Mathlib.", "No claim that selected consequences are mathematically novel.", "A bounded BFS advantage is search compression, not mathematical necessity.", "All test contexts come from the same generator family; domain transfer is unmeasured.", "Semantic baseline is transparent lexical cosine, not a pretrained theorem embedding model.", "Ensemble disagreement is not calibrated epistemic uncertainty.", "No GPU, LLM generation, or graph neural network is used.", "Labels are synthetic invariant names; they carry little genuine mathematical semantics."]}
    # Semantic hash excludes nondeterministic timing fields but covers outcomes.
    stable = json.loads(json.dumps(report))
    stable.pop("elapsed_seconds")
    for row in stable["records"]:
        row.pop("ranking_and_search_seconds")
    report["outcomes_sha256"] = hashlib.sha256(json.dumps(stable, sort_keys=True).encode()).hexdigest()
    if output_dir is not None:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "benchmark.json").write_text(json.dumps(report, indent=2) + "\n")
        (out / "model.json").write_text(json.dumps(model, indent=2) + "\n")
        (out / "certification-runs.json").write_text(json.dumps(certification_runs, indent=2) + "\n")
        (out / "contexts.json").write_text(json.dumps({"train": train, "validation": validation, "test": test}, indent=2) + "\n")
    return report
