from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
import sysconfig

from . import __version__
from .engine import METHODS, discover
from .lean import TOOLCHAIN, certify_run, import_lean, seed_source

MATHLIB_METHODS = ("learned", "learned_no_bonus", "learned_singleton", "structure_only", "random", "semantic", "graph", "proof_cost", "greedy_coverage", "branching_aware")


def data_root():
    repo = Path(__file__).resolve().parent.parent
    if (repo / "lab" / "index.html").is_file():
        return repo
    installed = Path(sysconfig.get_path("data")) / "share" / "proofripple"
    if (installed / "lab" / "index.html").is_file():
        return installed
    raise FileNotFoundError("Bundled LAB assets missing. Install the release wheel or run from the source checkout.")


def load_context(path):
    file = Path(path)
    if file.stat().st_size > 2_000_000:
        raise ValueError("Context exceeds 2 MB")
    return import_lean(file) if file.suffix == ".lean" else json.loads(file.read_text())


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


def save_run(run, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    if "lean_source" in run:
        (out / "ProofRipple.lean").write_text(run["lean_source"])
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description="ProofRipple · theorem consequences with auditable Lean evidence")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="Inspect free local runtime requirements")
    demo = commands.add_parser("demo", help="Discover and Lean-check the bundled example")
    demo.add_argument("--domain", choices=("mathlib", "lists", "implications"), default="lists")
    imp = commands.add_parser("discover", help="Import a supported JSON context or canonical Lean seed")
    imp.add_argument("input")
    for command in (demo, imp):
        command.add_argument("--out", default="outputs/run")
        command.add_argument("--budget", type=int, default=8)
        command.add_argument("--select", type=int, default=None)
        command.add_argument("--method", choices=tuple(dict.fromkeys((*METHODS, *MATHLIB_METHODS))), default=None)
        command.add_argument("--no-verify", action="store_true", help="Exploration only; all results stay proposed")
    export = commands.add_parser("export-seed", help="Create the supported canonical Lean theorem format")
    export.add_argument("input")
    export.add_argument("--out", required=True)
    bench = commands.add_parser("benchmark", help="Train and evaluate the frozen CPU experiment")
    bench.add_argument("--out", default="outputs/benchmark")
    bench.add_argument("--quick", action="store_true")
    bench.add_argument("--certify", action="store_true", help="Additionally Lean-check all test witnesses")
    bench.add_argument("--domain", choices=("mathlib", "lists", "implications"), default="lists")
    bench.add_argument("--frozen-protocol", help="Mathlib only: verify a saved protocol/data/source freeze before fitting")
    registered = commands.add_parser("import-declaration", help="Import an explicitly supported Lean core theorem")
    registered.add_argument("name", choices=("List.length_filter_le", "inf_sup_left"))
    registered.add_argument("--out", default="outputs/imported")
    lab = commands.add_parser("lab", help="Serve the local research workbench")
    lab.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)
    try:
        if args.command == "doctor":
            from .mathlib_runtime import runtime_info
            print(json.dumps({"version": __version__, "python": sys.version.split()[0], "lean": shutil.which("lean"), "required_toolchain": TOOLCHAIN, "assets": str(data_root()), "mathlib": runtime_info(), "paid_services": False}, indent=2))
        elif args.command in ("demo", "discover", "import-declaration"):
            if args.command == "import-declaration":
                if args.name == "inf_sup_left":
                    from .mathlib_benchmark import make_example
                else:
                    from .natural import make_example
                run = run_context(make_example())
                out = save_run(run, args.out)
                print(json.dumps({"imported_declaration": args.name, "verification": run["verification"]["status"], "output": str(out.resolve())}, indent=2))
                return 0 if run["verification"]["status"] == "kernel_verified" else 2
            if args.command == "demo" and args.domain == "mathlib":
                from .mathlib_benchmark import make_example
                context = make_example()
            else:
                filename = "list_capacity.json" if getattr(args, "domain", None) == "lists" else "invariants.json"
                path = data_root() / "examples" / filename if args.command == "demo" else args.input
                context = load_context(path)
            run = run_context(context, args.budget, args.select, not args.no_verify, args.method)
            out = save_run(run, args.out)
            status = run["verification"]["status"]
            print(json.dumps({"verification": status, "candidates": len(run["candidates"]), "metrics": run["metrics"], "output": str(out.resolve())}, indent=2))
            if not args.no_verify and status != "kernel_verified":
                print(run["verification"].get("log", ""), file=sys.stderr)
                return 2
        elif args.command == "export-seed":
            Path(args.out).write_text(seed_source(load_context(args.input)))
            print(args.out)
        elif args.command == "benchmark":
            if args.frozen_protocol and args.domain != "mathlib":
                raise ValueError("--frozen-protocol applies to the Mathlib benchmark")
            if args.domain == "mathlib":
                from .mathlib_benchmark import run_mathlib_benchmark
                report = run_mathlib_benchmark(args.out, args.quick, args.certify, frozen_dir=args.frozen_protocol)
            elif args.domain == "lists":
                from .natural_benchmark import run_natural_benchmark
                report = run_natural_benchmark(args.out, args.quick, args.certify)
            else:
                from .benchmark import run_benchmark
                report = run_benchmark(args.out, args.quick)
            if args.certify and args.domain == "implications":
                from .certification import certify_benchmark
                report = certify_benchmark(args.out)
                if report["formal_verification"]["status"] != "kernel_verified":
                    return 2
            if args.certify and report.get("formal_verification", {}).get("status") != "kernel_verified":
                return 2
            print(json.dumps(report["summary"], indent=2))
        elif args.command == "lab":
            from .server import serve
            serve(data_root(), args.port)
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(f"proofripple: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
