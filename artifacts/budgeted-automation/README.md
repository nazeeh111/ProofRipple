# Fixed-budget Lean automation evidence

These are actual Lean 4.33.1 sources, logs and audits from the two-goal case
study, not generated success fixtures. Source and raw log bytes were copied
unchanged from the initial run; `sha256.json` records their identities.

- `goal-*-baseline-gen8.lean` are deliberately unsuccessful proof attempts.
  Their Lean exit code is 1. Error recovery may expose `sorryAx` in diagnostic
  audits; those attempts are rejected and never counted as verified findings.
- `goal-*-augmented-gen8.lean` prove both goals at the same generation cap by
  adding the selected consequence as a local hypothesis. Both exit 0 and use
  only the three standard axioms.
- `goal-*-augmented-expanded-gen8.lean` additionally unfold local generated
  auxiliary proof constants and beta/zeta-reduce the proof. Both still contain
  the selected candidate constant, excluding an unused-have artifact.
- `control-gen32.lean` proves both pipeline goals and the two-buffer control
  without supplied candidate declarations. It exits 0, showing the narrow
  nature of the lower-generation assistance.
- `base.lean` is the identical pre-goal declaration environment used by every
  paired baseline/augmented attempt. `context.json` and `protocol.json` freeze
  the inputs and prospectively chosen budget. `summary.json` retains observed
  statuses, axioms, exact commands, hashes and limitations.

From the repository root, reproduce the experiment in a **new** directory:

```sh
python scripts/budgeted_automation.py --out outputs/reproduction-budgeted
```

The driver refuses overwrite, uses only generation 8 plus the fixed generation
32 control, and returns success when the expected statuses and proof-usage
checks reproduce. It does not sweep thresholds. To run one archived source:

```sh
ELAN_TOOLCHAIN=leanprover/lean4:v4.33.1 lean --json -j 1 -M 2048 -DmaxHeartbeats=400000 artifacts/budgeted-automation/goal-0-augmented-gen8.lean
ELAN_TOOLCHAIN=leanprover/lean4:v4.33.1 lean --json -j 1 -M 2048 -DmaxHeartbeats=400000 artifacts/budgeted-automation/control-gen32.lean
```

Use the driver for its 60-second per-process timeout. These files are evidence,
not a collection to compile indiscriminately: the baseline failures are
intentional. Generation limits are not equal CPU-work limits. This case study
makes no speedup, mathematical novelty, population-level or ranking-superiority
claim. See [the experiment report](../../docs/budgeted-automation.md).
