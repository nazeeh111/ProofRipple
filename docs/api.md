# Inputs and Python integration

## JSON context

```json
{
  "id": "chain", "title": "A short implication chain",
  "nodes": [{"id":"A","label":"A"},{"id":"B","label":"B"},{"id":"C","label":"C"},{"id":"D","label":"D"}],
  "edges": [{"id":"ab","source":"A","target":"B"},{"id":"bc","source":"B","target":"C"},{"id":"cd","source":"C","target":"D"}],
  "seed": {"id":"seed","source":"A","target":"C","path":["ab","bc"]},
  "goals": []
}
```

Identifiers must begin with an ASCII letter, contain letters/digits/underscores,
and have at most 24 characters. Contexts support 2–128 nodes, at most 1024 edges
for Lean certification, and at most 128 goals. Every seed witness must be a
composable nonempty primitive-edge path. Candidate ids are generated safely.
Labels are strings for display, not arbitrary Lean code.

The `.lean` format is created by `proofripple export-seed`. It contains an inert
JSON manifest and exactly the canonical, generated theorem declaration. The
importer checks the whole file against that canonical representation, then
reconstructs and checks the proof. Extra commands and edited arbitrary modules
are rejected. Edit the JSON context and export again to change the theorem.
The limitation prevents automatically executing user-supplied `#eval`/meta code.

## Library API

```python
import json
from proofripple.engine import discover
from proofripple.lean import certify_run

context = json.load(open("examples/invariants.json"))
proposed = discover(context, k=3, search_budget=8)
checked = certify_run(proposed)
assert checked["verification"]["status"] == "kernel_verified"
print(checked["metrics"])
```

`discover` is exploration only. `certify_run` rebuilds source/status from
witnesses, restores the canonical context seed and context hash, and starts a
fresh pinned Lean process. It does not trust imported proof strings or verdicts.
It checks mathematical witnesses, not empirical budget or metric bookkeeping;
rerun `discover` or the CLI from the context to reproduce those observations.
`verify_source` is an internal developer helper that executes generated Lean;
it is **not** a sandbox for arbitrary untrusted Lean files.

`proofripple.model.train_model(contexts)` trains on the supplied training contexts.
Call `discover(..., model=model, method="learned")` to use it. Baseline method
values are `random`, `semantic` (lexical), `graph`, and `proof_cost`.

## Local service

`proofripple lab` binds to `127.0.0.1:8765`. `POST /api/run` accepts
`{"context": CONTEXT, "budget": 8, "select": 3}` and returns the checked run JSON.
Search budgets are 1–128; selection budgets 0–16. The service checks loopback
Host/Origin headers and does not expose arbitrary filesystem or Lean execution.
It is for a local research session, not an internet-facing deployment.

## Artifact states

- `proposed`: candidate witness, without a successful complete Lean audit.
- `kernel_verified`: exact generated source accepted and every expected
  declaration audited under its explicit domain axiom policy.
- `failed`: compilation, audit or bounded process failure.
- `verification.status = unavailable`: Lean could not be started.

JSON is not a signed certificate. A recorded/imported `kernel_verified` field
reports its producer's evidence. Re-run certification locally when trust matters.

## Concrete list domain (v0.2)

Set `domain` to `list-capacity`. Every node adds `expression`: the first is
`{"op":"input"}`; later nodes use `{"op":"filter","input":"p0"}`
(or `map`, `reverse`, `take`) referring to an earlier node. All stages operate
on actual `List Nat` values with one shared arbitrary `f : Nat → Nat`,
`p : Nat → Bool`, and `k : Nat`. A node represents its stage's length being
at most an arbitrary `cap`. Primitive edges must point from an expression
ancestor to its descendant; their proof terms use registered Lean core facts.
No arbitrary implication-edge hypotheses are introduced in this domain.

```sh
proofripple import-declaration List.length_filter_le --out outputs/imported
proofripple demo --domain lists --method graph --select 1 --out outputs/lists
proofripple demo --domain lists --method learned --select 3 --out outputs/learned
proofripple demo --domain implications --out outputs/logic
proofripple benchmark --domain lists --out outputs/benchmark --certify
```

The default demo/discovery policy is graph ranking with one selected lemma for
list contexts, and learned ranking with three selected lemmas for implications.
`--method` and `--select` override those choices. The natural benchmark uses a
common cap of three for all policies; a smaller eligible pool yields fewer
selected lemmas, including none. The default benchmark domain is `lists`;
use `--domain implications` to reproduce the separate v0.1 experiment.

`POST /api/import-declaration` accepts
`{"name":"List.length_filter_le","budget":8,"select":1,"method":"graph"}`.
It imports the actual allowlisted declaration and runs its supported typed
pipeline context. This registry has one supported seed declaration; it does
not import arbitrary named Lean constants or user-selected modules.
`POST /api/run` also accepts `method`; its context determines the formal domain.

Canonical `.lean` export/import preserves the typed AST and the concrete proof
source. Extra commands are rejected in both domains. Natural certification
records `natural_domain.imported_seed` with the exact environment-read type,
axioms and named proof dependencies. `natural_domain.registered_templates`
labels supplied append/addition templates explicitly as undiscovered rules.

List proofs allow only standard `propext`. The separate direct `grind` control
allows and records the three standard foundational axioms. The propositional
backend remains axiom-free by default. There is no policy setting that permits
`sorryAx`, custom axioms or native-computation axioms.
