import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from proofripple.engine import discover
from proofripple.lean import TOOLCHAIN
from proofripple.natural import (
    build_automation_baseline, build_natural_source, make_example,
    validate_natural_context, length_normal_forms,
)


class NaturalContextTests(unittest.TestCase):
    def test_normalized_pool_excludes_equivalent_goals_and_restatements(self):
        from proofripple.engine import generate_candidates
        context = make_example()
        forms = length_normal_forms(context)
        self.assertEqual(forms["p1"], forms["p2"])
        self.assertEqual(forms["p2"], forms["p3"])
        self.assertEqual(forms["p9"], forms["p11"])
        candidates = generate_candidates(context)
        pairs = [(forms[c["source"]], forms[c["target"]]) for c in candidates]
        goals = {(forms[g["source"]], forms[g["target"]]) for g in context["goals"]}
        self.assertEqual(len(pairs), len(set(pairs)))
        self.assertFalse(set(pairs) & goals)
        self.assertTrue(all(a != b for a, b in pairs))
        self.assertEqual(len(candidates), 3)

    def test_normalizer_keeps_inner_map_when_it_changes_filter_inputs(self):
        context = make_example()
        forms = length_normal_forms(context)
        self.assertNotEqual(forms["p1"], forms["p5"])
        modified = copy.deepcopy(context)
        modified["nodes"][4]["expression"]["op"] = "map"
        self.assertNotEqual(length_normal_forms(modified)["p5"], forms["p5"])

    def test_example_is_real_typed_ast_and_manifest_matches(self):
        context = make_example()
        self.assertEqual(validate_natural_context(context), context)
        self.assertEqual(context["domain"], "list-capacity")
        saved = Path(__file__).resolve().parents[1] / "examples" / "list_capacity.json"
        self.assertEqual(context, json.loads(saved.read_text()))
        self.assertEqual(context["nodes"][1]["expression"], {"op": "filter", "input": "p0"})

    def test_nonancestor_edges_are_rejected(self):
        context = make_example()
        context["edges"][0].update(source="p1", target="p0")
        with self.assertRaisesRegex(ValueError, "ancestor"):
            validate_natural_context(context)

    def test_forward_refs_unknown_operations_and_source_injection_rejected(self):
        for expression in ({"op": "filter", "input": "p11"},
                           {"op": "filter", "input": ["p0"]},
                           {"op": "filter\naxiom bad : False", "input": "p0"},
                           {"op": "filter", "input": "p0", "lean": "sorry"}):
            context = make_example()
            context["nodes"][1]["expression"] = expression
            with self.assertRaises(ValueError):
                validate_natural_context(context)

    def test_source_has_closed_primitives_and_ignores_supplied_proof_flags(self):
        run = discover(make_example(), method="graph")
        run["verification"] = {"status": "kernel_verified"}
        run["seed"]["proof"] = "axiom bad : False"
        run["candidates"][0]["proof"] = "run_cmd IO.println 999"
        source, names, metadata = build_natural_source(run)
        self.assertIn("List Nat", source)
        self.assertIn("List.length_filter_le", names)
        self.assertIn("theorem pr_h0", source)
        self.assertNotIn("h_h0 :", source)
        self.assertNotIn(": Prop", source)
        self.assertNotIn("axiom bad", source)
        self.assertNotIn("IO.println", source)
        self.assertEqual(metadata["allowed_axioms"], ["propext"])
        self.assertTrue(all(not rule["discovered"] for rule in metadata["registered_templates"]))

    def test_forged_candidate_identifiers_and_noncomposable_witness_rejected(self):
        run = discover(make_example(), method="graph")
        bad = copy.deepcopy(run)
        bad["candidates"][0]["id"] = "bad\naxiom exploit : False"
        with self.assertRaises(ValueError):
            build_natural_source(bad)
        bad = copy.deepcopy(run)
        bad["candidates"][0]["path"] = ["h0", "h9"]
        with self.assertRaises(ValueError):
            build_natural_source(bad)

    def test_automation_baseline_omits_discovered_library(self):
        context = make_example()
        source, names = build_automation_baseline(context)
        self.assertEqual(len(names), len(context["goals"]) + 1)
        self.assertIn("grind (gen := 32)", source)
        self.assertNotIn("theorem pr_h0", source)
        self.assertNotIn("pr_breakthrough", source)
        self.assertNotIn("pr_ripple_", source)
        self.assertNotIn("prx_step_", source)
        with self.assertRaises(ValueError):
            build_automation_baseline(context, generation="32); sorry")

    def test_downstream_declaration_ids_avoid_legal_primitive_collisions(self):
        context = make_example()
        context["edges"][0]["id"] = "goal_1_augmented"
        run = discover(context, method="graph", k=1)
        source, names, metadata = build_natural_source(run)
        self.assertIn("pr_goal_1_augmented", names)
        self.assertIn("pr_goal_1_augmented_proof1", names)
        self.assertEqual(len(names), len(set(names)))
        self.assertIn("theorem pr_goal_1_augmented_proof1", source)


@unittest.skipUnless(shutil.which("lean"), "Pinned Lean required for kernel checks")
class NaturalKernelTests(unittest.TestCase):
    def _compile(self, source, names, allowed):
        env = os.environ.copy()
        env["ELAN_TOOLCHAIN"] = TOOLCHAIN
        with tempfile.TemporaryDirectory(prefix="proofripple-natural-test-") as folder:
            path = Path(folder) / "Natural.lean"
            path.write_text(source)
            process = subprocess.run([shutil.which("lean"), "--json", "-j", "1", "-M", "2048",
                                      "-DmaxHeartbeats=400000", str(path)],
                                     env=env, cwd=folder, text=True, capture_output=True, timeout=60)
        messages = []
        for line in process.stdout.splitlines():
            try:
                messages.append(json.loads(line))
            except json.JSONDecodeError:
                pass
        errors = [message for message in messages if message.get("severity") == "error"]
        self.assertEqual(process.returncode, 0, str(errors)[:2000])
        self.assertFalse(errors)
        audits = [json.loads(m["data"].split(" ", 1)[1]) for m in messages
                  if m.get("data", "").startswith("PROOFRIPPLE_AUDIT ")]
        self.assertEqual(set(names), {a["name"] for a in audits})
        self.assertEqual(len(names), len(audits))
        for audit in audits:
            self.assertLessEqual(set(audit["axioms"]), allowed)
            self.assertNotIn("sorryAx", audit["constants"])
        return {a["name"]: a for a in audits}

    def test_all_concrete_consequences_and_imported_seed_kernel_check(self):
        run = discover(make_example(), method="graph")
        source, names, metadata = build_natural_source(run)
        audits = self._compile(source, names, {"propext"})
        imported = audits[metadata["imported_seed"]["audit_name"]]
        self.assertIn("List.filter", imported["type"])
        self.assertIn("List.rec", imported["constants"])
        self.assertIn("Nat.le_trans", imported["constants"])
        for candidate in run["candidates"]:
            audit = audits["pr_" + candidate["id"]]
            self.assertIn("List Nat", audit["type"])
            self.assertIn("pr_breakthrough", audit["constants"])
        downstream = audits["prx_combined_buffer_safe"]
        self.assertIn("prx_paired_budget", downstream["constants"])

    def test_general_automation_solves_same_goals_without_discovered_lemmas(self):
        source, names = build_automation_baseline(make_example())
        audits = self._compile(source, names, {"propext", "Classical.choice", "Quot.sound"})
        self.assertEqual(len(audits), 3)
        self.assertTrue(all("List Nat" in audit["type"] for audit in audits.values()))


if __name__ == "__main__":
    unittest.main()
