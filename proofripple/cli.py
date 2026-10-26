from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
import sysconfig

from . import __version__
from .engine import discover
from .lean import TOOLCHAIN, certify_run, import_lean, seed_source


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


def load_model():
    file = data_root() / "artifacts" / "model.json"
    return json.loads(file.read_text()) if file.is_file() else None


def run_context(context, budget=8, select=3, verify=True):
    if not isinstance(budget, int) or isinstance(budget, bool) or not 1 <= budget <= 128:
        raise ValueError("Search expansion budget must be 1..128")
    if not isinstance(select, int) or isinstance(select, bool) or not 0 <= select <= 16:
        raise ValueError("Selected consequence budget must be 0..16")
    run = discover(context, model=load_model(), k=select, search_budget=budget)
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
    imp = commands.add_parser("discover", help="Import a supported JSON context or canonical Lean seed")
    imp.add_argument("input")
    for command in (demo, imp):
        command.add_argument("--out", default="outputs/run")
        command.add_argument("--budget", type=int, default=8)
        command.add_argument("--select", type=int, default=3)
        command.add_argument("--no-verify", action="store_true", help="Exploration only; all results stay proposed")
    export = commands.add_parser("export-seed", help="Create the supported canonical Lean theorem format")
    export.add_argument("input")
    export.add_argument("--out", required=True)
    bench = commands.add_parser("benchmark", help="Train and evaluate the frozen CPU experiment")
    bench.add_argument("--out", default="outputs/benchmark")
    bench.add_argument("--quick", action="store_true")
    bench.add_argument("--certify", action="store_true", help="Additionally Lean-check all test witnesses")
    lab = commands.add_parser("lab", help="Serve the local research workbench")
    lab.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)
    try:
        if args.command == "doctor":
            print(json.dumps({"version": __version__, "python": sys.version.split()[0], "lean": shutil.which("lean"), "required_toolchain": TOOLCHAIN, "assets": str(data_root()), "paid_services": False}, indent=2))
        elif args.command in ("demo", "discover"):
            path = data_root() / "examples" / "invariants.json" if args.command == "demo" else args.input
            run = run_context(load_context(path), args.budget, args.select, not args.no_verify)
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
            from .benchmark import run_benchmark
            report = run_benchmark(args.out, args.quick)
            if args.certify:
                from .certification import certify_benchmark
                report = certify_benchmark(args.out)
                if report["formal_verification"]["status"] != "kernel_verified":
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
