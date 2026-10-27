<p align="center"><img src="docs/media/wordmark.svg" alt="PROOFRIPPLE — Follow the consequences" width="820"></p>
<p align="center">
  <a href="https://github.com/nazeeh111/ProofRipple/actions/workflows/ci.yml"><img src="https://github.com/nazeeh111/ProofRipple/actions/workflows/ci.yml/badge.svg" alt="Tests and Lean verification"></a>
  <img src="https://img.shields.io/badge/Lean-4.33.1-164f49" alt="Lean 4.33.1">
  <img src="https://img.shields.io/badge/runtime-CPU%20%C2%B7%20zero%20Python%20dependencies-164f49" alt="CPU, zero Python dependencies">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-164f49" alt="MIT license"></a>
</p>

**A theorem matters for what it enables.** ProofRipple imports a supported Lean theorem, explores reusable consequences, independently checks their proofs, and measures whether they help solve later goals under a frozen search budget.

**v0.2 works with actual list mathematics.** Starting from `List.length_filter_le`, it composes checked facts about filtering, mapping, reversing and taking prefixes into concrete capacity bounds. A compact trained model investigates which consequences are useful. PROOFRIPPLE LAB makes the entire trail inspectable.

This is a small research engine for a registered Lean calculus, with an additional propositional testbed. It does not claim new human mathematics, unrestricted Lean/Mathlib ingestion, or superiority to Lean automation.

<p align="center"><img src="docs/media/v0.2/lab-desktop.png" alt="Actual PROOFRIPPLE LAB with concrete list-capacity consequences, imported theorem audit, and inspectable Lean proofs" width="1200"></p>

[Watch the actual LAB walkthrough](docs/media/v0.2/walkthrough.mp4) · [Mobile preview](docs/media/v0.2/lab-mobile.png) · [Download packages and proof evidence](https://github.com/nazeeh111/ProofRipple/releases)

## Try the laboratory

Python 3.10+; Lean is needed for fresh formal checks. Recorded evidence opens without Lean. No runtime Python dependencies, model endpoint, API key or GPU.

```sh
git clone https://github.com/nazeeh111/ProofRipple.git
cd ProofRipple
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .

# Install elan first if needed: https://github.com/leanprover/elan
elan toolchain install leanprover/lean4:v4.33.1
proofripple doctor
proofripple demo --out outputs/demo
proofripple lab
```

Open **http://127.0.0.1:8765/lab/**. Trace a consequence, inspect its Lean proof and assumptions, change the search/lemma budget or ranking policy, and export a reusable source artifact. Switch to the original implication testbed for a second domain. Recorded and imported statuses are reported evidence; use a fresh local run to recheck them.

## From a theorem to a useful consequence

The [list-capacity example](examples/list_capacity.json) contains twelve concrete `List Nat` stages. Primitive arrows are **proved theorems**, not arbitrary implication hypotheses. The starting library includes the verified composite seed.

1. **Import** `List.length_filter_le` and read its exact type, checked proof constants and transitive axioms from Lean's environment.
2. **Understand** the typed expression graph and its registered length rules.
3. **Explore** compositions that use the seed. Normalize common list identities, remove duplicates, and exclude equivalent held-out answers.
4. **Prove** three surviving consequences in a fresh pinned Lean process. All 42 expected demo declarations pass the explicit `propext`-only policy.
5. **Evaluate** one selected graph-ranked lemma: with eight BFS node expansions per goal, downstream success rises from **0/2 to 1/2**.
6. **Explain** the exact witness and its dependencies; export [the Lean source](artifacts/natural/Demo.lean) or [full run receipt](artifacts/natural/demo.json).

The demo uses a simple graph policy and a one-lemma budget. It is an illustrative workflow, not an unbiased performance estimate or a learned-model result. Registered append/addition templates also demonstrate a two-buffer capacity bound; they are explicitly marked as supplied inference templates, not invented discoveries.

**It also helps actual Lean automation under a fixed budget.** In a separate paired case study, `grind (gen := 8)` proves **0/2** showcase goals; supplying the selected consequence raises that to **2/2**. Both checked proofs use the consequence after auxiliary expansion and beta/zeta reduction. [Sources, audits and reproduction](docs/budgeted-automation.md).

The stronger `grind (gen := 32)` control proves both showcase goals and the two-buffer goal unaided. These results establish local search assistance at the stated generation limit, with no speedup, necessity or broad prover-superiority claim.

## Evaluate the usefulness model

The seven-member ridge ensemble combines twelve structural features, a sixteen-dimensional typed-syntax embedding, and four reuse features from successful frozen training proof witnesses. The embedding is deterministic symbolic feature hashing, not a pretrained semantic model. Reuse history is generated proof-motif usage, not Mathlib chronology. Ensemble disagreement supports budgeted exploration and overlapping proof witnesses receive a redundancy penalty.

The experiment freezes sixteen training, six validation and twelve test contexts. Operator skeleton families differ across splits; mathematical domain and graph-generator family remain shared. Recognized identity, already indexed, repeated, and previously seen goal statements are removed before fitting. Every policy sees the same normalized candidate pool and retained task endpoints, selects up to three lemmas, and receives eight BFS expansions per goal; query counts can differ between contexts. A structure-only model trained on the same data tests whether the extra features earn their cost. Zero, negative and empty-pool outcomes remain in the report.

<!-- NATURAL_RESULTS_START -->
| Selection policy | Solved / retained queries | Net additional | Newly solved | Regressed |
| --- | ---: | ---: | ---: | ---: |
| Goal-aware graph heuristic | 15 / 61 | +5 | 5 | 0 |
| 32-feature usefulness ensemble | 15 / 61 | +5 | 5 | 0 |
| Shortest primitive proof | 15 / 61 | +5 | 5 | 0 |
| Random (five repetitions) | 14.6 / 61 | +4.6 | 4.6 | 0 |
| Lexical similarity | 14 / 61 | +4 | 4 | 0 |
| 12-feature structure-only ensemble | 14 / 61 | +4 | 4 | 0 |

Starting registry: **10/61**. Learned ranking ties graph and proof-cost selection. Only **two** active test contexts offer a real ranking choice; this small study does not establish learned superiority. The retained queries represent **57** normalized statements, with zero recognized prior-index or own-fact target overlap. [Full report and limitations](docs/natural-research-report.md).
<!-- NATURAL_RESULTS_END -->

```sh
# CPU experiment; formal checks are explicit and can take several minutes
proofripple benchmark --domain lists --out outputs/reproduction --certify
python -m unittest discover -s tests -v
```

Proof checks run in separate memory/time-bounded processes, with at most two contexts concurrently. Theorem-count and search budgets are equal; wall time and verification costs are recorded separately. Test outcomes and proof paths never enter training or ranking features.

## Import and reuse

```sh
proofripple import-declaration List.length_filter_le --out outputs/imported
proofripple discover examples/list_capacity.json --out outputs/custom
proofripple export-seed examples/list_capacity.json --out outputs/ListSeed.lean
proofripple discover outputs/ListSeed.lean --out outputs/from-lean

# Compare policies and budgets explicitly
proofripple demo --method learned --select 3 --out outputs/learned
proofripple demo --domain implications --out outputs/logic
proofripple benchmark --domain implications --out outputs/logic-benchmark --certify
python scripts/budgeted_automation.py --out outputs/budgeted-automation
```

The supported declaration registry begins with `List.length_filter_le`. JSON inputs describe a validated typed expression graph. The `.lean` importer accepts the canonical exported theorem format and rejects appended executable commands. It does not run arbitrary user-supplied Lean source. See the [format, CLI and Python API](docs/api.md).

## Trust is a result

- **Lean decides validity.** A fresh subprocess checks generated proof terms. Exact audit coverage, source/context hashes, toolchain, theorem types, named proof dependencies and transitive axioms are recorded.
- **Axiom policies are explicit.** Propositional examples require no axioms. The list calculus allows only standard `propext`. The separate automation control records `propext`, `Classical.choice` and `Quot.sound`. Admitted, custom and native-computation axioms are rejected.
- **Equivalence checks guard the experiment.** Shared-predicate filter identities, reversal, take bounds and map commutation are normalized using [kernel-checked rules](examples/NormalizationRules.lean), with [separate review](docs/normalization-review.md). The normalizer is conservative, not a complete theorem-equivalence oracle.
- **Status is not self-authenticating.** An editable JSON file can report a verdict. Fresh certification rebuilds proof strings, seed metadata and hashes. Missing audits, errors and timeouts fail closed.
- **Claims stay bounded.** Known compositions are not new human mathematics. Exact Lean validity does not certify informal prose. Bounded failure is not mathematical necessity. More lemmas can change search order and reduce success.

## Research, evidence and scope

The contribution is an integrated, auditable **theorem → consequence → downstream-utility loop**, with inexpensive learned ranking and explicit counterchecks. Ridge regression, bootstrap ensembles, feature hashing and graph search are established techniques, not new algorithms claimed by this project.

The design draws on [Self-Supervised Theorem Discovery](https://arxiv.org/abs/2606.28747), [Learning to Discover Interesting Mathematics](https://arxiv.org/abs/2609.28603), [AI and the Structure of Mathematics](https://arxiv.org/abs/2604.06107), and [Lean Graph Search](https://arxiv.org/abs/2610.22339). [Research foundations](docs/research-foundations.md) also examines MathVet, Prove2Me, Verso Blueprint, PaperVizAgent and an optional, carefully scoped OpenAI/math case study.

[Current research report](docs/natural-research-report.md) · [Experiment protocol](docs/methodology.md) · [Architecture](docs/architecture.md) · [Implementation review](docs/independent-review-v0.2.md) · [Contributing](CONTRIBUTING.md)

### Limitations

The list calculus covers nonexpansive pipelines over one shared function, predicate and take bound. These are elementary known facts. Registry omissions create a controlled search problem; the pipeline's monotonicity is not an open mathematical question. Sparse candidate pools and small generated training data limit conclusions. Operator-skeleton holdout is not mathematical-domain transfer. A direct automation control covers the showcase, not every corpus goal under matched tactic resources.

There is no unrestricted Lean/Mathlib index, language model, neural theorem embedding, graph neural network, calibrated uncertainty estimate, global novelty detector, human statement-fidelity review, or open-problem claim. Explanations are deterministic witness-grounded templates. The optional large mathematical releases are references, not runtime dependencies. The [v0.1 experiment](docs/research-report.md) remains available as a separate, explicitly abstract implication testbed.

MIT licensed. Lean is a separately installed Apache-2.0 dependency. No external theorem corpus, paper figure or third-party application source is vendored; [attribution and media provenance](NOTICE.md) identify the research and tooling.
