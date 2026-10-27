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

theorem automation_goal_0 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p0 xs f p k).length ≤ cap → (stage_p11 xs f p k).length ≤ cap := by
  dsimp [stage_p0, stage_p1, stage_p2, stage_p3, stage_p4, stage_p5, stage_p6, stage_p7, stage_p8, stage_p9, stage_p10, stage_p11]
  grind (gen := 32)

theorem automation_goal_1 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p2 xs f p k).length ≤ cap → (stage_p11 xs f p k).length ≤ cap := by
  dsimp [stage_p0, stage_p1, stage_p2, stage_p3, stage_p4, stage_p5, stage_p6, stage_p7, stage_p8, stage_p9, stage_p10, stage_p11]
  grind (gen := 32)

theorem automation_combined_buffer_safe (xs ys : List Nat) (p q : Nat → Bool)
    (f : Nat → Nat) (k cap : Nat) (fits : xs.length + ys.length ≤ cap) :
    ((((xs.filter p).map f).reverse) ++ ((ys.filter q).take k).map f).length ≤ cap := by
  grind (gen := 32)

run_cmd do
  for n in #[`automation_goal_0, `automation_goal_1, `automation_combined_buffer_safe] do
    let env ← getEnv
    let some ci := env.find? n | throwError "missing declaration"
    let axs ← collectAxioms n
    let ty ← liftTermElabM <| Meta.ppExpr ci.type
    let some value := ci.value? (allowOpaque := true) | throwError "declaration has no checked proof body"
    let deps := value.getUsedConstants.toList.map Name.toString
    logInfo m!"PROOFRIPPLE_AUDIT {Json.compress <| Json.mkObj [("name", toJson n.toString), ("type", toJson ty.pretty), ("axioms", toJson (axs.toList.map Name.toString)), ("constants", toJson deps)]}"
