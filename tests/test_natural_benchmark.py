import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from proofripple.engine import discover, generate_candidates
from proofripple.natural import length_normal_forms, make_example, validate_natural_context
from proofripple.natural_benchmark import (
    FAMILIES, NATURAL_METHODS, _automation, _combined_run, _freeze_digest,
    _prepare_splits, make_natural_context, run_natural_benchmark,
)


class NaturalGeneratorTests(unittest.TestCase):
    def test_operator_skeleton_families_are_actually_disjoint(self):
        contexts = {split: make_natural_context(1700, split) for split in FAMILIES}
        for split, context in contexts.items():
            self.assertEqual(validate_natural_context(context), context)
            self.assertEqual(context["split"], split)
            self.assertEqual(len(context["goals"]), 20)
        operations = {split: [node["expression"]["op"] for node in context["nodes"]]
                      for split, context in contexts.items()}
        reducing = {"filter", "take"}
        preserving = {"map", "reverse"}
        self.assertIn(operations["train"][1], reducing)
        self.assertIn(operations["train"][2], preserving)
        self.assertTrue(all(op in preserving for op in operations["validation"][1:3]))
        self.assertIn(operations["validation"][3], reducing)
        self.assertTrue(all(op in reducing for op in operations["test"][1:4]))
        self.assertEqual(len({tuple(ops) for ops in operations.values()}), 3)
        # Changing only the operator skeleton family preserves the underlying
        # graph generator, a limitation the report explicitly discloses.
        self.assertEqual(contexts["train"]["edges"], contexts["test"]["edges"])

    def test_frozen_contexts_and_reducing_seed_are_reproducible(self):
        for split in FAMILIES:
            context = make_natural_context(1000, split)
            self.assertEqual(context, make_natural_context(1000, split))
            ids = [node["id"] for node in context["nodes"]]
            a = ids.index(context["seed"]["source"])
            b = ids.index(context["seed"]["target"])
            self.assertTrue(any(node["expression"]["op"] in {"filter", "take"}
                                for node in context["nodes"][a + 1:b + 1]))
            forms = length_normal_forms(context)
            self.assertNotEqual(forms[context["seed"]["source"]], forms[context["seed"]["target"]])
        with self.assertRaises(ValueError):
            make_natural_context(1000, "unknown")

    def test_every_frozen_context_has_nonidentity_seed_and_twenty_unique_goals(self):
        for split, seeds in (("train", range(1000, 1016)), ("validation", range(2000, 2006)), ("test", range(3000, 3012))):
            for seed in seeds:
                context = make_natural_context(seed, split)
                forms = length_normal_forms(context)
                self.assertNotEqual(forms[context["seed"]["source"]], forms[context["seed"]["target"]], context["id"])
                self.assertEqual(len({(g["source"], g["target"]) for g in context["goals"]}), 20)
                positions = {node["id"]: index for index, node in enumerate(context["nodes"])}
                self.assertTrue(all(positions[g["target"]] - positions[g["source"]] >= 6 for g in context["goals"]))
                forbidden = {(forms[g["source"]], forms[g["target"]]) for g in context["goals"]}
                for candidate in generate_candidates(context):
                    pair = forms[candidate["source"]], forms[candidate["target"]]
                    self.assertNotIn(pair, forbidden)
                    self.assertNotEqual(*pair)

    def test_distinct_policy_witnesses_are_preserved_once(self):
        context = make_example()
        a = discover(context, method="graph")
        b = discover(context, method="random", random_seed=7)
        combined, count = _combined_run([a, b, a])
        expected = {(goal["source"], goal["target"], tuple(goal[variant]["path"]))
                    for run in (a, b) for goal in run["goals"] for variant in ("baseline", "augmented")
                    if goal[variant]["solved"]}
        self.assertEqual(count, len(expected))
        actual = {(goal["source"], goal["target"], tuple(goal["baseline"]["path"])) for goal in combined["goals"]}
        self.assertEqual(actual, expected)
        self.assertEqual(len(combined["candidates"]), len(a["candidates"]))

    def test_outcome_digest_covers_results_but_not_clocks_or_certificate_paths(self):
        report = {"records": [{"marginal_solved": 2, "ranking_and_search_seconds": 1.5}],
                  "formal_verification": {"status": "kernel_verified", "elapsed_seconds": 10,
                                          "contexts": [{"source": "proofs/a.lean", "source_sha256": "abc", "elapsed_seconds": 2}]},
                  "automation_control": {"status": "kernel_verified", "solved": 5, "elapsed_seconds": 2},
                  "elapsed_seconds": 40}
        digest = _freeze_digest(report)
        changed = copy.deepcopy(report)
        changed["elapsed_seconds"] = 100
        changed["records"][0]["ranking_and_search_seconds"] = 200
        changed["formal_verification"]["contexts"][0].update(source="somewhere/b.lean", elapsed_seconds=999)
        self.assertEqual(digest, _freeze_digest(changed))
        changed["records"][0]["marginal_solved"] = 3
        self.assertNotEqual(digest, _freeze_digest(changed))
        changed = copy.deepcopy(report)
        changed["automation_control"]["status"] = "failed"
        self.assertNotEqual(digest, _freeze_digest(changed))

    def test_failed_automation_source_cannot_be_promoted_by_partial_audits(self):
        fake = {"status": "failed", "audits": [{"name": "automation_goal_0", "axioms": [], "constants": []}],
                "log": "bad", "source_sha256": "abc", "elapsed_seconds": 0.1}
        with tempfile.TemporaryDirectory() as folder, patch("proofripple.natural_benchmark.verify_source", return_value=fake):
            control = _automation(Path(folder), True)
        self.assertEqual(control["status"], "failed")
        self.assertEqual(control["solved"], 0)

    def test_statement_cleaning_is_label_free_and_retains_empty_contexts(self):
        train = make_example()
        train["id"] = "train_fixture"
        meaningful = copy.deepcopy(train["goals"][0])
        train["goals"] = [{"id": "identity", "source": "p0", "target": "p0"},
                          {"id": "own_fact", "source": "p0", "target": "p1"},
                          meaningful, {**meaningful, "id": "duplicate"}]
        validation = copy.deepcopy(train)
        validation["id"] = "validation_fixture"
        test = copy.deepcopy(train)
        test["id"] = "test_fixture"
        raw = {"train": [train], "validation": [validation], "test": [test]}
        preserved = copy.deepcopy(raw)
        with patch("proofripple.engine.search", side_effect=AssertionError("Cleaning must not inspect solve outcomes")):
            cleaned, summary, audit = _prepare_splits(raw)
        self.assertEqual(raw, preserved)
        self.assertEqual(len(cleaned["train"][0]["goals"]), 1)
        self.assertEqual(cleaned["validation"][0]["goals"], [])
        self.assertEqual(cleaned["test"][0]["goals"], [])
        self.assertEqual(len(cleaned["test"]), 1)
        self.assertEqual(summary["train"]["removed_reason_counts"]["removed_identity"], 1)
        self.assertEqual(summary["train"]["removed_reason_counts"]["removed_own_baseline_equivalent"], 1)
        self.assertEqual(summary["train"]["removed_reason_counts"]["removed_duplicate_normalized_pair"], 1)
        self.assertEqual(summary["test"]["active_goal_contexts"], 0)
        self.assertEqual(audit["test_goal_overlap_all_prior_index"], 0)
        self.assertEqual(audit["retained_goal_overlap_own_baseline_facts"], 0)


class NaturalBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = tempfile.TemporaryDirectory(prefix="proofripple-natural-benchmark-test-")
        cls.report = run_natural_benchmark(cls.folder.name, quick=True, certify=False)

    @classmethod
    def tearDownClass(cls):
        cls.folder.cleanup()

    def test_real_model_training_and_baselines_use_identical_budgets(self):
        report = self.report
        self.assertEqual(set(report["summary"]), set(NATURAL_METHODS))
        self.assertEqual(report["protocol"]["selection_budget"], 3)
        self.assertEqual(report["protocol"]["search_expansions_per_goal"], 8)
        self.assertTrue(all(len(row["selected"]) == min(3, row["candidate_count"]) for row in report["records"]))
        for context in {row["context_id"] for row in report["records"]}:
            self.assertEqual(len({row["selected_count"] for row in report["records"] if row["context_id"] == context}), 1)
        self.assertLessEqual(report["model_training"]["contexts"], 8)
        self.assertEqual(report["candidate_coverage"]["train"]["contexts"], 8)
        self.assertTrue(all(identifier.startswith("train_") for identifier in report["model_training"]["context_ids"]))
        self.assertGreater(report["model_training"]["examples"], 0)
        self.assertEqual(report["formal_verification"]["status"], "not_run")
        self.assertEqual(report["automation_control"]["status"], "not_run")
        for method, row in report["summary"].items():
            self.assertEqual(row["total_goals"], report["goal_cleaning"]["test"]["retained_registry_queries"])
            self.assertEqual(row["goals_per_context"], row["total_goals"] / row["contexts"])
        self.assertEqual(report["holdout_audit"]["test_goal_overlap_all_prior_index"], 0)
        self.assertEqual(report["holdout_audit"]["retained_goal_overlap_own_baseline_facts"], 0)
        self.assertEqual(report["automation_control"]["total"], len(make_example()["goals"]) + 1)

    def test_frozen_model_history_and_contexts_saved_without_test_fitting(self):
        out = Path(self.folder.name)
        model = json.loads((out / "model.json").read_text())
        structure = json.loads((out / "structure-model.json").read_text())
        contexts = json.loads((out / "contexts.json").read_text())
        self.assertEqual(len(model["feature_names"]), 32)
        self.assertEqual(model["training"]["context_ids"], structure["training"]["context_ids"])
        self.assertEqual(model["history"], self.report["model_history"])
        self.assertEqual(len(contexts["test"]), 4)
        self.assertIn("normalization.py", self.report["source_sha256"])
        self.assertTrue((out / "experiment-source" / "normalization.py").exists())
        self.assertEqual(self.report["candidate_coverage"]["test"]["contexts"], 4)
        self.assertEqual(len({row["sha256"] for row in self.report["contexts"]}), len(self.report["contexts"]))
        self.assertEqual(self.report["outcomes_sha256"], _freeze_digest(self.report))
        self.assertIn("not mathematical-domain", " ".join(self.report["limitations"]))
        self.assertTrue((out / "raw-contexts.json").exists())
        self.assertTrue((out / "holdout-audit.json").exists())


if __name__ == "__main__":
    unittest.main()
