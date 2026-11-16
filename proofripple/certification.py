"""Batch Lean certification of every concrete test-policy search witness."""
import hashlib
import json
from pathlib import Path

from .lean import _audit_many, build_source, verify_source
from .publication import _json, publish


def certify_benchmark(directory, timeout=240):
    out = Path(directory)
    report_bytes = (out / "benchmark.json").read_bytes()
    runs_bytes = (out / "certification-runs.json").read_bytes()
    report = json.loads(report_bytes)
    runs = json.loads(runs_bytes)
    grouped = {}
    for run in runs:
        cid = run["context"]["id"]
        group = grouped.setdefault(cid, {"context": run["context"], "candidates": run["candidates"], "goals": {}})
        for goal in run["goals"]:
            for variant in ("baseline", "augmented"):
                search = goal[variant]
                if search["solved"]:
                    key = (goal["source"], goal["target"], tuple(search["path"]))
                    group["goals"][key] = {"source": goal["source"], "target": goal["target"], "path": search["path"]}
    expected, contexts, checks = [], [], []
    files = {"input-benchmark.json": report_bytes, "certification-runs.json": runs_bytes}
    for index, (cid, group) in enumerate(grouped.items()):
        namespace = f"Context{index}"
        goals = [{"id": f"certificate_goal_{i}", **g} for i, g in enumerate(group["goals"].values())]
        source = build_source(group["context"], group["candidates"], goals)
        names = ["pr_" + item["id"] for item in [group["context"]["seed"], *group["candidates"], *goals]]
        expected.extend(namespace + "." + n for n in names)
        filename = f"proof-{index}.lean"
        files[filename] = source.encode("utf-8")
        check = verify_source(source, names, timeout=min(timeout, 60))
        checks.append({"context_id": cid, **check})
        contexts.append({"context_id": cid, "source": filename, "source_sha256": check["source_sha256"], "status": check["status"], "candidates": len(group["candidates"]), "distinct_goal_proofs": len(goals)})
        print(f"Lean {cid}: {check['status']} ({len(check['audits'])}/{len(names)} audits)", flush=True)
    audits = [{"context_id": check["context_id"], **audit} for check in checks for audit in check["audits"]]
    verification = {"status": "kernel_verified" if checks and all(c["status"] == "kernel_verified" for c in checks) else "failed",
                    "toolchain": checks[0]["toolchain"] if checks else None, "axiom_policy": "empty", "audits": audits,
                    "source_manifest_sha256": hashlib.sha256(json.dumps(contexts, sort_keys=True).encode()).hexdigest(),
                    "elapsed_seconds": sum(c["elapsed_seconds"] for c in checks), "checks": checks}
    # Full proof types and dependency audits retained apart from concise report.
    files["benchmark-audits.json"] = _json(verification)
    report["formal_verification"] = {k: v for k, v in verification.items() if k not in ("audits", "log", "checks")}
    report["formal_verification"].update(declarations=len(expected), audits_received=len(verification["audits"]),
                                         contexts=contexts, policy_runs=len(runs),
                                         scope="All candidate proofs and all distinct successful baseline/augmented test witnesses across every policy and random repetition. Failed searches produce no theorem.")
    report["formal_verification"]["audits_sha256"] = hashlib.sha256(files["benchmark-audits.json"]).hexdigest()
    files["benchmark.json"] = _json(report)
    publish(out / "certification", files, "benchmark-certification")
    return report
