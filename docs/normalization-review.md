# Independent normalization review

Scope: `proofripple/normalization.py`, its tests, the thirteen accompanying Lean
rewrite/fact witnesses, and the candidate-filter integration. Reviewed on
26 October 2026 by a reviewer who did not author the normalizer. No code,
benchmark artifacts or publication state was changed during this review.

Reviewed SHA-256 identities:

```text
normalization.py          62ab7fdf6fce576142c2d92a98f3cf220c043450228f436fa0d8f2811a327e04
test_normalization.py     28baacc3cd1e961045412946f90a651f27dbd380670f9f48eb45277e8a3afe75
NormalizationRules.lean   f1fe7337eebf929f2bd56a3f62d52caa6cc7931ee075226b781cabb9b2571ff3
```

## Verdict

No unsound list equality or length equality was found in the implemented rules.
The rules are appropriate for the actual domain: every stage shares the same
predicate `p`, map function `f` and take bound `k`. This conclusion would not
transfer to a language with separately parameterized filters or take limits.

One integration correction is required for reproducible provenance:
`natural_benchmark._source_hashes()` must include `normalization.py`. The
normalizer changes candidate pools and therefore scientific outcomes; its
source identity must be frozen alongside `natural.py` and `engine.py` before
the new benchmark run and release.

The normalizer remains a partial equivalence filter. The review did not find a
common missed universal equality in its bounded probe, but it does not certify
that all mathematically equivalent held-out goals are excluded.

## Rule assessment

- `_all_p` correctly propagates the fact that every element passes `p` through
  reversal and taking a prefix. It deliberately stops at a map, since `p (f x)`
  need not follow from `p x`. Deleting a later filter using this fact is sound.
- `_within_k` correctly recognizes that taking a prefix establishes a length
  bound and that every supported subsequent operation preserves it. Deleting
  a later take with the same bound is sound.
- Two reversals cancel. Map and filter commute with reversal; map commutes
  with take. The chosen rewrite orientations do not swap take and reverse,
  whose ordering can change which elements remain.
- `_length_key` removes only outer map and reverse, which preserve length. A
  take produces `min k` on the previous length. Repeated identical minima are
  idempotent. A filter retains the entire canonical input expression because
  inner maps and prefix/suffix choices can change which elements pass.
- The implementation validates the expression shape and requires earlier
  parent nodes. Its keys are derived from source ASTs rather than incoming
  claimed normal forms or proof statuses.
- Candidate filtering compares normalized endpoint pairs against existing
  edges, the seed and goal pairs, removes normalized identities, and retains
  one cheapest primitive-witness representative. The same filtered pool is
  passed to every selection policy. This review does not re-establish the
  separate search-cost or benchmark-statistics implementation.

The accompanying Lean file proves the generic identities and propagation facts
used by these rules. Its previously reported kernel check is supporting
evidence supplied by the parent; this review inspected its source but did not
repeat that proof run. A proof of each rule is not, by itself, a machine-checked
proof of the entire Python normalization algorithm.

## Independent concrete probe

A separate evaluator enumerated all 5,461 operation words of length zero
through six. It evaluated each word under 320 independently varied parameter
assignments using a fixed seed, for 1,747,520 word/model evaluations:

- lists of length 0–11 over the five values 0–4;
- arbitrary sampled Boolean predicates over those values;
- arbitrary sampled maps from those values to those values;
- independently selected take limits from 0–12.

For every parameter assignment, words with the same canonical-list key
produced identical concrete lists, and words with the same length key produced
identical lengths. No false merge was found. The evaluator used ordinary
Python list filtering, mapping, slicing and reversal, independently of the
normalizer's rewrite implementation. This is bounded concrete evidence, not a
universal proof.

The only distinct-key pair with matching sampled length signatures was not a
universal equivalence. Reading operations left to right:

```text
filter → map → filter → map → filter → take
filter → map → filter → map → take → filter
```

Choose `xs = [0, 3]`, `f(n) = n + 1`, `p(n) = (n ≠ 2)`, and `k = 1`.
The first pipeline yields `[5]`; the second yields `[]`. Keeping those keys
separate is correct. This counterexample also illustrates why sampled equality
alone must never promote a normalization identity.

Probe script retained at `/private/tmp/proofripple-review-normalizer.py` for
immediate review. It is a temporary diagnostic, not part of the released test
suite or a benchmark outcome.

## Release implication

After adding the normalizer to the experiment source manifest, regenerate the
candidate pools and rerun the affected natural-domain benchmark. Keep the
published qualification that equivalence filtering is conservative. The
review found no reason to weaken proof auditing, change the allowed axioms or
claim complete leakage prevention.
