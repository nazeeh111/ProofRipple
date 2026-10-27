# Natural-domain proposal: verified list pipeline capacity

Status: independently probed against the installed Lean 4.33.1 toolchain on
26 October 2026. This document is follow-on work after v0.1. It does not alter
the published implementation or claim that the proposed adapter is implemented.

## Result and decisive limit

A tractable next domain is **nonexpansive list pipelines**: filtering and taking
a prefix never increase list length, while mapping and reversal preserve it.
The actual core theorem `List.length_filter_le` can be imported, its checked
proof audited, and consequences synthesized by composing real operations.
A two-branch consequence combines independently transformed streams under a
shared capacity. Every tested proof uses only the standard `propext` axiom.

This demonstrates genuine mathematical objects and fully closed Lean proofs,
without free assumptions that primitive implication edges are valid. It is a
small domain, not evidence of broad mathematical discovery. More decisively,
Lean's existing `grind` tactic already proves the proposed two-branch downstream
goal directly in an isolated context. Any gain over a deliberately restricted
graph search must be reported alongside that strong baseline's success.

## Exact imported declarations

Installed source root:
`/Users/nazeeh/.elan/toolchains/leanprover--lean4---v4.33.1/src/lean/`.

| Declaration | Installed source | Verified type in substance |
| --- | --- | --- |
| `List.length_filter_le` | `Init/Data/List/Lemmas.lean:1272` | `∀ p xs, (xs.filter p).length ≤ xs.length` |
| `List.length_map` | `Init/Data/List/Lemmas.lean:1081` | `∀ f, (xs.map f).length = xs.length` |
| `List.length_reverse` | `Init/Data/List/Lemmas.lean:2431` | `xs.reverse.length = xs.length` |
| `List.length_take_le'` | `Init/Data/List/Nat/TakeDrop.lean:46` | `∀ n xs, (xs.take n).length ≤ xs.length` |
| `List.length_append` | `Init/Data/List/Basic.lean:631` | `(xs ++ ys).length = xs.length + ys.length` |
| `Nat.le_trans` | inspected through Lean environment | `n ≤ m → m ≤ k → n ≤ k` |
| `Nat.add_le_add` | inspected through Lean environment | `a ≤ b → c ≤ d → a + c ≤ b + d` |

`List.length_take_le` has a different useful bound, `(xs.take n).length ≤ n`.
Do not confuse it with `List.length_take_le'`, which bounds by the input length.
All listed declarations were present under `import Lean`. Their exact types,
proof-body constants and transitive axioms were read from Lean's environment,
not inferred from source text or theorem names.

SHA-256 of installed `Init/Data/List/Lemmas.lean`:
`0724ebc7c72c87ad6d480dba407c43cc60393e7a0facfbaa6670045f66f636ac`.

## Minimal integration contract

1. Add an explicit domain discriminator, for example `list-capacity-v1`. Keep
   v0.1's empty-axiom implication policy unchanged. This domain accepts only
   an audited subset of `{propext}`; an empty list is also valid. Reject
   `sorryAx`, native-computation axioms and every custom axiom.
2. Support import by a small registered declaration name, initially
   `List.length_filter_le`. Inspect its actual Lean environment entry, checked
   proof body, exact type, transitive axioms, constants and toolchain. Record
   source/module provenance and hashes. Accept no arbitrary Lean commands or
   user-selected module import. A registry is an explicit supported subset,
   not a claim to import all Lean theorems.
3. Reify list expressions using a validated AST: input, filter, map, reverse,
   take and eventually append. Functions and predicates are bound Lean
   parameters; bounds are natural-number parameters. Generate identifiers
   internally, enforce topological order and cap AST/candidate size.
4. A stage node denotes a concrete proposition such as
   `(stage_i xs).length ≤ cap`. Each primitive arrow receives a generated,
   checked proof from a core declaration. Do not quantify over arbitrary
   `h_edge` implications. Compose those actual proof constants to construct
   seed, candidate and downstream proofs. Candidate proof terms must contain
   the seed where seed dependence is claimed.
5. Extract graph edges from generated proof-body constants. Distinguish those
   observed references from possible alternative mathematical dependencies.
   Store explicit generation-rule provenance separately from proof references.
6. Reuse ranking/search infrastructure only with a domain/version marker.
   Retrain on actual domain data if claiming a natural-domain ML result. A
   synthetic graph-trained model applied unchanged is a transfer experiment,
   not trained evidence from historical mathematical reuse.

For a prefix-stage implementation, each later stage is nonexpansive by
construction, so every earlier-to-later capacity implication holds, regardless
of which edges are exposed to search. Randomly omitting edges creates a
controlled search challenge. It does not create a difficult mathematical
question. The two-branch append consequence below goes beyond one prefix chain
and provides a concrete later extension.

## Fully checked probe

The following exact source succeeded with exit code 0 using:

```sh
ELAN_TOOLCHAIN=leanprover/lean4:v4.33.1 lean /private/tmp/proofripple-capacity-probe.lean
```

The theorem statements and proof bodies are useful implementation examples.
They were written as probes; actual discovery must enumerate and select the
compositions rather than relabeling these hand-selected declarations as an
algorithmic discovery.

```lean
import Lean
open Lean Elab Command

-- Explicit arguments avoid unsolved implicit metavariables in a source generator.
theorem step_filter {α : Type} (xs : List α) (p : α → Bool) (cap : Nat) :
    xs.length ≤ cap → (xs.filter p).length ≤ cap :=
  fun h => Nat.le_trans (List.length_filter_le p xs) h

theorem step_map {α β : Type} (xs : List α) (f : α → β) (cap : Nat) :
    xs.length ≤ cap → (xs.map f).length ≤ cap := by
  rw [List.length_map]
  exact fun h => h

theorem step_reverse {α : Type} (xs : List α) (cap : Nat) :
    xs.length ≤ cap → xs.reverse.length ≤ cap := by
  rw [List.length_reverse]
  exact fun h => h

theorem step_take {α : Type} (xs : List α) (n cap : Nat) :
    xs.length ≤ cap → (xs.take n).length ≤ cap :=
  fun h => Nat.le_trans (List.length_take_le' n xs) h

theorem filtered_budget {α β : Type} (xs : List α) (p : α → Bool) (f : α → β) :
    (((xs.filter p).map f).reverse).length ≤ xs.length := by
  rw [List.length_reverse, List.length_map]
  exact List.length_filter_le p xs

-- Not only a renamed endpoint: branches combine with addition, then share a cap.
theorem paired_budget {α β : Type} (xs ys : List α) (p q : α → Bool)
    (f : α → β) (n : Nat) :
    ((((xs.filter p).map f).reverse) ++ ((ys.filter q).take n).map f).length ≤
      xs.length + ys.length := by
  rw [List.length_append]
  apply Nat.add_le_add (filtered_budget xs p f)
  rw [List.length_map]
  exact Nat.le_trans (List.length_take_le' n (ys.filter q)) (List.length_filter_le q ys)

theorem combined_buffer_safe {α β : Type} (xs ys : List α) (p q : α → Bool)
    (f : α → β) (n cap : Nat) (fits : xs.length + ys.length ≤ cap) :
    ((((xs.filter p).map f).reverse) ++ ((ys.filter q).take n).map f).length ≤ cap :=
  Nat.le_trans (paired_budget xs ys p q f n) fits

run_cmd do
  for n in #[`List.length_filter_le, `List.length_map, `List.length_reverse,
      `List.length_take_le', `List.length_append, `Nat.le_trans, `Nat.add_le_add,
      `step_filter, `step_map, `step_reverse, `step_take,
      `filtered_budget, `paired_budget, `combined_buffer_safe] do
    let env ← getEnv
    let some ci := env.find? n | throwError "missing"
    let axs ← collectAxioms n
    let ty ← liftTermElabM <| Meta.ppExpr ci.type
    let some value := ci.value? (allowOpaque := true) | throwError "no proof"
    let deps := value.getUsedConstants.toList.map Name.toString
    logInfo m!"PROBE {Json.compress <| Json.mkObj [("name", toJson n.toString), ("type", toJson ty.pretty), ("axioms", toJson (axs.toList.map Name.toString)), ("constants", toJson deps)]}"
```

The generated audit records confirm:

| Declaration | Transitive axioms |
| --- | --- |
| `List.length_filter_le` | `['propext']` |
| `List.length_map` | `['propext']` |
| `List.length_reverse` | `['propext']` |
| `List.length_take_le'` | `['propext']` |
| `List.length_append` | `['propext']` |
| `Nat.le_trans` | `[]` |
| `Nat.add_le_add` | `[]` |
| `step_filter` | `['propext']` |
| `step_map` | `['propext']` |
| `step_reverse` | `['propext']` |
| `step_take` | `['propext']` |
| `filtered_budget` | `['propext']` |
| `paired_budget` | `['propext']` |
| `combined_buffer_safe` | `['propext']` |

Probe source SHA-256:
`1548edc0f1d46bec9e111c28abcda9b66fe284ec8b2e19fd2b29327a6888b9d3`.
Full probe log SHA-256:
`b31ff14b1cb9cf496d708b7c3ed0076f3822f05cdfbe37d49547fb9e8b15b26b`.
The log's proof constants for `paired_budget` include `filtered_budget`; the
proof constants for `combined_buffer_safe` include `paired_budget`. This
establishes reuse in these actual emitted proofs, not mathematical necessity.

## Strong baseline countercheck

This exact source also succeeded with exit code 0. It imports no discovered
lemma and declares no seed theorem before the goal:

```lean
import Lean
set_option maxHeartbeats 400000
example {α β : Type} (xs ys : List α) (p q : α → Bool)
    (f : α → β) (n cap : Nat) (fits : xs.length + ys.length ≤ cap) :
    ((((xs.filter p).map f).reverse) ++ ((ys.filter q).take n).map f).length ≤ cap := by
  grind
```

Baseline source SHA-256:
`9e5e09dca87e2e53bbaf2a8ce41ad8e271b09e41189f6edd7531485880e1791b`.
Its output log was empty. This is evidence that `grind` solves this goal, not a
measured timing comparison. No runtime speedup was measured.

## Evaluation and leakage controls

- The imported `Lean` environment contains more theorems and automation than a
  restricted Python search registry. Freeze and disclose the registry. Run a
  direct `grind` control on each downstream goal before claiming utility.
- Keep candidate generation independent of test proof bodies. Split operator
  skeletons or pipeline families before training; renaming list/function
  variables is not a meaningful holdout. State whether goal statements are
  visible for task-directed ranking.
- Never offer the exact held-out goal as a candidate. A useful candidate is an
  intermediate bound reused under a later operation, an appended branch or a
  supplied total capacity. Record actual proof-term reuse.
- Count attempted proof-rule applications and kernel checks separately. Report
  candidate discovery/verification cost as well as downstream search cost.
  Identical process timeouts alone do not establish matched computational work.
- Penalize map/reverse-only restatements, duplicate normal forms and merely
  renamed expressions. Record novelty only relative to the registered corpus.
  All identities here are elementary known mathematics.
- Report the strong baseline's success even when the restricted search fails.
  A positive restricted-budget result is proof-search compression under that
  registry. A null improvement over `grind` is a valid scientific result.

## Alternative considered: list fusion

The installed `List.filter_map` at `Init/Data/List/Lemmas.lean:1370` and
`List.filter_filter` at line 1340 compose into a semantic pipeline fusion law.
A separate successful probe proved
`((xs.filter p).map f).filter q = (xs.filter (fun a => p a && q (f a))).map f`.
Normalizing the predicate order used `Bool.and_comm` plus function
extensionality, introducing `Quot.sound` as well as `propext`. That is a
legitimate standard axiom, but incompatible with a deliberately propext-only
capacity policy. Keep the capacity route minimal first. Do not claim that
fusion improves runtime without measuring evaluation counts and allocation.
