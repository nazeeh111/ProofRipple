"""Pinned, optional Mathlib environment. Verification never downloads packages."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

from .lean import TOOLCHAIN, verify_source

MATHLIB_REVISION = "0df444a360eaa60ab8c11dca51a86af692955474"
MATHLIB_TAG = "v4.33.1"
ALLOWED_AXIOMS = ("propext", "Classical.choice", "Quot.sound")
IMPORTS = ("Mathlib.Order.Lattice", "Mathlib.Data.Set.Lattice")


def runtime_root():
    configured = os.environ.get("PROOFRIPPLE_MATHLIB_ROOT")
    return Path(configured).expanduser().resolve() if configured else Path(__file__).resolve().parents[1] / ".runtime" / "mathlib-v4.33.1"


def runtime_info():
    root = runtime_root()
    result = {"available": False, "root": str(root), "revision": MATHLIB_REVISION,
              "tag": MATHLIB_TAG, "toolchain": TOOLCHAIN, "imports": list(IMPORTS)}
    remedy = "Run scripts/setup_mathlib.py from the source distribution, or set PROOFRIPPLE_MATHLIB_ROOT to that pinned checkout."
    try:
        if (root / "lean-toolchain").read_text().strip() != TOOLCHAIN:
            raise ValueError("Mathlib toolchain does not match the pinned Lean release")
        revision = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                                  capture_output=True, text=True, timeout=10, check=True).stdout.strip()
        if revision != MATHLIB_REVISION:
            raise ValueError("Mathlib checkout revision does not match the pinned source")
        dirty = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=no"],
                               capture_output=True, text=True, timeout=10, check=True).stdout
        if dirty:
            raise ValueError("Pinned Mathlib tracked source has local changes")
        for name in IMPORTS:
            if not (root / ".lake/build/lib/lean" / (name.replace(".", "/") + ".olean")).is_file():
                raise ValueError("Required targeted Mathlib cache is missing")
        manifest = (root / "lake-manifest.json").read_bytes()
        dependencies = [{"name": item["name"], "revision": item["rev"]}
                        for item in json.loads(manifest)["packages"]]
        for item in dependencies:
            package = root / ".lake/packages" / item["name"]
            actual = subprocess.run(["git", "-C", str(package), "rev-parse", "HEAD"],
                                    capture_output=True, text=True, timeout=10, check=True).stdout.strip()
            if actual != item["revision"]:
                raise ValueError("Pinned Mathlib dependency revision differs: " + item["name"])
            dirty = subprocess.run(["git", "-C", str(package), "status", "--porcelain", "--untracked-files=no"],
                                   capture_output=True, text=True, timeout=10, check=True).stdout
            if dirty:
                raise ValueError("Pinned Mathlib dependency has tracked changes: " + item["name"])
        elan = shutil.which("elan")
        if not elan:
            raise ValueError("Elan is required to resolve the already-installed pinned compiler without downloading it")
        compiler_env = {**os.environ, "ELAN_TOOLCHAIN": TOOLCHAIN}
        prefix = subprocess.run([elan, "run", TOOLCHAIN, "lean", "--print-prefix"],
                                capture_output=True, text=True, timeout=10, check=True, env=compiler_env).stdout.strip()
        compiler = Path(prefix) / "bin/lean"
        if not compiler.is_file():
            raise ValueError("The already-installed pinned Lean executable is missing")
        result.update(available=True, manifest_sha256=hashlib.sha256(manifest).hexdigest(),
                      dependencies=dependencies, lean_bin=str(compiler),
                      execution="Direct installed pinned Lean with explicit library paths; verification does not resolve or download dependencies.")
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        result["error"] = str(exc) + ". " + remedy
    return result


def verify_mathlib_source(source, expected_names, timeout=60):
    info = runtime_info()
    if not info["available"]:
        return {"status": "unavailable", "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
                "toolchain": TOOLCHAIN, "axiom_policy": "explicit_foundational_allowlist",
                "allowed_axioms": list(ALLOWED_AXIOMS), "audits": [], "log": info["error"],
                "elapsed_seconds": 0, "library": info}
    root = Path(info["root"])
    paths = [root / ".lake/build/lib/lean", *[root / ".lake/packages" / item["name"] / ".lake/build/lib/lean" for item in info["dependencies"]]]
    check = verify_source(source, expected_names, timeout=timeout, allowed_axioms=ALLOWED_AXIOMS,
                          lean_bin=info["lean_bin"], library_paths=paths)
    check["library"] = {key: value for key, value in info.items() if key not in {"root", "lean_bin"}}
    return check
