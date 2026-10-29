import copy
import gzip
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from proofripple.mathlib_benchmark import make_example
from scripts import mathlib_automation_control as control


def checked_result(source, names):
    return {"status": "kernel_verified", "source_sha256": control.sha256(source.encode()),
            "toolchain": control.TOOLCHAIN, "allowed_axioms": list(control.ALLOWED_AXIOMS),
            "library": {"revision": control.MATHLIB_REVISION}, "log": "synthetic check fixture",
            "elapsed_seconds": 0, "audits": [{"name": name, "type": "fixture type", "axioms": [],
                                              "constants": []} for name in names]}


class MathlibAutomationControlTests(unittest.TestCase):
    def test_only_preprocessing_guard_changes_source(self):
        original, repaired, names = control.repaired_source(make_example())
        self.assertEqual(repaired.replace(control.REPAIRED_PREPROCESS, control.ORIGINAL_PREPROCESS), original)
        self.assertEqual(repaired.count(control.REPAIRED_PREPROCESS), len(names))
        self.assertEqual(original.count("\n  aesop\n"), repaired.count("\n  aesop\n"))
        self.assertEqual([line for line in original.splitlines() if line.startswith("theorem ")],
                         [line for line in repaired.splitlines() if line.startswith("theorem ")])

    def test_unrecognized_builder_recipe_fails_closed(self):
        with patch.object(control, "build_automation_source", return_value=("theorem x := by aesop", ["x"])):
            with self.assertRaises(ValueError):
                control.repaired_source(make_example())

    def test_diagnostic_or_incomplete_or_admitted_audits_never_pass(self):
        source, names = "fixture", ["control_fixture"]
        good = checked_result(source, names)
        self.assertTrue(control.audit_is_valid(good, names, control.sha256(source.encode())))
        for change in ({"status": "failed"}, {"source_sha256": "forged"}, {"audits": []},
                       {"toolchain": "different"}, {"library": {"revision": "different"}}):
            bad = {**copy.deepcopy(good), **change}
            self.assertFalse(control.audit_is_valid(bad, names, control.sha256(source.encode())))
        for axiom in ("sorryAx", "customAxiom", "Lean.ofReduceBool"):
            bad = copy.deepcopy(good); bad["audits"][0]["axioms"] = [axiom]
            self.assertFalse(control.audit_is_valid(bad, names, control.sha256(source.encode())))
        bad = copy.deepcopy(good); bad["audits"][0]["constants"] = ["sorryAx"]
        self.assertFalse(control.audit_is_valid(bad, names, control.sha256(source.encode())))
        self.assertFalse(control.audit_is_valid(good, names, control.sha256(source.encode()), {names[0]: "different type"}))

    def test_existing_outputs_and_excess_concurrency_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "already exists"):
                control.run("missing corpus", directory)
            with self.assertRaisesRegex(ValueError, "two Lean"):
                control.run("missing corpus", Path(directory)/"new", jobs=3)

    def test_exact_frozen_corpus_and_sources_are_required(self):
        context = make_example(); context["id"] = "test_fixture"; context["metadata"]["split"] = "test"
        corpus = {"test": [context]}
        data = gzip.compress(json.dumps(corpus, sort_keys=True, separators=(",", ":")).encode(), mtime=0)
        freeze = {"corpus_sha256": {"contexts.json.gz": control.sha256(data)}, "data_sha256": control.canonical_hash(corpus),
                  "source_sha256": {name: control.sha256((control.ROOT/"proofripple"/name).read_bytes()) for name in control.CORE_NAMES},
                  "coverage_at_largest_k": {"test": {"contexts": 1, "goal_total": 1}}}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory); (path/"contexts.json.gz").write_bytes(data)
            (path/"source-freeze.json").write_text(json.dumps(freeze))
            loaded, provenance = control.load_frozen_contexts(path/"contexts.json.gz")
            self.assertEqual(loaded, [context]); self.assertEqual(provenance["all_test_goals"], 1)
            freeze["source_sha256"]["mathlib.py"] = "forged"
            (path/"source-freeze.json").write_text(json.dumps(freeze))
            with self.assertRaisesRegex(ValueError, "scientific sources"):
                control.load_frozen_contexts(path/"contexts.json.gz")

    def test_pilot_retains_exact_types_and_fixed_verifier_timeout(self):
        context = make_example()
        original, repaired, names = control.repaired_source(context)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory); old = path/"old"; old.mkdir()
            out = path/"fresh"; out.mkdir()
            for name in ("original-sources", "sources", "checks", "logs"):
                (out/name).mkdir()
            (old/(context["id"]+".lean")).write_text(original)
            (old/(context["id"]+".json")).write_text(json.dumps(checked_result(original, names)))
            with patch.object(control, "verify_mathlib_source", return_value=checked_result(repaired, names)) as verifier:
                row = control.check_context(context, out, old)
            verifier.assert_called_once_with(repaired, names, timeout=120)
            self.assertEqual(row["status"], "kernel_verified")
            self.assertTrue(row["original_audit_types_compared"])
            self.assertEqual(row["solved"], 1)
            self.assertEqual((out/"original-sources"/(context["id"]+".lean")).read_text(), original)


if __name__ == "__main__":
    unittest.main()
