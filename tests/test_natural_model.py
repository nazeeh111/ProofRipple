import copy
import json
import math
import os
import subprocess
import sys
import unittest

from proofripple.engine import generate_candidates
from proofripple.natural_model import (
    NATURAL_FEATURE_NAMES, natural_features, predict_natural,
    select_natural, symbolic_embedding, train_natural_model,
)


def typed_context(identifier="train_a", shift=0, nodes=10):
    operations = ["filter", "map", "reverse", "take"]
    stages = [{"id": "p0", "label": "Input list", "expression": {"op": "input"}}]
    for i in range(1, nodes):
        stages.append({"id": f"p{i}", "label": "Stage", "expression": {
            "op": operations[(i + shift) % len(operations)], "input": f"p{i-1}"}})
    return {"id": identifier, "nodes": stages,
            "edges": [{"id": f"h{i}", "source": f"p{i}", "target": f"p{i+1}"} for i in range(nodes-1)],
            "seed": {"id": "seed", "source": "p2", "target": "p4", "path": ["h2", "h3"]},
            "goals": [{"source": "p0", "target": f"p{nodes-1}"}, {"source": "p1", "target": f"p{nodes-1}"},
                      {"source": "p4", "target": f"p{nodes-1}"}]}


class NaturalModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train = [typed_context("train_a", 0), typed_context("train_b", 1, 11), typed_context("train_c", 2, 12)]
        cls.model = train_natural_model(cls.train, search_budget=5, members=3)

    def test_real_training_roundtrip_and_feature_contract(self):
        model = json.loads(json.dumps(self.model))
        self.assertEqual(model, train_natural_model(self.train, search_budget=5, members=3))
        self.assertEqual(len(model["feature_names"]), 32)
        self.assertEqual(model["feature_names"], NATURAL_FEATURE_NAMES)
        self.assertGreater(model["training"]["positive_labels"], 0)
        self.assertGreater(model["history"]["successful_training_goals"], 0)
        self.assertTrue(any(abs(weight) > 1e-8 for member in model["weights"] for weight in member[1:]))
        context = typed_context("test_d", 3, 13)
        candidate = generate_candidates(context)[0]
        features = natural_features(context, candidate, context["goals"], model["history"])
        mean, spread = predict_natural(model, features)
        self.assertTrue(math.isfinite(mean))
        self.assertGreaterEqual(spread, 0)
        with self.assertRaisesRegex(ValueError, "contract"):
            predict_natural({**model, "feature_names": ["wrong"]}, features)

    def test_symbolic_hash_ignores_names_and_outcomes_but_observes_operations(self):
        context = typed_context("test_d", 3, 13)
        candidate = generate_candidates(context)[0]
        original = symbolic_embedding(context, candidate)
        renamed = copy.deepcopy(context)
        mapping = {item["id"]: "q" + item["id"][1:] for item in renamed["nodes"]}
        for item in renamed["nodes"]:
            item["id"] = mapping[item["id"]]
            item["label"] = "Untrusted arbitrary words"
            if "input" in item["expression"]:
                item["expression"]["input"] = mapping[item["expression"]["input"]]
        for edge in renamed["edges"] + [renamed["seed"]] + renamed["goals"]:
            edge["source"], edge["target"] = mapping[edge["source"]], mapping[edge["target"]]
        renamed["id"] = "different_scenario"
        other = {**candidate, "source": mapping[candidate["source"]], "target": mapping[candidate["target"]]}
        self.assertEqual(original, symbolic_embedding(renamed, other))
        altered = copy.deepcopy(context)
        target = next(item for item in altered["nodes"] if item["id"] == candidate["target"])
        target["expression"]["op"] = "take" if target["expression"]["op"] != "take" else "filter"
        self.assertNotEqual(original, symbolic_embedding(altered, candidate))
        self.assertAlmostEqual(sum(value * value for value in original), 1.0)

    def test_hash_reproducible_across_python_hash_seeds(self):
        code = ("import json; from proofripple.natural_model import symbolic_embedding; "
                "from proofripple.engine import generate_candidates; "
                "c=json.loads(" + repr(json.dumps(typed_context())) + "); "
                "print(json.dumps(symbolic_embedding(c,generate_candidates(c)[0])))")
        outputs = [subprocess.check_output([sys.executable, "-c", code], env={**os.environ, "PYTHONHASHSEED": seed}, text=True)
                   for seed in ("1", "9821")]
        self.assertEqual(*outputs)

    def test_held_out_outcome_poisoning_changes_no_selection_or_features(self):
        context = typed_context("test_d", 3, 13)
        candidates = generate_candidates(context)
        selected = select_natural(context, candidates, context["goals"], 3, self.model)
        poisoned = copy.deepcopy(context)
        poisoned["results"] = {"solved": True, "proof": "not evidence"}
        for goal in poisoned["goals"]:
            goal.update({"solved": True, "marginal_solved": 999999,
                         "baseline": {"solved": False}, "augmented": {"solved": True},
                         "path": ["pretend_test_proof"]})
        poisoned_candidates = generate_candidates(poisoned)
        selected_again = select_natural(poisoned, poisoned_candidates, poisoned["goals"], 3, self.model)
        self.assertEqual([item["id"] for item in selected], [item["id"] for item in selected_again])
        self.assertEqual([(item["features"], item["score"], item["uncertainty"]) for item in candidates],
                         [(item["features"], item["score"], item["uncertainty"]) for item in poisoned_candidates])
        self.assertEqual(len(selected), 3)
        self.assertEqual(len({item["id"] for item in selected}), 3)
        self.assertEqual(self.model["training"]["context_ids"], ["train_a", "train_b", "train_c"])

    def test_history_matches_training_search_witnesses_and_is_frozen(self):
        history = self.model["history"]
        self.assertGreater(history["dependency_occurrences"], 0)
        self.assertEqual(sum(history["signature_counts"].values()), history["dependency_occurrences"])
        self.assertTrue(all(">" in signature and not any(name in signature for name in ("p0", "train_"))
                            for signature in history["signature_counts"]))
        before = copy.deepcopy(history)
        context = typed_context("test_d", 3, 13)
        select_natural(context, generate_candidates(context), context["goals"], 3, self.model)
        self.assertEqual(before, self.model["history"])

    def test_fail_closed_on_held_out_metadata_or_missing_explicit_model(self):
        context = typed_context("test_d")
        context["split"] = "test"
        with self.assertRaisesRegex(ValueError, "Held-out"):
            train_natural_model([context])
        with self.assertRaisesRegex(ValueError, "frozen model"):
            select_natural(context, generate_candidates(context), context["goals"])
        cyclic = typed_context()
        cyclic["nodes"][1]["expression"]["input"] = "p2"
        candidate = generate_candidates(cyclic)[0]
        with self.assertRaisesRegex(ValueError, "acyclic"):
            symbolic_embedding(cyclic, candidate)


if __name__ == "__main__":
    unittest.main()
