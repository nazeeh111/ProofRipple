"""Closed Mathlib set-lattice adapter with checked multi-premise proof trees.

Inputs contain data, never arbitrary Lean code. DNF normalization is used for
equivalence exclusions only; it does not silently solve bounded search goals.
"""
from __future__ import annotations

import copy
from functools import lru_cache
import itertools
import json

from .lean import _audit_many, _ident
from .mathlib_runtime import ALLOWED_AXIOMS, IMPORTS, MATHLIB_REVISION, verify_mathlib_source

DOMAIN = "mathlib-set-lattice"
LIBRARY_FACTS = ("inf_sup_left", "sup_le", "le_inf", "sup_le_sup", "inf_le_inf",
                 "le_trans", "inf_le_left", "inf_le_right", "le_sup_left", "le_sup_right")


def validate_term(term, variables=6):
    if not isinstance(variables, int) or isinstance(variables, bool) or not 1 <= variables <= 6:
        raise ValueError("Set-lattice contexts support one to six set variables")
    remaining = 127
    def visit(node, depth):
        nonlocal remaining
        remaining -= 1
        if remaining < 0 or depth > 12 or not isinstance(node, dict):
            raise ValueError("Set term exceeds the 127-node / depth-12 limit")
        if node.get("op") == "var":
            index = node.get("index")
            if set(node) != {"op", "index"} or not isinstance(index, int) or isinstance(index, bool) or not 0 <= index < variables:
                raise ValueError("A set variable needs an in-range integer index")
        elif node.get("op") in {"join", "meet"}:
            if set(node) != {"op", "left", "right"}:
                raise ValueError("A set operation needs exactly left and right terms")
            visit(node["left"], depth + 1)
            visit(node["right"], depth + 1)
        else:
            raise ValueError("Supported set operations: var, join, meet")
    visit(term, 0)
    return term


def _minimal(masks):
    ordered = sorted(set(masks), key=lambda x: (x.bit_count(), x))
    answer = []
    for mask in ordered:
        if not any(prior & mask == prior for prior in answer):
            answer.append(mask)
    return tuple(sorted(answer))


def normal_form(term):
    """Positive Boolean DNF antichain: bit masks denote conjunction clauses."""
    validate_term(term)
    def visit(node):
        if node["op"] == "var":
            return (1 << node["index"],)
        a, b = visit(node["left"]), visit(node["right"])
        return _minimal((*a, *b) if node["op"] == "join" else (x | y for x in a for y in b))
    return visit(term)


@lru_cache(maxsize=65536)
def _alpha_key(left, right):
    used = [i for i in range(6) if any(mask & (1 << i) for mask in left + right)]
    groups = {}
    # These occurrence invariants are unchanged by renaming. Only permutations
    # within equal groups are needed, including all ties rather than guessing.
    for i in used:
        signature = tuple(tuple(sorted(mask.bit_count() for mask in side if mask & (1 << i))) for side in (left, right))
        groups.setdefault(signature, []).append(i)
    groups = [groups[key] for key in sorted(groups)]
    best = None
    for choices in itertools.product(*(itertools.permutations(group) for group in groups)):
        order = tuple(i for group in choices for i in group)
        mapping = {old: 1 << new for new, old in enumerate(order)}
        def rename(side):
            return tuple(sorted(sum(mapping[i] for i in used if mask & (1 << i)) for mask in side))
        key = (rename(left), rename(right))
        if best is None or key < best:
            best = key
    return best


def statement_key(source, target, alpha=True):
    left, right = normal_form(source), normal_form(target)
    return _alpha_key(left, right) if alpha else (left, right)


def semantic_le(source, target):
    """Generation/review diagnostic only, never an uncharged search rule."""
    left, right = normal_form(source), normal_form(target)
    return all(any(b & a == b for b in right) for a in left)


def render_term(term):
    validate_term(term)
    def render(node):
        if node["op"] == "var":
            return "A" + str(node["index"])
        op = "∪" if node["op"] == "join" else "∩"
        return f"({render(node['left'])} {op} {render(node['right'])})"
    return render(term)


term_text = render_term


def _ast(item):
    value = item.get("proof_ast", item.get("proof"))
    if not isinstance(value, dict):
        raise ValueError("A generated consequence needs its data-only proof AST")
    return value


def infer_proof(proof, known=None, variables=6):
    """Infer and check both endpoints of every registered inference rule."""
    known = known or {}
    remaining = 4096
    def visit(node, depth):
        nonlocal remaining
        remaining -= 1
        if remaining < 0 or depth > 64 or not isinstance(node, dict):
            raise ValueError("Set proof exceeds the bounded proof-tree limit")
        source, target = node.get("source"), node.get("target")
        validate_term(source, variables)
        validate_term(target, variables)
        rule, children = node.get("rule"), node.get("children", [])
        if not isinstance(children, list) or len(children) > 2:
            raise ValueError("Proof children must contain at most two premises")
        pairs = [visit(child, depth + 1) for child in children]
        valid = False
        if rule == "refl" and not pairs:
            valid = source == target
        elif rule == "seed" and not pairs:
            if source.get("op") == "meet" and source["right"].get("op") == "join":
                a, b, c = source["left"], source["right"]["left"], source["right"]["right"]
                valid = target == {"op": "join", "left": {"op": "meet", "left": a, "right": b},
                                   "right": {"op": "meet", "left": a, "right": c}}
        elif rule in {"inf_left", "inf_right"} and not pairs:
            valid = source.get("op") == "meet" and target == source["left" if rule == "inf_left" else "right"]
        elif rule in {"sup_left", "sup_right"} and not pairs:
            valid = target.get("op") == "join" and source == target["left" if rule == "sup_left" else "right"]
        elif rule == "lemma" and not pairs:
            item = known.get(node.get("lemma_id"))
            valid = item is not None and (source, target) == (item["source"], item["target"])
        elif len(pairs) == 2:
            (a, b), (c, d) = pairs
            if rule == "trans":
                valid = b == c and (source, target) == (a, d)
            elif rule == "sup_le":
                valid = b == d and source == {"op": "join", "left": a, "right": c} and target == b
            elif rule == "le_inf":
                valid = a == c and source == a and target == {"op": "meet", "left": b, "right": d}
            elif rule in {"sup_mono", "inf_mono"}:
                op = "join" if rule == "sup_mono" else "meet"
                valid = source == {"op": op, "left": a, "right": c} and target == {"op": op, "left": b, "right": d}
        if not valid:
            raise ValueError(f"Invalid or unregistered lattice proof rule: {rule}")
        return source, target
    return visit(proof, 0)


def proof_uses_seed(proof):
    return proof.get("rule") == "seed" or any(proof_uses_seed(child) for child in proof.get("children", []))


def _proof_term(proof, variables):
    rule = proof["rule"]
    if rule == "seed":
        source = proof["source"]
        a, b, c = source["left"], source["right"]["left"], source["right"]["right"]
        return f"(pr_distributivity {render_term(a)} {render_term(b)} {render_term(c)})"
    if rule == "lemma":
        return "(pr_" + _ident(proof["lemma_id"]) + " " + " ".join("A" + str(i) for i in range(variables)) + ")"
    leaves = {"refl": "le_rfl", "inf_left": "inf_le_left", "inf_right": "inf_le_right",
              "sup_left": "le_sup_left", "sup_right": "le_sup_right"}
    if rule in leaves:
        return leaves[rule]
    name = {"trans": "le_trans", "sup_le": "sup_le", "le_inf": "le_inf",
            "sup_mono": "sup_le_sup", "inf_mono": "inf_le_inf"}[rule]
    return "(" + name + " " + " ".join(_proof_term(child, variables) for child in proof["children"]) + ")"


def validate_context(context):
    if not isinstance(context, dict) or context.get("domain") != DOMAIN:
        raise ValueError("Expected a registered Mathlib set-lattice context")
    variables = context.get("variables", 6)
    validate_term({"op": "var", "index": 0}, variables)
    seed = context.get("seed", {})
    if not isinstance(seed, dict) or seed.get("id") != "distributivity" or seed.get("declaration") != "inf_sup_left":
        raise ValueError("Registered Mathlib seed: inf_sup_left (distributivity)")
    candidates, goals = context.get("candidates", []), context.get("goals", [])
    if not isinstance(candidates, list) or len(candidates) > 256 or not isinstance(goals, list) or len(goals) > 128:
        raise ValueError("Context limit: 256 consequences and 128 goals")
    ids = {"distributivity"}
    goal_keys = set()
    for goal in goals:
        if not isinstance(goal, dict) or not all(key in goal for key in ("id", "source", "target")):
            raise ValueError("Each lattice goal needs an identifier and both endpoints")
        _ident(goal["id"])
        if goal["id"] in ids:
            raise ValueError("Duplicate lattice declaration identifier")
        ids.add(goal["id"])
        validate_term(goal["source"], variables)
        validate_term(goal["target"], variables)
        goal_keys.add(statement_key(goal["source"], goal["target"]))
    candidate_keys = set()
    for item in candidates:
        if not isinstance(item, dict) or not all(key in item for key in ("id", "source", "target")):
            raise ValueError("Each lattice consequence needs an identifier and both endpoints")
        _ident(item["id"])
        if item["id"] in ids:
            raise ValueError("Duplicate lattice declaration identifier")
        ids.add(item["id"])
        proof = _ast(item)
        if infer_proof(proof, variables=variables) != (item["source"], item["target"]):
            raise ValueError("Candidate endpoints differ from its inferred proof")
        if not proof_uses_seed(proof):
            raise ValueError("Every consequence proof must use the imported seed")
        key = statement_key(item["source"], item["target"])
        if key[0] == key[1] or key in goal_keys or key in candidate_keys:
            raise ValueError("Consequence is equivalent, duplicated or a held-out goal")
        source, target = item["source"], item["target"]
        if ((source.get("op") == "meet" and target in (source["left"], source["right"]))
                or (target.get("op") == "join" and source in (target["left"], target["right"]))):
            raise ValueError("Consequence is already a direct registered projection/injection")
        candidate_keys.add(key)
    return context


def build_mathlib_source(run):
    context = validate_context(run["context"])
    variables = context.get("variables", 6)
    binders = "(" + " ".join("A" + str(i) for i in range(variables)) + " : Set Nat)"
    header = "\n".join("import " + name for name in (*IMPORTS, "Lean")) + "\nopen Lean Elab Command\n\n"
    declarations = {"pr_distributivity": "theorem pr_distributivity (A B C : Set Nat) : A ∩ (B ∪ C) ⊆ (A ∩ B) ∪ (A ∩ C) :=\n  (inf_sup_left A B C).le\n"}
    candidates = run.get("candidates", [])
    if not isinstance(candidates, list) or any(not isinstance(item, dict) for item in candidates):
        raise ValueError("Run consequences must be a list of objects")
    expected_pool = {item["id"]: item for item in context["candidates"]}
    known = {}
    names = [*LIBRARY_FACTS, "pr_distributivity"]
    for item in candidates:
        identifier = _ident(item["id"])
        original = expected_pool.get(identifier)
        if original is None or (item["source"], item["target"], _ast(item)) != (original["source"], original["target"], _ast(original)):
            raise ValueError("Run consequence differs from its validated context pool")
        proof = _ast(item)
        infer_proof(proof, variables=variables)
        name = "pr_" + identifier
        declarations[name] = f"theorem {name} {binders} : {render_term(item['source'])} ⊆ {render_term(item['target'])} :=\n  {_proof_term(proof, variables)}\n"
        names.append(name)
        known[identifier] = item
    if len(known) != len(candidates) or set(known) != set(expected_pool):
        raise ValueError("Run must retain every canonical consequence exactly once")
    selected = run.get("selected", [])
    if not isinstance(selected, list) or any(not isinstance(identifier, str) for identifier in selected) or len(set(selected)) != len(selected) or not set(selected).issubset(known):
        raise ValueError("Selected consequence identifiers are invalid")
    selected_known = {identifier: known[identifier] for identifier in selected}
    used = set(names)
    goals = run.get("goals", [])
    if not isinstance(goals, list) or any(not isinstance(goal, dict) for goal in goals):
        raise ValueError("Run goals must be a list of objects")
    if [(goal.get("id"), goal.get("source"), goal.get("target")) for goal in goals] != [(goal["id"], goal["source"], goal["target"]) for goal in context["goals"]]:
        raise ValueError("Run goals differ from the validated context workload")
    goal_declarations = []
    for index, goal in enumerate(goals):
        for variant in ("baseline", "augmented"):
            result = goal.get(variant, {})
            if not isinstance(result, dict):
                raise ValueError("Goal search evidence must be an object")
            if not result.get("solved"):
                continue
            proof = result.get("proof")
            if infer_proof(proof, selected_known if variant == "augmented" else {}, variables) != (goal["source"], goal["target"]):
                raise ValueError("Successful goal witness proves different endpoints")
            base = f"pr_goal_{index}_{variant}"
            name, suffix = base, 0
            while name in used:
                suffix += 1
                name = base + "_" + str(suffix)
            used.add(name)
            declarations[name] = f"theorem {name} {binders} : {render_term(goal['source'])} ⊆ {render_term(goal['target'])} :=\n  {_proof_term(proof, variables)}\n"
            names.append(name)
            goal_declarations.append({"goal_id": goal["id"], "variant": variant, "name": name})
    source = header + "\n".join(declarations.values()) + "\n" + _audit_many(names)
    metadata = {"domain": DOMAIN, "library_revision": MATHLIB_REVISION,
                "allowed_axioms": list(ALLOWED_AXIOMS), "declarations": declarations,
                "goal_declarations": goal_declarations,
                "imported_seed": {"name": "inf_sup_left", "audit_name": "inf_sup_left"},
                "interpretation": f"Universally quantified inclusions between {variables} arbitrary sets of natural numbers. Union/intersection rules may require two premises. DNF equivalence exclusions are not free search steps.",
                "limitations": ["Registered positive set algebra only; no arbitrary Mathlib theorem import.",
                                "Consequences are known mathematics with novelty only relative to the bounded search registry.",
                                "Distinct normalized endpoints do not imply strict inclusion for every set assignment."]}
    return source, names, metadata


def build_automation_source(goals, variables=6):
    """Strong control: unfold membership, then ordinary aesop, without new facts.

    The same verifier enforces j1 / 2048 MB / 400000 heartbeats and an explicit
    timeout. These units differ from the bounded AND/OR search experiment.
    """
    validate_term({"op": "var", "index": 0}, variables)
    binders = "(" + " ".join("A" + str(i) for i in range(variables)) + " : Set Nat)"
    source = "\n".join("import " + name for name in (*IMPORTS, "Lean")) + "\nopen Lean Elab Command\n\n"
    names = []
    for item in goals:
        validate_term(item["source"], variables)
        validate_term(item["target"], variables)
        name = "control_" + _ident(item["id"])
        if name in names:
            raise ValueError("Duplicate automation-control goal")
        names.append(name)
        source += f"theorem {name} {binders} : {render_term(item['source'])} ⊆ {render_term(item['target'])} := by\n  intro x hx\n  simp only [Set.mem_union, Set.mem_inter] at *\n  aesop\n\n"
    return source + _audit_many(names), names


def certify_mathlib_run(run, timeout=60):
    result = copy.deepcopy(run)
    source, names, metadata = build_mathlib_source(result)
    from .engine import context_hash
    result["context_sha256"] = context_hash(result["context"])
    check = verify_mathlib_source(source, names, timeout)
    audits = {item["name"]: item for item in check["audits"]}
    for item in result["candidates"]:
        item["proof_ast"] = copy.deepcopy(_ast(item))
        item["proof"] = metadata["declarations"]["pr_" + item["id"]]
        item["status"] = check["status"] if check["status"] != "unavailable" else "proposed"
        audit = audits.get("pr_" + item["id"])
        item.update(statement=audit["type"] if audit else None,
                    axioms=audit["axioms"] if audit else None,
                    dependencies=audit["constants"] if audit else [])
        item["explanation"] = {"summary": f"{render_term(item['source'])} ⊆ {render_term(item['target'])}",
                               "why_useful": "A reusable seed-dependent inclusion; measured downstream search results are shown separately."}
    imported = metadata["imported_seed"]
    if imported["audit_name"] in audits:
        audit = audits[imported["audit_name"]]
        imported.update(statement=audit["type"], axioms=audit["axioms"], dependencies=audit["constants"])
    result["seed"] = copy.deepcopy(result["context"]["seed"])
    result["seed"].update(status=check["status"], proof=metadata["declarations"]["pr_distributivity"])
    seed_audit = audits.get("pr_distributivity")
    if seed_audit:
        result["seed"].update(statement=seed_audit["type"], axioms=seed_audit["axioms"], dependencies=seed_audit["constants"])
    result.update(verification=check, lean_source=source,
                  mathlib_domain={key: value for key, value in metadata.items() if key != "declarations"})
    result["timeline"] = [
        {"stage": "IMPORT", "detail": "Loaded the pinned Mathlib set-lattice theorem and audited its exact type."},
        {"stage": "UNDERSTAND", "detail": "Registered binary union/intersection inference rules."},
        {"stage": "EXPLORE", "detail": f"{len(result['candidates'])} non-equivalent, seed-dependent inclusions."},
        {"stage": "PROVE", "status": check["status"], "detail": f"{len(audits)}/{len(names)} fresh Lean declaration audits."},
        {"stage": "EVALUATE", "detail": "Compared bounded search under the displayed lemma and expansion budgets."},
        {"stage": "EXPLAIN", "detail": "Inspect the actual multi-premise proof tree and exported Lean term."}]
    return result
