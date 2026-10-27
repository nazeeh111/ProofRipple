# ProofRipple 0.2 research report

Recorded 26 October 2026. This is a controlled study of consequence selection
in a registered Lean list calculus. It is not evidence of new human mathematics,
Mathlib-scale generalization, or superiority to general Lean automation.

## Question and result

Can a compact learned policy select reusable, seed-dependent list-capacity
consequences that help a fixed-budget downstream search?

The starting registry solves 10 of 61 retained test queries. Learned, graph and
proof-cost selection each solve 15. The extra syntax/reuse features solve one
more query than the structure-only model, but the experiment has only two active
test contexts with a genuine selection choice. This does not establish a useful
learned advantage. The default demonstration therefore uses a transparent graph
policy. Bootstrap intervals and all paired comparisons are in the raw report.

| Selection policy | Solved / retained queries | Net additional | Newly solved | Regressed |
| --- | ---: | ---: | ---: | ---: |
| Goal-aware graph heuristic | 15 / 61 | +5 | 5 | 0 |
| 32-feature usefulness ensemble | 15 / 61 | +5 | 5 | 0 |
| Shortest primitive proof | 15 / 61 | +5 | 5 | 0 |
| Random (five repetitions) | 14.6 / 61 | +4.6 | 4.6 | 0 |
| Lexical similarity | 14 / 61 | +4 | 4 | 0 |
| 12-feature structure-only ensemble | 14 / 61 | +4 | 4 | 0 |

Random totals average five repetitions within each context before summing.
Net gain includes regressions. Counts are registry queries, not independent new
theorems. The 61 test queries represent 57 globally distinct normalized statement
pairs across the frozen contexts. Common theorem structures can still recur.

## Actual mathematical semantics

Every stage is a concrete `List Nat` expression of arbitrary `xs`, `f`, `p` and
`k`. Its proposition bounds that stage's length by an arbitrary `cap`. Filtering
and taking prefixes are nonexpansive; mapping and reversal preserve length.
Every primitive edge has a closed proof from registered Lean library facts.
There are no arbitrary implication-edge hypotheses in this domain.

The import registry begins with `List.length_filter_le`. Its exact elaborated
type, proof-body named constants and transitive axioms are read from Lean's
checked environment. Candidates compose verified primitive theorems through a
composite seed. Their proof terms actually reference that seed. They are
elementary known consequences, with novelty only relative to a frozen registry.
Append/addition rules are disclosed supplied templates, not discovered rules.

## Frozen data and leakage controls

The generator and split seeds are frozen in `benchmark.json`: sixteen training,
six validation and twelve test contexts, each initially with twenty endpoint
queries. All splits use the same procedural chain-plus-forward-edge DAG family
and mathematical domain. Training alternates reducing/preserving operators,
validation uses a different block pattern, and test uses reducing clusters.
This is operator-skeleton shift, not a new mathematical domain.

Before labels, fitting or test search, the pipeline removes recognized identity
goals, goals equal to the context's own primitive/seed facts, and repeated
normalized pairs within the context. Validation targets already in the complete
training declaration index are removed. Test targets already in the combined
training/validation index are removed. That index includes primitive facts,
seeds, retained goals and candidate declarations. No queries are refilled,
renamed or resampled to preserve a larger denominator.

| Split | Initial endpoint queries | Retained registry queries | Global normalized pairs |
| --- | ---: | ---: | ---: |
| Train | 320 | 122 | 121 |
| Validation | 120 | 28 | 28 |
| Test | 240 | 61 | 57 |

All five saved holdout checks are zero: prior-index overlap for validation/test,
own-baseline overlap, identities and within-context duplicates. This is equality
recognized by a sound partial normalizer, not a complete mathematical equivalence
decision procedure. Normalizer rewrites have thirteen kernel-checked generic
proofs. A separate source review and finite concrete-model tests support its
implementation; those finite tests alone are not a proof of all behavior.

## Model and available selection evidence

Seven context-bootstrap ridge members use twelve graph/task features, sixteen
signed feature-hash coordinates of typed operator syntax, and four frozen proof
reuse frequencies. Training has 36 candidate examples,
including 4 positive, 32 zero
and 0 negative single-lemma marginal utility labels.
This is a very small and imbalanced training set. Syntax hashing is not a
pretrained semantic model; proof-motif history is not chronological Mathlib reuse.

History comes only from successful training baseline proof witnesses. Features
can use unlabelled task endpoints and frozen graph structure. Test outcomes and
test proof paths are not features. Normalization excludes recognized equivalent
goal answers, identities, existing pairs and duplicate candidates. The lowest
primitive-proof-cost witness represents each surviving pair. Hyperparameters
were fixed before this final test evaluation; validation is reported without a
test-driven tuning sweep. Ensemble disagreement is not calibrated confidence.

The test has 21 eligible candidates across
twelve contexts, 3 empty candidate pools and
11 contexts with retained goals. Only
2 active contexts have more
than three candidates. In the others, policies often supply the same full set.
That sharply limits any ranking comparison or interpretation of high NDCG.

## Budgets, counterfactuals and costs

Every policy uses the identical normalized pool, a cap of three selected lemmas,
and eight dequeued BFS propositions per retained query. Fewer than three
candidates means all policies use the smaller pool. Empty-goal contexts remain
recorded. The starting registry includes the seed. A direct-target candidate is
excluded, including recognized equivalent formulations. Added lemmas can change
queue order and produce regressions; both new successes and losses are retained.

Candidate enumeration, model training and kernel checks are additional costs.
Primitive theorem applications and concrete list-operation steps are reported.
There is no matched wall-time claim. Context-bootstrap intervals describe this
small context collection; they do not establish broad generalization. Different
contexts may query the same normalized mathematical statement under different
registries, so the queries are not independent theorem samples.

The separate illustrative demo has two normalized-distinct goals and three
candidate consequences. One graph-selected intermediate lemma improves bounded
search from 0/2 to 1/2. Its 42 declaration audits use only `propext`. It is an
illustration chosen for inspectability, not a learned-policy performance estimate.

The stronger independent control unfolds stage definitions and uses
`grind (gen := 32)`, with no discovered seed/helper/edge/candidate declarations.
It proves 3/3 statements: both showcase goals
plus the supplied two-buffer template. Its actual axioms are separately audited
under the three standard foundational axioms. The control covers the showcase,
not all retained corpus queries, and uses different resources from BFS.

## Formal certification and provenance

All 3940 expected audits passed in thirty-four fresh,
bounded Lean 4.33.1 processes, at most two concurrently. The list corpus allows
only standard `propext`; the original propositional backend still requires an
empty axiom list. Admitted, custom and native-computation axioms are rejected.
The corpus checks every candidate declaration and successful baseline/canonical
selection witness in training/validation, plus all distinct successful test
witnesses across all policies and random repetitions. It does not separately
compile every training single-candidate label-search witness. Search labels are
empirical evidence; they are not promoted to mathematical proof by the model.

- Outcomes SHA256: `7b84c6cbe6ffccf075ccf61ef1eadcb9bec40b6981dcebcc76b1f569ea721082`.
- Compressed audit SHA256: `04ed26d7322b5758e829a25ab7446b6ea4d499dee85e4c0ce9d728e6067c9c78`.
- Raw audit SHA256: `1b39014165c81c7bc66d68b49a5c18b121096dd316390e2ae72b5d283ad009df`.
- Exact context/model/source hashes, thirty-four proof sources and individual
  audit coverage are in [the report](../artifacts/natural/benchmark.json).
- [Holdout audit](../artifacts/natural/holdout-audit.json),
  [proof sources](../artifacts/natural/proofs),
  [compressed audit](../artifacts/natural/benchmark-audits.json.gz),
  [implementation review](independent-review-v0.2.md),
  [normalization review](normalization-review.md).

## Matched Lean automation case study

A separate prospective generation-8 experiment supplies only the graph-selected
`pr_ripple_p4_p9` lemma as an additional local fact in an otherwise identical
pre-goal environment. Baseline proofs succeed on 0/2 goals; augmented proofs
succeed on 2/2. Both checked proofs still use the candidate after local auxiliary
expansion and beta/zeta reduction. The independent generation-32 control proves
all three controls unaided. These are two illustrative, related goals, not the
held-out corpus; no generation sweep, timing advantage, mathematical necessity
or broad prover-superiority claim follows. The generation limit controls tactic
instantiation depth rather than equal CPU work. See the [paired experiment](budgeted-automation.md)
and [public sources/audits](../artifacts/budgeted-automation/README.md).

## Rejected experiments and limits

Two preliminary natural experiments were rejected despite valid Lean proofs.
The first failed to normalize common shared-predicate/k identities and admitted
equivalent target answers. The second fixed local equivalence but still reused
some training statements as test goals. Their metrics were not adopted as release
results. Raw evidence is retained task-locally. The final index-based pruning is
label-free; this report describes the development sequence rather than claiming
external preregistration or an untouched competition test set.

All current consequences are known nonexpansive-list mathematics. Registry
omission creates search difficulty. A Lean theorem does not by itself establish
fidelity to informal prose, mathematical originality, necessity, optimal ranking,
or broad researcher usefulness. There is no Mathlib corpus, GNN, language model,
neural embedding or open-problem claim in this release. A useful next study needs
more diverse nonredundant candidates and many more genuine ranking decisions,
followed by a pinned natural Lean/Mathlib development with a leakage audit.

## Reproduce

```sh
proofripple benchmark --domain lists --out outputs/reproduction --certify
python -m unittest discover -s tests -v
python scripts/make_report.py
```

Fresh certification is optional and can take several minutes. Runtime clocks
are hardware-specific; see saved fields rather than treating them as benchmark
equivalence. [Research foundations](research-foundations.md) records primary
sources and attribution. The [v0.1 report](research-report.md) is a separate
propositional testbed and does not supply this release's mathematical results.
