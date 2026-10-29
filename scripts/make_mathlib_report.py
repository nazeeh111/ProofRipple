"""Build the Mathlib result report from completed, audited experiment data."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
folder = ROOT / "artifacts/mathlib"
report = json.loads((folder / "benchmark.json").read_text())
formal = report["formal_verification"]
assert formal["status"] == "kernel_verified", "Do not promote incomplete proof evidence"
assert formal["audits_received"] == formal["declarations"]
freeze = report["data_freeze"]
assert freeze["choice_gate_passed"]
primary = report["aggregate_summary"]
gains = primary["mean_context_profile_solve_fraction_gain"]
contrast = primary["contrasts"]["learned_minus_greedy_coverage"]
low, high = contrast["paired_context_bootstrap_95pct"]
names = {"learned": "Portfolio-aware learned ensemble", "learned_no_bonus": "Learned, no uncertainty bonus",
         "learned_singleton": "Singleton/static learned ablation", "structure_only": "Structural learned ablation",
         "greedy_coverage": "Dynamic greedy coverage", "branching_aware": "Complementary-branch heuristic",
         "graph": "Static structural estimate", "proof_cost": "Shortest available proof",
         "semantic": "Symbolic syntax cosine", "random": "Random, five repetitions"}
policies = ["learned", "greedy_coverage", "branching_aware", "graph", "proof_cost", "semantic", "random",
            "learned_no_bonus", "structure_only", "learned_singleton"]
aggregate_rows = ["| Policy | Mean gain over starting registry | Difference from greedy |",
                  "| --- | ---: | ---: |"]
for method in policies:
    aggregate_rows.append(f"| {names[method]} | {100*gains[method]:+.2f} pp | {100*(gains[method]-gains['greedy_coverage']):+.2f} pp |")
profile_rows = ["| Lemmas / goal visits | Starting registry | Learned | Greedy coverage | Complementary branches |",
                "| --- | ---: | ---: | ---: | ---: |"]
for k in (1, 3, 5):
    for budget in (4, 8, 12):
        values = report["profiles"][f"k{k}_b{budget}"]["summary"]
        total = values["learned"]["total_goals"]
        profile_rows.append(f"| {k} / {budget} | {values['learned']['total_baseline_solved']:g}/{total} | "
                            f"{values['learned']['total_solved']:g}/{total} | "
                            f"{values['greedy_coverage']['total_solved']:g}/{total} | "
                            f"{values['branching_aware']['total_solved']:g}/{total} |")
coverage = freeze["coverage_at_largest_k"]["test"]
training = report["model_training"]
control = report["automation_control"]
best = max((method for method in policies if method in {"greedy_coverage", "branching_aware", "graph", "proof_cost", "semantic", "random"}), key=gains.get)
if high < 0:
    verdict = "The learned policy underperforms the predeclared greedy comparator on the primary endpoint."
elif low > 0:
    verdict = "The primary contrast favors learned selection over the predeclared greedy comparator in this generated workload."
else:
    verdict = "The primary comparison does not establish a clear learned advantage over the predeclared greedy comparator."
if gains[best] >= gains["learned"]:
    verdict += f" The highest observed heuristic is {names[best].lower()}, which matches or exceeds the learned policy's mean gain."
else:
    verdict += " The learned mean exceeds the reported heuristic means; the paired intervals and domain limits remain essential to interpretation."

text = f'''# Mathlib set-algebra usefulness study

This study evaluates consequence selection over unions and intersections of six
arbitrary `Set Nat` values. It uses the pinned Mathlib declaration `inf_sup_left`
and checked multi-premise lattice proofs. These are known mathematical facts;
the experiment measures assistance to a restricted search procedure.

## Result

{verdict}

The predeclared learned-minus-greedy difference is
**{100*contrast['mean_context_profile_solve_fraction_difference']:+.2f} percentage points**,
with a paired whole-context bootstrap interval of **[{100*low:+.2f}, {100*high:+.2f}] pp**.
This is the mean difference in solved fraction, averaging the nine fixed budget
profiles within each context before averaging the 24 contexts. One percentage
point is 0.01 solved fraction. It is not a count of independent new theorems.

{chr(10).join(aggregate_rows)}

The greedy comparator and primary metric were fixed before outcomes. Other
paired contrasts are reported in the raw artifact. Their intervals are
descriptive and unadjusted for multiple comparisons. The highest observed
heuristic is identified descriptively, without a post-hoc significance claim.

## Every budget profile

{chr(10).join(profile_rows)}

The same retained queries recur in every row. They are not nine independent
datasets. Random selection averages five fixed repetitions within each context.
Newly solved goals, regressions, selected identifiers, individual goal decisions,
proof hashes and search work are retained for every policy and repetition.
The LAB summary uses the declared `k3_b8` profile; the primary analysis uses all
nine profiles rather than choosing the best-looking row.

## Data, exclusions and choices

The frozen split has 40 training, 12 validation and 24 test contexts. The final
test workload has {report['summary']['learned']['total_goals']} retained queries.
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

The fresh formal campaign received **{formal['audits_received']}/{formal['declarations']}**
expected declaration audits. This includes repeated library/candidate audits
across certificate chunks; it is not a count of new mathematical discoveries.
Every candidate and every distinct successful test witness across policies,
repetitions and budgets is covered. Training label probes are not individually
kernel certified. Exact proof sources, audit bytes, types, dependencies,
source hashes and the explicit foundational axiom profile are retained.

The separate strong Mathlib control reports **{control['solved']}/{control['total']}**
goals, status `{control['status']}`. It introduces an arbitrary element, unfolds
union/intersection membership, then runs ordinary `aesop` without the selected
consequences or the generated seed. This covers the entire retained test
workload. It uses a different resource unit from bounded goal-state visits;
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
python3 -m proofripple benchmark --domain mathlib --certify \\
  --frozen-protocol artifacts/mathlib --out outputs/mathlib-reproduction
```

Mathlib revision: `{formal['mathlib_revision']}`.
Scientific-outcome digest: `{report['outcomes_sha256']}`.
Code, model-byte and audit provenance hashes are separate from this digest.
The original list/implication studies remain versioned evidence from their own
source revisions; the v0.3 bridge does not rewrite their recorded fingerprints.

[Raw result](../artifacts/mathlib/benchmark.json) ·
[Protocol](../artifacts/mathlib/protocol.json) ·
[Setup](mathlib-setup.md) · [CLI and Python](mathlib-api.md) ·
[Prospective review](mathlib-protocol-review.md)
'''
(ROOT / "docs/mathlib-research-report.md").write_text(text)
print("Generated docs/mathlib-research-report.md from completed audited evidence")
