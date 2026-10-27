"""Frozen typed-list benchmark with operator-skeleton holdout and Lean receipts.

This controls a small proof-search registry. It measures no mathematical-domain
transfer, hard theorem discovery, or superiority to Lean's general automation.
"""
from __future__ import annotations

import copy
from concurrent.futures import ThreadPoolExecutor
import gzip
import hashlib
import json
from pathlib import Path
import random
import statistics
import time
import sysconfig

from .benchmark import _candidate_labels, _interval, _ranking_quality, make_context
from .engine import METHODS, context_hash, discover, generate_candidates
from .lean import TOOLCHAIN, verify_source
from .model import train_model
from .natural import build_automation_baseline, build_natural_source, length_normal_forms, make_example, validate_natural_context
from .natural_model import train_natural_model

BENCHMARK = "proofripple-natural-list-capacity-statement-holdout-v1"
NATURAL_METHODS = (*METHODS, "structure_only")
FAMILIES = {"train": "alternating_reducing_preserving",
            "validation": "two_preserving_one_reducing",
            "test": "clustered_reducing_mixed_operations"}
REDUCING = frozenset(("filter", "take"))
PRESERVING = frozenset(("map", "reverse"))


def _operators(seed, split, count):
    rng = random.Random(seed ^ 0x50A7C1)
    operations = ["input"]
    if split == "train":
        for index in range(1, count):
            operations.append(rng.choice(("filter", "take") if index % 2 else ("map", "reverse")))
    elif split == "validation":
        for index in range(1, count):
            operations.append(rng.choice(("filter", "take") if index % 3 == 0 else ("map", "reverse")))
    else:
        # A disjoint initial operation skeleton: three reducing stages. Later
        # clusters vary in length and alternate reducing/preserving classes.
        operations.extend(rng.choice(("filter", "take")) for _ in range(min(3, count - 1)))
        preserving = True
        while len(operations) < count:
            choices = ("map", "reverse") if preserving else ("filter", "take")
            cluster = rng.randrange(1, 4) if preserving else rng.randrange(2, 5)
            operations.extend(rng.choice(choices) for _ in range(min(cluster, count - len(operations))))
            preserving = not preserving
    return operations


def make_natural_context(seed, split):
    """Lift a deterministic DAG into an actual topological List Nat pipeline.

    Topology remains in the same procedural DAG family across all splits. Only
    operator skeleton families are deliberately held out. All graph edges are
    closed nonexpansiveness facts, not free implication assumptions.
    """
    if split not in FAMILIES:
        raise ValueError("Natural split must be train, validation or test")
    if not isinstance(seed, int) or isinstance(seed, bool) or not 0 <= seed <= 2**31 - 1:
        raise ValueError("Context seed must be a nonnegative 31-bit integer")
    context = make_context(seed, split)
    operations = _operators(seed, split, len(context["nodes"]))
    for index, (node, operation) in enumerate(zip(context["nodes"], operations)):
        node["expression"] = {"op": operation}
        if index:
            node["expression"]["input"] = context["nodes"][index - 1]["id"]
        node["label"] = "Input list capacity" if not index else f"{operation} stage {index} capacity"
    ids = [node["id"] for node in context["nodes"]]
    old_middle = ids.index(context["seed"]["source"])
    context["domain"] = "list-capacity"
    forms = length_normal_forms(context)
    # Every candidate contains the seed. A syntactically reducing operation can
    # still be an identity under the shared-predicate/k laws. Choose a window
    # with distinct strong equality keys before constructing goals or labels.
    windows = [index for index in range(len(ids) - 2)
               if any(operation in REDUCING for operation in operations[index + 1:index + 3])
               and forms[ids[index]] != forms[ids[index + 2]]]
    if not windows:
        raise ValueError("No nonidentity reducing seed exists in this frozen pipeline")
    middle = min(windows, key=lambda index: (abs(index - old_middle), index))
    edges = {(edge["source"], edge["target"]): edge["id"] for edge in context["edges"]}
    context["seed"] = {"id": "breakthrough", "source": ids[middle], "target": ids[middle + 2],
                       "path": [edges[(ids[middle], ids[middle + 1])], edges[(ids[middle + 1], ids[middle + 2])]]}
    rng = random.Random(seed ^ 0x60A15)
    pairs = [(i, j) for i in range(middle + 1) for j in range(middle + 3, len(ids)) if j - i >= 6]
    rng.shuffle(pairs)
    context["goals"] = [{"id": f"goal_{index}", "source": ids[i], "target": ids[j]}
                        for index, (i, j) in enumerate(pairs[:20])]
    if len(context["goals"]) != 20 or len({(goal["source"], goal["target"]) for goal in context["goals"]}) != 20:
        raise ValueError("Each frozen natural context must supply exactly 20 unique goals")
    context.update(domain="list-capacity", split=split,
                   title=f"Typed list capacity pipeline {seed}",
                   description="A frozen List Nat pipeline. Every graph edge is proved from registered core length bounds. All consequences are elementary known compositions.",
                   metadata={"split": split, "operator_skeleton_family": FAMILIES[split],
                             "operator_skeleton": operations,
                             "topology_family": "same procedural chain-plus-forward-DAG family in every split",
                             "seed_constraint": "Nearest two-step chain window containing filter/take with distinct strong length-normal-form endpoints; chosen before goals/labels",
                             "goal_minimum_stage_span": 6})
    return validate_natural_context(context)


def _source_hashes():
    directory = Path(__file__).resolve().parent
    names = ("natural_benchmark.py", "natural.py", "normalization.py", "natural_model.py", "engine.py", "model.py", "benchmark.py", "lean.py")
    return {name: hashlib.sha256((directory / name).read_bytes()).hexdigest() for name in names}


def _write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _signature(forms, item):
    return forms[item["source"]], forms[item["target"]]


def _declaration_index(contexts):
    """Index statements without fitting a model or inspecting search outcomes."""
    result = set()
    for context in contexts:
        forms = length_normal_forms(context)
        items = [*context["edges"], context["seed"], *context["goals"], *generate_candidates(context)]
        result.update(_signature(forms, item) for item in items)
    return result


def _prepare_splits(raw_splits):
    """Label-free theorem-statement cleaning, in train→validation→test order.

    Goal signatures ignore node/context spelling. Empty contexts are retained.
    No replacement query is sampled and no solve outcome enters these rules.
    """
    splits = copy.deepcopy(raw_splits)
    records = {}
    for split, contexts in splits.items():
        for context in contexts:
            forms = length_normal_forms(context)
            own_facts = {_signature(forms, item) for item in [*context["edges"], context["seed"]]}
            retained, seen = [], set()
            record = {"context_id": context["id"], "split": split,
                      "original_endpoint_queries": len(context["goals"]),
                      "raw_context_sha256": context_hash(context),
                      "removed_identity": 0, "removed_own_baseline_equivalent": 0,
                      "removed_duplicate_normalized_pair": 0, "removed_prior_index_equivalent": 0}
            for goal in context["goals"]:
                pair = _signature(forms, goal)
                if pair[0] == pair[1]:
                    record["removed_identity"] += 1
                elif pair in own_facts:
                    record["removed_own_baseline_equivalent"] += 1
                elif pair in seen:
                    record["removed_duplicate_normalized_pair"] += 1
                else:
                    seen.add(pair)
                    retained.append(goal)
            context["goals"] = retained
            records[context["id"]] = record
    training_index = _declaration_index(splits["train"])
    prior_index = set(training_index)
    for split in ("validation", "test"):
        for context in splits[split]:
            forms = length_normal_forms(context)
            before = len(context["goals"])
            context["goals"] = [goal for goal in context["goals"] if _signature(forms, goal) not in prior_index]
            records[context["id"]]["removed_prior_index_equivalent"] += before - len(context["goals"])
        if split == "validation":
            prior_index.update(_declaration_index(splits["validation"]))
    for split, contexts in splits.items():
        for context in contexts:
            record = records[context["id"]]
            record["retained_registry_queries"] = len(context["goals"])
            context.setdefault("metadata", {})["goal_cleaning"] = {key: value for key, value in record.items()
                                                                    if key not in ("context_id", "split", "raw_context_sha256")}
    summary = {}
    for split, contexts in splits.items():
        rows = [records[context["id"]] for context in contexts]
        signatures = {_signature(length_normal_forms(context), goal) for context in contexts for goal in context["goals"]}
        summary[split] = {"contexts": len(contexts), "active_goal_contexts": sum(bool(context["goals"]) for context in contexts),
                          "original_endpoint_queries": sum(row["original_endpoint_queries"] for row in rows),
                          "retained_registry_queries": sum(len(context["goals"]) for context in contexts),
                          "globally_unique_normalized_theorems": len(signatures),
                          "removed_reason_counts": {reason: sum(row[reason] for row in rows) for reason in
                                                    ("removed_identity", "removed_own_baseline_equivalent", "removed_duplicate_normalized_pair", "removed_prior_index_equivalent")},
                          "contexts_detail": rows}
    validation_overlap = sum(_signature(length_normal_forms(c), g) in training_index for c in splits["validation"] for g in c["goals"])
    test_overlap = sum(_signature(length_normal_forms(c), g) in prior_index for c in splits["test"] for g in c["goals"])
    own_overlap = 0
    identities = 0
    duplicates = 0
    for contexts in splits.values():
        for context in contexts:
            forms = length_normal_forms(context)
            own_facts = {_signature(forms, item) for item in [*context["edges"], context["seed"]]}
            pairs = [_signature(forms, goal) for goal in context["goals"]]
            own_overlap += sum(pair in own_facts for pair in pairs)
            identities += sum(a == b for a, b in pairs)
            duplicates += len(pairs) - len(set(pairs))
    audit = {"scope": "Recognized statement equality under the registered sound partial normalizer; no claim of deciding all mathematical equivalences.",
             "training_index_declaration_signatures": len(training_index),
             "training_plus_validation_index_signatures": len(prior_index),
             "validation_goal_overlap_training_index": validation_overlap,
             "test_goal_overlap_all_prior_index": test_overlap,
             "retained_goal_overlap_own_baseline_facts": own_overlap,
             "retained_identity_goals": identities, "within_context_duplicate_goals": duplicates,
             "test_context_ids": [context["id"] for context in splits["test"]]}
    if any((validation_overlap, test_overlap, own_overlap, identities, duplicates)):
        raise ValueError("Theorem holdout cleaning failed its zero-overlap checks")
    return splits, summary, audit


def _snapshot_sources(out, hashes):
    directory = Path(__file__).resolve().parent
    target = out / "experiment-source"
    target.mkdir(exist_ok=True)
    for name, digest in hashes.items():
        data = (directory / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError("Benchmark source changed during source snapshot")
        (target / name).write_bytes(data)
    rule_file = directory.parent / "examples" / "NormalizationRules.lean"
    if not rule_file.is_file():
        rule_file = Path(sysconfig.get_path("data")) / "share" / "proofripple" / "examples" / "NormalizationRules.lean"
    if rule_file.exists():
        data = rule_file.read_bytes()
        (target / rule_file.name).write_bytes(data)
        return {"source_sha256": hashlib.sha256(data).hexdigest(),
                "scope": "Generic shared-predicate/k equality-law provenance; this file does not certify the Python normalizer as a complete equivalence procedure."}
    return {"source_sha256": None, "scope": "Generic normalization rule source is absent from this installation; use the source repository for the independently checked law artifact."}


def _coverage(splits):
    result = {}
    for split, contexts in splits.items():
        counts = {context["id"]: len(generate_candidates(context, context["goals"])) for context in contexts}
        result[split] = {"contexts": len(contexts), "total_candidates": sum(counts.values()),
                         "empty_contexts": sum(count == 0 for count in counts.values()),
                         "nonempty_contexts": sum(count > 0 for count in counts.values()),
                         "contexts_filling_selection_cap": sum(count >= 3 for count in counts.values()),
                         "contexts_with_ranking_choice": sum(counts[context["id"]] > 3 and bool(context["goals"]) for context in contexts),
                         "active_goal_contexts": sum(bool(context["goals"]) for context in contexts),
                         "eligible_per_context": counts}
    return result


def _freeze_digest(report):
    """Digest scientific outcomes, not clocks, logs, or certificate filenames."""
    stable = copy.deepcopy(report)
    for key in ("elapsed_seconds", "outcomes_sha256"):
        stable.pop(key, None)
    for record in stable.get("records", []):
        record.pop("ranking_and_search_seconds", None)
    verification = stable.get("formal_verification", {})
    verification.pop("elapsed_seconds", None)
    verification.pop("summed_subprocess_elapsed_seconds", None)
    # Gzip bytes may vary across Python/zlib builds; the raw audit hash remains.
    verification.pop("audits_sha256", None)
    for context in verification.get("contexts", []):
        context.pop("elapsed_seconds", None)
        context.pop("source", None)
    stable.get("automation_control", {}).pop("elapsed_seconds", None)
    return hashlib.sha256(json.dumps(stable, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _summarize(records, contexts):
    summary = {}
    for method in NATURAL_METHODS:
        rows = [record for record in records if record["method"] == method]
        per_context = [statistics.mean(record["marginal_solved"] for record in rows if record["context_id"] == context["id"])
                       for context in contexts]
        ndcg = [record["ndcg_at_k"] for record in rows if record["ndcg_at_k"] is not None]
        def total(field):
            return sum(statistics.mean(record[field] for record in rows if record["context_id"] == context["id"]) for context in contexts)
        goal_count = sum(len(context["goals"]) for context in contexts)
        summary[method] = {
            "contexts": len(contexts), "goals_per_context": goal_count / len(contexts),
            "active_goal_contexts": sum(bool(context["goals"]) for context in contexts),
            "total_goals": goal_count, "total_baseline_solved": total("baseline_solved"),
            "total_solved": total("augmented_solved"), "total_newly_solved": total("newly_solved"),
            "total_regressed": total("regressed"), "total_marginal_solved": total("marginal_solved"),
            "total_interpretation": "One occurrence per retained context query; random-policy solved/new/regressed totals average its five repetitions before summing contexts.",
            "mean_baseline_solved": statistics.mean(record["baseline_solved"] for record in rows),
            "mean_augmented_solved": statistics.mean(record["augmented_solved"] for record in rows),
            "mean_marginal_solved": statistics.mean(per_context),
            "marginal_95pct_context_bootstrap": _interval(per_context),
            "mean_newly_solved": statistics.mean(record["newly_solved"] for record in rows),
            "mean_regressed": statistics.mean(record["regressed"] for record in rows),
            "mean_ndcg_at_k": statistics.mean(ndcg) if ndcg else None,
            "mean_positive_precision_at_k": statistics.mean(record["positive_precision_at_k"] for record in rows),
            "mean_augmented_expansions": statistics.mean(record["augmented_expansions"] for record in rows),
            "mean_selected_primitive_proof_edges": statistics.mean(record["selected_primitive_proof_edges"] for record in rows),
            "mean_selected_list_operation_steps": statistics.mean(record["selected_list_operation_steps"] for record in rows),
            "mean_selected_count": statistics.mean(record["selected_count"] for record in rows),
            "empty_candidate_contexts": sum(not any(record["candidate_count"] for record in rows if record["context_id"] == context["id"]) for context in contexts),
        }
    return summary


def _paired_comparisons(records, contexts):
    comparisons = {}
    for baseline in ("graph", "random", "semantic", "proof_cost", "structure_only"):
        values = []
        for context in contexts:
            learned = statistics.mean(r["marginal_solved"] for r in records if r["context_id"] == context["id"] and r["method"] == "learned")
            other = statistics.mean(r["marginal_solved"] for r in records if r["context_id"] == context["id"] and r["method"] == baseline)
            values.append(learned - other)
        comparisons["learned_minus_" + baseline] = {"mean_marginal_difference": statistics.mean(values),
                                                   "paired_context_bootstrap_95pct": _interval(values),
                                                   "context_differences": values}
    return comparisons


def _combined_run(runs):
    """One source per context, preserving every distinct successful witness."""
    first = copy.deepcopy(runs[0])
    proofs = {}
    for run in runs:
        for goal in run["goals"]:
            for variant in ("baseline", "augmented"):
                outcome = goal[variant]
                if outcome["solved"]:
                    key = (goal["source"], goal["target"], tuple(outcome["path"]))
                    proofs[key] = {"source": goal["source"], "target": goal["target"],
                                   "baseline": {"solved": True, "path": outcome["path"]},
                                   "augmented": {"solved": False, "path": []}}
    first["goals"] = list(proofs.values())
    return first, len(proofs)


def _certify(out, report, groups):
    started = time.perf_counter()
    proof_dir = out / "proofs"
    proof_dir.mkdir(parents=True, exist_ok=True)
    def check_group(group):
        run, distinct_goals = _combined_run(group["runs"])
        source, names, metadata = build_natural_source(run)
        cid = run["context"]["id"]
        source_file = proof_dir / f"{cid}.lean"
        source_file.write_text(source)
        check = verify_source(source, names, timeout=60, allowed_axioms=("propext",))
        # Retain actual output separately; compressed audit content excludes the
        # temporary compiler path, log timestamps, and measured runtime.
        (proof_dir / f"{cid}.log").write_text(check["log"])
        context = {"context_id": cid, "split": group["split"], "source": f"proofs/{cid}.lean",
                         "source_sha256": check["source_sha256"], "status": check["status"],
                         "expected_declarations": len(names), "audits_received": len(check["audits"]),
                         "candidates": len(run["candidates"]), "distinct_goal_proofs": distinct_goals,
                         "policy_runs": len(group["runs"]), "elapsed_seconds": check["elapsed_seconds"]}
        audit = {"context_id": cid, "split": group["split"], "source_sha256": check["source_sha256"],
                 "status": check["status"], "audits": check["audits"]}
        print(f"Lean natural {cid}: {check['status']} ({len(check['audits'])}/{len(names)} audits)", flush=True)
        return context, audit
    # Independent contexts have separate immutable source files and fresh Lean
    # working directories. Map preserves manifest order despite completion order.
    with ThreadPoolExecutor(max_workers=2) as executor:
        checked = list(executor.map(check_group, groups))
    contexts = [context for context, _ in checked]
    audits = [audit for _, audit in checked]
    audit_bytes = json.dumps({"schema_version": 1, "contexts": audits}, sort_keys=True, separators=(",", ":")).encode()
    compressed = gzip.compress(audit_bytes, mtime=0)
    (out / "benchmark-audits.json.gz").write_bytes(compressed)
    stable_manifest = [{key: value for key, value in context.items() if key not in ("elapsed_seconds", "source")} for context in contexts]
    verification = {
        "status": "kernel_verified" if contexts and all(context["status"] == "kernel_verified" for context in contexts) else "failed",
        "toolchain": TOOLCHAIN, "axiom_policy": "explicit_foundational_allowlist", "allowed_axioms": ["propext"],
        "declarations": sum(context["expected_declarations"] for context in contexts),
        "audits_received": sum(context["audits_received"] for context in contexts),
        "source_manifest_sha256": hashlib.sha256(json.dumps(stable_manifest, sort_keys=True).encode()).hexdigest(),
        "audits_sha256": hashlib.sha256(compressed).hexdigest(),
        "audits_uncompressed_sha256": hashlib.sha256(audit_bytes).hexdigest(),
        "elapsed_seconds": time.perf_counter() - started,
        "summed_subprocess_elapsed_seconds": sum(context["elapsed_seconds"] for context in contexts),
        "timing_interpretation": "Elapsed seconds is actual certification wall time. Summed subprocess elapsed seconds adds overlapping process wall times; neither is a measured CPU-time counter.",
        "parallel_process_limit": 2, "per_process_memory_limit_mb": 2048,
        "training_contexts": sum(context["split"] == "train" for context in contexts),
        "validation_contexts": sum(context["split"] == "validation" for context in contexts),
        "test_contexts": sum(context["split"] == "test" for context in contexts),
        "test_policy_runs": sum(context["policy_runs"] for context in contexts if context["split"] == "test"),
        "candidate_declarations": sum(context["candidates"] for context in contexts),
        "distinct_successful_goal_witnesses": sum(context["distinct_goal_proofs"] for context in contexts),
        "contexts": contexts,
        "scope": "All candidate proofs and successful baseline/one-canonical-selection witnesses in every training/validation context; every distinct successful baseline/augmented test witness across all policies and random repetitions. Training single-candidate label searches are not individually certified. Failed searches produce no theorem.",
    }
    report["formal_verification"] = verification
    return verification


def _automation(out, execute, benchmark_goal_count=None):
    example = make_example()
    goal_count = len(example["goals"])
    control = {
        "status": "not_run", "method": "Lean grind (gen := 32) after unfolding registered stage definitions",
        "showcase_goal_count": goal_count, "showcase_goals_solved": None,
        "registered_template_goal_count": 1, "registered_template_goals_solved": None,
        "solved": None, "total": goal_count + 1, "allowed_axioms": ["propext", "Classical.choice", "Quot.sound"],
        "source_sha256": None,
        "coverage": f"Showcase only: {goal_count} exact pipeline goals plus one registered two-buffer template; separate from the {benchmark_goal_count if benchmark_goal_count is not None else 'retained'} benchmark queries.",
        "interpretation": "Independent automation is tested without discovered lemmas. Resources differ from bounded graph search; no Lean-automation superiority claim.",
    }
    if not execute:
        return control
    source, names = build_automation_baseline(example, generation=32)
    (out / "automation-control.lean").write_text(source)
    check = verify_source(source, names, timeout=60, allowed_axioms=tuple(control["allowed_axioms"]))
    _write_json(out / "automation-audit.json", check)
    passed = {audit["name"] for audit in check["audits"]
              if set(audit["axioms"]).issubset(control["allowed_axioms"]) and "sorryAx" not in audit["constants"]}
    # A globally failed source is never promoted by picking successful messages.
    if check["status"] == "kernel_verified":
        control.update(solved=len(passed), showcase_goals_solved=sum(name.startswith("automation_goal_") for name in passed),
                       registered_template_goals_solved=int("automation_combined_buffer_safe" in passed))
    else:
        control.update(solved=0, showcase_goals_solved=0, registered_template_goals_solved=0)
    control.update(status=check["status"], source_sha256=check["source_sha256"], elapsed_seconds=check["elapsed_seconds"],
                   audits_received=len(check["audits"]),
                   interpretation="Ordinary Lean automation solves the showcase without discovered lemmas when this control succeeds. This is counterevidence to broad proving-superiority claims; resources differ from restricted graph search.")
    return control


def run_natural_benchmark(output_dir, quick=False, certify=False):
    started = time.perf_counter()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    train_seeds = list(range(1000, 1008 if quick else 1016))
    validation_seeds = list(range(2000, 2003 if quick else 2006))
    test_seeds = list(range(3000, 3004 if quick else 3012))
    raw_splits = {"train": [make_natural_context(seed, "train") for seed in train_seeds],
              "validation": [make_natural_context(seed, "validation") for seed in validation_seeds],
              "test": [make_natural_context(seed, "test") for seed in test_seeds]}
    # Every exclusion is computed before model/history fitting or label searches.
    splits, cleaning, holdout = _prepare_splits(raw_splits)
    _write_json(out / "raw-contexts.json", raw_splits)
    _write_json(out / "holdout-audit.json", holdout)
    print(f"HOLDOUT_AUDIT prior_test_overlap={holdout['test_goal_overlap_all_prior_index']} "
          f"own_baseline_overlap={holdout['retained_goal_overlap_own_baseline_facts']} "
          f"identities={holdout['retained_identity_goals']}; "
          f"retained train/validation/test={cleaning['train']['retained_registry_queries']}/"
          f"{cleaning['validation']['retained_registry_queries']}/{cleaning['test']['retained_registry_queries']}", flush=True)
    train, validation, test = (splits[key] for key in ("train", "validation", "test"))
    hashes = [context_hash(context) for contexts in splits.values() for context in contexts]
    if len(set(hashes)) != len(hashes):
        raise ValueError("Train/validation/test contexts overlap")
    budget, k = 8, 3
    model = train_natural_model(train, search_budget=budget)
    structure = train_model(train, search_budget=budget)
    _write_json(out / "model.json", model)
    _write_json(out / "structure-model.json", structure)
    _write_json(out / "contexts.json", splits)
    records, certification_runs, groups = [], [], []
    # All train/validation candidates are checked, along with one canonical
    # policy's concrete successes; this is not all train label-search witnesses.
    validation_results = []
    for split, contexts in (("train", train), ("validation", validation)):
        for context in contexts:
            run = discover(context, model, k, budget)
            groups.append({"split": split, "runs": [run]})
            if split == "validation":
                validation_results.append({"context_id": context["id"], **run["metrics"]})
    for context in test:
        candidates = generate_candidates(context, context["goals"])
        oracle_labels = _candidate_labels(context, candidates, context["goals"], budget)
        context_runs = []
        positions = {node["id"]: i for i, node in enumerate(context["nodes"])}
        for method in NATURAL_METHODS:
            for repetition in range(5 if method == "random" else 1):
                tick = time.perf_counter()
                run = discover(context, structure if method == "structure_only" else model, k, budget,
                               method="learned" if method == "structure_only" else method, random_seed=4400 + repetition)
                elapsed = time.perf_counter() - tick
                run["metrics"]["method"] = method
                selected = [next(candidate for candidate in run["candidates"] if candidate["id"] == identifier) for identifier in run["selected"]]
                quality = _ranking_quality(candidates, selected, oracle_labels)
                records.append({"context_id": context["id"], "context_sha256": context_hash(context),
                                "method": method, "repetition": repetition, **run["metrics"], **quality,
                                "baseline_expansions": sum(goal["baseline"]["expansions"] for goal in run["goals"]),
                                "augmented_expansions": sum(goal["augmented"]["expansions"] for goal in run["goals"]),
                                "selected": run["selected"],
                                "selected_count": len(selected),
                                "selected_primitive_proof_edges": sum(sum(len(context["seed"]["path"]) if edge == context["seed"]["id"] else 1 for edge in candidate["path"]) for candidate in selected),
                                "selected_list_operation_steps": sum(positions[candidate["target"]] - positions[candidate["source"]] for candidate in selected),
                                "ranking_and_search_seconds": elapsed})
                certification_runs.append(run)
                context_runs.append(run)
        groups.append({"split": "test", "runs": context_runs})
    _write_json(out / "certification-runs.json", certification_runs)
    report = {
        "schema_version": 1, "benchmark": BENCHMARK, "domain": "list-capacity", "quick": bool(quick),
        "protocol": {"train_seeds": train_seeds, "validation_seeds": validation_seeds, "test_seeds": test_seeds,
                     "selection_budget": k, "search_expansions_per_goal": budget, "candidate_limit": 256,
                     "max_candidate_path_edges": 6, "random_repetitions": 5, "model_seed": 2026,
                     "operator_skeleton_families": FAMILIES,
                     "holdout": "Distinct operator skeleton families and frozen seeds only. Every split uses the same procedural DAG topology generator and the same List Nat mathematical domain; this is not graph-family or mathematical-domain transfer.",
                     "seed_constraint": "Choose the nearest two-edge chain window containing filter/take whose endpoints have different strong length-normal-form keys, before goals or labels. A syntactically reducing operation alone is insufficient because shared-predicate/k identities can make it redundant.",
                     "goal_rule": "Start with the deterministic 20 endpoint pairs per context at minimum stage-index span six. Before any fitting or solve outcomes, prune identity, own-primitive/seed-equivalent statements, and within-context normalized duplicates. Train on retained training goals. Remove validation goals seen in any training primitive/seed/retained-goal/candidate declaration; remove test goals seen in that training index or any validation primitive/seed/retained-goal/candidate declaration. Do not refill, resample, or drop empty contexts. Denominators are actual retained query counts.",
                     "candidate_normalization": "Normalize with registered shared-predicate/k laws: filter idempotence on known-passing elements, redundant take on known-within-k lists, reverse cancellation and commuting rules, plus length-preserving outer map/reverse and repeated same-k minima. Exclude normalized identity, known-edge/seed, equivalent held-out-goal and duplicate pairs; keep the cheapest surviving witness for every policy. This is not a complete theorem-equivalence oracle.",
                     "rejected_predecessors": "Attempt1 was rejected for equivalent-goal leakage and a length-identity seed. Attempt2 was rejected because 46/240 test endpoint queries matched recognized training declarations (10 training-goal and 36 primitive-edge occurrences), despite valid kernel proofs. Both attempts and diagnostics are preserved. This run applies label-free prior-statement pruning and retrains without changing generator sizes, operator families or hyperparameters to obtain utility gains.",
                     "endpoint_visibility": "Unlabelled test goal endpoints visible to all task-conditioned rankers; no held-out outcomes or proof paths in model features.",
                     "label": "Measured one-candidate marginal goal-solve fraction, including zero and negative outcomes, training contexts only.",
                     "leakage_controls": ["Distinct split seed ranges and context hashes", "No exact evaluation-goal pair offered as a candidate", "Operator skeleton families disjoint by construction", "Same frozen candidate pool and k/BFS budget for all policies", "Structure-only ablation trained on identical natural training graphs", "Reuse motif history frozen from successful training baseline witnesses"],
                     "budget_accounting": "At most three selected lemmas (or the whole eligible pool when smaller) and at most eight dequeued BFS propositions per goal, every method. Every policy has identical selected count within each context. Primitive proof edges and concrete list-operation counts reported separately. Training, candidate enumeration, and kernel certification are additional costs. No matched wall-time or Lean tactic budget claim.",
                     "verification": "Independent fresh Lean processes certify actual List Nat propositions with a propext-only allowlist when certify=True. Graph search alone is not proof."},
        "source_sha256": _source_hashes(), "model_sha256": hashlib.sha256((out / "model.json").read_bytes()).hexdigest(),
        "structure_model_sha256": hashlib.sha256((out / "structure-model.json").read_bytes()).hexdigest(),
        "model_training": model["training"], "model_history": model["history"],
        "model_history_sha256": hashlib.sha256(json.dumps(model["history"], sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "validation": {"contexts": len(validation), "results": validation_results, "hyperparameter_selection": "Fixed in advance; validation is reported without tuning on test."},
        "contexts": [{"id": context["id"], "sha256": context_hash(context), "split": split,
                      "operator_skeleton_family": context["metadata"]["operator_skeleton_family"]}
                     for split, contexts in splits.items() for context in contexts],
        "candidate_coverage": _coverage(splits),
        "goal_cleaning": cleaning, "holdout_audit": holdout,
        "summary": _summarize(records, test), "paired_comparisons": _paired_comparisons(records, test), "records": records,
        "formal_verification": {"status": "not_run", "scope": "No Lean certification requested; all search outputs remain proposals."},
        "limitations": ["All consequences are globally known nonexpansive list-length compositions; no mathematical originality claim.",
                        "Registry omission creates search difficulty; it does not create a difficult mathematical theorem.",
                        "Operator-skeleton shift only, not mathematical-domain or graph-generator-family transfer.",
                        "Typed symbolic hashes are conventional feature hashing, not pretrained semantic embeddings.",
                        "Historical reuse is operator-motif frequency in generated training proofs, not Mathlib chronology or human citations.",
                        "Conservative normalization excludes recognized equivalent goals and restatements; unrecognized mathematical equivalences may remain.",
                        "Label-free theorem-statement cleaning can leave empty goal contexts, and equivalence filtering can leave sparse or empty candidate pools. Empty contexts remain in context averages with zero solved-goal contribution; actual retained query counts determine goal denominators.",
                        "When a context has at most three eligible candidates every policy supplies the entire pool, so it provides no selected-set ranking comparison. Count contexts with a genuine ranking choice before interpreting model differences.",
                        "Ensemble disagreement is not calibrated epistemic uncertainty.",
                        "A bounded graph-search failure is not proof that a candidate is mathematically necessary.",
                        "The stronger general Lean automation control covers the showcase only, with different resources and foundational axioms; no full-benchmark tactic superiority claim."]}
    report["normalization_rules"] = _snapshot_sources(out, report["source_sha256"])
    if certify:
        _certify(out, report, groups)
    report["automation_control"] = _automation(out, certify, cleaning["test"]["retained_registry_queries"])
    report["elapsed_seconds"] = time.perf_counter() - started
    if _source_hashes() != report["source_sha256"]:
        raise ValueError("Benchmark core source changed during the experiment; retain receipts but do not finalize this report")
    report["outcomes_sha256"] = _freeze_digest(report)
    _write_json(out / "benchmark.json", report)
    return report
