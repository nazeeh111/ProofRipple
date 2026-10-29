"""Small, closed Lean bridge. Never execute imported arbitrary Lean commands.

Python searches and proposes; Lean independently type checks proof terms and
reports transitive axioms. This domain requires an empty axiom list.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time

TOOLCHAIN = "leanprover/lean4:v4.33.1"
IDENT = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,63}\Z")
HEADER = "-- ProofRipple supported implication theorem. Do not add executable commands.\n"


def _ident(value):
    if not isinstance(value, str) or not IDENT.fullmatch(value):
        raise ValueError(f"Invalid implication identifier: {value!r}")
    return value


def _validate(context):
    from .engine import validate_context
    validate_context(context)
    if len(context["nodes"]) > 128 or len(context["edges"]) > 1024:
        raise ValueError("Context limit: 128 nodes and 1024 edges")
    for node in context["nodes"]:
        _ident(node["id"])
    for edge in [*context["edges"], context["seed"]]:
        _ident(edge["id"])


def _binders(context):
    nodes = " ".join("p_" + n["id"] for n in context["nodes"])
    hyps = " ".join(f"(h_{e['id']} : p_{e['source']} → p_{e['target']})" for e in context["edges"])
    return f"({nodes} : Prop) {hyps}"


def _arguments(context):
    return " ".join([*("p_" + n["id"] for n in context["nodes"]), *("h_" + e["id"] for e in context["edges"])])


def _term(context, source, target, path, known):
    edges = {e["id"]: e for e in context["edges"]}
    current, term = source, "hx"
    for eid in path:
        if eid in edges:
            edge, fn = edges[eid], "h_" + eid
        elif eid in known:
            edge = known[eid]
            fn = f"(pr_{_ident(eid)} {_arguments(context)})"
        else:
            raise ValueError(f"Unknown proof dependency: {eid}")
        if edge["source"] != current:
            raise ValueError(f"Non-composable proof at {eid}")
        current = edge["target"]
        term = f"({fn} {term})"
    if current != target:
        raise ValueError("Proof path does not prove the stated conclusion")
    return f"fun hx => {term}"


def _declaration(context, item, known):
    name = "pr_" + _ident(item["id"])
    proof = _term(context, item["source"], item["target"], item["path"], known)
    return f"theorem {name} {_binders(context)} : p_{item['source']} → p_{item['target']} :=\n  {proof}\n"


def seed_source(context):
    """Canonical supported .lean import/export format with an inert JSON manifest."""
    if isinstance(context, dict) and context.get("domain") == "mathlib-set-lattice":
        from .mathlib import build_mathlib_source, validate_context
        validate_context(context)
        source, _, _ = build_mathlib_source({"context": context, "candidates": context["candidates"], "selected": [],
            "goals": [{**goal, "baseline": {"solved": False}, "augmented": {"solved": False}} for goal in context["goals"]]})
        manifest = json.dumps(context, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return "-- ProofRipple supported Mathlib set-lattice context.\n-- proofripple-context: " + manifest + "\n\n" + source
    _validate(context)
    manifest = json.dumps(context, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    if context.get("domain") == "list-capacity":
        from .natural import build_natural_source
        source, _, _ = build_natural_source({"context": context, "candidates": [], "goals": []})
    else:
        source = _declaration(context, context["seed"], {})
    return HEADER + "-- proofripple-context: " + manifest + "\n\n" + source


def import_lean(path):
    """Accept only our canonical closed implication format, never general Lean IO."""
    text = Path(path).read_text(encoding="utf-8")
    if len(text) > 2_000_000:
        raise ValueError("Lean import exceeds 2 MB")
    lines = text.splitlines()
    if len(lines) < 2 or not lines[1].startswith("-- proofripple-context: "):
        raise ValueError("Unsupported Lean module. Use `proofripple export-seed` to create the supported implication format.")
    context = json.loads(lines[1].split(": ", 1)[1])
    if seed_source(context) != text:
        raise ValueError("Non-canonical Lean input rejected. Arbitrary Lean commands are not executed.")
    return context


def _audit(name):
    # Source is fixed; the only interpolated token is an already checked identifier.
    return f'''run_cmd do
  let n := `{name}
  let env ← getEnv
  let some ci := env.find? n | throwError "missing declaration"
  let axs ← collectAxioms n
  let ty ← liftTermElabM <| Meta.ppExpr ci.type
  let some value := ci.value? (allowOpaque := true) | throwError "declaration has no checked proof body"
  let deps := value.getUsedConstants.toList.map Name.toString
  logInfo m!"PROOFRIPPLE_AUDIT {{Json.compress <| Json.mkObj [("name", toJson n.toString), ("type", toJson ty.pretty), ("axioms", toJson (axs.toList.map Name.toString)), ("constants", toJson deps)]}}"
'''


def _audit_many(names):
    """Compile one audit routine, rather than a copy per declaration."""
    body = _audit("unused").split("  let env ← getEnv\n", 1)[1]
    body = "  let env ← getEnv\n" + body
    literals = ", ".join("`" + name for name in names)
    return "run_cmd do\n  for n in #[" + literals + "] do\n" + "\n".join("  " + line for line in body.splitlines()) + "\n"


def build_source(context, candidates=(), goals=()):
    _validate(context)
    known, declarations, items = {}, [], []
    for item in [context["seed"], *candidates, *goals]:
        eid = _ident(item["id"])
        if eid in known or any(e["id"] == eid for e in context["edges"]):
            raise ValueError("Duplicate declaration id")
        _ident(item["source"])
        _ident(item["target"])
        declarations.append(_declaration(context, item, known))
        known[eid] = item
        items.append(eid)
    body = "\n".join(declarations)
    return "import Lean\nopen Lean Elab Command\n\n" + body + "\n" + _audit_many(["pr_" + i for i in items])


def verify_source(source, expected_names, timeout=60, lean_bin=None, allowed_axioms=(), library_paths=None):
    """Internal verifier of generated source, not a public untrusted-code sandbox.

    Success requires process success, every expected audit exactly once, and only
    explicitly allowed foundational axioms. The default remains axiom-free.
    Error and timeout paths fail closed. Uses a fresh process and folder.
    """
    allowed_axioms = tuple(sorted(set(allowed_axioms)))
    foundational = {"propext", "Classical.choice", "Quot.sound"}
    if not set(allowed_axioms).issubset(foundational):
        raise ValueError("Only explicit Lean foundational axioms may be allowed; admitted/custom/native axioms are rejected")
    digest = hashlib.sha256(source.encode()).hexdigest()
    result = {"status": "unavailable", "source_sha256": digest, "toolchain": TOOLCHAIN,
              "axiom_policy": "empty" if not allowed_axioms else "explicit_foundational_allowlist",
              "allowed_axioms": list(allowed_axioms), "audits": [], "log": "", "elapsed_seconds": 0}
    executable = lean_bin or shutil.which("lean")
    if not executable:
        result["log"] = "Lean is missing. Install the pinned toolchain; no verification was performed."
        return result
    # Force the pinned installed toolchain without changing user's default or credentials.
    env = os.environ.copy()
    env["ELAN_TOOLCHAIN"] = TOOLCHAIN
    if library_paths is not None:
        env["LEAN_PATH"] = os.pathsep.join(str(path) for path in library_paths)
        env.pop("LEAN_SRC_PATH", None)
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="proofripple-lean-") as tmp:
        file = Path(tmp) / "ProofRipple.lean"
        file.write_text(source)
        command = [executable, "--json", "-j", "1", "-M", "2048", "-DmaxHeartbeats=400000", str(file)]
        try:
            proc = subprocess.run(command, capture_output=True, text=True, timeout=timeout, env=env, cwd=tmp)
        except subprocess.TimeoutExpired:
            result.update(status="failed", log=f"Lean verification exceeded {timeout}s")
        except OSError as exc:
            result.update(status="unavailable", log=str(exc))
        else:
            result["log"] = (proc.stdout + proc.stderr)[-1_000_000:]
            audits, errors = [], []
            for line in proc.stdout.splitlines():
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if msg.get("severity") == "error":
                    errors.append(msg)
                data = msg.get("data", "")
                marker = "PROOFRIPPLE_AUDIT "
                if isinstance(data, str) and data.startswith(marker):
                    try:
                        audits.append(json.loads(data[len(marker):]))
                    except json.JSONDecodeError:
                        errors.append({"data": "Malformed audit"})
            result["audits"] = audits
            names = [a.get("name") for a in audits]
            expected = list(expected_names)
            valid = (proc.returncode == 0 and not errors and "PANIC" not in proc.stderr and len(names) == len(set(names))
                     and set(names) == set(expected) and len(names) == len(expected)
                     and all(isinstance(a.get("axioms"), list) and set(a["axioms"]).issubset(allowed_axioms)
                             and isinstance(a.get("type"), str) for a in audits))
            result["status"] = "kernel_verified" if valid else "failed"
            result["returncode"] = proc.returncode
    result["elapsed_seconds"] = round(time.monotonic() - started, 4)
    return result


def certify_run(run, timeout=60):
    """Rebuild proofs from graph witnesses; incoming status/proof fields are ignored."""
    if run.get("context", {}).get("domain") == "mathlib-set-lattice":
        from .mathlib import certify_mathlib_run
        return certify_mathlib_run(run, timeout)
    result = copy.deepcopy(run)
    from .engine import context_hash
    result["seed"] = copy.deepcopy(result["context"]["seed"])
    result["context_sha256"] = context_hash(result["context"])
    candidates = result.get("candidates", [])
    for candidate in candidates:
        candidate.update(status="proposed", axioms=None)
    goals = []
    used_ids = {x["id"] for x in [*result["context"]["nodes"], *result["context"]["edges"], result["seed"], *candidates]}
    for index, goal in enumerate(result.get("goals", [])):
        for variant in ("baseline", "augmented"):
            search = goal.get(variant, {})
            if search.get("solved"):
                base_id, suffix = f"goal_{index}_{variant}", 0
                identifier = base_id
                while identifier in used_ids:
                    suffix += 1
                    identifier = f"{base_id}_{suffix}"
                used_ids.add(identifier)
                goals.append({"id": identifier, "source": goal["source"], "target": goal["target"], "path": search["path"]})
    natural_metadata = None
    if result["context"].get("domain") == "list-capacity":
        from .natural import build_natural_source
        source, expected, natural_metadata = build_natural_source(result)
        verification = verify_source(source, expected, timeout=timeout, allowed_axioms=("propext",))
    else:
        source = build_source(result["context"], candidates, goals)
        expected = ["pr_" + x["id"] for x in [result["context"]["seed"], *candidates, *goals]]
        verification = verify_source(source, expected, timeout=timeout)
    result["verification"] = verification
    result["lean_source"] = source
    audits = {a["name"]: a for a in verification["audits"]}
    for item in [result["seed"], *candidates]:
        audit = audits.get("pr_" + item["id"])
        item["status"] = verification["status"] if verification["status"] != "unavailable" else "proposed"
        if natural_metadata:
            item["proof"] = natural_metadata["declarations"]["pr_" + item["id"]]
            if item["id"] in natural_metadata.get("candidate_semantics", {}):
                semantics = natural_metadata["candidate_semantics"][item["id"]]
                item["explanation"] = semantics["explanation"]
                item["inference_rule"] = semantics["inference_rule"]
        else:
            item["proof"] = _declaration(result["context"], item, {result["seed"]["id"]: result["seed"]} if item is not result["seed"] else {})
        if audit:
            item.update(axioms=audit["axioms"], statement=audit["type"], dependencies=audit["constants"])
    if natural_metadata:
        if (result.get("ranking_model") or {}).get("kind") == "natural-list-capacity-context-bootstrap-ridge-v1":
            natural_metadata["limitations"][-1] = "Ranking is trained on generated list-pipeline proof workloads with held-out operator skeletons; transfer to external mathematical libraries remains unmeasured."
        elif result.get("metrics", {}).get("method") != "learned":
            natural_metadata["limitations"][-1] = "This run uses the displayed baseline selection policy. Learned models are evaluated separately on frozen proof workloads."
        imported = natural_metadata["imported_seed"]
        imported_audit = audits.get(imported["audit_name"])
        if imported_audit:
            imported.update(statement=imported_audit["type"], axioms=imported_audit["axioms"], dependencies=imported_audit["constants"])
        result["natural_domain"] = {k: v for k, v in natural_metadata.items() if k != "declarations"}
    result["timeline"] = [entry for entry in result.get("timeline", []) if entry.get("stage") in {"IMPORT", "UNDERSTAND", "EXPLORE"}]
    if natural_metadata:
        for entry in result["timeline"]:
            if entry.get("stage") == "IMPORT":
                entry["detail"] = "Validated typed list AST and imported registered Lean core theorem."
            elif entry.get("stage") == "UNDERSTAND":
                entry["detail"] = "Proved concrete primitive list-capacity arrows from registered library facts."
    result["timeline"].extend([
        {"stage": "PROVE", "status": verification["status"], "detail": f"Fresh Lean process; {len(audits)}/{len(expected)} declaration audits; axiom policy: {verification['axiom_policy']}."},
        {"stage": "EVALUATE", "detail": f"Equal-budget search comparison; successful witness certification: {verification['status']}."},
        {"stage": "EXPLAIN", "detail": "Deterministic witness-grounded explanations; exact Lean statements remain authoritative."}])
    return result
