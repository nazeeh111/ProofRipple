# Original registered automation attempt

These files preserve the first preregistered control exactly. The generated
preprocessing used `simp only [Set.mem_union, Set.mem_inter] at *`, which raises
an error when the goal is already unfolded. There were 117 such errors; Lean
recovery inserted 117 sorryAx placeholders. All 24 context bundles are FAILED
and none is promoted as a verified control. The 0/254 bundle-level summary is
not a count of aesop failures.

The separate post-study control repair changes only that preprocessing to
best-effort `try simp only ...`; it retains every goal, aesop and resource cap.
Its independent fresh results are stored under `../control-repair/`. Ranking,
training, goal selection and the original scientific outcome digest stay fixed.
