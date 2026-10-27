import random
import shutil
from pathlib import Path
import unittest

from proofripple.normalization import canonical_expressions, length_normal_forms


def stages(operations):
    return {"nodes": [{"id": "p0", "expression": {"op": "input"}}] + [
        {"id": f"p{i}", "expression": {"op": operation, "input": f"p{i-1}"}}
        for i, operation in enumerate(operations, 1)]}


class NormalizationTests(unittest.TestCase):
    def test_filter_fact_survives_reverse_take_but_not_map(self):
        forms = canonical_expressions(stages(["filter", "reverse", "take", "filter"]))
        self.assertEqual(forms["p3"], forms["p4"])
        forms = canonical_expressions(stages(["filter", "map", "filter"]))
        self.assertNotEqual(forms["p2"], forms["p3"])

    def test_filter_reverse_commutes_and_reverse_reverse_cancels(self):
        forms = canonical_expressions(stages(["reverse", "filter", "reverse"]))
        self.assertEqual(forms["p3"], ("filter", ("input", "xs")))
        forms = canonical_expressions(stages(["map", "reverse", "reverse"]))
        self.assertEqual(forms["p1"], forms["p3"])

    def test_take_is_identity_after_any_nonexpansive_pipeline_bounded_by_k(self):
        forms = canonical_expressions(stages(["take", "reverse", "map", "filter", "take"]))
        self.assertEqual(forms["p4"], forms["p5"])
        forms = canonical_expressions(stages(["map", "take", "take"]))
        self.assertEqual(forms["p2"], forms["p3"])

    def test_map_commutes_with_reverse_and_take(self):
        a = canonical_expressions(stages(["reverse", "map"]))["p2"]
        b = canonical_expressions(stages(["map", "reverse"]))["p2"]
        self.assertEqual(a, b)
        a = canonical_expressions(stages(["take", "map"]))["p2"]
        b = canonical_expressions(stages(["map", "take"]))["p2"]
        self.assertEqual(a, b)

    def test_inner_maps_and_take_reverse_order_remain_distinguishable(self):
        a = length_normal_forms(stages(["filter"]))["p1"]
        b = length_normal_forms(stages(["map", "filter"]))["p2"]
        self.assertNotEqual(a, b)
        a = canonical_expressions(stages(["take", "reverse"]))["p2"]
        b = canonical_expressions(stages(["reverse", "take"]))["p2"]
        self.assertNotEqual(a, b)

    def test_actual_held_out_equivalence_reproductions(self):
        from proofripple.natural_benchmark import make_natural_context
        forms = length_normal_forms(make_natural_context(3000, "test"))
        self.assertEqual(forms["p10"], forms["p27"])
        self.assertEqual(forms["p4"], forms["p29"])
        forms = length_normal_forms(make_natural_context(3001, "test"))
        self.assertEqual(forms["p20"], forms["p30"])

    def test_malformed_input_rejected(self):
        for context in ([], {"nodes": []}, {"nodes": [{"id": "p0", "expression": {"op": "filter", "input": "p1"}}]}):
            with self.assertRaises(ValueError):
                canonical_expressions(context)

    def test_normalization_preserves_actual_lists_across_varied_parameters(self):
        # A separate concrete interpreter checks the algorithm, including
        # conditional deletions. Predicate/function/limit vary independently.
        rng = random.Random(601311)
        for _ in range(400):
            operations = [rng.choice(("filter", "map", "reverse", "take"))
                          for _ in range(rng.randrange(1, 35))]
            context = stages(operations)
            canonical = canonical_expressions(context)[f"p{len(operations)}"]
            xs = [rng.randrange(8) for _ in range(rng.randrange(16))]
            passing = {value for value in range(8) if rng.randrange(2)}
            mapping = [rng.randrange(8) for _ in range(8)]
            k = rng.randrange(20)

            def apply(operation, values):
                if operation == "filter":
                    return [value for value in values if value in passing]
                if operation == "map":
                    return [mapping[value] for value in values]
                if operation == "reverse":
                    return values[::-1]
                return values[:k]

            def evaluate(expression):
                return xs if expression[0] == "input" else apply(
                    expression[0], evaluate(expression[1]))

            actual = xs
            for operation in operations:
                actual = apply(operation, actual)
            self.assertEqual(actual, evaluate(canonical), (operations, xs, k))


@unittest.skipUnless(shutil.which("lean"), "Pinned Lean required")
class NormalizationRuleKernelTests(unittest.TestCase):
    def test_registered_generic_rewrite_rules_are_kernel_verified(self):
        from proofripple.lean import verify_source
        source = (Path(__file__).resolve().parents[1] / "examples" / "NormalizationRules.lean").read_text()
        names = ["norm_" + name for name in (
            "all_filter", "all_reverse", "all_take", "filter_identity",
            "within_filter", "within_map", "within_reverse", "within_take",
            "take_identity", "reverse_reverse", "filter_reverse", "map_reverse", "map_take")]
        result = verify_source(source, names, allowed_axioms=("propext",))
        self.assertEqual(result["status"], "kernel_verified", result["log"])
        self.assertEqual(len(result["audits"]), 13)


if __name__ == "__main__":
    unittest.main()
