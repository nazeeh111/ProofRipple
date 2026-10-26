# Contributing

Use Python 3.10+ and the pinned Lean toolchain. Run `python -m unittest discover
-s tests -v`; without Lean the kernel tests explicitly skip. For changes to proof
construction, axiom policy or ranking, run the full certified benchmark and
include its outcomes digest and per-context audits. A changed benchmark outcome
needs an explanation, including regressions and changed costs.

Useful contributions include a well-scoped Lean/Mathlib adapter, corpus-relative
equivalence checks, natural mathematical benchmark families with leakage audits,
and ranking ablations. Keep new datasets licensed and attributed. Do not present
a search failure as mathematical necessity or a new endpoint pair as a globally
new theorem. Add tests for trust-boundary or behavioral changes rather than
mirroring internal implementation details.
