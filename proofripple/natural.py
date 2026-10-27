"""Closed Lean source generation for real ``List Nat`` capacity theorems.

The graph search still proposes implication shortcuts. Here the propositions
are concrete length bounds and primitive arrows are proved from Lean's List
library, rather than quantified implication assumptions. This is a deliberately
small registered calculus, not unrestricted natural-language formalization.
"""
from __future__ import annotations

import copy

from .engine import validate_context
from .lean import TOOLCHAIN, _audit_many, _ident

OPS = ("filter", "map", "reverse", "take")
CORE_THEOREMS = (
    "List.length_filter_le", "List.length_map", "List.length_reverse",
    "List.length_take_le'", "List.length_append", "Nat.le_trans", "Nat.add_le_add",
)
HELPER_NAMES = tuple("prx_step_" + op for op in OPS)
EXTRA_NAMES = ("prx_filtered_budget", "prx_paired_budget", "prx_combined_buffer_safe")
PARAMETERS = "(xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat)"
ARGS = "xs f p k cap"
STAGE_ARGS = "xs f p k"


def validate_natural_context(context):
    """Accept only a bounded, typed expression AST with proved monotone edges.

    AST means an expression tree represented by earlier-node references. No
    supplied Lean text, executable commands, or proof strings are consumed.
    Every primitive graph edge must follow the expression's ancestry.
    """
    try:
        validate_context(context)
    except (TypeError, KeyError, AttributeError) as exc:
        raise ValueError("Malformed list-capacity manifest") from exc
    if context.get("domain") != "list-capacity":
        raise ValueError("Expected domain='list-capacity'")
    if len(context["edges"]) > 1024:
        raise ValueError("List capacity contexts support at most 1024 edges")
    earlier = set()
    inputs = 0
    for node in context["nodes"]:
        expression = node.get("expression")
        if not isinstance(expression, dict):
            raise ValueError("Each list stage needs a typed expression object")
        operation = expression.get("op")
        if operation == "input":
            if set(expression) != {"op"}:
                raise ValueError("Input stages accept only the 'op' key")
            inputs += 1
            if earlier:
                raise ValueError("The list input must be the first stage")
        elif operation in OPS:
            if (set(expression) != {"op", "input"} or not isinstance(expression.get("input"), str)
                    or expression["input"] not in earlier):
                raise ValueError("List operations need exactly one earlier input-stage identifier")
        else:
            raise ValueError("Unsupported list operation; choose input/filter/map/reverse/take")
        earlier.add(node["id"])
    if inputs != 1:
        raise ValueError("Exactly one initial List Nat input stage is required")
    for edge in context["edges"]:
        _ancestor_operations(context, edge["source"], edge["target"])
    return context


def _ancestor_operations(context, source, target):
    nodes = {node["id"]: node for node in context["nodes"]}
    if source not in nodes or target not in nodes:
        raise ValueError("Unknown list-stage endpoint")
    operations = []
    current = target
    while current != source:
        expression = nodes[current]["expression"]
        if expression["op"] == "input":
            raise ValueError("A list-capacity edge must run from a strict expression ancestor to its descendant")
        operations.append(current)
        current = expression["input"]
    if not operations:
        raise ValueError("Identity list-capacity edges are unsupported")
    return list(reversed(operations))


def _stage(identifier):
    return f"(stage_{_ident(identifier)} {STAGE_ARGS})"


def length_normal_forms(context):
    """Sound partial keys, including the registered shared-predicate/k laws."""
    validate_natural_context(context)
    from .normalization import length_normal_forms as normalize
    return normalize(context)


def filter_redundant_candidates(context, candidates, goals=()):
    """One normalized pool for all policies, excluding equivalent held-out goals.

    Strip length-preserving outer maps/reversals and repeated same-k minima.
    This is conservative normalization, not a complete theorem-equivalence test.
    """
    forms = length_normal_forms(context)
    pair = lambda item: (forms[item["source"]], forms[item["target"]])
    known = {pair(item) for item in [*context["edges"], context["seed"]]}
    held_out = {pair(item) for item in goals}
    groups = {}
    def cost(item):
        return (sum(len(context["seed"]["path"]) if eid == context["seed"]["id"] else 1 for eid in item["path"]), item["id"])
    for item in sorted(candidates, key=cost):
        signature = pair(item)
        if signature in known or signature in held_out or signature[0] == signature[1] or signature in groups:
            continue
        item["normal_form"] = repr(signature)
        item["novelty"] = "Unindexed composition in a restricted registry; elementary known mathematics, with conservative length-equivalence filtering."
        groups[signature] = item
    return list(groups.values())


def _definitions(context):
    lines = []
    for node in context["nodes"]:
        expression = node["expression"]
        operation = expression["op"]
        if operation == "input":
            value = "xs"
        else:
            parent = _stage(expression["input"])
            value = {"filter": f"{parent}.filter p", "map": f"{parent}.map f",
                     "reverse": f"{parent}.reverse", "take": f"{parent}.take k"}[operation]
        lines.append(f"def stage_{_ident(node['id'])} (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=\n  {value}\n")
    return "\n".join(lines)


HELPERS = '''theorem prx_step_filter (xs : List Nat) (p : Nat → Bool) (cap : Nat) :
    xs.length ≤ cap → (xs.filter p).length ≤ cap :=
  fun h => Nat.le_trans (List.length_filter_le p xs) h

theorem prx_step_map (xs : List Nat) (f : Nat → Nat) (cap : Nat) :
    xs.length ≤ cap → (xs.map f).length ≤ cap := by
  rw [List.length_map]
  exact fun h => h

theorem prx_step_reverse (xs : List Nat) (cap : Nat) :
    xs.length ≤ cap → xs.reverse.length ≤ cap := by
  rw [List.length_reverse]
  exact fun h => h

theorem prx_step_take (xs : List Nat) (k cap : Nat) :
    xs.length ≤ cap → (xs.take k).length ≤ cap :=
  fun h => Nat.le_trans (List.length_take_le' k xs) h
'''


EXTRAS = '''-- Registered append/addition inference templates, not graph-discovered claims.
theorem prx_filtered_budget (xs : List Nat) (p : Nat → Bool) (f : Nat → Nat) :
    (((xs.filter p).map f).reverse).length ≤ xs.length := by
  rw [List.length_reverse, List.length_map]
  exact List.length_filter_le p xs

theorem prx_paired_budget (xs ys : List Nat) (p q : Nat → Bool)
    (f : Nat → Nat) (k : Nat) :
    ((((xs.filter p).map f).reverse) ++ ((ys.filter q).take k).map f).length ≤
      xs.length + ys.length := by
  rw [List.length_append]
  apply Nat.add_le_add (prx_filtered_budget xs p f)
  rw [List.length_map]
  exact Nat.le_trans (List.length_take_le' k (ys.filter q)) (List.length_filter_le q ys)

theorem prx_combined_buffer_safe (xs ys : List Nat) (p q : Nat → Bool)
    (f : Nat → Nat) (k cap : Nat) (fits : xs.length + ys.length ≤ cap) :
    ((((xs.filter p).map f).reverse) ++ ((ys.filter q).take k).map f).length ≤ cap :=
  Nat.le_trans (prx_paired_budget xs ys p q f k) fits
'''


def _capacity_statement(item):
    return f"{_stage(item['source'])}.length ≤ cap → {_stage(item['target'])}.length ≤ cap"


def _primitive_declaration(context, edge):
    nodes = {node["id"]: node for node in context["nodes"]}
    term = "hx"
    for target in _ancestor_operations(context, edge["source"], edge["target"]):
        expression = nodes[target]["expression"]
        operation = expression["op"]
        parent = _stage(expression["input"])
        operation_args = {"filter": "p cap", "map": "f cap", "reverse": "cap", "take": "k cap"}[operation]
        term = f"(prx_step_{operation} {parent} {operation_args} {term})"
    return f"theorem pr_{_ident(edge['id'])} {PARAMETERS} :\n    {_capacity_statement(edge)} :=\n  fun hx => {term}\n"


def _path_declaration(context, item, known):
    nodes = {node["id"] for node in context["nodes"]}
    if item.get("source") not in nodes or item.get("target") not in nodes:
        raise ValueError("Unknown consequence endpoint")
    path = item.get("path")
    if not isinstance(path, list) or len(path) > 128:
        raise ValueError("A concrete bounded theorem witness is required")
    current, term = item["source"], "hx"
    for identifier in path:
        _ident(identifier)
        dependency = known.get(identifier)
        if dependency is None or dependency["source"] != current:
            raise ValueError("Unknown or non-composable natural proof dependency")
        term = f"(pr_{identifier} {ARGS} {term})"
        current = dependency["target"]
    if current != item["target"]:
        raise ValueError("Natural proof witness has the wrong conclusion")
    return f"theorem pr_{_ident(item['id'])} {PARAMETERS} :\n    {_capacity_statement(item)} :=\n  fun hx => {term}\n"


def _successful_goals(run):
    context = run["context"]
    used = {_ident(item["id"]) for item in [*context["nodes"], *context["edges"],
                                           context["seed"], *run.get("candidates", [])]}
    goals = []
    for index, goal in enumerate(run.get("goals", [])):
        for variant in ("baseline", "augmented"):
            outcome = goal.get(variant, {})
            if outcome.get("solved"):
                base = f"goal_{index}_{variant}"
                identifier = base
                suffix = 1
                while identifier in used:
                    identifier = f"{base}_proof{suffix}"
                    suffix += 1
                used.add(_ident(identifier))
                goals.append({"id": identifier, "source": goal["source"],
                              "target": goal["target"], "path": outcome["path"]})
    return goals


def build_natural_source(run):
    """Return standalone Lean source, exact audit names, and honest metadata.

    Incoming verification flags/proof strings are ignored. Audits include the
    imported theorem's actual elaborated type, transitive axioms, and constants
    occurring in its checked proof body, obtained by Lean's environment API.
    """
    context = run["context"]
    validate_natural_context(context)
    declarations = [_definitions(context), HELPERS]
    known = {}
    roles = {name: "imported_library_theorem" for name in CORE_THEOREMS}
    roles.update({"stage_" + node["id"]: "concrete_list_definition" for node in context["nodes"]})
    roles.update({name: "registered_length_inference" for name in HELPER_NAMES})
    for edge in context["edges"]:
        declarations.append(_primitive_declaration(context, edge))
        known[edge["id"]] = edge
        roles["pr_" + edge["id"]] = "closed_primitive_capacity_theorem"
    items = [context["seed"], *run.get("candidates", []), *_successful_goals(run)]
    for index, item in enumerate(items):
        identifier = _ident(item["id"])
        if identifier in known:
            raise ValueError("Duplicate natural declaration identifier")
        declarations.append(_path_declaration(context, item, known))
        known[identifier] = item
        roles["pr_" + identifier] = "seed" if index == 0 else "composed_consequence_or_goal"
    declarations.append(EXTRAS)
    roles.update({name: "registered_append_addition_template" for name in EXTRA_NAMES})
    names = list(roles)
    source = "import Lean\nopen Lean Elab Command\n\n" + "\n".join(declarations) + "\n" + _audit_many(names)
    metadata = {
        "domain": "list-capacity", "toolchain": TOOLCHAIN,
        "meaning": "Each graph node denotes the actual proposition (stage xs f p k).length ≤ cap. Primitive edges are closed List Nat theorems; no arbitrary Prop or implication-edge hypotheses are assumed.",
        "imported_seed": {"name": "List.length_filter_le", "audit_name": "List.length_filter_le",
                          "source": "Lean core library at the pinned toolchain", "role": "registered seed length-bound theorem",
                          "evidence": "The verifier must read its exact type, transitive axioms and proof-body constants from the named Lean audit; these are not inferred from labels."},
        "allowed_axioms": ["propext"], "audit_roles": roles,
        "registered_operations": list(OPS),
        "candidate_semantics": {
            item["id"]: {"inference_rule": "capacity-bound transitivity",
                         "explanation": f"Compose {len(item['path'])} closed capacity theorems through the seed to transport the bound from {item['source']} to {item['target']}. Each stage is a concrete List Nat expression; this is a registered composition consequence, not a claim of new mathematics."}
            for item in run.get("candidates", [])},
        "registered_templates": [
            {"name": name, "kind": "registered_inference_template", "discovered": False,
             "explanation": "A fixed, disclosed append/addition rule demonstrates a concrete two-buffer capacity consequence. The graph exploration did not invent this rule."}
            for name in EXTRA_NAMES],
        "declarations": {"pr_" + item["id"]: _path_declaration(context, item, {key: value for key, value in known.items() if key != item["id"]}) for item in items},
        "limitations": ["A small registered list-length calculus, not arbitrary Lean theorem discovery.",
                        "Graph search savings do not establish superiority to Lean's general automation.",
                        "The labels are explanations; the exact typed List Nat statements are authoritative.",
                        "The existing usefulness model was trained on procedural implication graphs; transfer to natural mathematical families is unmeasured."]}
    return source, names, metadata


def build_automation_baseline(context, generation=32):
    """Direct Lean automation on the exact goals, with no discovered theorems.

    Definitions are transparently unfolded before ``grind``. No seed, graph-edge
    theorem, helper length lemma, or candidate declaration is supplied. Lean's
    standard imported automation remains free to retrieve its library facts.
    """
    validate_natural_context(context)
    if not isinstance(generation, int) or isinstance(generation, bool) or not 1 <= generation <= 64:
        raise ValueError("Automation generation limit must be an integer between 1 and 64")
    stage_names = ", ".join("stage_" + node["id"] for node in context["nodes"])
    declarations, names = [_definitions(context)], []
    for index, goal in enumerate(context.get("goals", [])):
        name = f"automation_goal_{index}"
        declarations.append(f"theorem {name} {PARAMETERS} :\n    {_capacity_statement(goal)} := by\n  dsimp [{stage_names}]\n  grind (gen := {generation})\n")
        names.append(name)
    declarations.append('''theorem automation_combined_buffer_safe (xs ys : List Nat) (p q : Nat → Bool)
    (f : Nat → Nat) (k cap : Nat) (fits : xs.length + ys.length ≤ cap) :
    ((((xs.filter p).map f).reverse) ++ ((ys.filter q).take k).map f).length ≤ cap := by
  grind (gen := GENERATION)
''')
    declarations[-1] = declarations[-1].replace("GENERATION", str(generation))
    names.append("automation_combined_buffer_safe")
    source = "import Lean\nopen Lean Elab Command\n\n" + "\n".join(declarations) + "\n" + _audit_many(names)
    return source, names


def make_example():
    """A disclosed, illustrative pipeline; its typed AST is the input authority."""
    operations = ["input", "filter", "map", "reverse", "take", "filter", "map", "reverse", "take", "filter", "map", "reverse"]
    nodes = []
    for index, operation in enumerate(operations):
        expression = {"op": operation}
        if index:
            expression["input"] = f"p{index - 1}"
        nodes.append({"id": f"p{index}", "label": "Input capacity" if index == 0 else f"Stage {index}: {operation} capacity", "expression": expression})
    context = {"id": "list_capacity", "domain": "list-capacity", "title": "Verified list-pipeline capacity",
               "description": "A concrete List Nat pipeline of filter, map, reverse and take operations. Each stage's length is at most its input capacity. The registered append/addition template also proves a two-buffer capacity consequence; it is not claimed as an invented theorem.",
               "nodes": nodes,
               "edges": [{"id": f"h{i}", "source": f"p{i}", "target": f"p{i + 1}"} for i in range(len(nodes) - 1)],
               "seed": {"id": "breakthrough", "source": "p4", "target": "p6", "path": ["h4", "h5"]},
               "goals": [{"id": "goal_input", "source": "p0", "target": "p11"},
                         {"id": "goal_mapped", "source": "p2", "target": "p11"}]}
    return copy.deepcopy(validate_natural_context(context))
