# Mathlib set-algebra usefulness study

This study evaluates consequence selection over unions and intersections of six
arbitrary `Set Nat` values. It uses the pinned Mathlib declaration `inf_sup_left`
and checked multi-premise lattice proofs. These are known mathematical facts;
the experiment measures assistance to a restricted search procedure.

## Result

The primary comparison does not establish a clear learned advantage over the predeclared greedy comparator. The highest observed heuristic is dynamic greedy coverage, which matches or exceeds the learned policy's mean gain.

The predeclared learned-minus-greedy difference is
**-0.64 percentage points**,
with a paired whole-context bootstrap interval of **[-1.55, +0.20] pp**.
This is the mean difference in solved fraction, averaging the nine fixed budget
profiles within each context before averaging the 24 contexts. One percentage
point is 0.01 solved fraction. It is not a count of independent new theorems.

| Policy | Mean gain over starting registry | Difference from greedy |
| --- | ---: | ---: |
| Portfolio-aware learned ensemble | +24.82 pp | -0.64 pp |
| Dynamic greedy coverage | +25.46 pp | +0.00 pp |
| Complementary-branch heuristic | +25.03 pp | -0.43 pp |
| Static structural estimate | +24.46 pp | -1.00 pp |
| Shortest available proof | +11.27 pp | -14.19 pp |
| Symbolic syntax cosine | +15.13 pp | -10.33 pp |
| Random, five repetitions | +13.42 pp | -12.04 pp |
| Learned, no uncertainty bonus | +24.78 pp | -0.68 pp |
| Structural learned ablation | +24.85 pp | -0.61 pp |
| Singleton/static learned ablation | +23.06 pp | -2.40 pp |

The greedy comparator and primary metric were fixed before outcomes. Other
paired contrasts are reported in the raw artifact. Their intervals are
descriptive and unadjusted for multiple comparisons. The highest observed
heuristic is identified descriptively, without a post-hoc significance claim.

## Every budget profile

| Lemmas / goal visits | Starting registry | Learned | Greedy coverage | Complementary branches |
| --- | ---: | ---: | ---: | ---: |
| 1 / 4 | 0/254 | 0/254 | 0/254 | 0/254 |
| 1 / 8 | 0/254 | 28/254 | 39/254 | 34/254 |
| 1 / 12 | 40/254 | 79/254 | 73/254 | 73/254 |
| 3 / 4 | 0/254 | 28/254 | 28/254 | 29/254 |
| 3 / 8 | 0/254 | 82/254 | 96/254 | 92/254 |
| 3 / 12 | 40/254 | 134/254 | 125/254 | 127/254 |
| 5 / 4 | 0/254 | 46/254 | 46/254 | 47/254 |
| 5 / 8 | 0/254 | 122/254 | 132/254 | 128/254 |
| 5 / 12 | 40/254 | 167/254 | 163/254 | 162/254 |

The same retained queries recur in every row. They are not nine independent
datasets. Random selection averages five fixed repetitions within each context.
Newly solved goals, regressions, selected identifiers, individual goal decisions,
proof hashes and search work are retained for every policy and repetition.
The LAB summary uses the declared `k3_b8` profile; the primary analysis uses all
nine profiles rather than choosing the best-looking row.

## Data, exclusions and choices

The frozen split has 40 training, 12 validation and 24 test contexts. The final
test workload has 254 retained queries.
All eligible contexts remain in the denominator, including empty ones if any.
The label-free feasibility check required at least 20 test contexts with goals
and more candidates than the maximum five-lemma budget; the actual coverage is
recorded in `data-freeze.json` and the profile-level coverage tables.

Positive Boolean DNF antichains remove associativity, commutativity,
idempotence, absorption and distributivity reformulations. A joint variable
renaming key excludes equivalent ordered endpoint pairs. Validation excludes
the retained training index; test excludes training plus validation declarations,
candidates and goals. Actual finite closed primitive facts and raw syntactic
leaf obligations are excluded. Arbitrary semantic substitution into generic
projection schemas is not an exclusion oracle: it would eliminate every valid
set inclusion. Raw inputs, removal counts and retained contexts are published.

The normalizer is a dataset tool. Search does not use DNF entailment, silent
semantic rewriting or outcome probes as free features. The generator varies
term shapes across splits within the same positive-set mathematical language.
This is generated structural and statement holdout, not transfer to unrelated
mathematical fields or a claim that Mathlib lacks equivalent general lemmas.

## Learned policy and strong heuristics

The compact CPU model uses context-bootstrap ridge ensembles, structural
features, signed symbolic syntax hashing and training-only proof-rule reuse.
For each training candidate, fixed deterministic partner portfolios at sizes
0, 1, 2, 3 and 4 exclude that candidate and are shared across search budgets.
Labels measure `U(S + candidate) - U(S)`. Features condition on the selected
portfolio, and the model rescores remaining candidates after each choice.
The actual training metadata are retained in `model.json`; all zero and
negative labels are included.

The singleton ablation fits only empty-prefix examples and uses static scores.
The structural ablation removes symbolic/history columns while retaining the
portfolio conditioning. The no-bonus ablation removes the uncertainty bonus.
Ensemble disagreement is not a calibrated probability, and immediate marginal
labels can still miss the future value of an initially unhelpful AND partner.
No rollout learner or pretrained language model is used.

Strong heuristics receive the same bounded raw obligation graph. Dynamic
greedy coverage recomputes estimated root-work savings after each selection.
The complementary-branch heuristic tracks actual sibling obligations rather
than treating any second match within a goal as a completed branch. Their
formulas, finite menus, ties and fixed bounds are in `protocol.json`.
Selection work and training costs are extra costs, reported separately from
the common goal-visit and selected-lemma budgets.

## Formal checks and general automation

The fresh formal campaign received **1997/1997**
expected declaration audits. This includes repeated library/candidate audits
across certificate chunks; it is not a count of new mathematical discoveries.
Every candidate and every distinct successful test witness across policies,
repetitions and budgets is covered. Training label probes are not individually
kernel certified. Exact proof sources, audit bytes, types, dependencies,
source hashes and the explicit foundational axiom profile are retained.

The separately repaired strong Mathlib control reports **254/254**
goals, status `kernel_verified`. It introduces an arbitrary element, unfolds
union/intersection membership, then runs ordinary `aesop` without the selected
consequences or the generated seed. This covers the entire retained test
workload. This is explicitly a **post-study mechanical control repair**. The
original registered control failed all 24 source bundles: preprocessing stopped
on 117 goals where `simp only` made no progress. Its bundle-level 0/254 is not a
measurement that `aesop` solves zero goals. Lean emitted 117 rejected `sorryAx`
recovery placeholders and 137 other individual audit messages; none of the failed
bundles were accepted. The repaired source inserts only `try` before each
preprocessing command, retains `aesop`, compares all 254 exact original goal
types, and passes fresh kernel checks. The original failed sources, logs and
benchmark remain unchanged. Both controls retain a 120-second per-process wall cap, one Lean thread,
2048 MiB and 400000 heartbeats. The repaired control does not change any ranking outcomes.

It uses a different resource unit from bounded goal-state visits;
the study makes no matched computational-work or unrestricted tactic-superiority
claim. A raw `grind` failure before exposing set membership was rejected as an
inadequate comparator during feasibility work.

Search charges failed branches, cache hits and cycle visits. Selected facts can
also guide the fixed midpoint menu, so measured effects include guidance as
well as proof compression. A bounded failure does not establish mathematical
necessity. Different endpoint normal forms establish a non-equivalent inclusion,
not a strict subset for every concrete assignment.

## Reproduce and inspect

```sh
python3 scripts/setup_mathlib.py
python3 -m proofripple benchmark --domain mathlib --certify \
  --frozen-protocol artifacts/mathlib --out outputs/mathlib-reproduction
```

Run the supplemental control separately, preserving the original control:

```sh
python3 scripts/mathlib_automation_control.py \
  --contexts artifacts/mathlib/contexts.json.gz \
  --original-controls artifacts/mathlib/automation \
  --out outputs/mathlib-control-repair-reproduction
```

Mathlib revision: `0df444a360eaa60ab8c11dca51a86af692955474`.
Scientific-outcome digest: `181c9295653d4ee547ef46f1fe2d95cfc5f5fa1e55147a3c9eb38ece5f13542f`.
Code, model-byte and audit provenance hashes are separate from this digest.
The original list/implication studies remain versioned evidence from their own
source revisions; the v0.3 bridge does not rewrite their recorded fingerprints.

[Raw result](../artifacts/mathlib/benchmark.json) ·
[Protocol](../artifacts/mathlib/protocol.json) ·
[Setup](mathlib-setup.md) · [CLI and Python](mathlib-api.md) ·
[Prospective review](mathlib-protocol-review.md) ·
[Independent result review](independent-review-v0.3.md) ·
[Supplemental control](../artifacts/mathlib/control-repair/summary.json)
