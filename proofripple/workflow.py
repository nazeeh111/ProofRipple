"""Shared context execution and frozen-model policy for CLI and LAB callers."""
from __future__ import annotations

import json
from pathlib import Path
import sysconfig

from .engine import discover
from .lean import certify_run

MATHLIB_METHODS = ("learned", "learned_no_bonus", "learned_singleton", "structure_only", "random", "semantic", "graph", "proof_cost", "greedy_coverage", "branching_aware")


def data_root():
    repo = Path(__file__).resolve().parent.parent
    if (repo / "lab" / "index.html").is_file():
        return repo
    installed = Path(sysconfig.get_path("data")) / "share" / "proofripple"
    if (installed / "lab" / "index.html").is_file():
        return installed
    raise FileNotFoundError("Bundled LAB assets missing. Install the release wheel or run from the source checkout.")


def load_model(domain=None):
    folder = data_root() / "artifacts"
    if domain == "mathlib-set-lattice":
        file = folder / "mathlib/model.json"
        if not file.is_file():
            raise ValueError("The frozen Mathlib usefulness model is missing; run the benchmark or choose a heuristic policy")
        return json.loads(file.read_text())
    file = folder / "natural" / "model.json" if domain == "list-capacity" else folder / "model.json"
    if file.is_file():
        return json.loads(file.read_text())
    if domain == "list-capacity":
        from .natural_model import train_natural_model
        contexts_file = folder / "natural" / "contexts.json"
        if contexts_file.is_file():
            train = json.loads(contexts_file.read_text())["train"]
        else:
            from .natural_benchmark import make_natural_context, _prepare_splits
            raw = {"train": [make_natural_context(seed, "train") for seed in range(1000, 1016)],
                   "validation": [make_natural_context(seed, "validation") for seed in range(2000, 2006)],
                   "test": [make_natural_context(seed, "test") for seed in range(3000, 3012)]}
            train = _prepare_splits(raw)[0]["train"]
        return train_natural_model(train)
    return None


def run_context(context, budget=8, select=None, verify=True, method=None):
    if not isinstance(context, dict):
        raise ValueError("Context must be a JSON object")
    natural = context.get("domain") == "list-capacity"
    mathlib = context.get("domain") == "mathlib-set-lattice"
    if select is None:
        select = 1 if natural else 3
    if method is None:
        method = "greedy_coverage" if mathlib else "graph" if natural else "learned"
    if not isinstance(budget, int) or isinstance(budget, bool) or not 1 <= budget <= 128:
        raise ValueError("Search expansion budget must be 1..128")
    if not isinstance(select, int) or isinstance(select, bool) or not 0 <= select <= 16:
        raise ValueError("Selected consequence budget must be 0..16")
    if mathlib:
        from .mathlib import certify_mathlib_run, validate_context
        from .mathlib_search import discover as discover_mathlib
        validate_context(context)
        model = load_model(context["domain"]) if method in {"learned", "learned_no_bonus", "learned_singleton", "structure_only"} else None
        run = discover_mathlib(context, model=model, k=select, search_budget=budget, method=method)
        return certify_mathlib_run(run) if verify else run
    if context.get("domain") == "list-capacity":
        from .natural import validate_natural_context
        validate_natural_context(context)
    model = load_model(context.get("domain")) if method == "learned" else None
    run = discover(context, model=model, k=select, search_budget=budget, method=method)
    return certify_run(run) if verify else run
