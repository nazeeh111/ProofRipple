import Lean
open Lean Elab Command

def stage_p0 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  xs

def stage_p1 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p0 xs f p k).filter p

def stage_p2 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p1 xs f p k).map f

def stage_p3 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p2 xs f p k).reverse

def stage_p4 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p3 xs f p k).take k

def stage_p5 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p4 xs f p k).filter p

def stage_p6 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p5 xs f p k).map f

def stage_p7 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p6 xs f p k).reverse

def stage_p8 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p7 xs f p k).take k

def stage_p9 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p8 xs f p k).filter p

def stage_p10 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p9 xs f p k).map f

def stage_p11 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p10 xs f p k).reverse

theorem prx_step_filter (xs : List Nat) (p : Nat → Bool) (cap : Nat) :
    xs.length ≤ cap → (xs.filter p).length ≤ cap :=
  fun h => Nat.le_trans (List.length_filter_le p xs) h

theorem prx_step_map (xs : List Nat) (f : Nat → Nat) (cap : Nat) :
    xs.length ≤ cap → (xs.map f).length ≤ cap := by
  rw [List.length_map]
  exact fun h => h

theorem prx_step_reverse (xs : List Nat) (cap : Nat) :
    xs.length ≤ cap → xs.reverse.length ≤ cap := by
  rw [List.length_reverse]
  exact fun h => h

theorem prx_step_take (xs : List Nat) (k cap : Nat) :
    xs.length ≤ cap → (xs.take k).length ≤ cap :=
  fun h => Nat.le_trans (List.length_take_le' k xs) h

theorem pr_h0 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p0 xs f p k).length ≤ cap → (stage_p1 xs f p k).length ≤ cap :=
  fun hx => (prx_step_filter (stage_p0 xs f p k) p cap hx)

theorem pr_h1 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p1 xs f p k).length ≤ cap → (stage_p2 xs f p k).length ≤ cap :=
  fun hx => (prx_step_map (stage_p1 xs f p k) f cap hx)

theorem pr_h2 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p2 xs f p k).length ≤ cap → (stage_p3 xs f p k).length ≤ cap :=
  fun hx => (prx_step_reverse (stage_p2 xs f p k) cap hx)

theorem pr_h3 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p3 xs f p k).length ≤ cap → (stage_p4 xs f p k).length ≤ cap :=
  fun hx => (prx_step_take (stage_p3 xs f p k) k cap hx)

theorem pr_h4 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p4 xs f p k).length ≤ cap → (stage_p5 xs f p k).length ≤ cap :=
  fun hx => (prx_step_filter (stage_p4 xs f p k) p cap hx)

theorem pr_h5 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p5 xs f p k).length ≤ cap → (stage_p6 xs f p k).length ≤ cap :=
  fun hx => (prx_step_map (stage_p5 xs f p k) f cap hx)

theorem pr_h6 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p6 xs f p k).length ≤ cap → (stage_p7 xs f p k).length ≤ cap :=
  fun hx => (prx_step_reverse (stage_p6 xs f p k) cap hx)

theorem pr_h7 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p7 xs f p k).length ≤ cap → (stage_p8 xs f p k).length ≤ cap :=
  fun hx => (prx_step_take (stage_p7 xs f p k) k cap hx)

theorem pr_h8 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p8 xs f p k).length ≤ cap → (stage_p9 xs f p k).length ≤ cap :=
  fun hx => (prx_step_filter (stage_p8 xs f p k) p cap hx)

theorem pr_h9 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p9 xs f p k).length ≤ cap → (stage_p10 xs f p k).length ≤ cap :=
  fun hx => (prx_step_map (stage_p9 xs f p k) f cap hx)

theorem pr_h10 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p10 xs f p k).length ≤ cap → (stage_p11 xs f p k).length ≤ cap :=
  fun hx => (prx_step_reverse (stage_p10 xs f p k) cap hx)

theorem pr_breakthrough (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p4 xs f p k).length ≤ cap → (stage_p6 xs f p k).length ≤ cap :=
  fun hx => (pr_h5 xs f p k cap (pr_h4 xs f p k cap hx))

theorem pr_ripple_p3_p6 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p3 xs f p k).length ≤ cap → (stage_p6 xs f p k).length ≤ cap :=
  fun hx => (pr_breakthrough xs f p k cap (pr_h3 xs f p k cap hx))

theorem pr_ripple_p4_p9 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p4 xs f p k).length ≤ cap → (stage_p9 xs f p k).length ≤ cap :=
  fun hx => (pr_h8 xs f p k cap (pr_h7 xs f p k cap (pr_h6 xs f p k cap (pr_breakthrough xs f p k cap hx))))

theorem pr_ripple_p0_p6 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p0 xs f p k).length ≤ cap → (stage_p6 xs f p k).length ≤ cap :=
  fun hx => (pr_breakthrough xs f p k cap (pr_h3 xs f p k cap (pr_h2 xs f p k cap (pr_h1 xs f p k cap (pr_h0 xs f p k cap hx)))))

-- Registered append/addition inference templates, not graph-discovered claims.
theorem prx_filtered_budget (xs : List Nat) (p : Nat → Bool) (f : Nat → Nat) :
    (((xs.filter p).map f).reverse).length ≤ xs.length := by
  rw [List.length_reverse, List.length_map]
  exact List.length_filter_le p xs

theorem prx_paired_budget (xs ys : List Nat) (p q : Nat → Bool)
    (f : Nat → Nat) (k : Nat) :
    ((((xs.filter p).map f).reverse) ++ ((ys.filter q).take k).map f).length ≤
      xs.length + ys.length := by
  rw [List.length_append]
  apply Nat.add_le_add (prx_filtered_budget xs p f)
  rw [List.length_map]
  exact Nat.le_trans (List.length_take_le' k (ys.filter q)) (List.length_filter_le q ys)

theorem prx_combined_buffer_safe (xs ys : List Nat) (p q : Nat → Bool)
    (f : Nat → Nat) (k cap : Nat) (fits : xs.length + ys.length ≤ cap) :
    ((((xs.filter p).map f).reverse) ++ ((ys.filter q).take k).map f).length ≤ cap :=
  Nat.le_trans (prx_paired_budget xs ys p q f k) fits


theorem budget_goal_0 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p0 xs f p k).length ≤ cap → (stage_p11 xs f p k).length ≤ cap := by
  have ripple := pr_ripple_p4_p9 xs f p k cap
  dsimp [stage_p0, stage_p1, stage_p2, stage_p3, stage_p4, stage_p5, stage_p6, stage_p7, stage_p8, stage_p9, stage_p10, stage_p11] at ripple ⊢
  grind (gen := 8)

run_cmd do
  let n := `budget_goal_0
  let env ← getEnv
  let some ci := env.find? n | throwError "missing declaration"
  let axs ← collectAxioms n
  let ty ← liftTermElabM <| Meta.ppExpr ci.type
  let some value := ci.value? (allowOpaque := true) | throwError "no proof body"
  let reduced ← liftTermElabM <| Meta.zetaReduce value
  let rawDeps := value.getUsedConstants.toList.map Name.toString
  let deps := reduced.getUsedConstants.toList.map Name.toString
  logInfo m!"BUDGET_AUDIT {Json.compress <| Json.mkObj [("name",toJson n.toString),("type",toJson ty.pretty),("axioms",toJson (axs.toList.map Name.toString)),("constants",toJson rawDeps),("zeta_constants",toJson deps)]}"
