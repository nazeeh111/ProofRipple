# Prospective Mathlib protocol review

Reviewed before any new corpus training or held-out utility results on 2026-10-27, with a fresh independent source/inventory pass on 2026-10-29. Status: **prospective domain, inventory and exact source/protocol snapshot accepted**. This is not a result report or approval of a completed artifact. A later scientific source change requires a new receipt and review before labels.

## Independently inspected feasibility evidence

The selected language is concrete `Set Nat` expressions over six arbitrary set parameters, union and intersection. The imported Mathlib declaration `inf_sup_left` supplies distributivity. The proposed proof AST includes genuinely binary `sup_le`, `le_inf`, `sup_le_sup`, `inf_le_inf` and transitivity rules, with both ordered child proofs retained. This can represent branching derivations rather than another unary implication graph.

Inspected the actual source `.runtime/mathlib-v4.33.1/LatticeVerified.lean`, its relocated JSON log and `domain-feasibility-receipt.json`. Recomputed source/log hashes, parsed all nine audits and matched them exactly to the receipt; no error messages were present. The candidate body references `pr_seed`, the two-branch downstream proof references `pr_candidate`, and the pointwise automation proof has the **same exact type** while referencing neither candidate nor seed. The source has no assumed set relations or primitive implication-edge hypotheses.

The concrete set proofs use the explicit foundational set `{propext, Classical.choice, Quot.sound}`. Generic `inf_sup_left` has only propext; the other inspected generic binary lattice facts have empty axiom lists. The new concrete-domain profile must be explicit and must not relax the legacy empty or list-domain propext-only profiles. Reject admitted, custom and native-computation axioms.

The actual pointwise automation probe succeeds. A raw grind probe that failed before exposing set membership is an inadequate baseline and must remain failed research evidence, not evidence of useful discovery.

## Conditions for protocol acceptance

1. **Freeze before outcomes.** Keep the agreed 40 train / 12 validation / 24 test contexts and publish a source/hash protocol before fitting, utility-label searches or held-out evaluation. Require at least 20 test contexts with nonempty eligible goals and more eligible candidates than the largest selected-lemma budget, after every exclusion. Eligibility may use only syntax/statement/rule data. No filtering or regeneration on measured solve rate, positive labels or learned advantage. Publish every attempted/rejected generation seed and the exact rejection rule if deterministic label-free rejection sampling is needed.
2. **Use complete endpoint equality keys for this positive set language.** DNF antichains must include associativity, commutativity, idempotence, absorption and distributivity. Canonicalize the ordered source/target pair under a consistent variable permutation, ignoring unused quantified variables. Test invariance under AC/DNF reorder and joint renaming; first-occurrence renaming after arbitrary sorting is insufficient by itself. Remove semantic endpoint identities and duplicate statement pairs. Separate exact endpoint equality from the vacuous claim that all proved universal propositions are logically true.
3. **Prevent closed-statement leakage.** Exclude evaluation goals equivalent to the finite actual registered closed-fact inventory (including seed instances), direct raw syntactic leaf goals, and prior split declarations/candidates/goals under the joint alpha/DNF key. Do not semantically instantiate arbitrary generic rule schemas during exclusion: every valid A⊆B is equivalent to a projection instance (A∩B)⊆B because DNF(A∩B)=DNF(A). That overbroad rule would eliminate every valid inclusion and act as a hidden implication solver. Preserve raw inventories, exclusion reasons and retained denominators; do not hide empty or sparse contexts.
4. **Keep semantic normalization out of runtime proof search.** DNF may establish exclusions/generation validity, but must not silently close, rewrite or prioritize search states through a complete semantic decision oracle. Any such oracle is a separately labeled and costed control. Backward-distributivity pivots may propose intermediates; both transitivity children must still be solved and emitted.
5. **Make branching actual.** Validate every proof-node interface and both child witnesses. Report binary-rule occurrences with two nontrivial children in generated candidates and in actual successful search proofs. A binary constructor with only reflexivity/projection leaves does not by itself demonstrate a difficult branching search workload. Candidate/selected-lemma use must be supported by checked proof bodies. For this closed adapter, direct constant-reference audits plus inspection of its explicit application-only proof grammar are sufficient: the generator emits no local auxiliary definitions or discardable let/lambda wrappers. This is emitted-proof use, not mathematical necessity or a general normalized dependency analysis.
6. **Budget actual attempted work.** The proposed backward AND/OR unit is one visited raw syntactic goal state, charged before a leaf, cache hit or cycle cut. Failed alternatives retain their spent work; a second child is visited only if the first succeeds, with no refund after second-child failure. Success memoization stays inside one request and one portfolio; every hit still costs one visit. Publish exact rule order, midpoint menu/order/cap, depth/cycle handling and tie breaks. Report applicable-rule attempts, cache hits and failed work separately. Do not call this a matched tactic-heartbeat or wall-time budget.
7. **Compare strong deployable selection policies.** Freeze the random, proof-cost, lexical, goal-aware greedy coverage/saving and branching-aware policies, including redundancy handling, before test outcomes. Features may see goal statements and shared structural subproblems; they may not run hidden candidate-versus-goal outcome searches for free. If a baseline uses measured task solves to choose lemmas, charge that search or label it an oracle. All policies receive the same candidates, primitive rules and search caps. Sorting selected facts by id avoids an accidental score-order proving advantage.
8. **Separate selection guidance from proof compression.** If selected endpoints enter the midpoint menu, the observed effect includes search guidance as well as replacing a proof subtree. Disclose this, freeze deterministic caps/order and retain regressions. Do not attribute every gain solely to a shorter proof.
9. **Prespecify the comparison grid and conclusion rule.** The domain design proposes every combination of k in {1,3,5} and goal-state budget in {4,8,12}; declare the primary endpoint and any validation-only model choices before test evaluation, publish all combinations, and retain zero/negative effects. Contexts, not correlated candidates, are the uncertainty unit. Count both nominal active-choice contexts and actual post-result portfolio differences; do not require a learned win for acceptance.
10. **Run strong actual Lean controls on every test goal.** Translate subset obligations pointwise, explicitly expose union/intersection membership and run the fixed strong aesop/tauto recipe without discovered facts. Record exact source, limits, preprocessing, audit types/dependencies/axioms and failures. This may solve every goal and is valid counterevidence to broad proving-superiority claims. Different resource units must remain separately labeled.

## Claims that are already bounded

A valid inclusion with different endpoint DNF keys is a **non-equivalent inclusion**, not a universally strict subset: assigning every set variable empty makes both endpoints equal. The generated theorem remains `⊆`.

These are known distributive-lattice/set facts in a restricted registry. Imported Mathlib, closed verified consequences, learned usefulness prediction and a held-out comparison are distinct evidence states. None establishes human mathematical novelty, historical Mathlib reuse or superiority to unrestricted Lean automation.

## Agreed prospective numeric contract

Before any corpus utility labels, the engine specified the following fixed design. It is coherent with the conditions above; final implementation/inventory acceptance remains pending.

- Search profiles: every k in {1,3,5} crossed with B in {4,8,12}; raw-state depth cap 32 and at most eight transitivity pivots. Selected facts are sorted by id. Direct selected/reflexive/projection/injection/seed leaves all cost one visit.
- Primary comparison: full learned model versus the predeclared dynamic goal-demand greedy policy. For each context, average the augmented-minus-baseline solve-fraction difference over all nine profiles. Empty-goal contexts contribute zero and remain present. Resample whole test contexts together, seed 2027 and 2000 bootstrap draws. Publish every other policy/profile rather than selecting a favorable test winner.
- Labels, as prospectively corrected before any corpus utility outcomes: training contexts only; each candidate at each of B=4,8,12 receives marginal solve fraction U(S+c)-U(S) for one deterministic uniform partner portfolio at each size 0,1,2,3,4. The candidate is excluded, partners are identical across B, and saturated duplicate portfolios are removed. Features condition on B and the selected prefix. Preserve the empty-prefix-only static model as `learned_singleton`. Immediate marginal labels still need not anticipate future AND completion from an empty prefix.
- History: only successful training **baseline** proof ASTs, deduplicated by context, raw goal pair and proof-AST hash across budgets before counting rules/transitions. It is generated proof usage, not Mathlib chronology.
- Model: seven context-bootstrap ridge members, alpha 4, exploration bonus .35 and diversity penalty .02; fixed before labels. Validation is sanity reporting only, with no hyperparameter selection.
- Shared features: raw AND/OR obligation inventory, depth four and at most 128 distinct pairs per goal. Strong greedy/branch policies use distinct pair and sibling identities and a bounded structural work estimator, not measured proof-search outcomes. Estimator/frontier constants, graph construction and method formulas must be published exactly in the final freeze. Its extra evaluations and selection time are additional costs.

During pre-label source review, an initial heuristic tracked only goal ids and gave an arbitrary second-hit bonus. That was insufficient for the requested strong comparator. The engine is replacing it with distinct-obligation coverage and real paired-premise structure before freeze. A further source correction distinguishes a supplied parent fact from its unproved OR-alternative premises; proving a parent does not make all transitivity intermediates true.

## Fresh independent inventory and source pass, 2026-10-29

The inventory check did not call the bounded utility search. It used a separate positive-DNF implementation and exhaustive permutations of all used variables, rather than calling the production `statement_key`. Across 21,420 distinct ordered DNF pairs, it independently reproduced the retained counts and finite-inventory holdout checks:

| Split | Contexts | Candidates | Goals | Active goal contexts | Pools larger than five |
| --- | ---: | ---: | ---: | ---: | ---: |
| Train | 40 | 412 | 461 | 40 | 40 |
| Validation | 12 | 53 | 103 | 12 | 3 |
| Test | 24 | 213 | 254 | 24 | 23 |

The independently computed training inventory contains 3,860 distinct statement keys; training plus retained validation contains 4,421. Validation goals, test goals and test candidates each have zero overlap with their appropriate prior inventory. Within every retained context there are no normalized endpoint identities, duplicate candidates, duplicate goals, candidate-goal collisions, or candidate/goal overlaps with that context's finite closed-fact inventory. The canonical retained-data digest matches `data-freeze.json`: `e25fec0e9d9fa6dcbd6d43b923f2f8f86807b49a5c0b1ee551b38d7c6a4f6071`.

The actual source was inspected for raw-state charging, failed alternatives, cache/cycle handling, both binary children, deterministic pivot order, goal-aware estimates, exact complementary-premise features, train-only history, fixed prefix partners, conditional rescoring, bootstrap denominators and all nine profiles. DNF/alpha normalization remains confined to generation validity and exclusions. The actual strong automation source introduces set membership, unfolds only union/intersection membership, and calls aesop under the shared verifier's one-thread, 2,048 MB, 400,000-heartbeat and explicit wall-time limits.

A fresh reviewer-run `python3 -m unittest tests.test_mathlib_search -q` passed all 11 synthetic search/model/freeze tests in 22.769 seconds. These tests use hand-declared or mocked utility cases and do not expose frozen corpus training labels or held-out outcomes.

Two reporting gaps were identified before labels: dynamic feature/prediction work was not separately counted, and benchmark records omitted search attempt/cache/cycle counters already computed by the search engine. Both corrections were inspected in the final snapshot. Validation sanity reporting was also expanded prospectively to include learned, greedy and branching-aware policies at the fixed k3/B8 profile. No result-dependent tuning is permitted.

The protocol's predeclared primary comparator is `greedy_coverage`; `branching_aware` must also be reported and used when describing whether learned ranking beats the strongest observed heuristic. A positive primary contrast alone would not support that broader claim. Compression and midpoint guidance remain combined effects, uncertainty remains uncalibrated, and the statement holdout is relative to the finite inspected inventory rather than all of Mathlib.

## Exact prospective snapshot acceptance

The reviewer independently verified all eight current scientific files against their saved `experiment-source` bytes and `source-freeze.json` hashes in `outputs/mathlib-protocol-v03-final`. The frozen protocol's canonical digest matches the receipt. Its 6,180 planned conditional training rows and both outcome-blind flags were checked before any corpus labels. Current acceptance names this exact snapshot; it does not authorize silently substituting later source bytes.

Both compact gzip corpora were independently checked against their stored byte hashes and zero gzip modification times, then parsed and canonically reserialized to compare with the preserved original JSON files. Their semantic values are identical. Compression changes storage only.

| Accepted evidence | SHA256 |
| --- | --- |
| `source-freeze.json` exact file | `d747d5e472ef9e85e2ace070e0fd4676d1367c3b84da2fcb8ddb80e797aa11b1` |
| `frozen-protocol.json` canonical content | `6f92e3fa53607b709d9ec66488d75085144c427ec258b46c9748599af87aca92` |
| Retained contexts canonical content | `e25fec0e9d9fa6dcbd6d43b923f2f8f86807b49a5c0b1ee551b38d7c6a4f6071` |
| Raw contexts canonical content | `2d573acf74b534a22627105368bab44d66593f204abd3ab91bfc16972ffe2bf0` |

This first accepted snapshot was superseded before labels by the narrowly reviewed optimization below. No empirical learned advantage has been observed or accepted by this review.

## Final narrow reacceptance, 2026-10-29

**Go for the first frozen study run.** The authoritative prospective snapshot is now `outputs/mathlib-protocol-v03-optimized`. The reviewer inspected the actual source differences against the previously accepted snapshot, rather than relying on the builder's equivalence report.

The search change memoizes exact JSON syntax strings within a single search/graph construction, retaining strong references to input nodes so object identities cannot be recycled. The memo does not survive a later caller mutation. A separate 32-entry cache stores only raw goal/intermediate-syntax graphs, direct syntactic primitive membership and the unchanged frontier-size priors; callers receive deep copies. No bounded proof outcomes, portfolio-conditioned estimates or utility labels are shared through this cache. Rule order, pivot order, budget charging, feature/heuristic formulas, partner choices and model fitting are unchanged. Logical work counters remain, with additional fields for physical graph-cache construction and preprocessing work. The benchmark changes also preserve already-compressed corpus bytes, fix deterministic certificate split ordering and make the outcome digest insensitive to certificate row order.

The reviewer independently loaded the old search module and compared it with the current module on the hand-declared fixture. All 24 cases, comprising eight candidate portfolios at three budgets, had exactly equal search results, including proof ASTs and search counters. A separate deterministic mock predictor exercised all ten policies; selected candidates, all candidate features/scores, selection traces and logical counters were exactly equal. These are synthetic differential checks, not corpus outcomes. A fresh reviewer-run `python3 -m unittest tests.test_mathlib_search -q` passed all 13 tests in 9.242 seconds, including cache mutation isolation and certificate-order digest checks.

All eight current scientific source hashes were independently matched to the optimized receipt and saved source bytes. Both gzip files are byte-identical to the earlier independently parsed/read-back corpora, so the complete inventory verification remains applicable without repeating it. The frozen protocol hash, unchanged retained-data hash, 6,180 planned training rows and both outcome-blind flags were checked. No corpus labels or held-out outcomes were exposed during this review.

| Final accepted evidence | SHA256 |
| --- | --- |
| Optimized `source-freeze.json` exact file | `dcc33a26ccd65926b582bd48abefefea000bd7a8f3b77f9fc97e36d1514bb541` |
| Optimized frozen protocol canonical content | `77b18b27e48db9a6cfa07341611517da13dca9fb628e496ab62e28a952566800` |
| Optimized `mathlib_search.py` | `7a459cdf04ea929c99e4ee1720bbcf72a1778cea19aa98ebfbff14e69cb7a63b` |
| Optimized `mathlib_benchmark.py` | `baa88df53034cd2b519e07993114d0f3555b2eba27ff18054fbbf464bc313e24` |

Acceptance is prospective and applies to these exact bytes. It supports running and reporting the predeclared study, including null effects and regressions. It does not establish a learned win, successful corpus kernel verification, or completion of the separate LAB work. Any later scientific source change requires a new receipt and proportionate review before treating its run as the accepted study.

## Additional independent implementation checks

The initial seven Mathlib adapter tests passed, including a fresh actual Mathlib compile of a binary candidate and augmented witness with audited seed/candidate dependencies and the explicit foundational allowlist. This is a small adapter check, not a corpus outcome.

Separately checked the optimized joint alpha key against full permutation orbits on all 324 ordered pairs of the 18 nonconstant three-variable positive Boolean functions (89 pair orbits), and on 40 six-variable samples. All checks passed. The existing DNF test also checked 100 random terms against all 64 Boolean assignments. These are useful finite checks plus inspection of the antichain construction, not a formal proof of the whole Python implementation.

## Inspected evidence fingerprints

| File | SHA256 |
| --- | --- |
| `docs/mathlib-domain-design.md` | `ccf947063b3b8aec2110bdc23affca27964dfdcdfc48b1685482986529122d04` |
| `.runtime/mathlib-v4.33.1/LatticeVerified.lean` | `d4b3ed27a36c938f6262ee769c45d201efdcc268655d9bc3c4711f068935fd23` |
| `.runtime/mathlib-v4.33.1/relocation-verified.log` | `24f7cd1e74c104983b092208cc30b67272f3461482ec5a24f7c3f71d33ceb9f5` |
| `.runtime/mathlib-v4.33.1/domain-feasibility-receipt.json` | `24c40b2a591ea2cb51d11d0461dabc435c7899478d4a555c33cc78e6103eb73d` |

Mathlib commit: `0df444a360eaa60ab8c11dca51a86af692955474`; toolchain: `leanprover/lean4:v4.33.1`. This review read source and audit receipts; it did not independently rerun the feasibility compiler process.

Initial inspected adapter snapshot (concurrent implementation may supersede these bytes):

| File | SHA256 |
| --- | --- |
| `proofripple/mathlib.py` | `25389c8022f4919072ce85662ec6f6a314a2ab92607866980f23dd3c5fbbd24b` |
| `proofripple/mathlib_runtime.py` | `8e340d0a03e52c5c9c3157881e650030263001192222c16d519db2bbeae31dc9` |
| `proofripple/mathlib_search.py` | `d8b5a9b06347a32ee9c48e8d45451af2d9958b9bc536cceaf1eb532e97572ebb` |
| `proofripple/mathlib_model.py` | `62a3f4e1c148e19526d2221d2d0bc5b028d52e663f916a11601b00f6e892c4e4` |
| `tests/test_mathlib.py` | `1bff29a7759a6c9d7b1f01e7a75ffe88f7d0fa8b27e012992defe50307dc384d` |
