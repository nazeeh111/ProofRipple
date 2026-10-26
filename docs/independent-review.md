# Independent implementation review

Review date: 2026-10-26. Scope: the finite implication prototype, its Lean trust boundary, learned usefulness ranking, experiment accounting, CLI, local server and LAB data contracts. This is a source-and-runtime review, not a security certification, proof of new mathematics, or validation of arbitrary Lean/Mathlib imports. No implementation files were edited by the reviewer.

## Findings and resolution status

1. **P2: LAB silently changed saved experimental budgets on rerun.** `loadRun` originally ignored `budget.search_expansions_per_goal`, and `explore` hardcoded `select:4` while the recorded demo/benchmark used 3. The initial browser controls therefore changed both budgets without saying so. Current source reads the actual expansion field and remembers `selected_lemmas`; final browser verification remains the integrator's responsibility.
2. **P2: accepted reflexive goals could not be certified.** A goal `p0 → p0` passed validation and search returned a valid identity witness with zero expansions and an empty path, but `_term` rejected every empty path. Confirmed by calling `discover` and `certify_run`. Root added identity-proof handling and a regression test; current final test results will be appended below.
3. **P2: generated declaration ids could collide with valid primitive ids.** A context with nodes A/B/C/D, primitive edges h0:A→B, h1:B→C, h2:C→D, ripple_A_D:D→A and ripple_A_D_consequence:D→B, and seed B→D along h1/h2 generated an already occupied consequence id. Certification failed with `Duplicate declaration id`. Current source allocates against the full used-id set with numeric suffixes. A regression test was added.
4. **P2: recertification could attach a seed audit to a different returned seed.** With an empty candidate/goal list, replacing the copied `run.seed` with p0→p1 while leaving `context.seed` p4→p6 returned `kernel_verified`, a p0→p1 displayed proof, and the p4→p6 audited statement. A forged `context_sha256` also survived. This was reproduced with real Lean. Current source resets seed from the validated context and recomputes its hash before verification; a regression test was added.
5. **Release verification initially incomplete:** the first complete benchmark certification timed out after 240 seconds and correctly returned `failed`, with 0/1274 audits. No theorem validity was inferred from search success. This historical attempt was superseded by successful per-context certification described below.

## Independent evidence

- The initial engine/model suite passed all 10 tests. A later suite including real Lean tests passed all 17 tests then present. Poisoned custom-axiom and admitted proofs were rejected, missing audits failed closed, and supported Lean import rejected appended executable commands.
- A separate full CPU benchmark rerun reproduced the shipped outcome digest exactly: `7a93f135ddc33ba372c460921af40b73d3132d5420123b82744aee84f08e9859`. Timing fields are intentionally excluded from this digest.
- Mean net additional goals solved per test context: learned 3.6667, graph 3.8333, random 1.4000, lexical semantic 1.4167, proof cost -0.0833. Regressions are retained in net utility and separately reported. These results do **not** establish that the learned ranker outperforms the structural graph heuristic.
- Independently reran the demo Lean source through a fresh pinned Lean process: `kernel_verified`, 25 audits, all with empty axiom sets. At this snapshot `Demo.lean` exactly matched `demo.json.lean_source` and its recorded SHA256, `fc4424a1e9f5b0324ef1e61619498f576c8efad4c2ed84f4dd9a54ea8aec5d31`.
- Inspected equal-candidate, selected-theorem-count and BFS-expansion budgets across methods. Test labels are computed for evaluation after the trained model is fixed; model training uses only train contexts. All rankers see goal endpoints and graph-derived features. Goal endpoint-pair candidates are excluded. This is task-conditioned selection on one procedural graph family, not a private theorem corpus or a domain-transfer evaluation.

## Material limits

Kernel audits certify the generated statements under every explicitly quantified primitive implication hypothesis. They do not validate natural-language node labels, mathematical novelty, optimal lemma selection, a search failure's impossibility, or empirical metric bookkeeping. `constants` is a direct named-constant dependency list; primitive assumptions are local binders visible in the exact theorem type and witness path, not global axioms. `collectAxioms` supplies the transitive axiom check.

Recorded JSON remains reported evidence: a user can edit it. The LAB explicitly says imported recorded statuses were not rechecked in the current session. Its green badges are not a signed attestation. The live `/api/run` route uses the bounded generated-source pipeline; arbitrary Lean commands are rejected by the canonical importer.

The server is loopback-only, checks Host and Origin, bounds request bodies, limits asset roots after resolution, and emits a restrictive content policy. This review did not perform a full adversarial server audit. Wheel installation, actual browser rendering and public release/CI were not yet available at this snapshot and require final integration checks.

## Exact inspected file snapshot

Files changed concurrently during integration. These hashes identify the reviewed bytes at the time this report was first saved; later verified snapshots are appended below.

| File | SHA256 |
| --- | --- |
| `proofripple/engine.py` | `40fedb52c8efe4b4b51e409607d151b82a30a83b052afb633ad5b7d3c1f595a2` |
| `proofripple/model.py` | `f2014fb0a95e28c14e808b257347ba857f3b625b5af9f939d0be15a8810a7e0c` |
| `proofripple/benchmark.py` | `fe50dec65d06a21e2582c6bf707d76c611c7be4c215694a1e11b1cf0e66914f5` |
| `proofripple/lean.py` | `daaf57e3a81d388c2a666794ed43d11acab9ec41b834c111a236ec7aa5dea3f5` |
| `proofripple/certification.py` | `f6ae10727dbed756c5ee2204956c9224059c289c85338dde25d4044442bca003` |
| `proofripple/cli.py` | `120bb9b9e1cef87221ea6522d8d990f2d3601d040c6150bd1d1e7be3f69b27ce` |
| `proofripple/server.py` | `dbf2b1f9777e8c3913d7b3a4c6f37fb7e28107218576aa6b6b85c708aa0e1b17` |
| `tests/test_engine.py` | `8a10cc4210d3fa251d2822156b446f1b17a2df49755e77d4d81a39895d2b8b64` |
| `tests/test_model.py` | `101d8afd57bc6bf031c3df4bbcfe5e7e7ca693acfb9b3009defe58423c70f053` |
| `tests/test_lean.py` | `32e6e496a589d9a1ecd15c64b397a76be1cc1f95bef88b79de4ac7a46d50216b` |
| `lab/app.js` | `28a4ba5677f1b7563c284f1ac8251cf5ffa7686c5af825c3ec0086a5b2f1528d` |
| `lab/index.html` | `39e2daa8529cea6af36379bf52c4d46150e3d0505f11314cc7b9ccc1fee2f277` |
| `setup.py` | `82703c7bf06ee9d87cc1ecc81d54ea364ef963f70131f2f3e93a58745ee4107c` |
| `MANIFEST.in` | `1b0f65aaf886f65e863e167da579f2bb3c771e083a7b0755ed99628785f9e8de` |
| `pyproject.toml` | `c10584f003b95d51b9c2e8a7175ee66e5fb1e5c32e028b14ae27db49e09a07b8` |
| `examples/invariants.json` | `5c8d6a3c6e2b941bdea75f53395a6a573f2a49d805eec69766bb18d34618d8c9` |
| `examples/no_gain.json` | `d90ff583e409c908baea090900096b619acbbf89a9a725d68730002b30c45ff3` |
| `artifacts/model.json` | `61a0b8b6c75d4b6a9497a35dfd045351d15cdbc26d849acdf2f78c2cb2f3cff2` |
| `artifacts/contexts.json` | `fd5e7d0a1ad70cc0d126035afad619a49f25e751d97af35d3cfa0b99f9384110` |
| `artifacts/benchmark.json` | `689b2e20588b59d54110cfe34a15906b7df357eee889f1d8f35f89bba12b6c53` |
| `artifacts/demo.json` | `0dc449b0841edf33453c60d88e0606b550e2302ecaacf8e829a6a31a5215e9f3` |
| `artifacts/Demo.lean` | `fc4424a1e9f5b0324ef1e61619498f576c8efad4c2ed84f4dd9a54ea8aec5d31` |

## Follow-up verification of fixes

All 18 tests passed after the identity, collision, seed/hash and shared-audit-loop changes (13.615 seconds). This included fresh real Lean checks of poisoned/admitted proofs, forged incoming status/proof/seed/hash, invalid proofs and missing audits. The reviewer also independently certified the original collision context with an additional reflexive goal in one fresh Lean process: `kernel_verified`, 5 audits, generated ids `ripple_A_D_1` and `ripple_B_A`.

The four P2 source issues above are resolved in the inspected implementation. No additional blocking source defect was found in this bounded review. The initial timeout remains recorded as a failed historical attempt; the subsequent complete benchmark certification passed as described below. No installation, browser or public-release result is inferred from source review.

### Verified implementation snapshot after fixes

| File | SHA256 |
| --- | --- |
| `proofripple/engine.py` | `40fedb52c8efe4b4b51e409607d151b82a30a83b052afb633ad5b7d3c1f595a2` |
| `proofripple/model.py` | `f2014fb0a95e28c14e808b257347ba857f3b625b5af9f939d0be15a8810a7e0c` |
| `proofripple/benchmark.py` | `fe50dec65d06a21e2582c6bf707d76c611c7be4c215694a1e11b1cf0e66914f5` |
| `proofripple/lean.py` | `daaf57e3a81d388c2a666794ed43d11acab9ec41b834c111a236ec7aa5dea3f5` |
| `proofripple/certification.py` | `f6ae10727dbed756c5ee2204956c9224059c289c85338dde25d4044442bca003` |
| `proofripple/cli.py` | `120bb9b9e1cef87221ea6522d8d990f2d3601d040c6150bd1d1e7be3f69b27ce` |
| `proofripple/server.py` | `dbf2b1f9777e8c3913d7b3a4c6f37fb7e28107218576aa6b6b85c708aa0e1b17` |
| `tests/test_engine.py` | `8a10cc4210d3fa251d2822156b446f1b17a2df49755e77d4d81a39895d2b8b64` |
| `tests/test_model.py` | `101d8afd57bc6bf031c3df4bbcfe5e7e7ca693acfb9b3009defe58423c70f053` |
| `tests/test_lean.py` | `32e6e496a589d9a1ecd15c64b397a76be1cc1f95bef88b79de4ac7a46d50216b` |
| `lab/app.js` | `28a4ba5677f1b7563c284f1ac8251cf5ffa7686c5af825c3ec0086a5b2f1528d` |
| `lab/index.html` | `39e2daa8529cea6af36379bf52c4d46150e3d0505f11314cc7b9ccc1fee2f277` |
| `setup.py` | `82703c7bf06ee9d87cc1ecc81d54ea364ef963f70131f2f3e93a58745ee4107c` |
| `MANIFEST.in` | `1b0f65aaf886f65e863e167da579f2bb3c771e083a7b0755ed99628785f9e8de` |
| `pyproject.toml` | `c10584f003b95d51b9c2e8a7175ee66e5fb1e5c32e028b14ae27db49e09a07b8` |

## Final certificate integration audit

The complete benchmark now reports `kernel_verified`, with **1274/1274 audits across 12 separate context sources and 108 policy runs**. The reviewer independently checked the saved certificate chain without repeating CPU training/search or Lean compilation:

- Every context and candidate proof witness agrees across its policy repetitions. Each published `artifacts/proofs/test_3000.lean` through `test_3011.lean` regenerates byte-for-byte from the concrete candidate and successful goal witnesses in `certification-runs.json` using the current source builder.
- Each source SHA256 agrees with both its report entry and per-context raw audit. Each expected declaration occurs exactly once in that context's audit; all checks report process return code 0 and empty axiom sets. Aggregated audits are exactly the context-tagged flattening of the individual checks.
- Report declarations, received audits, actual audit count, successful source declarations and policy-run totals agree. The source-manifest hash and raw audit-file hash recompute exactly. The benchmark outcome digest remains the independently reproduced `7a93f135ddc33ba372c460921af40b73d3132d5420123b82744aee84f08e9859`.
- Inspected the memory-bounded per-context certification change and final PROVE/EVALUATE/EXPLAIN timeline change. These preserve fail-closed theorem checking; timeline text does not promote missing/failed audits.

This closes the full benchmark certificate gate. Final wheel installation, browser rendering, release publication and remote CI remain separate integration checks and are not certified by this report.

Integrity references:

- Raw audit JSON SHA256: `cb7eb79ed545442b9ed8ff31a685b2487f08ad5592b4824d40c4e99e2ebab47b`. Any gzip distribution must decompress to these exact bytes.
- Source manifest SHA256: `a86a06386d67248b9a8367a91a20a7e54f450854fca9fdc17b3463649dce7f52`.

| File | SHA256 |
| --- | --- |
| `proofripple/lean.py` | `5848cfd98e337f2d4873f678978d6d03ecd9d23677eec94a2dcc2646fe5fd69c` |
| `proofripple/certification.py` | `af07cb8a07ad48180b16f3a0fe640ff3b91cea372f6fa755f3aa0398c3f13afd` |
| `artifacts/benchmark.json` | `f477dc4acd530e4001c2cc8e0bd35633a38d5bb6c5f2302eb2e068a86d53898e` |
| `artifacts/demo.json` | `7ba7d6b74b1668f24abb4ffc0e1e5605d8f78d59eee04195788b408115c26b64` |
| `artifacts/Demo.lean` | `3eeefa345cff75537b8c3077fa98419e12c0f05e6f47323b64ee42c1c731c036` |
| `artifacts/proofs/test_3000.lean` | `305e270103bdbe2e6813901af79acfa3fb24d67eb651681488b0bb3f7ec60d6a` |
| `artifacts/proofs/test_3001.lean` | `25586b6367e2db30f5e3f8bfe4194bd8efdca5557b6cd5e260b13a4902399a6d` |
| `artifacts/proofs/test_3002.lean` | `ed85d5213c6e83b69979d131b9c52fd39b1f2bad2b25e3ad73b449040690b848` |
| `artifacts/proofs/test_3003.lean` | `e551c2a9a94c04d958cfce2de09ddd1abdee7559d47164b62f15c5650484c48f` |
| `artifacts/proofs/test_3004.lean` | `3ea7a4a1214bd29b9d15d8be66ceeec825e3ad7f1269fc271b46bf5976a0a007` |
| `artifacts/proofs/test_3005.lean` | `59b284aef606605cdc22a8e747abc6caf6451fbd7cb5473f09ed322e5b751e38` |
| `artifacts/proofs/test_3006.lean` | `5f68b35699cb26756f8be6235a5c606afbf4d044fd557758d9238ae252219cd8` |
| `artifacts/proofs/test_3007.lean` | `7297aecee77c675f49a2b576b6ea44860f31646f0e1fe8ea0738fb94394e9ff1` |
| `artifacts/proofs/test_3008.lean` | `5fdbaa15e7a5e90a4b7ed3b53854cb7a206c22c0fc3eb2e2e83ebd2fa3a64616` |
| `artifacts/proofs/test_3009.lean` | `1cba3e1399b49742388fa684879b1750bacfd82051b2cf1263559d6414a56343` |
| `artifacts/proofs/test_3010.lean` | `e3acb68c31e8b4a5c3e8dcdfb079531a8b6870b73f5060d2105165ba95a9a5a1` |
| `artifacts/proofs/test_3011.lean` | `a050efc1c41d1c31c1f61da451d3eee8c57b05e45885bba1d475326c20bd3896` |
