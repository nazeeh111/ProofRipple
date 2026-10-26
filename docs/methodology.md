# Experiment protocol

## Formal domain

A node is a proposition `P : Prop`. A primitive edge is an explicitly quantified
hypothesis `P → Q`. A path is a composable proof term. The seed is a theorem
proved from primitive edges. Candidates must use the seed, cannot be existing
edges or identity statements, and cannot exactly match an evaluation goal.
This is finite propositional implication logic, not a natural-mathematics corpus.
Node labels are presentation metadata, not Lean expressions.

The available library for **every** downstream baseline contains all primitive
edges and the verified seed. Augmented searches additionally receive the same
number of selected candidate lemmas. Removing a selected lemma never removes
its primitive proof, so logical entailment stays unchanged.

## Frozen data and splits

Generator version `proofripple-implication-dag-v1` creates DAGs with a chain plus
random forward edges, randomly permuted proposition names, and synthetic labels.
The release contains 16 training contexts (seeds 1000–1015), 6 validation contexts
(2000–2005) and 12 test contexts (3000–3011). Each test context has 20 frozen goals.
Hashes and full manifests are in `artifacts/contexts.json` and `benchmark.json`.
The validation report is a sanity check, not an undisclosed tuning sweep.

All contexts use the same generator family. Disjoint seeds/hashes do not prove
structural non-equivalence or domain transfer. Candidate proof witnesses are
constructed from the frozen primitive graph and seed. A held-out goal's endpoints
are visible to every policy, while its outcome is never a model feature.
This is task-conditioned, transductive selection. It is not blind theorem
generation and does not test undiscovered reachability.

## Model

Seven ridge regressors are trained on bootstrap samples of entire training
contexts. Features are standardized using training statistics. The 12 features
encode primitive proof length, local degrees, ancestor/descendant counts,
task endpoint matches, task coverage, route shortening, and seed fraction.
Only training-context single-lemma solve-rate differences provide labels.
Zero and negative outcomes are retained. The mean prediction receives a fixed
0.35 times ensemble-spread bonus and a fixed 0.02 witness-overlap penalty during
greedy selection. Disagreement is a ranking signal, not calibrated uncertainty.
The output is not a probability, and interactions between selected lemmas can
differ from their individual labels.

## Equal-budget comparison

All policies receive the identical candidate pool (at most 256, witness length
at most 6 including the seed as one edge), select 3 lemmas, and use deterministic
BFS with a cap of 8 dequeued propositions per goal. A dequeued adjacency list
counts once, including empty lists. Success can occur while inspecting that
list. Edge ordering is identical for all policies. A new shortcut can change
queue order and produce regressions; net marginal success includes them.

Baselines: no added lemmas, five random repetitions, lexical token cosine,
goal-aware graph route-saving, and shortest primitive proof cost. Lexical
similarity is not a pretrained semantic model. The graph baseline is deliberately
strong because it exploits the same task-visible structure as the learner.
These are local baselines inspired by research mechanisms, not reproductions of
large published systems. Candidate enumeration and training are common/offline
costs. The theorem-count and BFS budgets are equal; wall time and primitive
proof-checking cost are reported separately, not assumed equal.

## Outcomes and uncertainty

Report baseline/augmented solved counts, newly solved and regressed goals,
expansions, primitive proof-edge costs, positive selection precision, and NDCG.
NDCG discounts relevant candidates at lower ranks, normalized by the best ordering
of the same measured single-lemma utilities. Nonpositive gains receive zero
ranking relevance; contexts with no positive candidates have undefined NDCG.
Net success metrics still retain negative outcomes. The 95% bootstrap interval
resamples test contexts, averaging random repetitions within context. It is not
a generalization guarantee or a calibrated interval for the ridge predictions.

The stable outcomes digest excludes elapsed/ranking timings. Lean checks exact
proof terms for the seed, all candidates, and every distinct successful test
goal witness across policies and random repetitions. Certification runs in
separate bounded processes per context. Failed searches generate no theorem.
Per-context source hashes, audit counts and the combined audit hash appear in
the report. A fresh proof check is independent of the Python search, but not an
independent mathematical review of a natural-language interpretation.

## Reproduce

```sh
proofripple benchmark --out outputs/reproduction --certify
python -m unittest discover -s tests -v
```

Use the full default benchmark when comparing the release digest. `--quick`
is a separate smoke experiment with smaller splits. Both are CPU-only.
