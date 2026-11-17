from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys

from . import __version__
from .engine import METHODS
from .lean import TOOLCHAIN, certify_run, import_lean, seed_source

from .workflow import MATHLIB_METHODS, data_root, load_model, run_context


def load_context(path):
    file = Path(path)
    if file.stat().st_size > 2_000_000:
        raise ValueError("Context exceeds 2 MB")
    return import_lean(file) if file.suffix == ".lean" else json.loads(file.read_text())


def save_run(run, out):
    from .publication import _json, publish
    files = {"run.json": _json(run)}
    if "lean_source" in run:
        files["ProofRipple.lean"] = run["lean_source"].encode("utf-8")
    return publish(out, files, "run")


def _port(value):
    try:
        port = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("choose a whole-number port from 0 to 65535")
    if not 0 <= port <= 65535:
        raise argparse.ArgumentTypeError("choose a port from 0 to 65535; 0 chooses an available port")
    return port


def main(argv=None):
    parser = argparse.ArgumentParser(description="ProofRipple · theorem consequences with auditable Lean evidence")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    verify = commands.add_parser("verify-run", help="Check a completed run generation (digests are not authentication)")
    verify.add_argument("directory")
    verify.add_argument("--recheck", action="store_true", help="Rebuild and rerun the existing Lean certification")
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
    lab = commands.add_parser("lab", help="Serve the local research workbench",
        description="Review recorded evidence and run bounded explorations in your browser. Open the printed loopback URL; Ctrl-C stops the server.")
    lab.add_argument("--port", type=_port, default=8765,
        help="Loopback port (default: 8765; 0 chooses an available port)")
    args = parser.parse_args(argv)
    try:
        if args.command == "verify-run":
            from .publication import admit
            manifest, run = admit(args.directory)
            if manifest["kind"] != "run":
                raise ValueError("Not a run generation")
            result = {"integrity": "verified", "authentication": "not provided", "lean_rechecked": False}
            if args.recheck:
                checked = certify_run(run)
                result.update(lean_rechecked=True, verification=checked["verification"]["status"])
            print(json.dumps(result, indent=2))
            if args.recheck and result["verification"] != "kernel_verified":
                return 2
        elif args.command == "doctor":
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
