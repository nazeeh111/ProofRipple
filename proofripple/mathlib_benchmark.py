"""Frozen, label-free Set Nat corpus and multi-budget usefulness evaluation."""
from __future__ import annotations

from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import copy
import gzip
import hashlib
import json
from pathlib import Path
import random
import statistics
import time

from .engine import context_hash
from .mathlib import (build_automation_source, build_mathlib_source, infer_proof,
                      normal_form, proof_uses_seed, semantic_le, statement_key,
                      validate_context, validate_term)
from .mathlib_runtime import MATHLIB_REVISION, verify_mathlib_source
from .mathlib_search import (METHODS, MAX_DEPTH, MAX_PIVOTS, OBLIGATION_CAP,
                            OBLIGATION_DEPTH, SCORE_TIE_DIGITS, direct_proof,
                            discover, nontrivial_and_nodes, op, proof, proof_cost,
                            search, subterms, syntax, term_size, var)

K_VALUES = (1, 3, 5)
BUDGETS = (4, 8, 12)
PRIMARY_HEURISTIC = "greedy_coverage"
SOURCE_NAMES = ("mathlib.py", "mathlib_runtime.py", "mathlib_search.py", "mathlib_model.py",
                "mathlib_benchmark.py", "lean.py", "model.py", "engine.py")
PROTOCOL = {
    "id": "mathlib-set-lattice-holdout-v1", "variables": 6,
    "seed": "Mathlib inf_sup_left; concrete Set Nat, union/intersection",
    "mathlib_revision": MATHLIB_REVISION,
    "train_seeds": list(range(1000, 1040)), "validation_seeds": list(range(2000, 2012)), "test_seeds": list(range(3000, 3024)),
    "candidate_target": 18, "candidate_attempt_cap": 512, "raw_goal_target": 12, "goal_attempt_cap": 256,
    "generation_families": {"train": "balanced", "validation": "left_chain", "test": "alternating_right_chain"},
    "generation": "Seed-dependent inclusions are weakened distributivity instances, shared-term monotonic wrappers, or binary monotonic combinations of two nontrivial seed-dependent proofs. Raw goals combine two distinct supplied candidate statements with union/intersection; reference derivations are used only to validate generation and are not supplied to selectors or bounded search.",
    "cleaning": "Complete positive-DNF endpoint antichains and a joint alpha-renaming key remove equality endpoints, actual finite registered closed facts, duplicate statement pairs and candidate-as-goal pairs. Prune validation against all retained training closed facts/candidates/goals, then test against training+validation. Exclude direct RAW syntactic zero-premise leaf goals. Generic inference schemas are not arbitrary semantic-substitution exclusions. Never refill from utility outcomes; retain empty contexts.",
    "choice_feasibility_gate": "Before any training labels or test solve outcomes: at least 20 of fixed 24 test contexts must have retained goals and more than five candidates. Every context remains in evaluation; failure stops this experiment rather than tuning to a desired gain.",
    "selected_lemma_caps": list(K_VALUES), "goal_visit_budgets": list(BUDGETS), "ui_summary_profile": "k3_b8",
    "search_unit": "One visited raw-syntax goal state, charged before leaf/cache/cycle checks. Failed branch work is never refunded; an AND second child is visited only after first-child success. Applicable-rule attempts/cache hits/cycle cuts are additionally reported. This is not a Lean heartbeat or tactic-step unit.",
    "search_order": "Selected exact lemma leaf (ID order), syntactic reflexivity/projections/injections/distributivity; same-root monotonicity; source-union sup_le; target-intersection le_inf; transitivity pivots.",
    "midpoint_menu": "At most eight: selected-lemma boundary matches in sorted ID order; syntactic forward/backward distributivity pivots; source-meet children/target-join children; at most eight frozen context intermediates sorted by syntax size/key. Deduplicate raw syntax, exclude endpoints, reject out-of-bound terms. Every transitivity child is solved and emitted. No DNF proof closure.",
    "search_depth_cap": MAX_DEPTH, "max_pivots": MAX_PIVOTS,
    "search_cache": "Success memo only within one goal and fixed portfolio; hit costs one visit. No failure cache or cross-goal/policy proof reuse.",
    "guidance_limit": "A supplied lemma also adds syntactic midpoint guidance, so benefit measures registry proof-search assistance, not only proof-node replacement.",
    "shared_features": {"raw_obligation_depth": OBLIGATION_DEPTH, "raw_obligation_pairs_per_goal": OBLIGATION_CAP,
                        "menu": "Same capped raw AND/OR obligation graph for all learned and goal-aware heuristics; no entailment or actual search probes in selection. Extra feature visits, estimator visits/calls and selection wall time are reported.",
                        "cost_fields": "candidate_feature_calls counts base feature vectors; conditional_feature_calls counts additional selected-prefix updates; model_prediction_calls counts every prediction, including initial and dynamic calls. selection_trace retains chosen score and prefix per round; candidate score_stage/score_portfolio identify the latest score context, not one common static ranking.",
                        "preprocessing_cache": "At most32 raw goal/intermediate-syntax graphs cached, with independent copies for every caller. Primitive membership and frontier size priors precomputed once per graph; no outcomes cached. obligation_visits is logical inventory work; obligation_build_visits and graph_primitive_preprocess_pairs count actual cache-miss construction/preprocessing, with graph_cache_hits/misses reported. Estimator recursion and all search visits remain individually charged. Request-local object-identity memo stores exact JSON syntax keys only; it cannot survive later caller mutation."},
    "heuristic_formulas": {
        "graph": "Static singleton estimated root-work decrease divided by B, plus crossing estimated cost<=B, averaged over goals.",
        "greedy_coverage": "Recompute that root-work objective after every portfolio addition on the raw AND/OR graph. Syntactic primitive or supplied leaf cost 1; unsupplied candidate pair prior is its available proof-AST node count; other frontier/cycle prior 2+min(8,total term nodes/32); AND cost 1+both children, OR minimum. Estimates are not bounded-search outcomes.",
        "branching_aware": "Dynamic greedy root-work score plus newly completed exact complementary child-pair groups whose parent is not already supplied. Known premises are supplied exact statement pairs plus direct raw syntactic leaves only. Closing a parent never globally proves its OR-route descendants; no arbitrary second match to a goal.",
        "semantic": "Transparent cosine of typed raw AST syntax tokens, not pretrained semantics.",
        "proof_cost": "Fewest available candidate proof-AST nodes; candidate proofs already generated for every method.",
        "random": "Five fixed repetitions, seeds 4400..4404; average repetitions within each context before summaries."},
    "score_ties": f"Round policy score to {SCORE_TIE_DIGITS} decimal places for deterministic ties, then greatest candidate identifier; raw published scores retained.",
    "training": {"members": 7, "ridge_alpha": 4.0, "seed": 2027, "exploration_bonus": 0.35, "diversity_penalty": 0.02,
                 "labels": "Training-only portfolio-conditioned marginal solved-goal fraction U(S+c)-U(S) at B4/8/12. For each candidate, one fixed seeded uniform partner portfolio at each size0/1/2/3/4, candidate excluded, same partners across B; deduplicate saturated small pools. Include zero/negative labels, feature conditioned on B and selected prefix. No utility-adaptive partner choices or test probes.",
                 "partner_sizes": [0, 1, 2, 3, 4],
                 "prospective_design_reason": "Before any corpus outcomes, objective review found singleton labels mismatched multi-premise portfolios. Conditioning and a singleton ablation were prospectively fixed, not chosen after a test result.",
                 "history": "Successful training baseline proof ASTs, deduplicated by context/goal raw pair/proof hash across B, then actual registered rule/transition frequencies.",
                 "ablations": ["learned_no_bonus: same conditional full model with uncertainty coefficient zero", "structure_only: retrained structural+selected-prefix ensemble, without symbolic/history columns", "learned_singleton: fit only empty-prefix rows and rank statically, the original standalone-utility objective"],
                 "validation": "Learned, greedy_coverage and branching_aware at fixed k3/B8, sanity report only; no hyperparameter sweep or test-dependent choice."},
    "primary_metric": "For each context, average across all nine k/B profiles the augmented-minus-baseline solved fraction. Empty-goal context difference is zero. Primary contrast full learned minus predeclared greedy_coverage. Report all policies/profiles and raw denominators.",
    "interval": {"unit": "paired whole-context cluster over the profile-averaged primary difference", "bootstrap_seed": 2027, "bootstrap_repetitions": 2000},
    "verification": "Independently kernel-check seed/candidate proofs and every distinct successful bounded-search proof across policies/profiles. Failed searches have no theorem. Full retained test workload also receives separate pointwise-unfolded Mathlib aesop control without discovered candidates; resource regimes differ.",
    "claim_limits": "Known distributive-lattice mathematics, not human mathematical originality. Same mathematical domain with structurally different generation families and recognized theorem-statement holdout. No learned superiority unless measured; no necessity inference from bounded failure. Symbolic hashes/bootstrap ridge are conventional, uncertainty is uncalibrated."
}


def _write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _read_corpus(directory, name):
    path = Path(directory)/(name+".json.gz")
    if path.exists():
        return json.loads(gzip.decompress(path.read_bytes()))
    return json.loads((Path(directory)/(name+".json")).read_text())


def _write_corpus(directory, name, value):
    data = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    (Path(directory)/(name+".json.gz")).write_bytes(gzip.compress(data, mtime=0))


def _base(a, b, c, branch=0):
    source = op("meet", a, op("join", b, c))
    distributed = op("join", op("meet", a, b), op("meet", a, c))
    if branch == 0:
        target = op("join", op("meet", a, b), c)
        children = [proof("refl", op("meet", a, b), op("meet", a, b)), proof("inf_right", op("meet", a, c), c)]
    else:
        target = op("join", b, op("meet", a, c))
        children = [proof("inf_right", op("meet", a, b), b), proof("refl", op("meet", a, c), op("meet", a, c))]
    return proof("trans", source, target, [proof("seed", source, distributed), proof("sup_mono", distributed, target, children)])


def _combine(a, b, kind):
    return proof("sup_mono" if kind == "join" else "inf_mono", op(kind, a["source"], b["source"]),
                 op(kind, a["target"], b["target"]), [a, b])


def _draw_term(rng, family):
    depth = rng.choice((1, 2))
    if family == "balanced":
        def build(level):
            return var(rng.randrange(6)) if level == 0 else op(rng.choice(("join", "meet")), build(level-1), build(level-1))
        return build(depth)
    term = var(rng.randrange(6))
    first = rng.choice(("join", "meet"))
    for index in range(2 * depth):
        kind = first if family == "left_chain" or index % 2 == 0 else ("meet" if first == "join" else "join")
        atom = var(rng.randrange(6))
        term = op(kind, term, atom) if family == "left_chain" else op(kind, atom, term)
    return term


def _draw_candidate(rng, family):
    def base():
        return _base(*[_draw_term(rng, family) for _ in range(3)], rng.randrange(2))
    value = base()
    style = rng.randrange(20)
    if style < 7:
        value = _combine(value, base(), rng.choice(("join", "meet")))
    elif style < 12:
        term = _draw_term(rng, family)
        value = _combine(value, proof("refl", term, term), rng.choice(("join", "meet")))
    return value


def _closed_inventory(terms):
    unique = {}
    for term in terms:
        unique.update(subterms(term))
    facts = []
    for term in sorted(unique.values(), key=lambda item: (term_size(item), syntax(item))):
        pairs = [(term, term)]
        if term["op"] == "meet":
            pairs.extend([(term, term["left"]), (term, term["right"])])
        if term["op"] == "join":
            pairs.extend([(term["left"], term), (term["right"], term)])
        for source, target in pairs:
            facts.append({"id": f"closed_{len(facts):04d}", "source": source, "target": target})
    return facts


def make_context(seed, split):
    family = PROTOCOL["generation_families"][split]
    rng = random.Random(seed)
    candidates, seen, references = [], set(), []
    for _ in range(PROTOCOL["candidate_attempt_cap"]):
        witness = _draw_candidate(rng, family)
        source, target = witness["source"], witness["target"]
        try:
            validate_term(source); validate_term(target)
            infer_proof(witness)
        except ValueError:
            continue
        key = statement_key(source, target)
        if key[0] == key[1] or key in seen or direct_proof(source, target):
            continue
        seen.add(key)
        candidates.append({"id": f"cand_{len(candidates):02d}", "source": source, "target": target, "proof": witness})
        if len(candidates) == PROTOCOL["candidate_target"]:
            break
    goals, seen_goals = [], set()
    if len(candidates) > 1:
        for _ in range(PROTOCOL["goal_attempt_cap"]):
            first, second = rng.sample(candidates, 2)
            reference = _combine(first["proof"], second["proof"], rng.choice(("join", "meet")))
            source, target = reference["source"], reference["target"]
            try:
                validate_term(source); validate_term(target); infer_proof(reference)
            except ValueError:
                continue
            key = statement_key(source, target)
            if key[0] == key[1] or key in seen or key in seen_goals or direct_proof(source, target):
                continue
            seen_goals.add(key)
            goals.append({"id": f"goal_{len(goals):02d}", "source": source, "target": target})
            references.append(nontrivial_and_nodes(reference))
            if len(goals) == PROTOCOL["raw_goal_target"]:
                break
    terms = [item[side] for item in [*candidates, *goals] for side in ("source", "target")]
    facts = _closed_inventory(terms)
    intermediates = {syntax(term): term for item in candidates for term in subterms(item["source"]).values()}
    context = {"id": f"{split}_{seed}", "domain": "mathlib-set-lattice", "variables": 6,
               "title": f"Mathlib set-lattice context {seed}", "seed": {"id": "distributivity", "declaration": "inf_sup_left"},
               "candidates": candidates, "goals": goals, "closed_facts": facts,
               "intermediates": sorted(intermediates.values(), key=lambda item: (term_size(item), syntax(item)))[:8],
               "metadata": {"split": split, "generator_family": family,
                            "candidate_nontrivial_and_nodes": sum(nontrivial_and_nodes(item["proof"]) for item in candidates),
                            "reference_goal_nontrivial_and_nodes": sum(references),
                            "reference_proofs_exposed": False}}
    return context


def _key(item):
    return statement_key(item["source"], item["target"])


def _index(contexts):
    return {_key(item) for context in contexts for item in [*context["closed_facts"], *context["candidates"], *context["goals"]]}


def _clean(raw):
    contexts = copy.deepcopy(raw)
    rows = []
    for split, items in contexts.items():
        for context in items:
            known = {_key(item) for item in context["closed_facts"]}
            goal_keys = {_key(item) for item in context["goals"]}
            seen = set()
            candidates = []
            for item in context["candidates"]:
                key = _key(item)
                if key[0] != key[1] and key not in known | goal_keys | seen and not direct_proof(item["source"], item["target"]):
                    seen.add(key); candidates.append(item)
            goals, seen = [], set()
            for item in context["goals"]:
                key = _key(item)
                if key[0] != key[1] and key not in known | seen and not direct_proof(item["source"], item["target"]):
                    seen.add(key); goals.append(item)
            row = {"context_id": context["id"], "split": split, "raw_candidates": len(context["candidates"]), "raw_goals": len(context["goals"]),
                   "removed_prior_candidates": 0, "removed_prior_goals": 0}
            context["candidates"], context["goals"] = candidates, goals
            rows.append(row)
    prior = _index(contexts["train"])
    training = set(prior)
    for split in ("validation", "test"):
        for context in contexts[split]:
            row = next(row for row in rows if row["context_id"] == context["id"])
            old_c, old_g = len(context["candidates"]), len(context["goals"])
            context["candidates"] = [item for item in context["candidates"] if _key(item) not in prior]
            context["goals"] = [item for item in context["goals"] if _key(item) not in prior]
            row.update(removed_prior_candidates=old_c-len(context["candidates"]), removed_prior_goals=old_g-len(context["goals"]))
        if split == "validation":
            prior.update(_index(contexts[split]))
    for split, items in contexts.items():
        for context in items:
            validate_context(context)
            row = next(row for row in rows if row["context_id"] == context["id"])
            row.update(candidates=len(context["candidates"]), goals=len(context["goals"]), context_sha256=context_hash(context),
                       nontrivial_candidate_and_nodes=sum(nontrivial_and_nodes(item["proof"]) for item in context["candidates"]))
    audit = {"normalization": "Complete positive DNF endpoint antichains and joint alpha orbit over used variables; not arbitrary semantic-substitution schema closure",
             "training_index_pairs": len(training), "prior_index_pairs": len(prior),
             "validation_goal_prior_overlap": sum(_key(item) in training for context in contexts["validation"] for item in context["goals"]),
             "test_goal_prior_overlap": sum(_key(item) in prior for context in contexts["test"] for item in context["goals"]),
             "test_candidate_prior_overlap": sum(_key(item) in prior for context in contexts["test"] for item in context["candidates"]),
             "contexts": rows}
    if any(audit[key] for key in ("validation_goal_prior_overlap", "test_goal_prior_overlap", "test_candidate_prior_overlap")):
        raise ValueError("Mathlib statement holdout validation failed")
    return contexts, audit


def _coverage(contexts, k):
    return {split: {"contexts": len(items), "active_goal_contexts": sum(bool(c["goals"]) for c in items),
                    "contexts_with_ranking_choice": sum(bool(c["goals"]) and len(c["candidates"])>k for c in items),
                    "candidate_total": sum(len(c["candidates"]) for c in items), "goal_total": sum(len(c["goals"]) for c in items),
                    "candidate_counts": {c["id"]: len(c["candidates"]) for c in items}}
            for split, items in contexts.items()}


def prepare_mathlib_data(output_dir, quick=False):
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    seeds = {"train": PROTOCOL["train_seeds"][:8] if quick else PROTOCOL["train_seeds"],
             "validation": PROTOCOL["validation_seeds"][:3] if quick else PROTOCOL["validation_seeds"],
             "test": PROTOCOL["test_seeds"][:4] if quick else PROTOCOL["test_seeds"]}
    raw = {split: [make_context(seed, split) for seed in values] for split, values in seeds.items()}
    contexts, audit = _clean(raw)
    coverage = _coverage(contexts, 5)
    required = min(20, len(contexts["test"]))
    passed = coverage["test"]["contexts_with_ranking_choice"] >= required
    receipt = {"schema_version": 1, "phase": "label_free_data_freeze", "quick": quick,
               "protocol_sha256": hashlib.sha256(json.dumps(PROTOCOL, sort_keys=True).encode()).hexdigest(),
               "data_sha256": hashlib.sha256(json.dumps(contexts, sort_keys=True).encode()).hexdigest(),
               "contexts": {split: [context_hash(context) for context in items] for split, items in contexts.items()},
               "coverage_at_largest_k": coverage, "required_choice_contexts": required, "choice_gate_passed": passed,
               "test_outcomes_observed": False, "holdout": audit}
    _write(out/"protocol.json", PROTOCOL); _write_corpus(out, "raw-contexts", raw)
    _write_corpus(out, "contexts", contexts); _write(out/"data-freeze.json", receipt)
    if not passed:
        raise ValueError("Label-free Mathlib ranking-choice feasibility gate failed; inspect data-freeze.json, do not tune on solve outcomes")
    return contexts, receipt


def make_example():
    first = _base(var(0), var(1), var(2))
    second = _base(op("join", var(3), var(4)), var(1), var(5))
    extra_term = op("meet", var(3), var(4))
    third = _combine(first, proof("refl", extra_term, extra_term), "join")
    candidates = [{"id": f"cand_{i:02d}", "source": value["source"], "target": value["target"], "proof": value}
                  for i, value in enumerate((first, second, third))]
    reference = _combine(first, second, "join")
    context = {"id": "mathlib_demo", "domain": "mathlib-set-lattice", "variables": 6,
               "title": "Two-premise set-inclusion consequence", "seed": {"id": "distributivity", "declaration": "inf_sup_left"},
               "candidates": candidates, "goals": [{"id": "goal_00", "source": reference["source"], "target": reference["target"]}],
               "intermediates": [var(i) for i in range(6)], "metadata": {"split": "illustrative", "generator_family": "hand-declared; not selected from held-out data"}}
    return validate_context(context)


def _provenance(out):
    folder = Path(__file__).resolve().parent
    target = out/"experiment-source"; target.mkdir(exist_ok=True)
    hashes = {}
    for name in SOURCE_NAMES:
        data = (folder/name).read_bytes(); (target/name).write_bytes(data)
        hashes[name] = hashlib.sha256(data).hexdigest()
    return hashes


def freeze_mathlib_protocol(output_dir, data_dir=None, quick=False):
    """Freeze exact scientific bytes before any utility-label searches.

    An existing label-free corpus may be reused after its content digest and
    generation contract are checked. Changes to prospective model/policy text
    do not require regenerating identical statement data.
    """
    from .mathlib_model import partner_portfolios
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    if data_dir is None:
        contexts, data_receipt = prepare_mathlib_data(out, quick)
    else:
        source = Path(data_dir)
        contexts = _read_corpus(source, "contexts")
        data_receipt = json.loads((source/"data-freeze.json").read_text())
        protocol_path = source/"frozen-protocol.json" if (source/"frozen-protocol.json").exists() else source/"protocol.json"
        old_protocol = json.loads(protocol_path.read_text())
        generation_fields = ("variables", "seed", "mathlib_revision", "train_seeds", "validation_seeds", "test_seeds",
                             "candidate_target", "candidate_attempt_cap", "raw_goal_target", "goal_attempt_cap",
                             "generation_families", "generation", "cleaning", "choice_feasibility_gate")
        if any(old_protocol.get(key) != PROTOCOL[key] for key in generation_fields):
            raise ValueError("Existing label-free corpus has a different generation contract")
        if data_receipt.get("quick") != quick or data_receipt.get("test_outcomes_observed") is not False:
            raise ValueError("Expected an outcome-blind corpus with the requested full/quick scope")
        digest = hashlib.sha256(json.dumps(contexts, sort_keys=True).encode()).hexdigest()
        if digest != data_receipt.get("data_sha256") or not data_receipt.get("choice_gate_passed"):
            raise ValueError("Existing label-free corpus digest or feasibility gate failed")
        previous_freeze = json.loads((source/"source-freeze.json").read_text()) if (source/"source-freeze.json").exists() else {}
        for name in ("contexts", "raw-contexts"):
            compressed = source/(name+".json.gz")
            if compressed.exists():
                data = compressed.read_bytes()
                expected = previous_freeze.get("corpus_sha256", {}).get(compressed.name)
                if expected is not None and hashlib.sha256(data).hexdigest() != expected:
                    raise ValueError("Existing compressed corpus differs from its prior freeze")
                if source.resolve() != out.resolve():
                    (out/compressed.name).write_bytes(data)
            else:
                _write_corpus(out, name, contexts if name == "contexts" else _read_corpus(source, name))
        if source.resolve() != out.resolve():
            (out/"data-freeze.json").write_bytes((source/"data-freeze.json").read_bytes())
    hashes = _provenance(out)
    protocol_digest = hashlib.sha256(json.dumps(PROTOCOL, sort_keys=True).encode()).hexdigest()
    receipt = {"schema_version": 1, "phase": "prospective_source_protocol_freeze", "quick": quick,
               "protocol_sha256": protocol_digest, "data_sha256": data_receipt["data_sha256"],
               "source_sha256": hashes, "training_labels_observed": False, "test_outcomes_observed": False,
               "corpus_sha256": {name: hashlib.sha256((out/name).read_bytes()).hexdigest()
                                 for name in ("contexts.json.gz", "raw-contexts.json.gz")},
               "coverage_at_largest_k": _coverage(contexts, 5),
               "planned_training_rows": sum(len(partner_portfolios(context, candidate))*len(BUDGETS)
                                            for context in contexts["train"] for candidate in context["candidates"])}
    _write(out/"frozen-protocol.json", PROTOCOL)
    _write(out/"source-freeze.json", receipt)
    return receipt


def _load_frozen_protocol(directory, quick):
    directory = Path(directory)
    receipt = json.loads((directory/"source-freeze.json").read_text())
    protocol = json.loads((directory/"frozen-protocol.json").read_text())
    contexts = _read_corpus(directory, "contexts")
    data_receipt = json.loads((directory/"data-freeze.json").read_text())
    folder = Path(__file__).resolve().parent
    current = {name: hashlib.sha256((folder/name).read_bytes()).hexdigest() for name in SOURCE_NAMES}
    snapshots = {name: hashlib.sha256((directory/"experiment-source"/name).read_bytes()).hexdigest() for name in SOURCE_NAMES}
    if current != receipt["source_sha256"] or snapshots != current or protocol != PROTOCOL:
        raise ValueError("Scientific source/protocol differs from the prospective freeze")
    if {name: hashlib.sha256((directory/name).read_bytes()).hexdigest()
            for name in ("contexts.json.gz", "raw-contexts.json.gz")} != receipt["corpus_sha256"]:
        raise ValueError("Compressed corpus differs from the prospective freeze")
    if (receipt.get("quick") != quick or receipt.get("test_outcomes_observed") is not False
            or receipt.get("training_labels_observed") is not False
            or hashlib.sha256(json.dumps(protocol, sort_keys=True).encode()).hexdigest() != receipt["protocol_sha256"]
            or hashlib.sha256(json.dumps(contexts, sort_keys=True).encode()).hexdigest() != receipt["data_sha256"]
            or data_receipt["data_sha256"] != receipt["data_sha256"]):
        raise ValueError("Invalid prospective corpus freeze")
    return contexts, data_receipt, receipt


def _proof_hash(witness):
    return hashlib.sha256(json.dumps(witness, sort_keys=True, separators=(",", ":")).encode()).hexdigest() if witness else None


def _lemma_ids(witness):
    if witness is None:
        return set()
    return ({witness["lemma_id"]} if witness["rule"] == "lemma" else set()).union(*(_lemma_ids(child) for child in witness.get("children", [])))


def _expanded(witness, candidates):
    if witness["rule"] == "lemma":
        return candidates[witness["lemma_id"]]["proof"]
    return {**witness, "children": [_expanded(child, candidates) for child in witness.get("children", [])]}


def _summary(records, contexts):
    result = {}
    for method in METHODS:
        rows = [row for row in records if row["method"] == method]
        def total(key):
            return sum(statistics.mean(row[key] for row in rows if row["context_id"] == context["id"]) for context in contexts)
        total_goals = sum(len(context["goals"]) for context in contexts)
        result[method] = {"contexts": len(contexts), "active_goal_contexts": sum(bool(c["goals"]) for c in contexts),
                          "total_goals": total_goals, "total_baseline_solved": total("baseline_solved"),
                          "total_solved": total("augmented_solved"), "total_newly_solved": total("newly_solved"),
                          "total_regressed": total("regressed"), "total_marginal_solved": total("marginal_solved"),
                          "mean_baseline_solved": total("baseline_solved")/len(contexts),
                          "mean_augmented_solved": total("augmented_solved")/len(contexts),
                          "mean_marginal_solved": total("marginal_solved")/len(contexts),
                          "mean_solve_fraction": total("augmented_solved")/max(1, total_goals),
                          "random_interpretation": "Five repetitions averaged within context before totals; one retained query counted once per profile."}
    return result


def _primary(records, contexts):
    context_scores = {}
    for method in METHODS:
        values = []
        for context in contexts:
            profiles = []
            for k in K_VALUES:
                for budget in BUDGETS:
                    rows = [row for row in records if row["context_id"] == context["id"] and row["method"] == method and row["k"] == k and row["search_budget"] == budget]
                    profiles.append(statistics.mean(row["marginal_solved"] for row in rows)/max(1, len(context["goals"])))
            values.append(statistics.mean(profiles))
        context_scores[method] = values
    contrasts = {}
    for other in METHODS:
        if other == "learned":
            continue
        differences = [a-b for a, b in zip(context_scores["learned"], context_scores[other])]
        rng = random.Random(2027)
        boot = sorted(statistics.mean(rng.choices(differences, k=len(differences))) for _ in range(2000))
        contrasts["learned_minus_"+other] = {"mean_context_profile_solve_fraction_difference": statistics.mean(differences),
                                            "paired_context_bootstrap_95pct": [boot[49], boot[1949]], "context_differences": differences}
    return {"metric": PROTOCOL["primary_metric"], "primary_comparator": PRIMARY_HEURISTIC,
            "mean_context_profile_solve_fraction_gain": {method: statistics.mean(values) for method, values in context_scores.items()},
            "contrasts": contrasts, "context_scores": context_scores}


def _certificate_run(context, witnesses):
    context = copy.deepcopy(context)
    goals, outcomes = [], []
    for index, item in enumerate(witnesses):
        identifier = f"certificate_{index:03d}"
        goal = {"id": identifier, "source": item["source"], "target": item["target"]}
        goals.append(goal)
        outcomes.append({**goal, "baseline": {"solved": False, "proof": None},
                         "augmented": {"solved": True, "proof": item["proof"]}})
    context["goals"] = goals
    return {"context": context, "candidates": copy.deepcopy(context["candidates"]),
            "selected": [item["id"] for item in context["candidates"]], "goals": outcomes}


def _certify(out, contexts, witnesses):
    directory = out/"proofs"; directory.mkdir(exist_ok=True)
    jobs = []
    for split in ("train", "validation", "test"):
        items = contexts[split]
        for context in items:
            values = list(witnesses[context["id"]].values())
            for number, start in enumerate(range(0, max(1, len(values)), 128)):
                run = _certificate_run(context, values[start:start+128])
                source, names, metadata = build_mathlib_source(run)
                jobs.append((split, context["id"], number, source, names, len(context["candidates"]), len(run["goals"])))
    def check(job):
        split, cid, number, source, names, candidates, goals = job
        stem = f"{cid}_{number:02d}"
        (directory/(stem+".lean")).write_text(source)
        result = verify_mathlib_source(source, names, timeout=120)
        (directory/(stem+".log")).write_text(result["log"])
        item = {"split": split, "context_id": cid, "chunk": number, "status": result["status"],
                "source": "proofs/"+stem+".lean", "source_sha256": result["source_sha256"],
                "expected_declarations": len(names), "audits_received": len(result["audits"]),
                "candidates": candidates, "successful_witnesses": goals, "elapsed_seconds": result["elapsed_seconds"]}
        print(f"Mathlib {stem}: {result['status']} {len(result['audits'])}/{len(names)}", flush=True)
        return item, {"context_id": cid, "chunk": number, "status": result["status"], "audits": result["audits"]}
    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=2) as pool:
        checked = list(pool.map(check, jobs))
    rows, audits = [row for row, _ in checked], [audit for _, audit in checked]
    plain = json.dumps(audits, sort_keys=True, separators=(",", ":")).encode()
    compressed = gzip.compress(plain, mtime=0); (out/"benchmark-audits.json.gz").write_bytes(compressed)
    return {"status": "kernel_verified" if rows and all(row["status"] == "kernel_verified" for row in rows) else "failed",
            "mathlib_revision": MATHLIB_REVISION, "allowed_axioms": ["propext", "Classical.choice", "Quot.sound"],
            "declarations": sum(row["expected_declarations"] for row in rows), "audits_received": sum(row["audits_received"] for row in rows),
            "contexts": rows, "audits_sha256": hashlib.sha256(compressed).hexdigest(), "audits_uncompressed_sha256": hashlib.sha256(plain).hexdigest(),
            "elapsed_seconds": time.perf_counter()-started, "summed_subprocess_elapsed_seconds": sum(row["elapsed_seconds"] for row in rows),
            "parallel_processes": 2,
            "scope": "Every candidate and every distinct successful held-out proof across all policies, random repetitions and nine budget profiles. Train uses canonical greedy k3/B8 successes; validation retains learned/greedy/branching k3/B8 witnesses. Training label probes are not individually certified. Repeated candidate/library audits across chunks are not new discoveries."}


def _automation(out, contexts):
    directory = out/"automation"; directory.mkdir(exist_ok=True)
    def check(context):
        source, names = build_automation_source(context["goals"], context.get("variables", 6))
        (directory/(context["id"]+".lean")).write_text(source)
        result = verify_mathlib_source(source, names, timeout=120)
        _write(directory/(context["id"]+".json"), result)
        return {"context_id": context["id"], "status": result["status"], "goals": len(context["goals"]),
                "solved": len(context["goals"]) if result["status"] == "kernel_verified" else 0,
                "source_sha256": result["source_sha256"], "audits_received": len(result["audits"]),
                "elapsed_seconds": result["elapsed_seconds"]}
    with ThreadPoolExecutor(max_workers=2) as pool:
        rows = list(pool.map(check, contexts))
    return {"status": "kernel_verified" if rows and all(row["status"] == "kernel_verified" for row in rows) else "failed",
            "method": "Pointwise Set Nat membership unfolding, simp only[mem_union,mem_inter] at *, aesop; no seed/candidates",
            "total": sum(row["goals"] for row in rows), "solved": sum(row["solved"] for row in rows), "contexts": rows,
            "coverage": "Entire retained test workload, not a showcase sample.",
            "interpretation": "Separate stronger Mathlib automation under its fixed resource cap; goal visits are not tactic heartbeats, so no matched computational-work claim."}


def _outcomes(report):
    """Discrete scientific decisions; provenance bytes and raw floats separate."""
    projection = {"protocol": report["protocol"], "data_sha256": report["data_freeze"]["data_sha256"],
                  "records": [{key: value for key, value in row.items() if key not in ("selection_cost",)} for row in report["records"]]}
    for key in ("formal_verification", "automation_control"):
        value = report[key]
        projection[key] = {field: value[field] for field in ("status", "declarations", "audits_received", "total", "solved") if field in value}
        projection[key]["contexts"] = [{field: row[field] for field in ("context_id", "chunk", "status", "source_sha256", "expected_declarations", "audits_received", "goals", "solved") if field in row}
                                      for row in sorted(value.get("contexts", []), key=lambda row: (row["context_id"], row.get("chunk", 0)))]
    return hashlib.sha256(json.dumps(projection, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def run_mathlib_benchmark(output_dir, quick=False, certify=False, frozen_dir=None):
    from .mathlib_model import train_mathlib_model
    started = time.perf_counter(); out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    source_freeze = None
    if frozen_dir is None:
        contexts, receipt = prepare_mathlib_data(out, quick)
    else:
        contexts, receipt, source_freeze = _load_frozen_protocol(frozen_dir, quick)
        for name in ("contexts.json.gz", "raw-contexts.json.gz", "data-freeze.json", "frozen-protocol.json", "source-freeze.json"):
            (out/name).write_bytes((Path(frozen_dir)/name).read_bytes())
        _write(out/"protocol.json", PROTOCOL)
    hashes = _provenance(out)
    labels = []; model = train_mathlib_model(contexts["train"], label_sink=labels)
    _write(out/"model.json", model)
    (out/"training-labels.json.gz").write_bytes(gzip.compress(json.dumps(labels, sort_keys=True).encode(), mtime=0))
    witnesses = {context["id"]: {} for items in contexts.values() for context in items}
    branching = {"surface_nontrivial_and_nodes": 0, "expanded_nontrivial_and_nodes": 0}
    def retain(context, run):
        known = {item["id"]: item for item in context["candidates"]}
        for goal in run["goals"]:
            for variant in ("baseline", "augmented"):
                result = goal[variant]
                if result["solved"]:
                    allowed = set() if variant == "baseline" else set(run["selected"])
                    if not _lemma_ids(result["proof"]).issubset(allowed):
                        raise ValueError("A search witness used an unselected consequence")
                    infer_proof(result["proof"], known={key: known[key] for key in allowed})
                    key = (_proof_hash(result["proof"]), syntax(goal["source"]), syntax(goal["target"]))
                    witnesses[context["id"]][key] = {"source": goal["source"], "target": goal["target"], "proof": result["proof"]}
                    branching["surface_nontrivial_and_nodes"] += nontrivial_and_nodes(result["proof"])
                    branching["expanded_nontrivial_and_nodes"] += nontrivial_and_nodes(_expanded(result["proof"], known))
    validation = []
    for split in ("train", "validation"):
        for context in contexts[split]:
            for method in (("learned", "greedy_coverage", "branching_aware") if split == "validation" else ("greedy_coverage",)):
                run = discover(context, model, 3, 8, method)
                retain(context, run)
                if split == "validation":
                    validation.append({"context_id": context["id"], "k": 3, "search_budget": 8,
                                       "selected": run["selected"], **run["metrics"]})
    records, profiles = [], {}
    for k in K_VALUES:
        for budget in BUDGETS:
            profile_id = f"k{k}_b{budget}"
            profile_rows = []
            for context in contexts["test"]:
                for method in METHODS:
                    for repetition in range(5 if method == "random" else 1):
                        run = discover(context, model, k, budget, method, 4400+repetition)
                        retain(context, run)
                        row = {"context_id": context["id"], "context_sha256": context_hash(context), "profile": profile_id,
                               "k": k, "search_budget": budget, "method": method, "repetition": repetition,
                               **run["metrics"], "selected": run["selected"], "selection_cost": run["selection_cost"],
                               "baseline_goal_visits": sum(goal["baseline"]["expansions"] for goal in run["goals"]),
                               "augmented_goal_visits": sum(goal["augmented"]["expansions"] for goal in run["goals"]),
                               "goal_decisions": [{"id": goal["id"], **{variant: {"solved": goal[variant]["solved"],
                                                                                   "goal_visits": goal[variant]["expansions"],
                                                                                   **{key: goal[variant][key] for key in ("applicable_rule_attempts", "cache_hits", "cycle_cuts")},
                                                                                   "proof_sha256": _proof_hash(goal[variant]["proof"])}
                                                                           for variant in ("baseline", "augmented")}}
                                                  for goal in run["goals"]]}
                        records.append(row); profile_rows.append(row)
                print(f"Mathlib evaluation {profile_id} {context['id']}", flush=True)
            profiles[profile_id] = {"k": k, "budget": budget, "summary": _summary(profile_rows, contexts["test"]),
                                    "candidate_coverage": _coverage(contexts, k)}
    compressed_witnesses = {cid: list(values.values()) for cid, values in witnesses.items()}
    (out/"search-witnesses.json.gz").write_bytes(gzip.compress(json.dumps(compressed_witnesses, sort_keys=True).encode(), mtime=0))
    report = {"schema_version": 1, "domain": "mathlib-set-lattice", "benchmark": PROTOCOL["id"], "quick": quick,
              "protocol": PROTOCOL, "data_freeze": receipt, "source_sha256": hashes,
              "prospective_source_freeze": source_freeze,
              "model_sha256": hashlib.sha256((out/"model.json").read_bytes()).hexdigest(), "model_training": model["training"],
              "model_history": model["history"], "validation": validation, "profiles": profiles,
              "summary_profile": "k3_b8", "summary": profiles["k3_b8"]["summary"],
              "aggregate_summary": _primary(records, contexts["test"]), "records": records, "branching": branching,
              "formal_verification": {"status": "not_run"}, "automation_control": {"status": "not_run"},
              "limitations": PROTOCOL["claim_limits"]}
    if certify:
        report["formal_verification"] = _certify(out, contexts, witnesses)
        report["automation_control"] = _automation(out, contexts["test"])
    report["elapsed_seconds"] = time.perf_counter()-started
    current = {name: hashlib.sha256((Path(__file__).resolve().parent/name).read_bytes()).hexdigest() for name in hashes}
    if current != hashes:
        raise ValueError("Mathlib scientific source changed during experiment; retain evidence without promoting report")
    report["outcomes_sha256"] = _outcomes(report)
    _write(out/"benchmark.json", report)
    return report
