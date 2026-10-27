import unittest
import json
from pathlib import Path
import tempfile
from unittest.mock import patch
from proofripple.cli import run_context, load_model
from proofripple.engine import discover


class InputContractTests(unittest.TestCase):
    def test_missing_model_retrains_the_frozen_cleaned_training_corpus(self):
        root = Path(__file__).resolve().parents[1]
        expected = json.loads((root / "artifacts/natural/model.json").read_text())
        contexts = json.loads((root / "artifacts/natural/contexts.json").read_text())
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            folder = base / "artifacts/natural"
            folder.mkdir(parents=True)
            (folder / "contexts.json").write_text(json.dumps(contexts))
            with patch("proofripple.cli.data_root", return_value=base):
                recovered = load_model("list-capacity")
        # Python 3.12 improved floating-point sum accuracy. Re-fitting on 3.10
        # can differ in the last few bits without changing the model's behavior.
        def compare(actual, recorded, path="model"):
            if isinstance(recorded, float):
                self.assertAlmostEqual(actual, recorded, delta=1e-10, msg=path)
            elif isinstance(recorded, dict):
                self.assertEqual(actual.keys(), recorded.keys(), path)
                for key in recorded:
                    compare(actual[key], recorded[key], path + "/" + key)
            elif isinstance(recorded, list):
                self.assertEqual(len(actual), len(recorded), path)
                for index, (a, b) in enumerate(zip(actual, recorded)):
                    compare(a, b, path + "/" + str(index))
            else:
                self.assertEqual(actual, recorded, path)
        compare(recovered, expected)
        for split in contexts.values():
            for context in split:
                before = discover(context, expected, 3, 8)
                after = discover(context, recovered, 3, 8)
                self.assertEqual(after["selected"], before["selected"], context["id"])
                self.assertEqual(after["metrics"], before["metrics"], context["id"])

    def test_nonobject_contexts_fail_cleanly_before_dispatch(self):
        for value in ([], None, "not a context", 0):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "JSON object"):
                run_context(value)


if __name__ == "__main__":
    unittest.main()
