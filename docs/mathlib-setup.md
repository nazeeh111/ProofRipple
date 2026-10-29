# Optional Mathlib runtime

The lattice domain uses Mathlib **v4.33.1**, exact commit
`0df444a360eaa60ab8c11dca51a86af692955474`, with Lean **4.33.1**.
The ordinary implication and list-capacity examples do not require Mathlib.
Setup is explicit: theorem verification does not download this dependency.

## Source checkout

Have Python 3, Git and the pinned Lean toolchain installed, with `lean` and
`lake` on `PATH`. If using Elan, the setup script resolves the already installed
toolchain using `elan run` without `--install`; it does not download Lean or
change its default. Missing tools or a different compiler produce an error.

From the ProofRipple repository root:

```sh
python scripts/setup_mathlib.py
```

This creates `.runtime/mathlib-v4.33.1/` only if it is absent. It clones the
public pinned tag, checks its exact commit and checked-in dependency manifest,
and fetches only these official compiled-cache import closures:

```text
Mathlib.Order.Lattice
Mathlib.Data.Set.Lattice
```

The cache command always has explicit module arguments. It never requests the
whole `Mathlib` root and never builds the entire library. The cache utility may
compile locally during bootstrap. `MATHLIB_NO_CACHE_ON_UPDATE=1` prevents a
Mathlib update hook from initiating an argument-free cache download.

The trial's lattice, set and additional exploratory finite-set modules consumed
about 1 GB unpacked, with 57 MB of compressed cache archives. The selected two
module closures are a subset of that trial. Allow working space for source,
pinned dependency checkouts and unpacked compiled files; exact size depends on
the pinned closure and platform. Network access is needed during explicit setup
for public GitHub repositories and Mathlib's official cache service. No paid API,
provider key or GPU is used.

Compressed archives use a new disposable system temporary directory by default;
it is removed when that setup command finishes. Needed source and unpacked
runtime dependencies remain durable under `.runtime/`. To retain compressed
archives in a chosen non-synced directory:

```sh
python scripts/setup_mathlib.py --cache-dir /private/tmp/proofripple-mathlib-cache
```

This does not clean an existing supplied cache directory. A compatible ready
runtime is reused without fetching its cache again.

## Offline check and provenance receipt

```sh
python scripts/setup_mathlib.py --check
```

The check verifies the exact root commit, clean tracked source, toolchain file,
manifest SHA-256, all eight dependency checkouts at their pinned commits, and
the two required compiled modules. It then runs a small closed distributivity
proof through the installed Lean binary using explicit existing library paths,
without invoking Lake dependency resolution. The proof must pass an explicit
allowlist of `propext`, `Classical.choice` and `Quot.sound`; admitted or custom
axioms are rejected.

The command prints a JSON receipt containing:

- `ready`, the root and revision, and whether a cache fetch occurred;
- the observed Lean version and both imported compiled-module hashes;
- manifest hash and all eight verified dependency revisions;
- the smoke proof's source hash, output hash and actual transitive axioms.

The pinned manifest hash is
`1009a101f52a9d5d8ca57666f0256bae91abdb693e0f27b5a4622cffcc38cf03`.
It fixes `plausible`, `LeanSearchClient`, `importGraph`, `proofwidgets`, `aesop`,
`Qq`, `batteries` and `Cli`. The script checks the installed dependency revisions,
not just the manifest's claims.

`--check` is read-only with respect to the checkout and never downloads. It
creates only a temporary smoke-proof file. Save stdout to a task-specific file
if a persistent receipt is useful. Failure returns a nonzero exit code and a
JSON error; readiness is never inferred from a directory merely existing.

## Custom destination and installed package

Keep the runtime in a durable directory of your choice:

```sh
python scripts/setup_mathlib.py --root /absolute/durable/path/mathlib-v4.33.1
export PROOFRIPPLE_MATHLIB_ROOT=/absolute/durable/path/mathlib-v4.33.1
```

For an installed wheel, run the setup utility from the source distribution or
repository, then point `PROOFRIPPLE_MATHLIB_ROOT` to that checkout before using
the Mathlib domain. This avoids storing a large optional runtime inside an
installed package. The environment variable does not change Lean's default
installation or grant permission to execute arbitrary Lean source.

To check a custom runtime:

```sh
python scripts/setup_mathlib.py --root /absolute/durable/path/mathlib-v4.33.1 --check
```

An existing wrong revision, invalid checkout or tracked source modification is
preserved and rejected. The script never resets, pulls, deletes or replaces an
existing runtime. Untracked build outputs and probe files are preserved; they
are excluded from the tracked-source cleanliness check. If a download is
interrupted, any partial destination is retained for inspection. Choose a fresh
`--root` if the existing directory cannot pass the pinned checks.

The setup's dependency and import smoke checks establish runtime readiness.
Individual theorem verification still needs exact statement, proof and axiom
audits. A Mathlib cache file is not evidence that a proposed consequence was
proved or useful.
