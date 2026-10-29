import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from proofripple.mathlib import infer_proof
from proofripple.mathlib_benchmark import (PROTOCOL, _load_frozen_protocol, _outcomes,
    freeze_mathlib_protocol, make_example)
from proofripple.mathlib_model import (BASE_FEATURE_NAMES, FEATURE_NAMES, condition_features,
    features, partner_portfolios, train_mathlib_model)
from proofripple.mathlib_search import (demand_graphs, direct_proof, discover,
    obligation_graph, op, proof, search, select, syntax, var)


class MathlibSearchTests(unittest.TestCase):
    def test_outcome_digest_does_not_depend_on_certificate_row_order(self):
        report = {"protocol": {}, "data_freeze": {"data_sha256": "synthetic"}, "records": [],
                  "formal_verification": {"status": "kernel_verified", "contexts": [
                      {"context_id": "train_1", "chunk": 0, "status": "kernel_verified"},
                      {"context_id": "test_1", "chunk": 0, "status": "kernel_verified"}]},
                  "automation_control": {"status": "not_run", "contexts": []}}
        digest = _outcomes(report)
        report["formal_verification"]["contexts"].reverse()
        self.assertEqual(digest, _outcomes(report))

    def test_and_requires_both_children_and_charges_visits(self):
        a, b, c, d = map(var, range(4))
        source, target = op("join", a, b), op("join", op("join", a, c), op("join", b, d))
        self.assertFalse(search(source, target, 2)["solved"])
        result = search(source, target, 3)
        self.assertTrue(result["solved"])
        self.assertEqual(result["expansions"], 3)
        self.assertEqual(len(result["proof"]["children"]), 2)
        self.assertEqual(infer_proof(result["proof"]), (source, target))
        self.assertEqual(search(op("join", a, b), c, 12)["expansions"], 2)
        failed_second = search(op("join", a, b), a, 3)
        self.assertFalse(failed_second["solved"])
        self.assertEqual(failed_second["expansions"], 3)

    def test_memo_hits_cost_a_visit_and_no_semantic_free_closure(self):
        a, b = var(0), var(1)
        source, target = op("join", op("meet", a, b), op("meet", a, b)), op("join", a, a)
        result = search(source, target, 3)
        self.assertTrue(result["solved"])
        self.assertEqual(result["cache_hits"], 1)
        self.assertEqual(result["expansions"], 3)
        self.assertFalse(search(op("join", a, b), op("join", b, a), 1)["solved"])
        self.assertFalse(search(a, a, 0)["solved"])
        for bad in (True, -1, 257, 1.2):
            with self.assertRaises(ValueError): search(a, a, bad)

    def test_graph_cache_isolated_from_caller_mutation(self):
        source, target = op("join", var(0), var(1)), op("join", var(2), var(3))
        first = obligation_graph(source, target, [var(4)])
        first["nodes"].clear()
        following = obligation_graph(source, target, [var(4)])
        self.assertTrue(following["nodes"])
        self.assertTrue(following["construction_cache_hit"])
        source["left"]["index"] = 5
        changed = obligation_graph(source, target, [var(4)])
        self.assertNotEqual(following["root"], changed["root"])
        a, b = var(0), var(0)
        self.assertTrue(search(a, b, 1)["solved"])
        a["index"] = 1
        self.assertFalse(search(a, b, 1)["solved"])

    def test_registered_primitives_have_checkable_interfaces(self):
        a, b, c = map(var, range(3))
        pairs = [(a, a), (op("meet", a, b), a), (op("meet", a, b), b),
                 (a, op("join", a, b)), (b, op("join", a, b)),
                 (op("meet", a, op("join", b, c)), op("join", op("meet", a, b), op("meet", a, c)))]
        for source, target in pairs:
            witness = direct_proof(source, target)
            self.assertIsNotNone(witness)
            self.assertEqual(infer_proof(witness), (source, target))

    def test_outcome_metadata_cannot_change_selection(self):
        context = make_example()
        forged = copy.deepcopy(context)
        forged["metadata"]["test_success"] = 999
        for item in forged["candidates"]:
            item.update(observed_utility=1000, status="kernel_verified", score=1e99, features=[1e99])
        for item in forged["goals"]:
            item.update(baseline={"solved": True}, augmented={"solved": False}, target_label=1)
        for method in ("random", "semantic", "proof_cost", "graph", "greedy_coverage", "branching_aware"):
            left, right = discover(context, method=method), discover(forged, method=method)
            self.assertEqual(left["selected"], right["selected"], method)
            self.assertEqual(left["metrics"], right["metrics"], method)

    def test_conditional_and_features_require_actual_sibling_identity(self):
        a, b, c, d = map(var, range(4))
        ka, kb, kc = (syntax(a), syntax(b)), (syntax(c), syntax(d)), (syntax(a), syntax(c))
        parent = (syntax(op("join", a, c)), syntax(op("join", b, d)))
        graph = {"nodes": {parent: [("sup_mono", ka, kb)]},
                 "terms": {parent: (op("join", a, c), op("join", b, d)), ka: (a, b), kb: (c, d)},
                 "root": parent, "_direct_pairs": set()}
        def item(name, pair):
            return {"id": name, "source": json.loads(pair[0]), "target": json.loads(pair[1]),
                    "proof": proof("refl", a, a)}
        candidate, sibling, unrelated = item("a", ka), item("b", kb), item("c", kc)
        base = [0] * len(BASE_FEATURE_NAMES)
        def vector(selected):
            return condition_features(base, candidate, [{}], [{parent, ka, kb}], [graph], selected)
        index = FEATURE_NAMES.index("new_exact_and_complement_fraction")
        self.assertEqual(vector([])[index], 0)
        self.assertEqual(vector([unrelated])[index], 0)
        self.assertEqual(vector([sibling])[index], 1)

    def test_features_share_graph_and_ignore_fake_outcomes(self):
        context = make_example()
        graphs = demand_graphs(context)
        candidate = context["candidates"][0]
        vector = features(context, candidate, context["goals"], 8, {})
        explicit = features(context, candidate, context["goals"], 8, {}, [set(g["nodes"]) for g in graphs], graphs=graphs)
        self.assertEqual(vector, explicit)
        forged = copy.deepcopy(candidate); forged["measured_target"] = 10000
        self.assertEqual(vector, features(context, forged, context["goals"], 8, {}))
        self.assertEqual(len(vector), len(FEATURE_NAMES))

    def test_dynamic_rescoring_records_prefix_and_actual_call_counts(self):
        context = make_example()
        def predict(model, vector, **kwargs):
            return vector[FEATURE_NAMES.index("selected_count")], 0.0
        with patch("proofripple.mathlib_model.predict", side_effect=predict):
            chosen, cost = select(context, copy.deepcopy(context["candidates"]), context["goals"], 3,
                                  "learned", {"history": {}}, 8)
        self.assertEqual(cost["candidate_feature_calls"], 3)
        self.assertEqual(cost["conditional_feature_calls"], 6)
        self.assertEqual(cost["model_prediction_calls"], 9)
        for number, row in enumerate(cost["selection_trace"]):
            self.assertEqual(row["round"], number)
            self.assertEqual(row["portfolio_before"], [item["id"] for item in chosen[:number]])
            self.assertEqual(row["chosen_id"], chosen[number]["id"])
            self.assertEqual(chosen[number]["score_portfolio"], row["portfolio_before"])

    def test_partners_are_candidate_excluded_and_deterministic(self):
        context = make_example()
        for candidate in context["candidates"]:
            portfolios = partner_portfolios(context, candidate)
            self.assertEqual(portfolios, partner_portfolios(context, candidate))
            self.assertEqual([len(p) for p in portfolios], [0, 1, 2])
            self.assertTrue(all(candidate["id"] not in [item["id"] for item in portfolio] for portfolio in portfolios))
        large = {"id": "synthetic", "candidates": [{"id": f"c{i}"} for i in range(7)]}
        self.assertEqual([len(p) for p in partner_portfolios(large, large["candidates"][0])], [0, 1, 2, 3, 4])

    def test_training_rejects_heldout_before_search(self):
        for split, identifier in (("test", "synthetic"), ("train", "test_3000"), ("train", "validation_2000")):
            context = make_example(); context["id"] = identifier; context["metadata"]["split"] = split
            with patch("proofripple.mathlib_model.search") as mocked:
                with self.assertRaises(ValueError): train_mathlib_model([context])
                mocked.assert_not_called()

    def test_synthetic_training_labels_are_conditional_marginals(self):
        context = make_example(); context["id"] = "synthetic_train"; context["metadata"]["split"] = "train"
        labels = []
        def synthetic_search(source, target, budget, lemmas=(), intermediates=()):
            return {"solved": len(lemmas) >= 2, "proof": None}
        with patch("proofripple.mathlib_model.search", side_effect=synthetic_search):
            model = train_mathlib_model([context], members=2, label_sink=labels)
        self.assertEqual(len(labels), 27)
        self.assertEqual(model["training"]["singleton_examples"], 9)
        for row in labels:
            self.assertNotIn(row["candidate_id"], row["prefix_ids"])
            self.assertEqual(row["marginal_solve_fraction"], int(len(row["prefix_ids"]) == 1))
        grouped = {}
        for row in labels:
            grouped.setdefault(row["candidate_id"], {}).setdefault(row["budget"], []).append(row["prefix_ids"])
        for budgets in grouped.values():
            self.assertEqual(budgets[4], budgets[8]); self.assertEqual(budgets[8], budgets[12])

    def test_freeze_checks_source_snapshot_before_any_labels(self):
        context = make_example()
        contexts = {split: [copy.deepcopy(context)] for split in ("train", "validation", "test")}
        digest = hashlib.sha256(json.dumps(contexts, sort_keys=True).encode()).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            for name, value in (("contexts.json", contexts), ("raw-contexts.json", contexts), ("protocol.json", PROTOCOL),
                                ("data-freeze.json", {"quick": True, "test_outcomes_observed": False,
                                                      "data_sha256": digest, "choice_gate_passed": True})):
                (path/name).write_text(json.dumps(value))
            receipt = freeze_mathlib_protocol(path, data_dir=path, quick=True)
            self.assertFalse(receipt["training_labels_observed"])
            self.assertEqual(_load_frozen_protocol(path, True)[0], contexts)
            repacked = path/"repacked"
            freeze_mathlib_protocol(repacked, data_dir=path, quick=True)
            self.assertEqual(_load_frozen_protocol(repacked, True)[0], contexts)
            self.assertEqual((path/"contexts.json.gz").read_bytes(), (repacked/"contexts.json.gz").read_bytes())
            (path/"experiment-source"/"mathlib_search.py").write_text("tampered")
            with self.assertRaises(ValueError): _load_frozen_protocol(path, True)


if __name__ == "__main__":
    unittest.main()
