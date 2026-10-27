# Budgeted Lean automation experiment

This small exploratory experiment tests actual Lean automation, independently
of the Python graph-search evaluator. It uses the frozen two-goal list-capacity
demonstration and the graph policy's single selected candidate
`pr_ripple_p4_p9` from its three-candidate pool.

## Observed result

| Automation setting | Baseline | With selected consequence |
| --- | --- | --- |
| `grind (gen := 8)` | 0 of 2 proofs | 2 of 2 proofs |
| `grind (gen := 32)` direct control | 2 of 2 pipeline goals, plus the separate two-buffer goal | Not tested |

The two generation-8 baseline attempts returned Lean exit code 1 with explicit
`grind` failure diagnostics. Both augmented attempts returned exit code 0 and
passed exact-declaration audits. The generation-32 control independently proved
all three control statements without supplied candidate theorems. No process
timed out. The experiment tested generation 8 prospectively and did not sweep
generation limits until a positive result appeared.

This establishes useful assistance to `grind` under this particular generation
limit and demonstration. It does not establish superiority over Lean's ordinary
higher-budget automation, speedup, mathematical necessity, a trained-ranking
advantage, or performance on a broader population of goals.

## Paired environment and proof integrity

For each of the two goal statements, the baseline and augmented sources share
identical bytes before the goal declaration: all concrete stage definitions,
registered helpers, closed primitive theorems, seed and three candidate
statements. There are no previously proved downstream goal theorems in that
base. The declarations are unannotated; the difference is explicitly presenting
the selected implication as a local hypothesis to `grind`.

Baseline proof body:

```lean
by
  dsimp [stage_p0, stage_p1, stage_p2, stage_p3, stage_p4, stage_p5,
    stage_p6, stage_p7, stage_p8, stage_p9, stage_p10, stage_p11]
  grind (gen := 8)
```

Augmented proof body:

```lean
by
  have ripple := pr_ripple_p4_p9 xs f p k cap
  dsimp [stage_p0, stage_p1, stage_p2, stage_p3, stage_p4, stage_p5,
    stage_p6, stage_p7, stage_p8, stage_p9, stage_p10, stage_p11] at ripple ⊢
  grind (gen := 8)
```

Each goal was tested in a separate Lean process, so one failed proof could not
mask another successful proof. The successful augmented declarations have only
`propext`, `Classical.choice` and `Quot.sound` as transitive axioms. The same
three-axiom allowlist was applied to both variants and the direct control;
`sorryAx`, native-evaluation axioms and custom axioms are rejected. This
three-axiom policy applies to the independent automation experiment, not to the
stricter propext-only emitted list-capacity composition certificates.

Both augmented checked proof terms still contain `pr_ripple_p4_p9` after
expanding their local generated auxiliary proof constants and applying
beta/zeta reduction. This rules out an unused local `have` and an unused
argument to an opaque generated helper as the reason for the recorded
reference. Occurrence in a proof term remains distinct from proof necessity.
The expanded checks were separate successful reruns with identical goal
proofs; their standalone sources and logs are retained alongside the original
paired evidence.

## Fixed resources and limits

All processes used `-j 1`, `-M 2048`, `-DmaxHeartbeats=400000` and a 60-second
wall-clock timeout. The generation control limits tactic instantiation depth;
it does not equate the number of primitive computations or CPU time. Processes
ran concurrently, so their elapsed times are retained as diagnostics and are
not a controlled timing benchmark. Constructing and checking the consequence
also has an upstream cost, which this demonstration does not amortize.

The demonstration's two related goals are not an independent test set. Their
structure and the generation-32 control were already known. This experiment
supports a narrow case study of local lemma presentation; it is separate from
the frozen held-out ranking benchmark and must not be pooled into its results.

## Retained evidence

Full standalone Lean sources, exact context, process commands, logs, audit
records, hashes and the prospectively saved protocol are publicly retained in
[artifacts/budgeted-automation](../artifacts/budgeted-automation/README.md).
See the [summary](../artifacts/budgeted-automation/summary.json),
[source/log hashes](../artifacts/budgeted-automation/sha256.json),
[successful augmented source](../artifacts/budgeted-automation/goal-0-augmented-gen8.lean),
[expanded proof-use check](../artifacts/budgeted-automation/goal-0-augmented-expanded-gen8.lean),
and [strong control](../artifacts/budgeted-automation/control-gen32.lean).
The archived baseline sources are deliberately failed attempts, with failure
logs preserved; their diagnostic admitted terms are not verified findings.

Reproduce the fixed experiment from the repository root:

```sh
python scripts/budgeted_automation.py --out outputs/reproduction-budgeted
```

The [standalone driver](../scripts/budgeted_automation.py) refuses to overwrite
an existing output directory and returns success only when the expected
statuses, axiom audits and expanded candidate-use checks reproduce. It pins
the toolchain and resource limits, and offers no generation-threshold sweep.
To run the strong archived control directly:

```sh
ELAN_TOOLCHAIN=leanprover/lean4:v4.33.1 lean --json -j 1 -M 2048 -DmaxHeartbeats=400000 artifacts/budgeted-automation/control-gen32.lean
```

Use the driver to enforce the per-process timeout. Full sources can also be
checked directly without candidate generation. The original local capture
remains at `outputs/budgeted-automation-v02/` as provenance.

Toolchain observed:

```text
Lean (version 4.33.1, arm64-apple-darwin24.6.0, commit 819816b2e0a3bf405af45ae5c7af2491d8f5bee6, Release)
```

Shared pre-goal environment SHA-256:
`6f31cf3f8b668f345639026f58d6c00ba27c00196d6fd30b3cb0dd162a1fd927`.

| Source | SHA-256 | Exit code |
| --- | --- | --- |
| `goal-0-baseline-gen8.lean` | `bd0fd28dd963fee49eeebab8b8fe0c3979b26bcd58a76ea079d2c92c9e8382b9` | 1 |
| `goal-0-augmented-gen8.lean` | `60c94058d0b611e9efde52567876d5de45f4bdeb2352c08b9321230828f58a86` | 0 |
| `goal-1-baseline-gen8.lean` | `2bb5ef129b131bee982b2650b8e91f21a68b44db2a74fa3018290ee6a1acab8f` | 1 |
| `goal-1-augmented-gen8.lean` | `122e193c11bb19e6bb5f65bb843c794b4e48d2261af424b583b2874ed44939c7` | 0 |
| `control-gen32.lean` | `e0bbacf718ae5c0508495b6bdea6f7be379ac4b26817063bca90737f685bd4b7` | 0 |
