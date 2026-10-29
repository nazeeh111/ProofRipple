#!/usr/bin/env python3
"""Supplemental post-study repair of the fixed Mathlib automation control.

Only make membership preprocessing best-effort with `try simp only`; retain
the original goal types, aesop, pinned compiler and verifier resource limits.
This does not replace the preserved failed controls or alter the ranking study.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from proofripple.engine import context_hash
from proofripple.lean import TOOLCHAIN
from proofripple.mathlib import build_automation_source, validate_context
from proofripple.mathlib_runtime import ALLOWED_AXIOMS, MATHLIB_REVISION, verify_mathlib_source

ORIGINAL_PREPROCESS = "\n  simp only [Set.mem_union, Set.mem_inter] at *\n"
REPAIRED_PREPROCESS = "\n  try simp only [Set.mem_union, Set.mem_inter] at *\n"
TIMEOUT_SECONDS = 120
MAX_PROCESSES = 2
CORE_NAMES = ("engine.py", "lean.py", "mathlib.py", "mathlib_benchmark.py",
              "mathlib_model.py", "mathlib_runtime.py", "mathlib_search.py", "model.py")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def canonical_hash(value):
    return sha256(json.dumps(value, sort_keys=True).encode())


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def repaired_source(context):
    """The reversible one-token-per-goal repair is the entire source delta."""
    original, names = build_automation_source(context["goals"], context.get("variables", 6))
    if original.count(ORIGINAL_PREPROCESS) != len(names) or REPAIRED_PREPROCESS in original:
        raise ValueError("Frozen automation builder no longer matches the exact preprocessing repair")
    repaired = original.replace(ORIGINAL_PREPROCESS, REPAIRED_PREPROCESS)
    if repaired.replace(REPAIRED_PREPROCESS, ORIGINAL_PREPROCESS) != original:
        raise ValueError("Automation source repair changed more than the preprocessing guard")
    return original, repaired, names


def load_frozen_contexts(path):
    path = Path(path).expanduser().resolve()
    freeze_path = path.parent/"source-freeze.json"
    freeze_bytes = freeze_path.read_bytes()
    freeze = json.loads(freeze_bytes)
    corpus_bytes = path.read_bytes()
    if sha256(corpus_bytes) != freeze["corpus_sha256"]["contexts.json.gz"]:
        raise ValueError("Context corpus bytes differ from the authoritative freeze")
    contexts = json.loads(gzip.decompress(corpus_bytes))
    if canonical_hash(contexts) != freeze["data_sha256"]:
        raise ValueError("Context corpus data hash differs from the authoritative freeze")
    current = {name: sha256((ROOT/"proofripple"/name).read_bytes()) for name in CORE_NAMES}
    if current != freeze["source_sha256"]:
        raise ValueError("One of the eight frozen scientific sources has changed")
    test = contexts["test"]
    expected = freeze["coverage_at_largest_k"]["test"]
    if len(test) != expected["contexts"] or sum(len(c["goals"]) for c in test) != expected["goal_total"]:
        raise ValueError("Test workload denominator differs from the authoritative freeze")
    ids = [context["id"] for context in test]
    if len(set(ids)) != len(ids) or any(not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", cid) for cid in ids):
        raise ValueError("Invalid or repeated context identifier")
    for context in test:
        validate_context(context)
        if context.get("metadata", {}).get("split") != "test":
            raise ValueError("Automation control requires the frozen test split")
    goals = [{"context_id": c["id"], "variables": c.get("variables", 6), "goals": c["goals"]} for c in test]
    return test, {"contexts_path": str(path), "contexts_gzip_sha256": sha256(corpus_bytes),
                  "data_sha256": freeze["data_sha256"], "source_freeze_sha256": sha256(freeze_bytes),
                  "scientific_source_sha256": current, "all_test_goal_statements_sha256": canonical_hash(goals),
                  "all_test_contexts": len(test), "all_test_goals": sum(len(c["goals"]) for c in test)}


def audit_is_valid(result, names, source_digest, original_types=None):
    """Keep failure diagnostic audits distinct from accepted checked proofs."""
    audits = result.get("audits", [])
    actual = [audit.get("name") for audit in audits]
    if (result.get("status") != "kernel_verified" or result.get("source_sha256") != source_digest
            or result.get("toolchain") != TOOLCHAIN
            or result.get("library", {}).get("revision") != MATHLIB_REVISION
            or set(result.get("allowed_axioms", [])) != set(ALLOWED_AXIOMS)
            or len(actual) != len(set(actual)) or len(actual) != len(names) or set(actual) != set(names)):
        return False
    for audit in audits:
        if (not isinstance(audit.get("type"), str) or not isinstance(audit.get("axioms"), list)
                or not set(audit["axioms"]).issubset(ALLOWED_AXIOMS)
                or not isinstance(audit.get("constants"), list) or "sorryAx" in audit["constants"]):
            return False
        if original_types is not None and original_types.get(audit["name"]) != audit["type"]:
            return False
    return True


def check_context(context, out, original_controls=None):
    cid = context["id"]
    original, source, names = repaired_source(context)
    (out/"original-sources"/(cid+".lean")).write_text(original)
    (out/"sources"/(cid+".lean")).write_text(source)
    original_types = None
    original_check_sha = None
    if original_controls is not None:
        old_source = Path(original_controls)/(cid+".lean")
        old_check = Path(original_controls)/(cid+".json")
        if old_source.read_bytes() != original.encode():
            raise ValueError("Preserved original control source differs from the frozen builder: "+cid)
        previous_bytes = old_check.read_bytes()
        previous = json.loads(previous_bytes)
        original_types = {audit["name"]: audit["type"] for audit in previous["audits"]}
        if set(original_types) != set(names) or len(previous["audits"]) != len(names):
            raise ValueError("Preserved original control did not audit the same exact declarations: "+cid)
        original_check_sha = sha256(previous_bytes)
    result = verify_mathlib_source(source, names, timeout=TIMEOUT_SECONDS)
    result["supplemental_audit_valid"] = audit_is_valid(result, names, sha256(source.encode()), original_types)
    save_json(out/"checks"/(cid+".json"), result)
    (out/"logs"/(cid+".log")).write_text(result.get("log", ""))
    accepted = result["supplemental_audit_valid"]
    row = {"context_id": cid, "context_sha256": context_hash(context),
           "goal_statements_sha256": canonical_hash({"variables": context.get("variables", 6), "goals": context["goals"]}),
           "goal_ids": [goal["id"] for goal in context["goals"]], "goals": len(names),
           "solved": len(names) if accepted else 0, "status": "kernel_verified" if accepted else "failed",
           "verifier_status": result["status"], "audits_received": len(result.get("audits", [])),
           "expected_names": names, "original_source_sha256": sha256(original.encode()),
           "repaired_source_sha256": sha256(source.encode()), "original_check_sha256": original_check_sha,
           "original_audit_types_compared": original_types is not None,
           "audit_type_sha256": {audit["name"]: sha256(audit["type"].encode()) for audit in result.get("audits", [])},
           "check_sha256": sha256((out/"checks"/(cid+".json")).read_bytes()),
           "log_sha256": sha256(result.get("log", "").encode()), "elapsed_seconds": result["elapsed_seconds"]}
    save_json(out/(cid+".json"), row)
    print(f"Supplemental control {cid}: {row['status']} {row['solved']}/{row['goals']}", flush=True)
    return row


def run(contexts_path, output_dir, context_id=None, jobs=MAX_PROCESSES, original_controls=None):
    out = Path(output_dir).expanduser().resolve()
    if out.exists():
        raise ValueError("Output already exists; preserve earlier controls: "+str(out))
    if jobs not in (1, 2):
        raise ValueError("At most two Lean subprocesses are allowed")
    contexts, provenance = load_frozen_contexts(contexts_path)
    if context_id is not None:
        contexts = [context for context in contexts if context["id"] == context_id]
        if not contexts:
            raise ValueError("Requested pilot context is absent from the frozen test split")
    out.mkdir(parents=True)
    for name in ("original-sources", "sources", "checks", "logs"):
        (out/name).mkdir()
    receipt = {"schema_version": 1, "phase": "post_study_control_plumbing_repair",
               "scope": "single_context_pilot" if context_id is not None else "entire_frozen_test_workload",
               "method": "Pointwise Set Nat membership; try simp only [Set.mem_union,Set.mem_inter] at *; unchanged aesop, no seed/candidates",
               "source_delta": "Only insert try before each existing simp only preprocessing command",
               "limits": {"lean_threads_per_process": 1, "memory_mib_per_process": 2048,
                          "max_heartbeats": 400000, "timeout_seconds": TIMEOUT_SECONDS, "parallel_processes": jobs},
               "allowed_axioms": list(ALLOWED_AXIOMS), "mathlib_revision": MATHLIB_REVISION, "toolchain": TOOLCHAIN,
               "driver_sha256": sha256(Path(__file__).read_bytes()), "provenance": provenance,
               "original_controls_path": str(Path(original_controls).resolve()) if original_controls else None,
               "interpretation": "Post-study mechanical preprocessing repair. Original failed control bundles remain failed and preserved; ranking/model/data outcomes are unchanged. Resource regimes differ from bounded proof search."}
    save_json(out/"repair-plan.json", receipt)
    started = time.monotonic()
    def check(context):
        try:
            return check_context(context, out, original_controls)
        except Exception as exc:
            row = {"context_id": context["id"], "status": "failed", "solved": 0, "goals": len(context["goals"]),
                   "audits_received": 0, "error": type(exc).__name__+": "+str(exc)}
            save_json(out/(context["id"]+".json"), row)
            print(f"Supplemental control {context['id']}: failed ({row['error']})", flush=True)
            return row
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        rows = list(pool.map(check, contexts))
    summary = {**receipt, "status": "kernel_verified" if rows and all(row["status"] == "kernel_verified" for row in rows) else "failed",
               "total": sum(row["goals"] for row in rows), "solved": sum(row["solved"] for row in rows),
               "audits_received": sum(row["audits_received"] for row in rows), "contexts": rows,
               "elapsed_seconds": round(time.monotonic()-started, 4)}
    save_json(out/"summary.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contexts", type=Path, required=True, help="Exact frozen contexts.json.gz, beside source-freeze.json")
    parser.add_argument("--out", type=Path, required=True, help="New output directory; refuses overwrite")
    parser.add_argument("--context", help="Single named frozen test context, explicitly labeled as a pilot")
    parser.add_argument("--jobs", type=int, choices=(1, 2), default=MAX_PROCESSES)
    parser.add_argument("--original-controls", type=Path, help="Optional preserved original .lean/.json bundles; compare source bytes and exact audited types")
    args = parser.parse_args()
    try:
        result = run(args.contexts, args.out, args.context, args.jobs, args.original_controls)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps({key: result[key] for key in ("status", "scope", "total", "solved", "audits_received", "elapsed_seconds")}, indent=2))
    return 0 if result["status"] == "kernel_verified" else 1


if __name__ == "__main__":
    raise SystemExit(main())
