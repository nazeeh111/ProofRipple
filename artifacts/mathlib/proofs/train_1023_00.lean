import Mathlib.Order.Lattice
import Mathlib.Data.Set.Lattice
import Lean
open Lean Elab Command

theorem pr_distributivity (A B C : Set Nat) : A ∩ (B ∪ C) ⊆ (A ∩ B) ∪ (A ∩ C) :=
  (inf_sup_left A B C).le

theorem pr_cand_00 (A0 A1 A2 A3 A4 A5 : Set Nat) : ((((A1 ∩ A3) ∩ (A0 ∩ A5)) ∩ (((A2 ∩ A3) ∩ (A2 ∩ A0)) ∪ ((A5 ∪ A4) ∩ (A1 ∪ A4)))) ∪ (((A3 ∩ A3) ∩ (A3 ∩ A4)) ∩ ((A0 ∩ A3) ∪ ((A3 ∩ A4) ∩ (A1 ∩ A2))))) ⊆ (((((A1 ∩ A3) ∩ (A0 ∩ A5)) ∩ ((A2 ∩ A3) ∩ (A2 ∩ A0))) ∪ ((A5 ∪ A4) ∩ (A1 ∪ A4))) ∪ ((((A3 ∩ A3) ∩ (A3 ∩ A4)) ∩ (A0 ∩ A3)) ∪ ((A3 ∩ A4) ∩ (A1 ∩ A2)))) :=
  (sup_le_sup (le_trans (pr_distributivity ((A1 ∩ A3) ∩ (A0 ∩ A5)) ((A2 ∩ A3) ∩ (A2 ∩ A0)) ((A5 ∪ A4) ∩ (A1 ∪ A4))) (sup_le_sup le_rfl inf_le_right)) (le_trans (pr_distributivity ((A3 ∩ A3) ∩ (A3 ∩ A4)) (A0 ∩ A3) ((A3 ∩ A4) ∩ (A1 ∩ A2))) (sup_le_sup le_rfl inf_le_right)))

theorem pr_cand_04 (A0 A1 A2 A3 A4 A5 : Set Nat) : ((A5 ∪ A5) ∩ (((A2 ∩ A4) ∪ (A4 ∩ A5)) ∪ (A3 ∩ A0))) ⊆ (((A2 ∩ A4) ∪ (A4 ∩ A5)) ∪ ((A5 ∪ A5) ∩ (A3 ∩ A0))) :=
  (le_trans (pr_distributivity (A5 ∪ A5) ((A2 ∩ A4) ∪ (A4 ∩ A5)) (A3 ∩ A0)) (sup_le_sup inf_le_right le_rfl))

theorem pr_cand_08 (A0 A1 A2 A3 A4 A5 : Set Nat) : (((A2 ∪ A4) ∩ ((A0 ∪ A2) ∪ (A0 ∪ A3))) ∩ ((A4 ∪ A1) ∩ ((A0 ∪ A5) ∪ (A0 ∪ A1)))) ⊆ ((((A2 ∪ A4) ∩ (A0 ∪ A2)) ∪ (A0 ∪ A3)) ∩ ((A0 ∪ A5) ∪ ((A4 ∪ A1) ∩ (A0 ∪ A1)))) :=
  (inf_le_inf (le_trans (pr_distributivity (A2 ∪ A4) (A0 ∪ A2) (A0 ∪ A3)) (sup_le_sup le_rfl inf_le_right)) (le_trans (pr_distributivity (A4 ∪ A1) (A0 ∪ A5) (A0 ∪ A1)) (sup_le_sup inf_le_right le_rfl)))

theorem pr_cand_10 (A0 A1 A2 A3 A4 A5 : Set Nat) : (((A3 ∪ A1) ∩ (((A3 ∩ A0) ∩ (A5 ∩ A1)) ∪ (A2 ∩ A5))) ∩ ((A1 ∩ A4) ∪ (A5 ∩ A4))) ⊆ ((((A3 ∪ A1) ∩ ((A3 ∩ A0) ∩ (A5 ∩ A1))) ∪ (A2 ∩ A5)) ∩ ((A1 ∩ A4) ∪ (A5 ∩ A4))) :=
  (inf_le_inf (le_trans (pr_distributivity (A3 ∪ A1) ((A3 ∩ A0) ∩ (A5 ∩ A1)) (A2 ∩ A5)) (sup_le_sup le_rfl inf_le_right)) le_rfl)

theorem pr_cand_11 (A0 A1 A2 A3 A4 A5 : Set Nat) : (((A1 ∪ A3) ∩ ((A4 ∪ A4) ∪ ((A4 ∩ A5) ∪ (A0 ∪ A5)))) ∩ ((A5 ∩ A5) ∩ (((A2 ∩ A2) ∪ (A3 ∩ A5)) ∪ (A5 ∩ A4)))) ⊆ ((((A1 ∪ A3) ∩ (A4 ∪ A4)) ∪ ((A4 ∩ A5) ∪ (A0 ∪ A5))) ∩ (((A2 ∩ A2) ∪ (A3 ∩ A5)) ∪ ((A5 ∩ A5) ∩ (A5 ∩ A4)))) :=
  (inf_le_inf (le_trans (pr_distributivity (A1 ∪ A3) (A4 ∪ A4) ((A4 ∩ A5) ∪ (A0 ∪ A5))) (sup_le_sup le_rfl inf_le_right)) (le_trans (pr_distributivity (A5 ∩ A5) ((A2 ∩ A2) ∪ (A3 ∩ A5)) (A5 ∩ A4)) (sup_le_sup inf_le_right le_rfl)))

theorem pr_cand_13 (A0 A1 A2 A3 A4 A5 : Set Nat) : ((A0 ∩ A5) ∩ (((A1 ∩ A4) ∪ (A5 ∩ A2)) ∪ (A1 ∪ A4))) ⊆ (((A1 ∩ A4) ∪ (A5 ∩ A2)) ∪ ((A0 ∩ A5) ∩ (A1 ∪ A4))) :=
  (le_trans (pr_distributivity (A0 ∩ A5) ((A1 ∩ A4) ∪ (A5 ∩ A2)) (A1 ∪ A4)) (sup_le_sup inf_le_right le_rfl))

theorem pr_cand_14 (A0 A1 A2 A3 A4 A5 : Set Nat) : (((A0 ∩ A1) ∩ ((A0 ∩ A4) ∪ (A4 ∩ A2))) ∪ ((A0 ∩ A1) ∩ (((A2 ∪ A2) ∩ (A0 ∩ A1)) ∪ (A5 ∩ A2)))) ⊆ (((A0 ∩ A4) ∪ ((A0 ∩ A1) ∩ (A4 ∩ A2))) ∪ (((A0 ∩ A1) ∩ ((A2 ∪ A2) ∩ (A0 ∩ A1))) ∪ (A5 ∩ A2))) :=
  (sup_le_sup (le_trans (pr_distributivity (A0 ∩ A1) (A0 ∩ A4) (A4 ∩ A2)) (sup_le_sup inf_le_right le_rfl)) (le_trans (pr_distributivity (A0 ∩ A1) ((A2 ∪ A2) ∩ (A0 ∩ A1)) (A5 ∩ A2)) (sup_le_sup le_rfl inf_le_right)))

theorem pr_cand_15 (A0 A1 A2 A3 A4 A5 : Set Nat) : (((A0 ∪ A2) ∩ ((A5 ∪ A4) ∪ (A3 ∪ A3))) ∩ ((A0 ∩ A3) ∪ (A2 ∪ A1))) ⊆ ((((A0 ∪ A2) ∩ (A5 ∪ A4)) ∪ (A3 ∪ A3)) ∩ ((A0 ∩ A3) ∪ (A2 ∪ A1))) :=
  (inf_le_inf (le_trans (pr_distributivity (A0 ∪ A2) (A5 ∪ A4) (A3 ∪ A3)) (sup_le_sup le_rfl inf_le_right)) le_rfl)

theorem pr_cand_16 (A0 A1 A2 A3 A4 A5 : Set Nat) : ((((A0 ∩ A1) ∪ (A3 ∩ A2)) ∩ ((A5 ∩ A1) ∪ (A1 ∩ A5))) ∩ (((A3 ∩ A5) ∩ (A4 ∩ A4)) ∩ (((A2 ∪ A0) ∩ (A2 ∪ A4)) ∪ ((A0 ∪ A0) ∪ (A5 ∪ A1))))) ⊆ (((A5 ∩ A1) ∪ (((A0 ∩ A1) ∪ (A3 ∩ A2)) ∩ (A1 ∩ A5))) ∩ (((A2 ∪ A0) ∩ (A2 ∪ A4)) ∪ (((A3 ∩ A5) ∩ (A4 ∩ A4)) ∩ ((A0 ∪ A0) ∪ (A5 ∪ A1))))) :=
  (inf_le_inf (le_trans (pr_distributivity ((A0 ∩ A1) ∪ (A3 ∩ A2)) (A5 ∩ A1) (A1 ∩ A5)) (sup_le_sup inf_le_right le_rfl)) (le_trans (pr_distributivity ((A3 ∩ A5) ∩ (A4 ∩ A4)) ((A2 ∪ A0) ∩ (A2 ∪ A4)) ((A0 ∪ A0) ∪ (A5 ∪ A1))) (sup_le_sup inf_le_right le_rfl)))

theorem pr_goal_0_augmented (A0 A1 A2 A3 A4 A5 : Set Nat) : ((((A0 ∩ A1) ∩ ((A0 ∩ A4) ∪ (A4 ∩ A2))) ∪ ((A0 ∩ A1) ∩ (((A2 ∪ A2) ∩ (A0 ∩ A1)) ∪ (A5 ∩ A2)))) ∩ ((((A1 ∩ A3) ∩ (A0 ∩ A5)) ∩ (((A2 ∩ A3) ∩ (A2 ∩ A0)) ∪ ((A5 ∪ A4) ∩ (A1 ∪ A4)))) ∪ (((A3 ∩ A3) ∩ (A3 ∩ A4)) ∩ ((A0 ∩ A3) ∪ ((A3 ∩ A4) ∩ (A1 ∩ A2)))))) ⊆ ((((A0 ∩ A4) ∪ ((A0 ∩ A1) ∩ (A4 ∩ A2))) ∪ (((A0 ∩ A1) ∩ ((A2 ∪ A2) ∩ (A0 ∩ A1))) ∪ (A5 ∩ A2))) ∩ (((((A1 ∩ A3) ∩ (A0 ∩ A5)) ∩ ((A2 ∩ A3) ∩ (A2 ∩ A0))) ∪ ((A5 ∪ A4) ∩ (A1 ∪ A4))) ∪ ((((A3 ∩ A3) ∩ (A3 ∩ A4)) ∩ (A0 ∩ A3)) ∪ ((A3 ∩ A4) ∩ (A1 ∩ A2))))) :=
  (inf_le_inf (pr_cand_14 A0 A1 A2 A3 A4 A5) (pr_cand_00 A0 A1 A2 A3 A4 A5))

theorem pr_goal_1_augmented (A0 A1 A2 A3 A4 A5 : Set Nat) : ((((A5 ∩ A4) ∩ (A3 ∪ A0)) ∩ (((A2 ∩ A3) ∩ (A1 ∪ A1)) ∪ ((A1 ∪ A3) ∪ (A0 ∩ A1)))) ∩ ((((A1 ∩ A3) ∩ (A0 ∩ A5)) ∩ (((A2 ∩ A3) ∩ (A2 ∩ A0)) ∪ ((A5 ∪ A4) ∩ (A1 ∪ A4)))) ∪ (((A3 ∩ A3) ∩ (A3 ∩ A4)) ∩ ((A0 ∩ A3) ∪ ((A3 ∩ A4) ∩ (A1 ∩ A2)))))) ⊆ ((((A2 ∩ A3) ∩ (A1 ∪ A1)) ∪ (((A5 ∩ A4) ∩ (A3 ∪ A0)) ∩ ((A1 ∪ A3) ∪ (A0 ∩ A1)))) ∩ (((((A1 ∩ A3) ∩ (A0 ∩ A5)) ∩ ((A2 ∩ A3) ∩ (A2 ∩ A0))) ∪ ((A5 ∪ A4) ∩ (A1 ∪ A4))) ∪ ((((A3 ∩ A3) ∩ (A3 ∩ A4)) ∩ (A0 ∩ A3)) ∪ ((A3 ∩ A4) ∩ (A1 ∩ A2))))) :=
  (inf_le_inf (le_trans (pr_distributivity ((A5 ∩ A4) ∩ (A3 ∪ A0)) ((A2 ∩ A3) ∩ (A1 ∪ A1)) ((A1 ∪ A3) ∪ (A0 ∩ A1))) (sup_le_sup inf_le_right le_rfl)) (pr_cand_00 A0 A1 A2 A3 A4 A5))

theorem pr_goal_2_augmented (A0 A1 A2 A3 A4 A5 : Set Nat) : ((((A2 ∪ A4) ∩ ((A0 ∪ A2) ∪ (A0 ∪ A3))) ∩ ((A4 ∪ A1) ∩ ((A0 ∪ A5) ∪ (A0 ∪ A1)))) ∪ (((A2 ∩ A3) ∩ (A0 ∩ A4)) ∩ (((A2 ∪ A0) ∪ (A5 ∪ A4)) ∪ ((A5 ∪ A0) ∪ (A0 ∩ A5))))) ⊆ (((((A2 ∪ A4) ∩ (A0 ∪ A2)) ∪ (A0 ∪ A3)) ∩ ((A0 ∪ A5) ∪ ((A4 ∪ A1) ∩ (A0 ∪ A1)))) ∪ ((((A2 ∩ A3) ∩ (A0 ∩ A4)) ∩ ((A2 ∪ A0) ∪ (A5 ∪ A4))) ∪ ((A5 ∪ A0) ∪ (A0 ∩ A5)))) :=
  (sup_le_sup (pr_cand_08 A0 A1 A2 A3 A4 A5) (le_trans (pr_distributivity ((A2 ∩ A3) ∩ (A0 ∩ A4)) ((A2 ∪ A0) ∪ (A5 ∪ A4)) ((A5 ∪ A0) ∪ (A0 ∩ A5))) (sup_le_sup le_rfl inf_le_right)))

theorem pr_goal_3_augmented (A0 A1 A2 A3 A4 A5 : Set Nat) : (((((A1 ∩ A3) ∩ (A0 ∩ A5)) ∩ (((A2 ∩ A3) ∩ (A2 ∩ A0)) ∪ ((A5 ∪ A4) ∩ (A1 ∪ A4)))) ∪ (((A3 ∩ A3) ∩ (A3 ∩ A4)) ∩ ((A0 ∩ A3) ∪ ((A3 ∩ A4) ∩ (A1 ∩ A2))))) ∪ (((A2 ∩ A3) ∩ (A0 ∩ A4)) ∩ (((A2 ∪ A0) ∪ (A5 ∪ A4)) ∪ ((A5 ∪ A0) ∪ (A0 ∩ A5))))) ⊆ ((((((A1 ∩ A3) ∩ (A0 ∩ A5)) ∩ ((A2 ∩ A3) ∩ (A2 ∩ A0))) ∪ ((A5 ∪ A4) ∩ (A1 ∪ A4))) ∪ ((((A3 ∩ A3) ∩ (A3 ∩ A4)) ∩ (A0 ∩ A3)) ∪ ((A3 ∩ A4) ∩ (A1 ∩ A2)))) ∪ ((((A2 ∩ A3) ∩ (A0 ∩ A4)) ∩ ((A2 ∪ A0) ∪ (A5 ∪ A4))) ∪ ((A5 ∪ A0) ∪ (A0 ∩ A5)))) :=
  (sup_le_sup (pr_cand_00 A0 A1 A2 A3 A4 A5) (le_trans (pr_distributivity ((A2 ∩ A3) ∩ (A0 ∩ A4)) ((A2 ∪ A0) ∪ (A5 ∪ A4)) ((A5 ∪ A0) ∪ (A0 ∩ A5))) (sup_le_sup le_rfl inf_le_right)))

theorem pr_goal_4_augmented (A0 A1 A2 A3 A4 A5 : Set Nat) : (((A3 ∪ A2) ∩ ((A2 ∪ A5) ∪ (A5 ∩ A1))) ∪ (((A2 ∪ A4) ∩ ((A0 ∪ A2) ∪ (A0 ∪ A3))) ∩ ((A4 ∪ A1) ∩ ((A0 ∪ A5) ∪ (A0 ∪ A1))))) ⊆ (((A2 ∪ A5) ∪ ((A3 ∪ A2) ∩ (A5 ∩ A1))) ∪ ((((A2 ∪ A4) ∩ (A0 ∪ A2)) ∪ (A0 ∪ A3)) ∩ ((A0 ∪ A5) ∪ ((A4 ∪ A1) ∩ (A0 ∪ A1))))) :=
  (sup_le_sup (le_trans (pr_distributivity (A3 ∪ A2) (A2 ∪ A5) (A5 ∩ A1)) (sup_le_sup inf_le_right le_rfl)) (pr_cand_08 A0 A1 A2 A3 A4 A5))

theorem pr_goal_5_augmented (A0 A1 A2 A3 A4 A5 : Set Nat) : ((((A2 ∪ A4) ∩ ((A0 ∪ A2) ∪ (A0 ∪ A3))) ∩ ((A4 ∪ A1) ∩ ((A0 ∪ A5) ∪ (A0 ∪ A1)))) ∩ (((A5 ∪ A3) ∪ (A4 ∪ A0)) ∩ ((A5 ∪ A2) ∪ ((A0 ∩ A0) ∪ (A1 ∪ A2))))) ⊆ (((((A2 ∪ A4) ∩ (A0 ∪ A2)) ∪ (A0 ∪ A3)) ∩ ((A0 ∪ A5) ∪ ((A4 ∪ A1) ∩ (A0 ∪ A1)))) ∩ ((((A5 ∪ A3) ∪ (A4 ∪ A0)) ∩ (A5 ∪ A2)) ∪ ((A0 ∩ A0) ∪ (A1 ∪ A2)))) :=
  (inf_le_inf (pr_cand_08 A0 A1 A2 A3 A4 A5) (le_trans (pr_distributivity ((A5 ∪ A3) ∪ (A4 ∪ A0)) (A5 ∪ A2) ((A0 ∩ A0) ∪ (A1 ∪ A2))) (sup_le_sup le_rfl inf_le_right)))

run_cmd do
  for n in #[`inf_sup_left, `sup_le, `le_inf, `sup_le_sup, `inf_le_inf, `le_trans, `inf_le_left, `inf_le_right, `le_sup_left, `le_sup_right, `pr_distributivity, `pr_cand_00, `pr_cand_04, `pr_cand_08, `pr_cand_10, `pr_cand_11, `pr_cand_13, `pr_cand_14, `pr_cand_15, `pr_cand_16, `pr_goal_0_augmented, `pr_goal_1_augmented, `pr_goal_2_augmented, `pr_goal_3_augmented, `pr_goal_4_augmented, `pr_goal_5_augmented] do
    let env ← getEnv
    let some ci := env.find? n | throwError "missing declaration"
    let axs ← collectAxioms n
    let ty ← liftTermElabM <| Meta.ppExpr ci.type
    let some value := ci.value? (allowOpaque := true) | throwError "declaration has no checked proof body"
    let deps := value.getUsedConstants.toList.map Name.toString
    logInfo m!"PROOFRIPPLE_AUDIT {Json.compress <| Json.mkObj [("name", toJson n.toString), ("type", toJson ty.pretty), ("axioms", toJson (axs.toList.map Name.toString)), ("constants", toJson deps)]}"
