# Media provenance

`wordmark.svg` is an original editable vector. `lab-desktop.png` and
`lab-mobile.png` are actual current-source browser captures using the bundled
Lean-certified demo. `walkthrough.mp4` records real browser interactions with
that recorded experiment, not the duration of a live proof-verification run.
The recorded-experiment notice and research-prototype scope remain visible.

Editable/reusable capture sources are `scripts/check_lab.cjs` and
`scripts/record_walkthrough.cjs`. They require the optional free Playwright
development package and an installed Chrome (or Playwright Chromium). Set
`PROOFRIPPLE_CHROME` to a Chrome executable when using system Chrome. For video,
install Playwright's FFmpeg helper with `playwright install ffmpeg`. Run the
local LAB, then invoke the scripts with an empty output directory.

The release clip is silent H.264, 1440×1000. The original WebM and verification
frames are retained in task-local outputs. Transcoding preserved normal timing;
no generated mathematical results, stock footage, third-party music, narration,
or cloned identity is present. See `provenance.json` for exact output hashes.
