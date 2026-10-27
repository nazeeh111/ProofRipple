"""Sound partial normalization for the shared-parameter List Nat calculus.

All filters use the same predicate p, maps the same function f, and takes the
same bound k. These identities do not extend to arbitrary separately
parameterized operations. Inner maps remain observable to later filters.

The result is a conservative equality key, not a complete equivalence prover.
No proof status or user-supplied normal-form field is consumed.
"""
from __future__ import annotations


_OPERATIONS = frozenset(("filter", "map", "reverse", "take"))
_INPUT = ("input", "xs")


def _all_p(expression):
    """Every element passes p; map deliberately invalidates this fact."""
    operation = expression[0]
    if operation == "filter":
        return True
    if operation in ("reverse", "take"):
        return _all_p(expression[1])
    return False


def _within_k(expression):
    """Length is at most k; every supported operation preserves this fact."""
    operation = expression[0]
    if operation == "take":
        return True
    if operation in ("filter", "map", "reverse"):
        return _within_k(expression[1])
    return False


def _apply(operation, parent):
    """Apply one operation to an already canonical list expression.

    Reordering moves reverse outward across map/filter and take outward across
    map. Recursion consumes one of those parent constructors; it cannot grow an
    expression or cycle. Conditional deletions use only the facts above.
    """
    if operation == "reverse" and parent[0] == "reverse":
        return parent[1]
    if operation == "filter" and _all_p(parent):
        return parent
    if operation == "take" and _within_k(parent):
        return parent
    if operation in ("filter", "map") and parent[0] == "reverse":
        return _apply("reverse", _apply(operation, parent[1]))
    if operation == "map" and parent[0] == "take":
        return _apply("take", _apply("map", parent[1]))
    return (operation, parent)


def canonical_expressions(context):
    """Return exact-list equality keys for data-only earlier-node ASTs.

    Full manifest validation remains the caller's responsibility. This helper
    also rejects unknown operators, forward references and malformed ASTs so a
    bad expression cannot silently become an equality key.
    """
    if not isinstance(context, dict) or not isinstance(context.get("nodes"), list):
        raise ValueError("Normalization requires a context with list stages")
    result = {}
    for node in context["nodes"]:
        if not isinstance(node, dict) or not isinstance(node.get("id"), str):
            raise ValueError("Every list stage needs a string identifier")
        identifier = node["id"]
        if identifier in result:
            raise ValueError("List stage identifiers must be unique")
        expression = node.get("expression")
        if not isinstance(expression, dict):
            raise ValueError("Every list stage needs an expression")
        operation = expression.get("op")
        if operation == "input":
            if set(expression) != {"op"} or result:
                raise ValueError("One initial input stage is required")
            result[identifier] = _INPUT
        elif isinstance(operation, str) and operation in _OPERATIONS:
            parent = expression.get("input")
            if (set(expression) != {"op", "input"} or not isinstance(parent, str)
                    or parent not in result):
                raise ValueError("List operations require an earlier input stage")
            result[identifier] = _apply(operation, result[parent])
        else:
            raise ValueError("Unsupported list operation")
    if not result:
        raise ValueError("A list input stage is required")
    return result


def _length_key(expression):
    operation = expression[0]
    if operation == "input":
        return ("length", "xs")
    if operation in ("map", "reverse"):
        return _length_key(expression[1])
    if operation == "take":
        previous = _length_key(expression[1])
        return previous if previous[0] == "min_k" else ("min_k", previous)
    # Keep the full canonical argument. A map below this filter can change p.
    return ("filter_length", expression[1])


def length_normal_forms(context):
    """Compatible length-equality keys, including common p/k identities."""
    return {identifier: _length_key(expression)
            for identifier, expression in canonical_expressions(context).items()}
