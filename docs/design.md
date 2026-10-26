# PROOFRIPPLE LAB design

The workbench uses warm paper, dark ink and restrained green to make formal evidence legible. Vermilion distinguishes the imported seed theorem; green identifies selected consequences. These encodings are repeated in line styles and explicit labels, so color alone carries no status. The ripple mark draws on the seed-and-consequence model rather than a generic AI icon.

The main canvas is an actual implication graph generated from the loaded run, not an illustrative network. Node selection filters related consequences. The evidence inspector keeps exact Lean source, reported verification status, assumptions and model estimates distinct. Proposed and failed results remain visible. The downstream comparison displays literal recorded solves and expansion counts; it does not imply mathematical necessity or unrestricted proof-search superiority.

The static app has no framework, remote font, analytics or external asset dependencies. It can inspect recorded JSON without a model or Lean installation; live exploration uses the optional local Python server. Importing context JSON runs that server's bounded pipeline. Importing run JSON only displays its reported evidence and does not rerun verification.

Interactions include search, status filtering, accessible graph node selection, arrow-key evidence tabs, run JSON import, Lean export, source copying and recorded goal-path inspection. Keyboard focus is visible; animations are limited to short feedback transitions and removed for reduced-motion preferences. On small screens the graph, evidence inspector, candidates and comparisons become a single reading order.
