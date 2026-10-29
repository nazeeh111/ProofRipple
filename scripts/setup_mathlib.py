#!/usr/bin/env python3
"""Set up or check ProofRipple's optional, pinned, targeted Mathlib runtime.

No credential access, toolchain-default changes, resets, deletion or full cache
fetch. --check never downloads or modifies the checkout. Receipts print as JSON.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

REPO = Path(__file__).resolve().parents[1]
REVISION = "0df444a360eaa60ab8c11dca51a86af692955474"
TAG = "v4.33.1"
TOOLCHAIN = "leanprover/lean4:v4.33.1"
URL = "https://github.com/leanprover-community/mathlib4.git"
IMPORTS = ("Mathlib.Order.Lattice", "Mathlib.Data.Set.Lattice")
MANIFEST_SHA256 = "1009a101f52a9d5d8ca57666f0256bae91abdb693e0f27b5a4622cffcc38cf03"
DEPENDENCIES = {
    "plausible": "b7eb3304aeae834b12dda98993a37f6a41f6f0bb",
    "LeanSearchClient": "5f4d51b81cbd3f6b32b156bfad9056621a040404",
    "importGraph": "16f02aa7642864af59f1ff0e384a015994db9118",
    "proofwidgets": "4be2e3d5087eeb272cf5a8853b8f9dd025ef5957",
    "aesop": "3448c0bcc5ce01b2d1546e483ec3620e32df3d0e",
    "Qq": "92c15be17b7caf78c2ad767ec40f89052d908d81",
    "batteries": "4488d40d070b9700d4d5a6aa342f0d40c31b2a2d",
    "Cli": "6130a47896ce867c6a4a55373441e59e565bad0f",
}
SMOKE_SOURCE = '''import Mathlib.Order.Lattice
import Mathlib.Data.Set.Lattice
import Lean
open Lean Elab Command

theorem proofripple_setup_smoke (a b c : Set Nat) :
    a ⊓ (b ⊔ c) ≤ (a ⊓ b) ⊔ (a ⊓ c) := (inf_sup_left a b c).le

run_cmd do
  let axioms ← collectAxioms `proofripple_setup_smoke
  logInfo m!"SETUP_AXIOMS {Json.compress (toJson (axioms.toList.map Name.toString))}"
'''


class SetupError(RuntimeError):
    pass


def command(args, *, cwd=None, env=None, timeout=30, visible=False):
    try:
        result = subprocess.run(args, cwd=cwd, env=env, capture_output=True,
                                text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise SetupError(f"Command unavailable or exceeded {timeout}s: {args[0]}") from exc
    if visible:
        # Tool diagnostics may contain ordinary source paths, never credentials.
        if result.stdout:
            print(result.stdout, file=sys.stderr, end="")
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="")
    if result.returncode:
        detail = (result.stderr or result.stdout).strip()[-2000:]
        raise SetupError(f"Command failed with exit {result.returncode}: {args[0]}\n{detail}")
    return result


def checked_checkout(git, path, revision):
    if not path.is_dir():
        raise SetupError(f"Expected checkout directory: {path}")
    actual_root = command([git, "-C", str(path), "rev-parse", "--show-toplevel"]).stdout.strip()
    if Path(actual_root).resolve() != path:
        raise SetupError(f"Destination is not its own Git checkout: {path}")
    actual = command([git, "-C", str(path), "rev-parse", "HEAD"]).stdout.strip()
    if actual != revision:
        raise SetupError(f"Wrong checkout revision at {path}: {actual}; expected {revision}. Preserved unchanged.")
    dirty = command([git, "-C", str(path), "status", "--porcelain", "--untracked-files=no"]).stdout
    if dirty:
        raise SetupError(f"Tracked source has local changes at {path}. Preserved unchanged; use a fresh --root.")


def inspect(git, root, *, allow_missing=False):
    checked_checkout(git, root, REVISION)
    if (root / "lean-toolchain").read_text().strip() != TOOLCHAIN:
        raise SetupError("Pinned Mathlib toolchain mismatch")
    manifest_bytes = (root / "lake-manifest.json").read_bytes()
    if hashlib.sha256(manifest_bytes).hexdigest() != MANIFEST_SHA256:
        raise SetupError("Pinned Mathlib dependency manifest hash mismatch")
    manifest = json.loads(manifest_bytes)
    packages = manifest.get("packages", [])
    if {item["name"]: item["rev"] for item in packages} != DEPENDENCIES:
        raise SetupError("Expected exactly the eight pinned dependency revisions")
    dependencies, missing = [], []
    for name, revision in DEPENDENCIES.items():
        path = root / ".lake/packages" / name
        if not path.exists():
            missing.append(name)
            continue
        checked_checkout(git, path.resolve(), revision)
        dependencies.append(dict(name=name, revision=revision, tracked_source_clean=True))
    if missing and not allow_missing:
        raise SetupError("Missing pinned dependency checkouts: " + ", ".join(missing))
    oleans = {module: root / ".lake/build/lib/lean" / (module.replace(".", "/") + ".olean")
              for module in IMPORTS}
    return dependencies, missing, oleans


def check_imports(lean, root, env):
    # Direct Lean plus explicit existing paths avoids Lake dependency resolution
    # and its possible downloads during --check or ordinary verification.
    check_env = env.copy()
    check_env["LEAN_PATH"] = os.pathsep.join(str(path) for path in
        [root / ".lake/build/lib/lean", *[
            root / ".lake/packages" / name / ".lake/build/lib/lean" for name in DEPENDENCIES]])
    with tempfile.TemporaryDirectory(prefix="proofripple-mathlib-smoke-") as tmp:
        source = Path(tmp) / "Smoke.lean"
        source.write_text(SMOKE_SOURCE)
        result = command([lean, "--json", "-j", "1", "-M", "2048",
                          "-DmaxHeartbeats=400000", str(source)], cwd=tmp,
                         env=check_env, timeout=60)
    audits, errors = [], []
    for line in result.stdout.splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if item.get("severity") == "error":
            errors.append(item.get("data"))
        data = item.get("data", "")
        if isinstance(data, str) and data.startswith("SETUP_AXIOMS "):
            audits.append(json.loads(data[len("SETUP_AXIOMS "):]))
    allowed = {"propext", "Classical.choice", "Quot.sound"}
    if errors or len(audits) != 1 or not set(audits[0]) <= allowed:
        raise SetupError("Mathlib smoke proof did not pass its explicit foundational axiom audit")
    return dict(status="kernel_verified", axioms=audits[0],
                source_sha256=hashlib.sha256(SMOKE_SOURCE.encode()).hexdigest(),
                output_sha256=hashlib.sha256(result.stdout.encode()).hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO / ".runtime/mathlib-v4.33.1")
    parser.add_argument("--cache-dir", type=Path, help="Optional non-synced compressed-cache directory")
    parser.add_argument("--check", action="store_true", help="Read-only offline readiness check; never downloads")
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    binaries = {name: shutil.which(name) for name in ("git", "lean", "lake")}
    missing = [name for name, path in binaries.items() if not path]
    if missing:
        parser.error("Required executables are missing: " + ", ".join(missing))
    env = os.environ.copy()
    env["ELAN_TOOLCHAIN"] = TOOLCHAIN
    # Keep unrelated project or user Lean paths from contaminating the probe.
    env.pop("LEAN_PATH", None)
    env.pop("LEAN_SRC_PATH", None)
    started = time.monotonic()
    try:
        # `elan run` installs only with its explicit --install flag, which is
        # deliberately omitted. Resolve real binaries to avoid proxy auto-install.
        elan = shutil.which("elan")
        if elan:
            prefix = command([elan, "run", TOOLCHAIN, "lean", "--print-prefix"],
                             env=env, timeout=60).stdout.strip()
            for name in ("lean", "lake"):
                actual = Path(prefix) / "bin" / name
                if not actual.is_file():
                    raise SetupError(f"Pinned installed executable is missing: {actual}")
                binaries[name] = str(actual)
        observed = command([binaries["lean"], "--version"], env=env, timeout=60).stdout
        if "version 4.33.1," not in observed:
            raise SetupError("Install Lean 4.33.1 explicitly before Mathlib setup; no compiler is downloaded here")
        if root.exists() and not root.is_dir():
            raise SetupError(f"Destination exists and is not a directory: {root}; preserved unchanged")
        if not root.exists():
            if args.check:
                raise SetupError(f"Runtime is absent: {root}; run setup without --check")
            # Check the existing pinned compiler before a potentially large clone.
            command([binaries["lean"], "--version"], env=env, timeout=60)
            root.parent.mkdir(parents=True, exist_ok=True)
            command([binaries["git"], "clone", "--depth", "1", "--branch", TAG,
                     URL, str(root)], timeout=180, visible=True)
        dependencies, missing_deps, oleans = inspect(binaries["git"], root, allow_missing=not args.check)
        cached = all(path.is_file() for path in oleans.values())
        downloaded = False
        if missing_deps or not cached:
            if args.check:
                raise SetupError("Required targeted compiled cache is missing; run setup without --check")
            # The checked-in manifest pins every dependency. Refuse dirty/wrong
            # existing packages before asking Lake to fetch any missing ones.
            env["MATHLIB_NO_CACHE_ON_UPDATE"] = "1"
            def cache_get(cache_path):
                cache_env = env.copy()
                cache_env["MATHLIB_CACHE_DIR"] = str(cache_path)
                command([binaries["lake"], "exe", "cache", "get", *IMPORTS],
                        cwd=root, env=cache_env, timeout=600, visible=True)
            if args.cache_dir:
                cache_path = args.cache_dir.expanduser().resolve()
                cache_path.mkdir(parents=True, exist_ok=True)
                cache_get(cache_path)
            else:
                with tempfile.TemporaryDirectory(prefix="proofripple-mathlib-cache-") as tmp:
                    cache_get(Path(tmp))
            downloaded = True
            dependencies, _, oleans = inspect(binaries["git"], root)
            if not all(path.is_file() for path in oleans.values()):
                raise SetupError("Targeted cache fetch completed but required modules remain missing")
        version = command([binaries["lean"], "--version"], env=env, timeout=60).stdout.strip()
        smoke = check_imports(binaries["lean"], root, env)
        receipt = dict(kind="proofripple-mathlib-setup-v1", ready=True,
                       mode="offline_check" if args.check else "setup_or_reuse", root=str(root),
                       revision=REVISION, tag=TAG, toolchain=TOOLCHAIN, observed_lean=version,
                       imports=list(IMPORTS), manifest_sha256=MANIFEST_SHA256,
                       dependencies=dependencies, cache_fetch_performed=downloaded,
                       compiled_modules={name: hashlib.sha256(path.read_bytes()).hexdigest()
                                         for name, path in oleans.items()}, smoke=smoke,
                       elapsed_seconds=round(time.monotonic() - started, 4))
        print(json.dumps(receipt, indent=2, sort_keys=True))
    except (SetupError, OSError, ValueError, KeyError) as exc:
        print(json.dumps(dict(ready=False, root=str(root), error=str(exc)), indent=2), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
