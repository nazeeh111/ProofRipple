# Mathlib domain design: distributive-lattice consequence selection

Status: runtime and proof-schema feasibility verified on 27 October 2026.
This document specifies the selected follow-on domain; it does not report a
completed ranking benchmark. The implementation and outcome report must retain
that distinction.

## Selected domain and actual runtime

Use concrete sets of natural numbers, ordered by inclusion, with intersection
and union as lattice meet and join. This changes the reasoning structure from
a chain of nonexpansive operations to binary expression trees and multi-premise
inference. Imported Mathlib theorem `inf_sup_left` supplies distributivity;
closed candidate proofs combine it with projections, transitivity and binary
lattice bounds. No implication-edge validity is assumed as a free hypothesis.

The pinned source is Mathlib tag `v4.33.1`, commit
`0df444a360eaa60ab8c11dca51a86af692955474`. Its checked-in `lean-toolchain`
requires `leanprover/lean4:v4.33.1`, matching the existing installed toolchain.
The durable, task-local runtime is `.runtime/mathlib-v4.33.1/`; it is a local
dependency, not a source or release artifact.

The trial fetched the official cache for `Mathlib.Order.Lattice`, then compared
`Mathlib.Data.Set.Lattice` and `Mathlib.Data.Finset.Card`. It downloaded 627
compiled-file archives in total, about 57 MB compressed. The source checkout,
eight pinned dependency repositories and unpacked artifacts occupy about 1 GB.
Only the cache utility was compiled locally; no full Mathlib build occurred.
The final chosen lattice domain does not require the exploratory Finset module.
The dependency closure was successfully rechecked after relocation into the
durable runtime. Exact cache counts are observations of this trial, not a
promise about future Mathlib versions.

A fresh setup can use the following scoped route, with the cache directory
chosen in non-synced temporary storage and without changing the user's default
Lean toolchain:

```sh
git clone --depth 1 --branch v4.33.1 https://github.com/leanprover-community/mathlib4.git .runtime/mathlib-v4.33.1
cd .runtime/mathlib-v4.33.1
MATHLIB_NO_CACHE_ON_UPDATE=1 MATHLIB_CACHE_DIR=/private/tmp/proofripple-mathlib-cache ELAN_TOOLCHAIN=leanprover/lean4:v4.33.1 lake exe cache get Mathlib/Order/Lattice.lean Mathlib/Data/Set/Lattice.lean
```

The cache's [official source](https://github.com/leanprover-community/mathlib4/blob/v4.33.1/Cache/Main.lean)
explicitly supports fetching named modules and their import closures. Do not
use argument-free `cache get`, which targets the complete Mathlib root.
No credential, provider API, GPU or paid service was used. Mathlib's
[Apache-2.0 license](https://github.com/leanprover-community/mathlib4/blob/v4.33.1/LICENSE)
and dependency manifests remain in the runtime.

## Frozen expression and proof contract

A term is a validated data-only AST:

```json
{"op":"var","index":0}
{"op":"join","left":{"op":"var","index":0},"right":{"op":"var","index":1}}
{"op":"meet","left":{"op":"var","index":0},"right":{"op":"var","index":1}}
```

Indices refer to six arbitrary bound values `s0 … s5 : Set Nat`. The adapter
owns Lean identifier generation and the fixed imports. No supplied Lean source,
module name, proof script or claimed verification state is executed.

An inequality consists of a source term and target term. A proof node contains
its inference rule, exact source/target terms and ordered children. The formal
adapter must validate every child's interface and serialize only these fixed
rule templates. The engine and adapter may choose internal field names, but
the mathematical contract is:

| Rule | Required premises | Lean proof template |
| --- | --- | --- |
| Reflexivity | none | `le_rfl` |
| Join introduction | none | `le_sup_left`, `le_sup_right` |
| Meet projection | none | `inf_le_left`, `inf_le_right` |
| Join bound | `a ≤ c`, `b ≤ c` | `sup_le h1 h2` |
| Meet bound | `c ≤ a`, `c ≤ b` | `le_inf h1 h2` |
| Join monotonicity | `a ≤ b`, `c ≤ d` | `sup_le_sup h1 h2` |
| Meet monotonicity | `a ≤ b`, `c ≤ d` | `inf_le_inf h1 h2` |
| Transitivity | `a ≤ b`, `b ≤ c` | `le_trans h1 h2` |
| Imported distributive seed | explicit `a,b,c` terms | `(inf_sup_left a b c).le` |

The seed direction is `a ⊓ (b ⊔ c) ≤ (a ⊓ b) ⊔ (a ⊓ c)`. It is an equality's
forward inequality, not an arbitrary proposition. Candidate proof terms must
actually reference the checked seed instance where dependence is claimed.
The adapter audits direct constants in checked proof bodies. Its closed proof
grammar emits explicit theorem applications, without local helper definitions
or discardable let/lambda wrappers. Inspect those applications when attributing
seed or selected-lemma use. This is not a general normalized dependency analyzer
and does not establish mathematical necessity.

## Exact successful proof probe

The following source was accepted by Lean, including all nine exact-declaration
audits appended in `LatticeVerified.lean`. It succeeded both before and after
runtime relocation:

```lean
import Mathlib.Order.Lattice
import Mathlib.Data.Set.Lattice
import Lean
open Lean Elab Command

theorem pr_seed (A B C : Set Nat) : A ⊓ (B ⊔ C) ≤ (A ⊓ B) ⊔ (A ⊓ C) :=
  (inf_sup_left A B C).le

theorem pr_candidate (A B C : Set Nat) : A ⊓ (B ⊔ C) ≤ (A ⊓ B) ⊔ C :=
  le_trans (pr_seed A B C) (sup_le_sup le_rfl inf_le_right)

theorem pr_downstream (A B C D E F : Set Nat) :
    (A ⊓ (B ⊔ C)) ⊔ (D ⊓ (E ⊔ F)) ≤
      ((A ⊓ B) ⊔ C) ⊔ ((D ⊓ E) ⊔ F) :=
  sup_le_sup (pr_candidate A B C) (pr_candidate D E F)

theorem pr_pointwise_automation (A B C D E F : Set Nat) :
    (A ⊓ (B ⊔ C)) ⊔ (D ⊓ (E ⊔ F)) ≤
      ((A ⊓ B) ⊔ C) ⊔ ((D ⊓ E) ⊔ F) := by
  change (A ∩ (B ∪ C)) ∪ (D ∩ (E ∪ F)) ⊆ ((A ∩ B) ∪ C) ∪ ((D ∩ E) ∪ F)
  intro x hx
  simp only [Set.mem_union, Set.mem_inter] at *
  aesop

```

Observed transitive axioms:

| Declaration | Axioms |
| --- | --- |
| `inf_sup_left` | `['propext']` |
| `sup_le` | `[]` |
| `le_inf` | `[]` |
| `sup_le_sup` | `[]` |
| `inf_le_inf` | `[]` |
| `pr_seed` | `['propext', 'Classical.choice', 'Quot.sound']` |
| `pr_candidate` | `['propext', 'Classical.choice', 'Quot.sound']` |
| `pr_downstream` | `['propext', 'Classical.choice', 'Quot.sound']` |
| `pr_pointwise_automation` | `['propext', 'Classical.choice', 'Quot.sound']` |

The foundational three-axiom policy is explicit. Generic `inf_sup_left` itself
uses only `propext`; concrete `Set Nat` typeclass construction in these proofs
also introduces `Classical.choice` and `Quot.sound`. Reject `sorryAx`, native
computation axioms and custom axioms. The direct pointwise control proves the
same downstream inclusion without referencing either discovered theorem.

Probe source SHA-256:
`d4b3ed27a36c938f6262ee769c45d201efdcc268655d9bc3c4711f068935fd23`.
Relocated successful log SHA-256:
`24f7cd1e74c104983b092208cc30b67272f3461482ec5a24f7c3f71d33ceb9f5`.
The exact sources, logs and `domain-feasibility-receipt.json` are retained
inside the ignored runtime for integration. The source uses the imported
Mathlib theorem, and the proof audit identifies its actual declaration, type,
axioms and proof-body constants.

## Equality, novelty and split safeguards

For deduplication, interpret a positive set expression as its free distributive
lattice disjunctive normal form: an antichain of finite variable sets.

- A variable is one singleton conjunction.
- Join unions the antichains and removes duplicate/superset conjunctions.
- Meet forms pairwise unions of conjunction variable sets, then removes
  duplicate/superset conjunctions.

This gives exact endpoint equality keys for union/intersection formulas. Use
it for identity, existing-statement and held-out-equivalent filtering, not to
silently solve or normalize the actual proof-search states. A valid non-equivalent
inclusion can have distinct source and target keys, so this filter need not
remove every candidate. Equality consequences have matching endpoint keys and
are deliberately excluded from the useful candidate pool.
The source and target are not equivalent as symbolic set expressions. This
does not mean strict containment for every assignment of
the set variables; assigning all variables the empty set makes them equal.

A statement's key is the ordered pair of endpoint normal forms. This is not
logical equivalence of the entire universally closed proposition: every
successfully proved universal inclusion is true, making that definition useless
for novelty filtering. Exclude direct closed imported seed instances and
registered closed statement collisions; do not exclude every theorem merely
obtainable from a generic two-premise inference schema.

For train/validation/test separation, canonicalize these endpoint pairs under
consistent permutations of the variables. Six variables permit an exact orbit
check over at most 720 permutations. A renamed or reassociated statement must
not become a new held-out goal. Freeze the goal and candidate inventories
before evaluating usefulness labels, and publish the rejected-overlap counts.
Corpus-relative novelty does not mean new human mathematics.

## Prospective ranking experiment

The agreed small benchmark uses 40 training, 12 validation and 24 test contexts.
Require at least 20 test contexts to retain active non-equivalent goals and more
candidates than the selection budget after label-free equivalence filtering.
Depth, shape, meet/join alternation, branch sharing and variable-role patterns
must vary; changing only variable names does not establish transfer.

Report every predeclared combination of selected-lemma budget `k ∈ {1,3,5}`
and proof-search expansion budget `{4,8,12}`, including zero and negative
effects. At minimum compare random, proof-cost, lexical, strongest goal-aware
greedy route/saving/coverage, and branching-aware heuristics. Their features may
use visible goal statements, but never measured held-out proof outcomes.
An exact outcome oracle is a separately labeled, costed diagnostic, not a
baseline heuristic or learned feature.

Count attempted multi-premise rule applications and kernel-check cost. Preserve
failed searches and proof failures. Verify every reported emitted proof in a
fresh process, with exact declarations and axioms, and audit candidate use in
successful augmented witnesses. Keep the same candidate pool, primitive rules,
tie-breaking and search accounting for all policies. Fit the usefulness model
only from training outcomes; validation selects only declared hyperparameters.
Report denominators, paired context-level uncertainty and ranking losses as
well as gains. No positive effect is assumed.

## Strong actual Lean controls

Run direct semantic automation on **all** held-out goals, not a favorable
example subset. Use the same frozen declarations and imports, without supplied
candidate facts in the baseline. Pointwise unfold each `Set Nat` expression
into membership conjunctions/disjunctions before invoking `aesop` or another
predeclared tactic under matched limits. Record preprocessing cost separately.

A raw `grind (gen := 8)` probe failed on the example because its selected
E-matching rules did not expose lattice-set membership. That failure is
preserved as an unsuccessful probe with `sorryAx`; it is not a verified result
and is not evidence of useful discovery. The pointwise `aesop` probe succeeded.
Comparing only against raw `grind` would therefore make the baseline
artificially weak.

The complete propositional decision route is a meaningful upper control for
this finite positive set language. It may solve every test goal. If so, any
ranker gain remains a result about the disclosed bounded compositional search,
not superiority over Mathlib or general Lean automation. Equal generation
limits do not equate CPU work, and no timing advantage has been established.

## Alternatives investigated

Finite-set cardinality was independently executable: importing
`Finset.card_union_add_card_inter` allowed composition of two overlap identities
and a shared-capacity consequence, all with the standard three axioms. However,
the source already registers `grind_pattern`s for that valuation identity;
direct `grind` also solved the supplied budget consequence. This option is
feasible but not selected for the next adapter. Natural-number coprimality was
inspected at source level only; no runtime result is claimed for it.
