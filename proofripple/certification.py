"""Batch Lean certification of every concrete test-policy search witness."""
import hashlib
import json
from pathlib import Path

from .lean import _audit_many, build_source, verify_source


def certify_benchmark(directory, timeout=240):
    out = Path(directory)
    report = json.loads((out / "benchmark.json").read_text())
    runs = json.loads((out / "certification-runs.json").read_text())
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
    proof_dir = out / "proofs"
    proof_dir.mkdir(exist_ok=True)
    for index, (cid, group) in enumerate(grouped.items()):
        namespace = f"Context{index}"
        goals = [{"id": f"certificate_goal_{i}", **g} for i, g in enumerate(group["goals"].values())]
        source = build_source(group["context"], group["candidates"], goals)
        names = ["pr_" + item["id"] for item in [group["context"]["seed"], *group["candidates"], *goals]]
        expected.extend(namespace + "." + n for n in names)
        source_file = proof_dir / f"{cid}.lean"
        source_file.write_text(source)
        check = verify_source(source, names, timeout=min(timeout, 60))
        checks.append({"context_id": cid, **check})
        contexts.append({"context_id": cid, "source": f"proofs/{cid}.lean", "source_sha256": check["source_sha256"], "status": check["status"], "candidates": len(group["candidates"]), "distinct_goal_proofs": len(goals)})
        print(f"Lean {cid}: {check['status']} ({len(check['audits'])}/{len(names)} audits)", flush=True)
    audits = [{"context_id": check["context_id"], **audit} for check in checks for audit in check["audits"]]
    verification = {"status": "kernel_verified" if checks and all(c["status"] == "kernel_verified" for c in checks) else "failed",
                    "toolchain": checks[0]["toolchain"] if checks else None, "axiom_policy": "empty", "audits": audits,
                    "source_manifest_sha256": hashlib.sha256(json.dumps(contexts, sort_keys=True).encode()).hexdigest(),
                    "elapsed_seconds": sum(c["elapsed_seconds"] for c in checks), "checks": checks}
    # Full proof types and dependency audits retained apart from concise report.
    (out / "benchmark-audits.json").write_text(json.dumps(verification, indent=2) + "\n")
    report["formal_verification"] = {k: v for k, v in verification.items() if k not in ("audits", "log", "checks")}
    report["formal_verification"].update(declarations=len(expected), audits_received=len(verification["audits"]),
                                         contexts=contexts, policy_runs=len(runs),
                                         scope="All candidate proofs and all distinct successful baseline/augmented test witnesses across every policy and random repetition. Failed searches produce no theorem.")
    report["formal_verification"]["audits_sha256"] = hashlib.sha256((out / "benchmark-audits.json").read_bytes()).hexdigest()
    (out / "benchmark.json").write_text(json.dumps(report, indent=2) + "\n")
    return report
