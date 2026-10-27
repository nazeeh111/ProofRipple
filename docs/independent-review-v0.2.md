# v0.2 final implementation and artifact review

Reviewed on 2026-10-26 against the actual working-tree source and the final canonical `artifacts/natural` campaign. The final data/proof receipt integrity checks pass. Earlier leakage and input findings are resolved in this campaign. Publication, installation, final browser rendering and remote CI remain separate integration outcomes; this report does not infer them from source or root-reported test counts.

## Final independent checks

- Independently rebuilt **all 34 Lean proof sources byte-for-byte**, without repeating the full compiler run. Their actual SHA256 values match the report and compressed raw audits. Every expected declaration name appears exactly once in its context audit; every transitive axiom set is contained in propext and no checked proof body uses sorryAx. Totals agree at **3940 expected / 3940 received audits** across 16 training, six validation and 12 test contexts.
- Recomputed compressed/uncompressed audit hashes, source-manifest hash and outcome digest. All eight core source modules, including normalization, match their frozen `experiment-source` copies and recorded hashes. The saved artifact is tied to the inspected source version.
- Independently reconstructed goal cleaning from `raw-contexts.json`, without calling the implementation's `_prepare_splits`. Every retained goal list matches exactly. The rules remove recognized identities, own primitive/seed equivalents and within-context duplicates in every split; validation goals exclude the cleaned training declaration index, and test goals exclude all cleaned training/validation declarations. The indexes include primitives, seeds, retained goals and candidates. These operations inspect statements only, run before fitting/history/label searches, retain original order, and do **not** resample or refill removed queries.
- Independently found **zero retained goal overlaps** with the applicable prior index, zero own-baseline-equivalent retained goals, zero retained identity goals and zero within-context duplicate signatures. All final seeds have different normalized endpoint length keys. Every candidate pool excludes recognized identities, own known facts, equivalent retained goals and duplicate pairs. This is a sound partial normalization check, not a complete mathematical-equivalence oracle.
- Retained goals total **122 train / 28 validation / 61 test**. Test queries represent **57 globally distinct recognized statement pairs** across 11 goal-active contexts out of 12; the empty context remains in all relevant averages. No denominator is silently restored to the original 20-query proposal.
- Checked all **120 test policy runs** against their saved contexts and canonical pools. Every policy selects exactly min(3, eligible pool size), without duplicate ids, and uses at most eight BFS expansions per goal. All 610 saved test goal comparisons replay exactly through 1220 fresh baseline/augmented BFS calls, including expansion counts and witness paths. Recomputed baseline/augmented/newly-solved/regressed/net counts match the saved run metrics and report rows.
- Model file hashes and training-context ids/hashes match. Frozen history exactly recomputes from successful **training-only** baseline proof witnesses. The fit has **36 candidate rows across 13 nonempty training contexts: four positive, zero negative and 32 zero labels**. No held-out labels or supplied proof/outcome fields enter the ranker.
- Rebuilt the final demo source and checked full-source/run/audit hash agreement: **42 audits**, three candidates, two distinct retained goals, and actual graph-policy search improvement **0/2 → 1/2** with k=1. The separate ordinary Lean automation control has matching source/audit receipts and solves **3/3** showcase goals: these two pipeline goals plus the disclosed registered two-buffer template.

## Interpretation of the final result

The test pool has **21 eligible candidates**, three empty pools and only **two contexts with a selected-set ranking choice**. Most contexts contain at most k candidates, so policies supply the same set there. These data support an inspectable bounded research prototype, not a strong general ranking evaluation.

| Policy | Solved retained test queries | Net additional queries |
| --- | ---: | ---: |
| Learned typed-syntax/reuse ensemble | 15 / 61 | 5 |
| Graph heuristic | 15 / 61 | 5 |
| Shortest proof | 15 / 61 | 5 |
| Random, mean across five repetitions | 14.6 / 61 | 4.6 |
| Lexical similarity | 14 / 61 | 4 |
| Structure-only ensemble | 14 / 61 | 4 |

No final policy has a measured regression in this campaign. The learned ranker ties the graph and proof-cost baselines. Its one-query improvement over the structure-only ablation, with only two ranking-choice contexts and four positive training rows, does **not** establish a reliable benefit from the additional features. No broad positive ML, semantic-understanding, Mathlib-transfer or proving-superiority claim is supported. Context bootstrap intervals describe this small generated workload; contexts are the resampling unit.

Ordinary Lean automation solves the entire showcase without discovered lemmas. It uses a separate propext/Classical.choice/Quot.sound allowlist and different resources; it is not an equal-budget graph-policy comparator. The natural adapter remains propext-only and the legacy implication adapter retains its empty default allowlist. The broader automation profile does not relax either artifact domain's gate.

## Supported implementation claims and limits

The registered adapter audits the actual pinned Lean core declaration `List.length_filter_le`, including its elaborated type, direct proof-body constants and transitive axioms. The orange graph seed is a separate composition of closed capacity theorems. List stages are concrete typed expressions, and primitive edges are proved from the library instead of assumed as arbitrary implication hypotheses. Import supports this explicit declaration registry and canonical generated modules, not unrestricted Lean or natural-language formalization.

Candidate generation composes known nonexpansive list-length facts. Fixed append/addition examples are explicitly marked registered templates and `discovered: false`. None is claimed as new mathematics. Graph search gains measure compression within an intentionally restricted registry, not mathematical necessity or difficulty for Lean's ordinary tactics.

The trained model is conventional context-bootstrap ridge regression over 12 structural features, 16 signed symbolic-hash coordinates and four training-reuse motif features. The hash is typed syntax, not a pretrained semantic embedding. Reuse is generated training proof usage, not chronological Mathlib history or human citations. All policies can see task endpoints and the graph. Splits share the same DAG generator and mathematical domain; raw operator skeletons and recognized normalized goal signatures are held out under the documented cleaning rule.

The canonical importer rejects arbitrary appended Lean commands and does not consume supplied proof text as code. The closed-source builder rebuilds proofs and status evidence. Imported LAB statuses remain **reported data**, with an explicit notice that the file has not been rechecked in the current session; green badges are not signed attestations.

## Resolved review findings and rejected campaigns

1. **Equivalent-goal/identity candidate leakage:** the first normalizer missed repeated same-p filtering, reverse/filter commutation and redundant same-k operations. The reviewer kernel-checked concrete counterexamples: test_3001 `ripple_p20_p30` was an identity, and test_3000 `ripple_p10_p4` matched held-out p27→p29 after length equalities. That campaign was rejected and archived.
2. **Residual semantic holdout overlap:** the next corrected pool still had one train-goal signature repeated in ten test queries. A successful matching training baseline proof contributed motif history, although the context supplied no supervised candidate rows. That campaign was also superseded. The final label-free ordered declaration-index pruning removes this overlap without replacing queries; independent final checks found zero.
3. **Malformed input dispatch:** non-object context JSON originally reached `.get` before validation. The bounded object check now rejects it cleanly; its focused regression test passed. The server's payload guard was also inspected.
4. **Stale collision test:** an initial suite had 42/43 tests pass; its failing fixture expected an unsolved goal-0 witness and did not exercise its artificial name collision. The fixture now targets the successful goal 3 case and passed the focused check. This was not a production collision-allocator defect.

## Normalizer contribution and independence

After independently finding the first leakage issue, the integrator explicitly assigned this reviewer a targeted fix. The reviewer wrote `proofripple/normalization.py` and `tests/test_normalization.py`; review of that contribution is therefore **not independent of its implementation**. Integration review belongs to the root agent.

The helper uses sound shared-f/p/k laws: all-p membership survives reverse/take but is invalidated by map; length≤k survives all supported operations; redundant filter/take can then be removed. Double reverse cancels; map/filter commute with reverse, and map commutes with take. An inner map before a filter is preserved. Eight focused tests passed, including 400 separate concrete-list executions varying p, f, k and input data.

Thirteen generic rule/fact lemmas were kernel-checked under propext only, including a constructive induction proof of filter identity. Their retained `NormalizationRules.lean` source hash is `f1fe7337eebf929f2bd56a3f62d52caa6cc7931ee075226b781cabb9b2571ff3`. This establishes the rewrite basis, not a formal proof of the complete Python normalizer or completeness of its equality keys.

## Final artifact fingerprints

- Outcome digest: `7b84c6cbe6ffccf075ccf61ef1eadcb9bec40b6981dcebcc76b1f569ea721082`.
- `audits_sha256`: `04ed26d7322b5758e829a25ab7446b6ea4d499dee85e4c0ce9d728e6067c9c78`.
- `audits_uncompressed_sha256`: `1b39014165c81c7bc66d68b49a5c18b121096dd316390e2ae72b5d283ad009df`.
- `source_manifest_sha256`: `5770b6f649cb77ff0e6b0fe75dec9e5adb0eb1b294c65946469831ca5da2c33f`.

| Inspected file | SHA256 |
| --- | --- |
| `proofripple/benchmark.py` | `fe50dec65d06a21e2582c6bf707d76c611c7be4c215694a1e11b1cf0e66914f5` |
| `proofripple/engine.py` | `aa812638796e9296dfff0426eb60e74db1ed5ffcea42268002e6d9290320078e` |
| `proofripple/lean.py` | `1be15209702cf449cc9bc32d18076736de82323f4fa4be77dc6599e73929277d` |
| `proofripple/model.py` | `f2014fb0a95e28c14e808b257347ba857f3b625b5af9f939d0be15a8810a7e0c` |
| `proofripple/natural.py` | `8df13c811222b88c24ad7c74627407a94d46f84edc429d093c98d65956b25bdd` |
| `proofripple/natural_benchmark.py` | `3c9e825f01c5ce2d81190f0b6327a83764a84840c999e5c19d091f9b528ceea2` |
| `proofripple/natural_model.py` | `ac5eb439546caa582f4a581efd6d953e9970677e345771e131a64360aa1cef31` |
| `proofripple/normalization.py` | `62ab7fdf6fce576142c2d92a98f3cf220c043450228f436fa0d8f2811a327e04` |
| `proofripple/cli.py` | `7be34f4651c8e611f23857bbc625b380bb2972abcb223a2637c5209590cec0ad` |
| `proofripple/server.py` | `ac32a06b84e827b2f13863ef194ed9f460a3ea4af22789aa584dfeb0da7f7902` |
| `lab/app.js` | `74b99fd7331bfda5b8de3ca3c0f443c2b35cef2a84fd5e6c6c52233ec8583521` |
| `lab/index.html` | `d0827cdb64f4e0dcae379de08f5038693548761a0ac3b4108c9d07dfa0b72659` |
| `setup.py` | `508b3dd61676bd3dc79a9ef6499ce8c51af01fb032aca95bcd13c621c96d66c4` |
| `MANIFEST.in` | `22b8f95e8c060e76d90ff4ae2920afbe0d02fea5e0f11dc24292dc3dda4b4eb4` |
| `tests/test_normalization.py` | `fd1d539075f3234043e294d64e3efe43b8389320a4ea3194bbe0b42b207549f0` |
| `artifacts/natural/benchmark.json` | `87ce0f2b05708435ddc6ad0ba63e07ae27992ce87a17545d6201d217ca38909e` |
| `artifacts/natural/model.json` | `251dc6ae4b301396c4242f2bd6ae4afb552c8385d92076bf958fc63e1b988bbe` |
| `artifacts/natural/structure-model.json` | `b4c324c04289e2493f8d2475abda57347fa02d94c2c7aa18b5cb5a31f3377a21` |
| `artifacts/natural/raw-contexts.json` | `cb2ad46736e97350a45d954eed1656b2f468d3626da83cc2bb47c4585fc428b2` |
| `artifacts/natural/contexts.json` | `5f10e950abedd5bf3989577d4ab344b0fc78d2463d858a9f4e378e65a48ca2e2` |
| `artifacts/natural/holdout-audit.json` | `ac5c78d8d3f4a18b65cc4528c24f04cf12414eb5c4ec4c4ed267f21a853caa46` |
| `artifacts/natural/certification-runs.json` | `e499ba88c6a391bc38f37198ba7b4ed2dfec3bff8ce90b62702252677ccae287` |
| `artifacts/natural/demo.json` | `f0a16a32ef9734c4769b00de1d0cf9b7c68b38ae57407257fd1c5517c40a8c1d` |
| `artifacts/natural/Demo.lean` | `92f15565abf1edb80839f5e4a6f92e3874f492534a75221350489c956f24e76c` |
| `artifacts/natural/automation-control.lean` | `e0bbacf718ae5c0508495b6bdea6f7be379ac4b26817063bca90737f685bd4b7` |
| `artifacts/natural/automation-audit.json` | `cdd8292e5b5ee3c7491ca1fb3020deb1476a0c39fae1de1f381096cecde85826` |
| `artifacts/natural/experiment-source/NormalizationRules.lean` | `f1fe7337eebf929f2bd56a3f62d52caa6cc7931ee075226b781cabb9b2571ff3` |
