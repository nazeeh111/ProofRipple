# One consequence, two outcomes

This is a source-bound **implication-calculus illustration**, not the Mathlib evaluation. The nodes are arbitrary propositions, the primitive arrows are hypotheses, and every theorem is conditional on those hypotheses. The seed p4 → p6 composes h4 and h5. The graph heuristic selects `ripple_p4_p11`, composing that seed with h6…h10. Its six witness entries are not six new assumptions: the seed itself has two primitive premises.

The starting registry already contains the seed. At eight dequeued-proposition search expansions per goal, the four goals p0…p3 → p11 change from **1/4 to 4/4** with one selected consequence. This is one chosen explanatory case, not a comparative performance estimate. Nineteen candidate consequences, the seed and solved goal witnesses have actual Lean 4.33.1 declaration audits with empty transitive axiom lists. Inspect the exact universally quantified types in each `run.json`; no assumption is presented as an independently proved fact.

- [Selected run](selected/run.json), [generated Lean](selected/ProofRipple.lean), [generation manifest](selected/manifest.json)
- [No selected lemma](without/run.json): 1/4 → 1/4 with the same eight-expansion limit.
- [Longer retained chain](negative/run.json): 0/4 → 0/4, even with the selected consequence. Search failure is **not a counterexample**.
- [Edited budget](edited/run.json): five expansions, 0/4 → 4/4. This edit changes the resource limit, not the logical premises.
- [Figure specification and raw rows](figure-manifest.json), [stdlib generator](figure.py).

| Goal | Starting registry, expansions/result | With selected consequence, expansions/result |
| --- | --- | --- |
| p0 → p11 | 8 / not found | 5 / solved |
| p1 → p11 | 8 / not found | 4 / solved |
| p2 → p11 | 8 / not found | 3 / solved |
| p3 → p11 | 8 / solved | 2 / solved |

## Actual laboratory journey

[Desktop capture](lab-desktop.png) · [375px phone capture](lab-phone.png). These show the actual current-main LAB after changing the budget from eight to five. The controls, application code and recorded studies are unchanged. Select Implication calculus, Graph heuristic, one consequence and eight expansions; Run exploration. Change Search budget to five and run again. Export run JSON and Lean, open a fresh LAB page, and import the saved JSON. The reopened result explicitly says **file-reported** until a fresh run checks it. A malformed import leaves the previous result visible. `browser-export.json` and `browser-export.lean` are those actual browser downloads, not a completed CLI generation.

## Reopen the portable case

[Download the complete small case](proofripple-case.zip). Extract into a fresh directory and run `python3 read_case.py`. The standard-library reader checks the bundle's listed bytes, native generation member sets and hashes, and prints each recorded outcome. This is integrity checking, not proof or authentication. Python and Lean are external runtimes; no runtime binaries, Mathlib cache or study model are bundled.

With the installed current project and **Lean 4.33.1** on PATH:

```sh
proofripple verify-run selected --recheck
proofripple discover invariants.json --method graph --select 1 --budget 8 --out fresh-run
proofripple discover Seed.lean --method graph --select 1 --budget 8 --out from-seed
```

Run these commands from the extracted case. Every output directory must be new. Rechecking reconstructs supported proof source from admitted run bytes; it does not execute uploaded saved Lean as an arbitrary script. The canonical seed importer rejects appended executable commands. The bundle does not include the LAB itself; run `proofripple lab --port 0` from the installed project for the browser workflow.

## Provenance and limits

Current main `f63eae7899c8bf34e4819cb41a7fa60ebcab169c`, Lean `leanprover/lean4:v4.33.1`, ProofRipple `0.3.2.dev0`. Fresh CPU-only core Lean runs on 2026-11-17; no training, new study, provider call or Mathlib rerun. The graph heuristic is an existing supported policy. Candidate generation is bounded; budgets count this implementation's search work, not Lean kernel work or general theorem-proving effort. Exact types, dependencies, audits and source hashes are retained in each run. Formal validity does not certify a natural-language interpretation, novelty or usefulness outside this case.

The separate recorded Mathlib study remains unchanged and does not establish learned-policy advantage. See the repository's research report and independent-review documents. Project/source and this new material: MIT, see root LICENSE and the LICENSE included in the case. Lean is an external Apache-2.0 dependency, not redistributed here.
