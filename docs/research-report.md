# ProofRipple v0.1 research report

Recorded 26 October 2026. This is a controlled proof-search-compression experiment, not evidence of new mathematical theorems or Mathlib generalization.

## Question

Can a small learned policy select seed-dependent intermediate consequences that improve downstream bounded proof search under equal theorem-count and node-expansion budgets?

## Result

The learned ensemble improves over random, lexical and cheapest-proof selection on this frozen test set, but does not beat the goal-aware graph heuristic. This negative comparison limits the case for learning in the present domain. A simpler graph policy is a competitive default for these small explicit graphs.

| Policy | Mean solved / 20 | Mean net gain | Newly solved | Regressed | NDCG@3 |
| --- | ---: | ---: | ---: | ---: | ---: |
| learned | 8.583 | +3.667 | 4.000 | 0.333 | 0.599 |
| random | 6.317 | +1.400 | 1.850 | 0.450 | 0.199 |
| semantic | 6.333 | +1.417 | 1.667 | 0.250 | 0.214 |
| graph | 8.750 | +3.833 | 4.083 | 0.250 | 0.633 |
| proof_cost | 4.833 | -0.083 | 0.583 | 0.667 | 0.046 |

Starting library mean: 4.917/20. Test: 12 contexts, 240 goals; random has five repetitions per context. Intervals and complete per-context records are in [benchmark.json](../artifacts/benchmark.json).

## Reproduction evidence

- Stable outcomes SHA256: `7a93f135ddc33ba372c460921af40b73d3132d5420123b82744aee84f08e9859`.
- Formal status: **kernel_verified**, 1274/1274 expected declaration audits, empty-axiom policy.
- Toolchain: `leanprover/lean4:v4.33.1`.
- Audit artifact SHA256: `cb7eb79ed545442b9ed8ff31a685b2487f08ad5592b4824d40c4e99e2ebab47b`.
- Recorded Python experiment elapsed time: 18.28s; per-context Lean total 45.98s on the local Mac. Hardware-specific timings, not equal-wall-time results.

Each context proof file and hash is listed in the formal_verification.contexts report field. Certification covers the seed, every candidate, and every distinct successful downstream proof across all test policies and random repetitions. Search failures have no proof claim. Training/validation labels come from the Python search calculus; formal certification covers test evaluation and the separate demo.

Two unsuccessful combined-file certification attempts were retained in task-local outputs: one timed out at 240 seconds; the second exceeded the 2048 MB memory cap. Both failed closed. The successful protocol checks one frozen context per fresh process under the same memory cap. These engineering attempts did not change benchmark data, model parameters, selected lemmas or outcomes.

## Interpretation and scientific limits

A finite implication graph already makes reachability decidable and cheap. Candidate construction knows witnesses, and structural features expose route information. The scientific question here is selection for a deliberately bounded downstream search, not discovery of unknown truth. The benchmark separates train/test graphs but uses one generator family. Equivalent local motifs can recur across splits; no structural-family or mathematical-domain transfer claim is justified.

The model uses conventional context-bootstrap ridge regression. No algorithmic novelty, human mathematical originality, pretrained semantic embedding, historical Mathlib reuse analysis, calibrated uncertainty or large-model comparison is claimed. Goal endpoints are visible to all policies. Direct target consequences are excluded from candidates. Net success retains queue-order regressions. Bootstrap intervals describe variability across these test contexts.

The showcase context was chosen to illustrate the workflow; its 1/4→4/4 result is not an unbiased benchmark estimate. A separate no-gain example shows 0/4→0/4. Lean establishes the explicit conditional implication statements, not the semantic interpretation of arbitrary invariant labels.

## Next decisive experiments

1. Add structurally held-out graph families and ablations of uncertainty bonus, witness-diversity penalty and task features.
2. Import a pinned, manageable Lean/Mathlib development through an actual environment adapter; extract types, axioms and dependencies while preventing equivalent target lemmas in imports.
3. Train on historical lemma reuse and frozen downstream proof attempts, with real theorem embeddings only if they improve equal-budget utility over the graph heuristic.
4. Measure proof-search wall time and verification cost as additional equal-resource budgets; current comparisons equalize counts only.
5. Use human mathematical review for statement fidelity, scientific interest and any originality claim. Scope an OpenAI/math case to one declaration and pinned dependencies before attempting large downloads.

See [methodology](methodology.md), [primary-source foundations](research-foundations.md), and [independent review](independent-review.md).
