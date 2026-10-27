import unittest
import json
from pathlib import Path
import tempfile
from unittest.mock import patch
from proofripple.cli import run_context, load_model


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
        self.assertEqual(recovered, expected)

    def test_nonobject_contexts_fail_cleanly_before_dispatch(self):
        for value in ([], None, "not a context", 0):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "JSON object"):
                run_context(value)


if __name__ == "__main__":
    unittest.main()
