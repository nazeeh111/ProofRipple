import copy
import unittest

from proofripple.benchmark import make_context
from proofripple.engine import generate_candidates, select_candidates
from proofripple.model import predict, train_model


class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contexts = [make_context(i, "train") for i in (1000, 1001, 1002)]
        cls.model = train_model(cls.contexts, members=3)

    def test_trained_weights_and_disagreement_are_real_and_reproducible(self):
        self.assertEqual(self.model, train_model(self.contexts, members=3))
        self.assertGreater(self.model["training"]["examples"], 0)
        self.assertGreater(self.model["training"]["positive_labels"], 0)
        self.assertTrue(any(abs(w) > 1e-6 for row in self.model["weights"] for w in row[1:]))
        c = make_context(3000, "test")
        candidate = generate_candidates(c)[0]
        mean, uncertainty = predict(self.model, candidate["features"])
        self.assertIsInstance(mean, float)
        self.assertGreaterEqual(uncertainty, 0)

    def test_test_outcomes_do_not_enter_ranker(self):
        c = make_context(3000, "test")
        candidates = generate_candidates(c)
        selected = select_candidates(c, candidates, c["goals"], model=self.model)
        poisoned = copy.deepcopy(c)
        for goal in poisoned["goals"]:
            goal["solved"] = True
            goal["marginal_solved"] = 1_000_000
            goal["proof"] = "cheat"
        selected_again = select_candidates(poisoned, generate_candidates(poisoned), poisoned["goals"], model=self.model)
        self.assertEqual([x["id"] for x in selected], [x["id"] for x in selected_again])
        self.assertTrue(all(cid.startswith("train_") for cid in self.model["training"]["context_ids"]))

    def test_methods_receive_identical_selection_count(self):
        c = make_context(3000, "test")
        candidates = generate_candidates(c)
        for method in ("learned", "random", "semantic", "graph", "proof_cost"):
            selected = select_candidates(c, candidates, c["goals"], k=3, method=method, model=self.model)
            self.assertEqual(len(selected), 3)
            self.assertEqual(len({x["id"] for x in selected}), 3)


if __name__ == "__main__":
    unittest.main()
