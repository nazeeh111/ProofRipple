#!/usr/bin/env python3
"""Reproduce the fixed gen=8 Lean case study and gen=32 strong control.

No threshold sweep. Failed baseline attempts are expected observations, never
accepted proofs. All outputs go to a new directory; existing work is preserved.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from proofripple.engine import discover
from proofripple.lean import TOOLCHAIN
from proofripple.natural import (
    PARAMETERS, _capacity_statement, build_automation_baseline,
    build_natural_source, make_example,
)

CANDIDATE = "pr_ripple_p4_p9"
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
EXPECTED_BASE = "6f31cf3f8b668f345639026f58d6c00ba27c00196d6fd30b3cb0dd162a1fd927"
EXPECTED_CONTEXT = "92831cfccfe068320437528c11cf2995a4974bba7909c0ad0379c6753478859d"

AUDIT = '''
run_cmd do
  let n := `GOALNAME
  let env ← getEnv
  let some ci := env.find? n | throwError "missing declaration"
  let axs ← collectAxioms n
  let ty ← liftTermElabM <| Meta.ppExpr ci.type
  let some value := ci.value? (allowOpaque := true) | throwError "no proof body"
  let reduced ← liftTermElabM <| Meta.zetaReduce value
  let rawDeps := value.getUsedConstants.toList.map Name.toString
  let deps := reduced.getUsedConstants.toList.map Name.toString
  logInfo m!"BUDGET_AUDIT {Json.compress <| Json.mkObj [("name",toJson n.toString),("type",toJson ty.pretty),("axioms",toJson (axs.toList.map Name.toString)),("constants",toJson rawDeps),("zeta_constants",toJson deps)]}"
'''

EXPANDED_AUDIT = '''
run_cmd do
  let env ← getEnv
  let some ci := env.find? `GOAL | throwError "missing"
  let some value := ci.value? (allowOpaque := true) | throwError "no proof"
  let expanded ← liftTermElabM <| Core.transform value (pre := fun e => do
    if let .const n us := e then
      if n.toString.startsWith "GOAL." then
        if let some info := env.find? n then
          if let some v := info.value? (allowOpaque := true) then
            return .visit (v.instantiateLevelParams info.levelParams us)
    return .continue)
  let reduced ← liftTermElabM <| Meta.zetaReduce expanded
  let deps := reduced.getUsedConstants.toList.map Name.toString
  logInfo m!"EXPANDED_AUDIT {Json.compress <| Json.mkObj [("name",toJson "GOAL"),("expanded_zeta_constants",toJson deps)]}"
'''


def digest(data):
    return hashlib.sha256(data).hexdigest()


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def text_output(value):
    return value.decode(errors="replace") if isinstance(value, bytes) else (value or "")


def execute(job, out, executable, env, version):
    filename, variant, goal, generation, expected_names = job
    path = out / filename
    command = [executable, "--json", "-j", "1", "-M", "2048",
               "-DmaxHeartbeats=400000", str(path)]
    result = dict(file=filename, variant=variant, goal_index=goal,
                  generation=generation, source_sha256=digest(path.read_bytes()),
                  command=command, toolchain=version)
    start = time.monotonic()
    try:
        proc = subprocess.run(command, cwd=out, env=env, capture_output=True,
                              text=True, timeout=60)
        result.update(returncode=proc.returncode, timed_out=False)
        log = proc.stdout + proc.stderr
    except subprocess.TimeoutExpired as exc:
        result.update(returncode=None, timed_out=True)
        log = text_output(exc.stdout) + text_output(exc.stderr)
    except OSError as exc:
        result.update(returncode=None, timed_out=False)
        log = str(exc)
    path.with_suffix(".log").write_text(log)
    audits, expanded, errors = [], [], []
    for line in log.splitlines():
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        if message.get("severity") == "error":
            errors.append(message.get("data"))
        data = message.get("data", "")
        if not isinstance(data, str):
            continue
        for marker, target in (("BUDGET_AUDIT ", audits),
                               ("PROOFRIPPLE_AUDIT ", audits),
                               ("EXPANDED_AUDIT ", expanded)):
            if data.startswith(marker):
                try:
                    target.append(json.loads(data[len(marker):]))
                except json.JSONDecodeError:
                    errors.append("Malformed audit record")
    names = [audit.get("name") for audit in audits]
    valid_audits = (len(names) == len(set(names)) == len(expected_names)
                    and set(names) == set(expected_names)
                    and all(isinstance(a.get("axioms"), list)
                            and set(a["axioms"]) <= ALLOWED_AXIOMS
                            and isinstance(a.get("type"), str) for a in audits))
    verified = result["returncode"] == 0 and not errors and valid_audits
    used_zeta = verified and any(CANDIDATE in a.get("zeta_constants", []) for a in audits)
    used_expanded = (verified and len(expanded) == 1
                     and expanded[0].get("name") in expected_names
                     and CANDIDATE in expanded[0].get("expanded_zeta_constants", []))
    expected_failure = (variant == "baseline" and result["returncode"] not in (None, 0)
                        and any(isinstance(e, str) and "`grind` failed" in e for e in errors))
    result.update(audits=audits, expanded_audits=expanded, errors=errors,
                  kernel_verified=verified, candidate_used_after_zeta=used_zeta,
                  candidate_used_after_local_auxiliary_expansion_and_beta_zeta=used_expanded,
                  expected_failure=expected_failure,
                  status=("kernel_verified" if verified else
                          "expected_failed_proof_attempt" if expected_failure else "failed_or_unavailable"),
                  diagnostic_audits_are_proofs=verified,
                  elapsed_seconds=round(time.monotonic() - start, 4),
                  log_sha256=digest(log.encode()))
    save_json(path.with_suffix(".json"), result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True, help="New output directory; refuses overwrite")
    args = parser.parse_args()
    out = args.out.expanduser().resolve()
    if out.exists():
        parser.error(f"Output already exists: {out}")
    executable = shutil.which("lean")
    if not executable:
        parser.error("Lean is required; install the pinned toolchain from lean-toolchain")
    env = os.environ.copy()
    env["ELAN_TOOLCHAIN"] = TOOLCHAIN
    version_proc = subprocess.run([executable, "--version"], env=env,
                                  capture_output=True, text=True, timeout=60)
    if version_proc.returncode != 0:
        parser.error("Pinned Lean toolchain is unavailable: " + version_proc.stderr.strip())
    context = make_example()
    run = discover(context, k=1, method="graph", search_budget=8)
    if run["selected"] != [CANDIDATE.removeprefix("pr_")] or len(run["candidates"]) != 3:
        parser.error("Frozen candidate pool or selection changed")
    run["goals"] = []
    source, _, _ = build_natural_source(run)
    base = source.split("\nrun_cmd do", 1)[0] + "\n"
    context_hash = digest(json.dumps(context, sort_keys=True, separators=(",", ":")).encode())
    if digest(base.encode()) != EXPECTED_BASE or context_hash != EXPECTED_CONTEXT:
        parser.error("Frozen source/context changed; this case study requires its versioned input")
    out.mkdir(parents=True, exist_ok=False)
    (out / "base.lean").write_text(base)
    save_json(out / "context.json", context)
    version = version_proc.stdout.strip()
    protocol = dict(protocol="Fixed prospective generation=8 comparison and generation=32 control; no sweep.",
                    context_sha256=context_hash, base_sha256=EXPECTED_BASE,
                    selected_candidate=CANDIDATE, candidate_pool=3, goal_count=2,
                    common_limits=dict(maxHeartbeats=400000, threads=1, memory_MB=2048, timeout_seconds=60),
                    axiom_policy=sorted(ALLOWED_AXIOMS),
                    note="Same pre-goal environment for each pair; gen limits are not equal CPU work.")
    save_json(out / "protocol.json", protocol)
    stages = ", ".join("stage_" + node["id"] for node in context["nodes"])
    jobs, expanded_jobs = [], []
    for i, goal in enumerate(context["goals"]):
        name = f"budget_goal_{i}"
        for variant in ("baseline", "augmented"):
            proof = f"  dsimp [{stages}]\n  grind (gen := 8)\n"
            if variant == "augmented":
                proof = (f"  have ripple := {CANDIDATE} xs f p k cap\n"
                         f"  dsimp [{stages}] at ripple ⊢\n  grind (gen := 8)\n")
            text = (base + f"\ntheorem {name} {PARAMETERS} :\n    {_capacity_statement(goal)} := by\n"
                    + proof + AUDIT.replace("GOALNAME", name))
            filename = f"goal-{i}-{variant}-gen8.lean"
            (out / filename).write_text(text)
            jobs.append((filename, variant, i, 8, [name]))
            if variant == "augmented":
                filename = f"goal-{i}-augmented-expanded-gen8.lean"
                (out / filename).write_text(text + EXPANDED_AUDIT.replace("GOAL", name))
                expanded_jobs.append((filename, "augmented_expanded_check", i, 8, [name]))
    control, names = build_automation_baseline(context, generation=32)
    (out / "control-gen32.lean").write_text(control)
    jobs.append(("control-gen32.lean", "control", None, 32, names))
    # Fresh processes keep failed attempts from contaminating another goal.
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda job: execute(job, out, executable, env, version), jobs))
    with ThreadPoolExecutor(max_workers=2) as pool:
        checks = list(pool.map(lambda job: execute(job, out, executable, env, version), expanded_jobs))
    counts = dict(baseline_gen8=sum(r["kernel_verified"] for r in results if r["variant"] == "baseline"),
                  baseline_expected_failures=sum(r["expected_failure"] for r in results),
                  augmented_gen8=sum(r["kernel_verified"] for r in results if r["variant"] == "augmented"),
                  augmented_used=sum(r["candidate_used_after_zeta"] for r in results if r["variant"] == "augmented"),
                  strong_control_gen32=sum(len(r["audits"]) for r in results if r["variant"] == "control" and r["kernel_verified"]),
                  expanded_candidate_used=sum(r["candidate_used_after_local_auxiliary_expansion_and_beta_zeta"] for r in checks))
    reproduced = counts == dict(baseline_gen8=0, baseline_expected_failures=2, augmented_gen8=2,
                                augmented_used=2, strong_control_gen32=3, expanded_candidate_used=2)
    summary = dict(**protocol, toolchain=version, results=results,
                   expanded_candidate_usage=checks, summary=counts, reproduced_expected_outcomes=reproduced,
                   limitations=["Two related illustrative goals, not a held-out population.",
                                "No timing/speedup claim; processes run concurrently.",
                                "The higher-generation direct control solves all goals unaided.",
                                "Candidate construction cost is not amortized or compared here."])
    save_json(out / "summary.json", summary)
    print(json.dumps(dict(summary=counts, reproduced_expected_outcomes=reproduced, output=str(out)), indent=2))
    return 0 if reproduced else 1


if __name__ == "__main__":
    raise SystemExit(main())
