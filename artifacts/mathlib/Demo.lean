import Mathlib.Order.Lattice
import Mathlib.Data.Set.Lattice
import Lean
open Lean Elab Command

theorem pr_distributivity (A B C : Set Nat) : A ∩ (B ∪ C) ⊆ (A ∩ B) ∪ (A ∩ C) :=
  (inf_sup_left A B C).le

theorem pr_cand_00 (A0 A1 A2 A3 A4 A5 : Set Nat) : (A0 ∩ (A1 ∪ A2)) ⊆ ((A0 ∩ A1) ∪ A2) :=
  (le_trans (pr_distributivity A0 A1 A2) (sup_le_sup le_rfl inf_le_right))

theorem pr_cand_01 (A0 A1 A2 A3 A4 A5 : Set Nat) : ((A3 ∪ A4) ∩ (A1 ∪ A5)) ⊆ (((A3 ∪ A4) ∩ A1) ∪ A5) :=
  (le_trans (pr_distributivity (A3 ∪ A4) A1 A5) (sup_le_sup le_rfl inf_le_right))

theorem pr_cand_02 (A0 A1 A2 A3 A4 A5 : Set Nat) : ((A0 ∩ (A1 ∪ A2)) ∪ (A3 ∩ A4)) ⊆ (((A0 ∩ A1) ∪ A2) ∪ (A3 ∩ A4)) :=
  (sup_le_sup (le_trans (pr_distributivity A0 A1 A2) (sup_le_sup le_rfl inf_le_right)) le_rfl)

theorem pr_goal_0_augmented (A0 A1 A2 A3 A4 A5 : Set Nat) : ((A0 ∩ (A1 ∪ A2)) ∪ ((A3 ∪ A4) ∩ (A1 ∪ A5))) ⊆ (((A0 ∩ A1) ∪ A2) ∪ (((A3 ∪ A4) ∩ A1) ∪ A5)) :=
  (sup_le_sup (pr_cand_00 A0 A1 A2 A3 A4 A5) (pr_cand_01 A0 A1 A2 A3 A4 A5))

run_cmd do
  for n in #[`inf_sup_left, `sup_le, `le_inf, `sup_le_sup, `inf_le_inf, `le_trans, `inf_le_left, `inf_le_right, `le_sup_left, `le_sup_right, `pr_distributivity, `pr_cand_00, `pr_cand_01, `pr_cand_02, `pr_goal_0_augmented] do
    let env ← getEnv
    let some ci := env.find? n | throwError "missing declaration"
    let axs ← collectAxioms n
    let ty ← liftTermElabM <| Meta.ppExpr ci.type
    let some value := ci.value? (allowOpaque := true) | throwError "declaration has no checked proof body"
    let deps := value.getUsedConstants.toList.map Name.toString
    logInfo m!"PROOFRIPPLE_AUDIT {Json.compress <| Json.mkObj [("name", toJson n.toString), ("type", toJson ty.pretty), ("axioms", toJson (axs.toList.map Name.toString)), ("constants", toJson deps)]}"
