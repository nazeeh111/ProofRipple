# Contributing

Use Python 3.10+ and the pinned Lean toolchain. Run `python -m unittest discover
-s tests -v`; without Lean the kernel tests explicitly skip. For changes to proof
construction, axiom policy or ranking, run the relevant certified domain benchmark and
include its outcomes digest and per-context audits. A changed benchmark outcome
needs an explanation, including regressions and changed costs.

The Mathlib adapter needs the optional pinned runtime from
`python scripts/setup_mathlib.py`. Run the focused adapter/search tests with
`python -m unittest discover -s tests -p 'test_mathlib*.py' -v`.
The published study can be reproduced with `benchmark --domain mathlib --certify
--frozen-protocol artifacts/mathlib`. That receipt rejects changed scientific
source or data. Changes to the study protocol require a new versioned freeze
before new evaluation outcomes are inspected. Keep prior evidence, regressions
and null results visible; do not tune against the published held-out outcomes.

Useful contributions include a well-scoped Lean/Mathlib adapter, corpus-relative
equivalence checks, natural mathematical benchmark families with leakage audits,
and ranking ablations. Keep new datasets licensed and attributed. Do not present
a search failure as mathematical necessity or a new endpoint pair as a globally
new theorem. Add tests for trust-boundary or behavioral changes rather than
mirroring internal implementation details.
