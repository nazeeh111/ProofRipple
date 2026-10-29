# Mathlib set-algebra workflow

ProofRipple supports inclusions between unions and intersections of up to six
arbitrary `Set Nat` values. It imports the registered Mathlib theorem
`inf_sup_left`, constructs seed-dependent consequences, and checks their
multi-premise proof trees in a separate Lean process.

## Run from source

Install Lean 4.33.1, then prepare the optional pinned Mathlib dependency:

```sh
python3 scripts/setup_mathlib.py
python3 -m proofripple doctor
python3 -m proofripple demo --domain mathlib --out outputs/mathlib-demo
python3 -m proofripple import-declaration inf_sup_left --out outputs/imported
python3 -m proofripple lab
```

[Setup details](mathlib-setup.md) describe the targeted cache and installed-wheel
configuration. Verification uses the existing compiler and library paths;
it does not download dependencies. The original list and implication domains
remain available through `--domain lists` and `--domain implications`.

## Change the selection policy

```sh
python3 -m proofripple demo --domain mathlib --method greedy_coverage --select 3 --budget 8
python3 -m proofripple demo --domain mathlib --method learned --select 3 --budget 8
python3 -m proofripple benchmark --domain mathlib --out outputs/mathlib-study --certify
```

The learned variants use the same frozen training artifact:
`learned`, `learned_no_bonus`, `structure_only` and `learned_singleton`.
The first three condition on the already selected portfolio; the singleton
ablation retains the static single-lemma objective. Other policies are
`greedy_coverage`, `branching_aware`, `graph`, `proof_cost`, `semantic` and
`random`. The semantic policy uses symbolic syntax similarity, not a pretrained
language model. Missing training artifacts produce an error rather than an
implicit fit on the supplied workload.

The proof-search budget counts visited raw syntax goal states, including failed
branches, cache hits and cycle checks. It differs from Lean's heartbeat limit
and from wall time. Selection work, candidate construction and kernel checks
are additional costs. Supplying a consequence can guide midpoint selection as
well as compress a proof. Bounded failure does not establish necessity.

## Python

```python
from proofripple.cli import run_context
from proofripple.mathlib_benchmark import make_example

run = run_context(make_example(), budget=8, select=3,
                  method="greedy_coverage", verify=True)
assert run["verification"]["status"] == "kernel_verified"
print(run["metrics"])
print(run["lean_source"])
```

`proofripple.mathlib_search.discover` performs exploration without Lean.
Its results remain proposals. `proofripple.mathlib.certify_mathlib_run`
validates the context, reconstructs every proof from registered rules, and
audits the exact declarations. Successful formal verification establishes the
emitted theorem statements and proofs; it does not certify empirical metric
bookkeeping or a natural-language interpretation.

## Supported data and trust

Terms use `var`, `join` and `meet` AST nodes. Proof trees retain both child
proofs for binary bounds, monotonicity and transitivity. The canonical Lean
context format is data plus generated source; appended arbitrary Lean commands
are rejected. General Mathlib modules and user-supplied tactics are not an
import interface.

This domain explicitly permits `propext`, `Classical.choice` and `Quot.sound`.
Admitted results, custom axioms and native-computation axioms are rejected.
The list domain still permits only propext, and the implication domain still
requires an empty axiom set. Imported JSON badges report saved evidence until
a fresh local run verifies it.

DNF antichains and joint variable renaming remove recognized equivalent
statements from the experiment. These keys do not close search goals for free.
Different endpoint keys mean a non-equivalent inclusion, not a strict subset
for every assignment. All consequences in this supported algebra are known
mathematics.
