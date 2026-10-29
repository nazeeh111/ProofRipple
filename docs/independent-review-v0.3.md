# Independent Mathlib artifact review

Reviewed on 2026-10-29 against the saved first study artifact at `outputs/ci-40823797426-mathlib/mathlib`, from [CI run 40823797426](https://github.com/nazeeh111/ProofRipple/actions/runs/40823797426). The reviewer previously accepted the exact source/data protocol before labels; that review is in `docs/mathlib-protocol-review.md`.

**Status: the ranking study, certified proof evidence and separate repaired automation control pass independent artifact checks.** The repaired stronger control proves **254/254** exact held-out goals. The original automation bundles remain failed evidence. This review does not treat their zero promoted bundles as zero aesop solves.

## Result and claim boundary

The primary learned-minus-greedy contrast is **−0.64195 percentage points**, with the predeclared paired whole-context bootstrap interval **[−1.55093, +0.19571] pp**. This does not establish learned superiority over the strong predeclared greedy comparator. Greedy has the highest observed aggregate mean among the reported heuristics. At the fixed product summary profile k3/B8, learned solves **82/254**, greedy **96/254**, and branching-aware **92/254**.

The primary endpoint averages the nine budget profiles within each of 24 held-out contexts, then averages contexts equally. It is not a pooled theorem count. Random's five repetitions are averaged inside each context/profile. The 2,000 bootstrap draws resample paired whole contexts, seed 2027. All nine profile results and all nine learned-policy contrasts were independently recomputed, including negative differences. Secondary intervals are unadjusted for multiple comparisons.

| Lemma cap / goal visits | Starting registry | Learned | Greedy coverage | Branching-aware |
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

These are known positive set-algebra facts over six arbitrary `Set Nat` parameters. The finite statement holdout is not a claim of mathematical originality or absence from all of Mathlib. Selected facts can guide midpoint search as well as replace proof subtrees. Goal visits, failed branches and cache hits are charged under the frozen custom search unit; this unit is not a Lean tactic heartbeat or a matched wall-time budget. Direct constant references in checked proof bodies establish emitted-proof use under the closed application-only proof grammar, not mathematical necessity.

## Independent checks completed

The replay/check code and machine-readable receipt are task-local at `outputs/independent-review-v03/review_artifact.py` and `artifact-review.json`; its actual output is in `artifact-review.log`. It does not modify the eight scientific source files, fit a new model, select a favorable test subset, or replace recorded outcomes.

- Matched all eight current scientific source files, saved experiment sources and the pre-label optimized receipt. Both corpus gzip files are byte-identical to the prospectively accepted files. The complete independent DNF/full-variable-permutation inventory check from the prospective review therefore still applies: 40/12/24 train/validation/test contexts, 412/53/213 candidates and 461/103/254 goals; all 24 test contexts active, 23 candidate pools larger than five; zero recognized prior-statement overlaps.
- Checked all **3,024 records** for complete context/profile/method/repetition coverage, exact goal denominators, legal unique candidate portfolios, correct k limits, baseline consistency, goal-visit bounds, proof-hash presence and visit/attempt/cache/cycle counters. Recomputed per-goal solved/new/regressed/marginal counts and all **90 policy/profile summaries**. No recorded regression occurs; failures and zero effects remain present.
- Independently reproduced the scientific outcome digest and all nine paired context-bootstrap contrasts. Learned and greedy choose different portfolio sets in **126/216** context/profile pairs, so this is an actual ranking comparison. Learned differs from branching-aware in 100/216 and static graph in 157/216.
- Checked model bytes against their report hash and all **6,180 train-only conditional label rows** against their digest, legal budget, deterministic uniform partner sampling and candidate exclusion. The model uses exactly the 40 frozen training contexts; labels comprise 2,200 positive, 3,980 zero and zero negative values. This label distribution is observed evidence, not an eligibility filter. The static singleton ablation has 1,236 rows.
- Matched all **1,997 certified audit entries** to original Lean log entries, saved source hashes and reconstructed source bytes. Rechecked every saved successful witness through the closed proof AST interface and matched every successful recorded decision's proof hash/endpoints/selected dependencies to that witness inventory. Failed searches have no witness theorem.
- Independently parsed Lean's pretty-printed types back into raw set-expression ASTs for all **1,161 candidate and successful-witness declarations**, checking exact ordered endpoints rather than semantic equality. All **678 candidates** directly reference `pr_distributivity`; 443 successful-witness declarations reference candidate constants matching their exact proof AST dependencies. All certified audit axiom lists are contained in `{propext, Classical.choice, Quot.sound}`; no certified `sorryAx`, custom or native-computation axiom is accepted. The remaining 836 audits are repeated seed/library facts, not new discoveries.
- Replayed **27 actual selections and 540 baseline/augmented searches**, spanning all nine profiles with fixed learned/test_3000, greedy/test_3011 and branching-aware/test_3023 pairs. Selected IDs, decisions, proof hashes and search counters matched exactly. Replayed **14 additional selections and full score traces** on test_3007 at k3/B8, covering all ten policies and all five random repetitions. Also replayed **15 evenly spaced conditional training-label rows** against their actual prefix/augmented searches; every marginal label matched. These fixed checks do not refit the model.

The reviewer did not locally refit the full ensemble or recompile every corpus theorem. The saved CI source/log/audit evidence is checked in full; fresh local search replay is a fixed sample. A second full CI reproduction remains separate evidence and must be verified before claiming it succeeded. Candidate declarations and every distinct successful held-out witness are certified; the entire training utility-label search workload is not individually kernel-certified.

## Original failed automation control

All 24 original bundles report failure. Independently inspected logs contain exactly **117 errors**, all `` `simp` made no progress ``. Lean recovery produced 117 corresponding `sorryAx` diagnostic audits; they are excluded from certified findings. Another 137 goal audits have allowed foundational axioms, but the original bundle-level accounting correctly promotes none of the failed bundles. No aesop failure error was observed. This is a preprocessing-pipeline failure and does not support a claim that aesop solves 0/254 goals.

The supplemental driver `scripts/mathlib_automation_control.py` was inspected separately. Its only generated Lean source change is the reversible insertion of `try` before each existing `simp only [Set.mem_union, Set.mem_inter] at *` line. It keeps the exact 254 goal statements, `intro x hx`, aesop, Mathlib revision, one-thread/2,048 MB/400,000-heartbeat limits and 120-second context timeout. It preserves original sources/results and checks exact original audited type strings. Six reviewer-run synthetic driver tests pass. This is an explicitly post-study mechanical control repair, outside the frozen eight scientific files; no ranking, labels, data or model parameters are changed.

The complete repaired output at `outputs/mathlib-control-repair` is **independently accepted: 24/24 contexts, 254/254 goals and 254/254 valid audits**. For every context, the reviewer checked source bytes against the preserved original, verified that inserting `try` is the entire change, matched all source/check/log/type hashes, matched exact original declaration names and type strings, and checked every logged audit against its saved check. The original type strings had already been independently parsed against the frozen goal ASTs. All processes report success, no Lean errors appear, and the axiom union is exactly `{propext, Quot.sound}` with no `sorryAx` or discovered seed/candidate dependencies. The original benchmark file hash is unchanged.

The independent control check and receipt are `outputs/independent-review-v03/review_control.py` and `control-review.json`. This adds a separately labeled, stronger automation result rather than revising the frozen ranking experiment or its failed original control bundles. Its 254/254 outcome is counterevidence to any broad proving-superiority claim for the bounded registry search. Different resource regimes still prevent a matched-compute comparison.

## Evidence identifiers

| Artifact | SHA256 |
| --- | --- |
| Authoritative pre-label source-freeze file | `dcc33a26ccd65926b582bd48abefefea000bd7a8f3b77f9fc97e36d1514bb541` |
| Canonical frozen protocol | `77b18b27e48db9a6cfa07341611517da13dca9fb628e496ab62e28a952566800` |
| Canonical retained corpus | `e25fec0e9d9fa6dcbd6d43b923f2f8f86807b49a5c0b1ee551b38d7c6a4f6071` |
| Original study `benchmark.json` bytes | `e67c6112c0cfaa7d67133a2d98becbe6666ee2df1b726fb0856df3c6401737e6` |
| Original scientific outcome digest | `181c9295653d4ee547ef46f1fe2d95cfc5f5fa1e55147a3c9eb38ece5f13542f` |
| Original compressed certified audits | `bf823a819740a8cdf7928c01c0c3024d372f6bbaa9ac54aa9b727e45dbdf79e2` |
| Supplemental control `summary.json` | `0c7bc7c3e0e2d5a43625589ff0f721233dce30d3f911063fd56aaef11df284d0` |
| Supplemental control driver | `6d2e806dadbd5d731908cc114d330cbfd4830b586c2e11d837932993c0eb89e0` |
