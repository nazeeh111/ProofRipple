import copy
import json
from pathlib import Path
import unittest

from proofripple.engine import discover, generate_candidates, search, validate_context
from proofripple.benchmark import make_context


ROOT = Path(__file__).resolve().parents[1]


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.context = json.loads((ROOT / "examples" / "invariants.json").read_text())

    def test_candidates_are_seed_dependent_composable_non_goal_consequences(self):
        candidates = generate_candidates(self.context)
        lookup = {e["id"]: e for e in self.context["edges"] + [self.context["seed"]]}
        forbidden = {(e["source"], e["target"]) for e in self.context["edges"] + [self.context["seed"]] + self.context["goals"]}
        pairs = set()
        self.assertTrue(candidates)
        for c in candidates:
            self.assertIn("breakthrough", c["path"])
            self.assertNotIn((c["source"], c["target"]), forbidden)
            self.assertNotIn((c["source"], c["target"]), pairs)
            pairs.add((c["source"], c["target"]))
            at = c["source"]
            for eid in c["path"]:
                self.assertEqual(lookup[eid]["source"], at)
                at = lookup[eid]["target"]
            self.assertEqual(at, c["target"])
            self.assertEqual(c["status"], "proposed")
            self.assertIsNone(c["axioms"])

    def test_budget_counts_dequeued_propositions_and_keeps_witnesses(self):
        result = search(self.context, "p0", "p3", 2)
        self.assertFalse(result["solved"])
        self.assertEqual(result["expansions"], 2)
        result = search(self.context, "p0", "p3", 3)
        self.assertTrue(result["solved"])
        self.assertEqual(result["path"], ["h0", "h1", "h2"])
        self.assertFalse(search(self.context, "p0", "p1", 0)["solved"])

    def test_search_success_cannot_claim_kernel_verification(self):
        run = discover(self.context, method="graph")
        self.assertGreater(run["metrics"]["marginal_solved"], 0)
        self.assertEqual(run["verification"]["status"], "unavailable")
        self.assertTrue(all(c["status"] == "proposed" for c in run["candidates"]))

    def test_bad_seed_and_injected_identifiers_rejected(self):
        bad = copy.deepcopy(self.context)
        bad["seed"]["path"] = ["h0", "h5"]
        with self.assertRaises(ValueError):
            validate_context(bad)
        bad = copy.deepcopy(self.context)
        bad["nodes"][0]["id"] = "p0\naxiom exploit : False"
        with self.assertRaises(ValueError):
            validate_context(bad)
        bad = copy.deepcopy(self.context)
        bad["goals"][0]["target"] = "unknown"
        with self.assertRaises(ValueError):
            generate_candidates(bad)

    def test_no_gain_is_reported_without_discarding_failures(self):
        c = json.loads((ROOT / "examples" / "no_gain.json").read_text())
        run = discover(c, method="graph")
        self.assertEqual(run["metrics"]["augmented_solved"], 0)
        self.assertEqual(len(run["goals"]), 4)
        self.assertTrue(all(not g["augmented"]["solved"] for g in run["goals"]))

    def test_explicit_empty_goal_override_and_zero_selection(self):
        run = discover(self.context, goals=[], k=0, method="random")
        self.assertEqual(run["goals"], [])
        self.assertEqual(run["selected"], [])

    def test_frozen_context_reproducibility_and_split_identity(self):
        self.assertEqual(make_context(3000, "test"), make_context(3000, "test"))
        self.assertNotEqual(make_context(1000, "train")["edges"], make_context(3000, "test")["edges"])


if __name__ == "__main__":
    unittest.main()
