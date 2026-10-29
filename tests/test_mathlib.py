import copy
import itertools
import random
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from proofripple.mathlib import (
    DOMAIN, build_mathlib_source, certify_mathlib_run, infer_proof,
    normal_form, semantic_le, statement_key, validate_context, validate_term,
)
from proofripple.mathlib_runtime import runtime_info, verify_mathlib_source


def variable(index):
    return {"op": "var", "index": index}


def operation(op, left, right):
    return {"op": op, "left": left, "right": right}


def witness(rule, source, target, *children, **extra):
    return {"rule": rule, "source": source, "target": target, "children": list(children), **extra}


def example_run():
    a, b, c, d = map(variable, range(4))
    ab, ac = operation("meet", a, b), operation("meet", a, c)
    source = operation("meet", a, operation("join", b, c))
    middle, target = operation("join", ab, ac), operation("join", ab, c)
    seed = witness("seed", source, middle)
    weaker = witness("sup_mono", middle, target, witness("refl", ab, ab), witness("inf_right", ac, c))
    candidate = {"id": "c0", "source": source, "target": target, "proof": witness("trans", source, target, seed, weaker)}
    gs, gt = operation("join", source, d), operation("join", target, d)
    proof = witness("sup_mono", gs, gt, witness("lemma", source, target, lemma_id="c0"), witness("refl", d, d))
    goal = {"id": "goal0", "source": gs, "target": gt}
    context = {"id": "formal_test", "domain": DOMAIN, "variables": 6,
               "seed": {"id": "distributivity", "declaration": "inf_sup_left"},
               "candidates": [candidate], "goals": [goal]}
    return {"context": context, "candidates": [copy.deepcopy(candidate)], "selected": ["c0"],
            "goals": [{**goal, "baseline": {"solved": False}, "augmented": {"solved": True, "proof": proof}}]}


class MathlibClosedAdapterTests(unittest.TestCase):
    def test_binary_tree_is_checked_and_rendered(self):
        run = example_run()
        validate_context(run["context"])
        source, names, metadata = build_mathlib_source(run)
        self.assertIn("sup_le_sup", source)
        self.assertIn("pr_distributivity", source)
        self.assertIn("pr_goal_0_augmented", names)
        self.assertEqual(metadata["imported_seed"]["name"], "inf_sup_left")

    def test_tampered_rule_and_unselected_dependency_fail_closed(self):
        run = example_run()
        bad = copy.deepcopy(run["context"]["candidates"][0]["proof"])
        bad["children"][1]["children"][1]["rule"] = "inf_left"
        with self.assertRaises(ValueError):
            infer_proof(bad)
        run["selected"] = []
        with self.assertRaisesRegex(ValueError, "lemma"):
            build_mathlib_source(run)

    def test_context_cannot_execute_source_or_certify_a_different_workload(self):
        with self.assertRaises(ValueError):
            validate_term({"op": "var", "index": "0; run_cmd"})
        run = example_run()
        run["goals"][0]["source"] = variable(0)
        with self.assertRaisesRegex(ValueError, "workload"):
            build_mathlib_source(run)
        for bad in (None, [], "seed"):
            run = example_run()
            run["context"]["seed"] = bad
            with self.assertRaises(ValueError):
                validate_context(run["context"])

    def test_goal_declaration_collision_keeps_both_checked_proofs(self):
        run = example_run()
        for item in (run["context"]["candidates"][0], run["candidates"][0]):
            item["id"] = "goal_0_augmented"
        run["selected"] = ["goal_0_augmented"]
        run["goals"][0]["augmented"]["proof"]["children"][0]["lemma_id"] = "goal_0_augmented"
        source, names, metadata = build_mathlib_source(run)
        self.assertIn("pr_goal_0_augmented", names)
        self.assertIn("pr_goal_0_augmented_1", names)
        self.assertEqual(len(names), len(set(names)))

    def test_unavailable_library_is_not_a_verified_result(self):
        with patch("proofripple.mathlib_runtime.runtime_info", return_value={"available": False, "error": "missing pinned runtime"}):
            result = verify_mathlib_source("invalid source", [])
        self.assertEqual(result["status"], "unavailable")
        self.assertEqual(result["audits"], [])

    def test_canonical_mathlib_import_rejects_appended_commands(self):
        from proofripple.lean import import_lean, seed_source
        context = example_run()["context"]
        source = seed_source(context)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "Context.lean"
            path.write_text(source)
            self.assertEqual(import_lean(path), context)
            path.write_text(source + '\nrun_cmd logInfo "injected"\n')
            with self.assertRaisesRegex(ValueError, "Non-canonical"):
                import_lean(path)

    def test_dnf_is_equivalent_on_every_boolean_assignment(self):
        rng = random.Random(703)
        def term(depth):
            if not depth or rng.random() < .25:
                return variable(rng.randrange(6))
            return operation(rng.choice(("join", "meet")), term(depth - 1), term(depth - 1))
        def evaluate(t, mask):
            if t["op"] == "var":
                return bool(mask & (1 << t["index"]))
            a, b = evaluate(t["left"], mask), evaluate(t["right"], mask)
            return a or b if t["op"] == "join" else a and b
        for _ in range(100):
            t = term(4)
            dnf = normal_form(t)
            for mask in range(64):
                self.assertEqual(evaluate(t, mask), any(clause & mask == clause for clause in dnf))

    def test_joint_alpha_key_preserves_renamings_and_endpoint_direction(self):
        run = example_run()
        source, target = run["candidates"][0]["source"], run["candidates"][0]["target"]
        key = statement_key(source, target)
        def rename(t, permutation):
            if t["op"] == "var":
                return variable(permutation[t["index"]])
            return operation(t["op"], rename(t["left"], permutation), rename(t["right"], permutation))
        for permutation in itertools.permutations(range(4)):
            self.assertEqual(key, statement_key(rename(source, permutation), rename(target, permutation)))
        self.assertNotEqual(key, statement_key(target, source))
        self.assertTrue(semantic_le(source, target))
        self.assertFalse(semantic_le(target, source))


@unittest.skipUnless(runtime_info()["available"], "Optional pinned Mathlib runtime required")
class MathlibKernelTests(unittest.TestCase):
    def test_actual_binary_mathlib_proof_and_seed_dependency(self):
        original = example_run()
        original["context_sha256"] = "forged"
        run = certify_mathlib_run(original)
        from proofripple.engine import context_hash
        self.assertEqual(run["context_sha256"], context_hash(run["context"]))
        self.assertEqual(run["verification"]["status"], "kernel_verified", run["verification"]["log"][-3000:])
        candidate = run["candidates"][0]
        self.assertIn("pr_distributivity", candidate["dependencies"])
        audits = {item["name"]: item for item in run["verification"]["audits"]}
        self.assertIn("pr_c0", audits["pr_goal_0_augmented"]["constants"])
        self.assertTrue(set(candidate["axioms"]).issubset({"propext", "Classical.choice", "Quot.sound"}))


if __name__ == "__main__":
    unittest.main()
