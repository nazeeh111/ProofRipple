# Research foundations and scope

Reviewed 26 October 2026. This is a source review and an architectural argument,
not a replication of the cited experiments. Repository default branches and
websites can change. Paper versions are explicit below.

## What the research supports

The useful unit of discovery is a verified lemma plus evidence that it improves
later reasoning. Counting generated statements rewards specialization,
restatement and duplication. The papers below give complementary ways to avoid
that failure: remove specializations, identify proof bottlenecks, measure proof
compression, and inspect actual downstream reuse.

| Primary source | Established method or purpose | Consequence for ProofRipple |
| --- | --- | --- |
| Ota, Osa and Harada, [Self-Supervised Theorem Discovery in a Formal Axiomatic System, v1](https://arxiv.org/html/2606.28747v1), 27 June 2026, §§4.1–4.3 | Alternates proof search, extraction and library growth in a propositional Hilbert system. Removes substitution-specializations, then ranks candidates using smoothed reprovability estimates. | Include a generality/reprovability-inspired baseline. A previously proved but difficult-to-rederive lemma can be useful. This paper does not establish the same result for arbitrary Lean mathematics. |
| Patel et al., [Learning to Discover Interesting Mathematics, v1](https://arxiv.org/html/2609.28603v1), 23 September 2026, §§2–3 and Appendix C | Defines interestingness using proof length relative to statement length, and extrinsic utility through compression of the surrounding theorem library. Trains a 27B difficulty predictor. | Compare compact ranking with a proof-compression heuristic and direct downstream utility. Its reported utility correlation excludes declarations without downstream users; that qualification matters. Proof length depends on notation, tactics and corpus. A CPU ranker here is a separate experiment, not a reproduction of the 27B model. |
| Barkeshli, Douglas and Freedman, [Artificial Intelligence and the Structure of Mathematics, v1](https://arxiv.org/html/2604.06107v1), 7 April 2026, §§2 and 6.2 | Proposes proof/structural hypergraphs and criteria for mathematical discovery, including verification, novelty detection, selection and closed-loop expansion. | Preserve the distinction between a dependency graph extracted from one proof and all possible mathematical implications. Its comparative system ratings are model judgments, not experimental ground truth. |
| Xu et al., [Lean Graph Search for Formal Theorem Proving, v1](https://arxiv.org/html/2610.22339v1), 15 October 2026, §3 | Starts with semantic matches, propagates relevance through formal dependencies using personalized PageRank, then reranks. | Include a dependency-based retrieval baseline. Retrieval improves access to existing lemmas; it does not itself discover new consequences. A small structural baseline is not a reproduction of its embedding/reranker stack. |
| Kasaura et al., [Discovering New Theorems via LLMs with In-Context Proof Learning in Lean, v4](https://arxiv.org/abs/2509.14274v4), revised 29 June 2026 | Alternates conjecturing and proving while conditioning subsequent iterations on verified prior outputs. | Keep candidate generation separate from verification, and permit verified results to seed later exploration. Proof success alone does not demonstrate downstream usefulness or worldwide originality. |

These sources motivate the design; they do not establish that ProofRipple's
ranking method outperforms other systems. That requires its own frozen-context
experiments.

## Verification and neighboring tools

**Lean 4.** The [official axiom reference](https://lean-lang.org/doc/reference/latest/Axioms/),
§§8.4–8.5, documents transitive `#print axioms` auditing. `sorryAx` can prove
anything. Native evaluation introduces additional axioms depending on the
compiler. Compilation success is therefore insufficient: record the exact
declaration and reject admitted proofs and unexpected axioms. A conservative
policy can permit `propext`, `Classical.choice` and `Quot.sound`, while recording
them explicitly. Axiom-free examples support an even stronger local claim.
Lean's [repository](https://github.com/leanprover/lean4) is Apache-2.0 licensed.

**Mathlib.** The [community library](https://github.com/leanprover-community/mathlib4)
provides definitions, lemmas and tactics under Apache-2.0. Pin the Mathlib commit
and compatible Lean toolchain. A full Mathlib import can already contain a
held-out target or an equivalent lemma. Imported environments need a leakage
audit, not only separate target files. CPU examples can begin with Lean's
standard library and state that boundary explicitly.

**MathVet.** Its [README](https://github.com/mathvet/mathvet/blob/main/README.md)
reviews correspondence between formal statements and source claims, separately
from Lean validity. Its review is explicitly pre-referee. Use this distinction
in every artifact: a checked Lean theorem does not certify the intended prose.
The README labels its paired statement dataset Apache-2.0; that is not a
license determination for every repository artifact. No review verdict or
dataset is incorporated here.

**Prove2Me.** The [platform FAQ](https://beta.prove2.me/faq) describes collaborative
formalization missions, reusable proved statements and private missions. The
[proof submission reference](https://github.com/prove2me/prove2me_workspace/blob/main/references/prove.md)
documents target-type checks and pinned verification environments. This is a
potential interoperability target, not a required dependency. No mission,
submission or public contribution is authorized merely by citing it, and this
project does not claim server verification from a local Lean run. The initial
homepage fetch timed out; the FAQ and reference were accessible. No platform
content is copied.

**Verso Blueprint.** The [project documentation](https://github.com/leanprover/verso-blueprint)
separates original sources, informal exposition and formal Lean content. It
supports inferred dependency edges, formalization progress and exported
metadata. This suggests future metadata export rather than recreating a
Blueprint renderer. Its license was not established from the accessed files;
do not vendor its code on this review alone.

**LeanDojo.** The [original README](https://github.com/lean-dojo/LeanDojo)
now redirects new projects to v2. The [v2 README](https://github.com/lean-dojo/LeanDojo-v2)
describes repository tracing, Pantograph-based proof interaction and model
training, with a CUDA-oriented full installation. A small subprocess adapter
avoids that stack for bounded CPU examples; it does not replace its training
or tracing capabilities.

## Optional OpenAI case study

The [OpenAI math collection](https://github.com/openai/math/blob/main/README.md)
describes manuscripts and proof artifacts at different verification stages,
explicitly characterizing them as research data. Its
[license](https://github.com/openai/math/blob/main/LICENSE) is Apache-2.0.
The [Lean catalogue](https://github.com/openai/math/blob/main/lean/formalization.yaml)
and comparator instructions are the starting points for selecting an individual
case. A scoped case study must pin a commit, identify a declaration, reproduce
its dependencies and compare its formal statement with the manuscript. Merely
indexing the repository cannot establish any headline conjecture. None of its
large proof developments is a mandatory download for the CPU demonstration.

## Evaluation design inferred from this evidence

1. Freeze the available context before generating candidates. Save source
   hashes, imports, toolchain, candidate statements and proof-search settings.
2. Split by mathematical problem family or structure before training. Renamed
   copies and equivalent restatements must stay in one split. Keep test-goal
   proof bodies out of candidate generation, feature construction and training.
3. Rank using only information available at selection time. Historical reuse
   may come from the training corpus; test-goal success is a label, never a
   ranking feature. Distinguish structural/text features from learned semantic
   embeddings.
4. Compare no-added-lemma, random, text similarity, graph heuristics and a
   compression/reprovability-inspired policy under the same search allowance.
   Record verification cost separately from downstream proof-search cost.
5. Recheck each emitted proof in Lean. Record actual use of the new lemma in
   successful downstream proof terms, plus baseline successes and failures.
   A bounded baseline failure establishes search assistance within that budget,
   not mathematical necessity.
6. Report denominators, all seeds, uncertainty and failures. A small synthetic
   domain is a controlled benchmark, not evidence of broad Mathlib performance.
   Corpus-relative novelty is not a claim of new human mathematics.

## Diagrams and launch media

[PaperVizAgent, formerly PaperBanana](https://github.com/google-research/papervizagent)
uses reference retrieval, planning, styling, visualization and iterative critique.
Its documented execution requires model-provider configuration; it is not a
free local diagram renderer by itself. Its
[code license](https://github.com/google-research/papervizagent/blob/main/LICENSE)
is Apache-2.0. The useful transferable method is to derive a diagram from the
actual system, inspect it and revise it. Proof dependency diagrams must be
generated from proof data; an image model's edges are not evidence.

[/brag](https://github.com/latent-spaces/brag) provides a launch-video skill using
HyperFrames, and a separate slim route. Its
[license](https://github.com/latent-spaces/brag/blob/main/LICENSE) is MIT. A local
launch clip can combine recorded application behavior and verified results.
The cited service and installation commands were investigated, not executed by
this source review. Screenshots or clips must retain the distinction between
recorded evidence and a live proof run.

No third-party source code, paper figure, theorem dataset or proof corpus was
copied while producing this review. Citations acknowledge conceptual sources;
any later incorporation requires artifact-specific attribution and licensing.
