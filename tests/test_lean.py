import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from proofripple.lean import _audit, build_source, certify_run, import_lean, seed_source, verify_source
from proofripple.engine import discover

ROOT = Path(__file__).resolve().parents[1]


class ImportBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.context = json.loads((ROOT / "examples/invariants.json").read_text())

    def test_supported_theorem_round_trip_and_command_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "Seed.lean"
            file.write_text(seed_source(self.context))
            self.assertEqual(import_lean(file), self.context)
            file.write_text(file.read_text() + '\n#eval IO.println "untrusted"\n')
            with self.assertRaisesRegex(ValueError, "Non-canonical"):
                import_lean(file)

    def test_witness_tampering_fails_before_lean(self):
        bad = copy.deepcopy(self.context["seed"])
        bad["id"] = "wrong"
        bad["path"] = list(reversed(bad["path"]))
        with self.assertRaisesRegex(ValueError, "Non-composable"):
            build_source(self.context, [bad])

    def test_missing_lean_cannot_verify(self):
        result = verify_source("", [], lean_bin="/nonexistent/proofripple-lean")
        self.assertEqual(result["status"], "unavailable")

    def test_reflexive_goals_have_valid_identity_proof(self):
        source = build_source(self.context, goals=[{"id": "identity", "source": "p0", "target": "p0", "path": []}])
        self.assertIn("fun hx => hx", source)

    def test_candidate_id_collisions_remain_exportable(self):
        from proofripple.engine import generate_candidates
        context = {"nodes": [{"id": n} for n in "ABCD"], "edges": [
            {"id": "h0", "source": "A", "target": "B"}, {"id": "h1", "source": "B", "target": "C"},
            {"id": "h2", "source": "C", "target": "D"}, {"id": "ripple_A_D", "source": "D", "target": "A"},
            {"id": "ripple_A_D_consequence", "source": "D", "target": "B"}],
            "seed": {"id": "seed", "source": "B", "target": "D", "path": ["h1", "h2"]}}
        candidates = generate_candidates(context)
        used = {e["id"] for e in context["edges"]}
        self.assertFalse(used & {c["id"] for c in candidates})
        build_source(context, candidates)


@unittest.skipUnless(shutil.which("lean"), "Pinned Lean runtime not installed")
class KernelTests(unittest.TestCase):
    def test_foundational_allowlist_is_explicit_and_cannot_allow_custom_axioms(self):
        source = ("import Lean\nopen Lean Elab Command\n"
                  "theorem extensional (P Q : Prop) (h : P ↔ Q) : P = Q := propext h\n" + _audit("extensional"))
        strict = verify_source(source, ["extensional"])
        self.assertEqual(strict["status"], "failed")
        permissive = verify_source(source, ["extensional"], allowed_axioms=("propext",))
        self.assertEqual(permissive["status"], "kernel_verified")
        self.assertEqual(permissive["audits"][0]["axioms"], ["propext"])
        with self.assertRaisesRegex(ValueError, "foundational"):
            verify_source(source, ["extensional"], allowed_axioms=("customLie",))

    def test_admitted_and_custom_axiom_proofs_rejected(self):
        source = ("import Lean\nopen Lean Elab Command\n"
                  "axiom customLie : False\n"
                  "theorem poisoned : False := customLie\n"
                  "theorem admitted : False := by sorry\n" + _audit("poisoned") + _audit("admitted"))
        result = verify_source(source, ["poisoned", "admitted"])
        self.assertEqual(result["status"], "failed")
        audits = {a["name"]: a for a in result["audits"]}
        self.assertIn("customLie", audits["poisoned"]["axioms"])
        self.assertIn("sorryAx", audits["admitted"]["axioms"])

    def test_forged_status_and_proof_rebuilt_with_real_kernel_audit(self):
        context = json.loads((ROOT / "examples/invariants.json").read_text())
        # k=0 still verifies generated candidates and baseline witnesses.
        run = discover(context, k=0)
        run["verification"] = {"status": "kernel_verified"}
        run["seed"].update(source="p0", target="p1", path=["h0"])
        run["context_sha256"] = "forged"
        for candidate in run["candidates"]:
            candidate.update(status="kernel_verified", proof="by sorry", axioms=[])
        checked = certify_run(run)
        self.assertEqual(checked["verification"]["status"], "kernel_verified", checked["verification"]["log"])
        self.assertTrue(all(c["axioms"] == [] and "sorry" not in c["proof"] for c in checked["candidates"]))
        self.assertTrue(any("pr_breakthrough" in c["dependencies"] for c in checked["candidates"]))
        self.assertEqual(checked["seed"], {**checked["seed"], **context["seed"]})
        self.assertNotEqual(checked["context_sha256"], "forged")

    def test_invalid_proof_and_missing_audit_fail_closed(self):
        source = "import Lean\nopen Lean Elab Command\ntheorem wrong : False := True.intro\n" + _audit("wrong")
        self.assertEqual(verify_source(source, ["wrong"])["status"], "failed")
        self.assertEqual(verify_source("import Lean\n", ["missing"])["status"], "failed")


if __name__ == "__main__":
    unittest.main()
