# PROOFRIPPLE LAB design

The workbench uses warm paper, dark ink and restrained green to make formal evidence legible. Vermilion distinguishes the composite graph seed; green identifies selected consequences. The imported Lean library declaration is shown separately in the formal-basis card. These encodings are repeated in line styles and explicit labels, so color alone carries no status. The ripple mark draws on the seed-and-consequence model rather than a generic AI icon.

The main canvas is an actual implication graph generated from the loaded run, not an illustrative network. Node selection filters related consequences. The evidence inspector keeps exact Lean source, reported verification status, assumptions and model estimates distinct. Proposed and failed results remain visible. The downstream comparison displays literal recorded solves and expansion counts; it does not imply mathematical necessity or unrestricted proof-search superiority.

The static app has no framework, remote font, analytics or external asset dependencies. It can inspect recorded JSON without a model or Lean installation; live exploration uses the optional local Python server. Importing context JSON runs that server's bounded pipeline. Importing run JSON only displays its reported evidence and does not rerun verification.

Interactions include search, status filtering, accessible graph node selection, arrow-key evidence tabs, run JSON import, Lean export, source copying and recorded goal-path inspection. Keyboard focus is visible; animations are limited to short feedback transitions and removed for reduced-motion preferences. On small screens the graph, evidence inspector, candidates and comparisons become a single reading order.

## v0.2: Concrete mathematical domain

The default example is a typed `List Nat` capacity pipeline. Graph nodes show proposition identifiers and operation names; their precise typed meanings appear in the Lean inspector. The formal-basis card exposes `List.length_filter_le` with its actual audited statement, dependencies and axioms. Its imported theorem role is explicitly distinct from the composite seed edge. Primitive capacity edges are closed theorems, whereas the original implication example retains explicit hypotheses.

The active trust policy is visible: the concrete list domain permits `propext`, while the original implication calculus rejects any axiom dependency. Each inspected theorem still reports its own actual axiom set. Fixed append/addition templates are labeled as registered rules, not discovered mechanisms.

The example selector loads each domain's recorded run and benchmark together. Switching runs immediately clears stale benchmark and automation evidence; a failed load preserves the previous context. Imported run JSON is labeled as reported evidence and does not inherit a bundled benchmark. The optional registered-theorem button requests a real local import and audit, preserving prior results on error.

The list benchmark may display a strong automation control only when its recorded status is `kernel_verified` with actual solved and total counts. This control concerns its explicitly stated showcase coverage; it does not turn bounded graph-search gains into a claim of superiority over Lean automation. Benchmark results remain literal data, including negative comparisons against graph heuristics and structure-only ablations.

The ranking selector exposes the actual policy and restores it from each run. Graph-heuristic scores and learned ensemble estimates have different inspector labels; a deterministic graph score never appears as a learned prediction or ensemble uncertainty. The editable lemma budget (0–16) appears alongside the expansion budget and is restored from each loaded run. Both budgets are preserved on local reruns and registered-theorem imports. This permits inspecting cases where adding more lemmas helps less under bounded search. The showcase may use a graph policy even when the experiment includes learned models; no showcase gain is attributed to a model that did not produce it.
