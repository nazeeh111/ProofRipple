# Attribution and provenance

ProofRipple's source, interface, wordmark, example manifests and model-training
implementation are original to this repository and MIT licensed.

Lean 4 is a separately installed Apache-2.0 project by Microsoft and contributors:
https://github.com/leanprover/lean4. Its actual compiler and standard libraries
perform proof checks. No Lean source or binary is redistributed here.

The research works and neighboring tools in `docs/research-foundations.md` inform
the design. Their results are not ProofRipple results. No third-party theorem
dataset, paper figure, research code or application source is vendored.

The optional Mathlib set-algebra domain uses Mathlib's separately downloaded
Apache-2.0 source and official compiled cache, pinned to v4.33.1 at
`0df444a360eaa60ab8c11dca51a86af692955474`:
https://github.com/leanprover-community/mathlib4. Its dependency manifest and
licenses remain in the local runtime. The repository and release packages
contain ProofRipple's generated example proofs and audit receipts, rather than
redistributing that compiler/library cache. Actual theorem names and source
revisions are recorded with the proof evidence. OpenAI/math, MathVet, Prove2Me
and Verso Blueprint remain research references.

PaperVizAgent's inspect-and-refine method informed diagram review; its model
pipeline was not run. The installed [brag skill](https://github.com/latent-spaces/brag)
informed the authentic launch clip. The clip uses actual local LAB interactions,
retains the recorded-experiment notice, and has no generated proof results,
music, cloned voice or third-party media.
