import json
from pathlib import Path
import shutil
import tempfile
import unittest

from proofripple.engine import discover
from proofripple.lean import certify_run, import_lean, seed_source
from proofripple.natural import make_example


class NaturalImportTests(unittest.TestCase):
    def test_canonical_list_theorem_round_trip_does_not_become_arbitrary_props(self):
        context = make_example()
        text = seed_source(context)
        self.assertIn("List Nat", text)
        self.assertNotIn(": Prop", text)
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "Seed.lean"
            file.write_text(text)
            self.assertEqual(import_lean(file), context)
            file.write_text(text + '\n#eval IO.println "untrusted"\n')
            with self.assertRaisesRegex(ValueError, "Non-canonical"):
                import_lean(file)

    @unittest.skipUnless(shutil.which("lean"), "Pinned Lean required")
    def test_certification_imports_real_statement_and_records_domain_policy(self):
        run = discover(make_example(), k=1, method="graph")
        run["seed"]["proof"] = "by sorry"
        checked = certify_run(run)
        self.assertEqual(checked["verification"]["status"], "kernel_verified", checked["verification"]["log"])
        self.assertEqual(checked["verification"]["allowed_axioms"], ["propext"])
        imported = checked["natural_domain"]["imported_seed"]
        self.assertIn("List.filter", imported["statement"])
        self.assertEqual(imported["axioms"], ["propext"])
        self.assertTrue(all(isinstance(c["explanation"], str) for c in checked["candidates"]))
        self.assertEqual(checked["metrics"]["baseline_solved"], 0)
        self.assertEqual(checked["metrics"]["augmented_solved"], 1)
        self.assertNotIn("implication hypotheses", json.dumps(checked["timeline"]))


if __name__ == "__main__":
    unittest.main()
