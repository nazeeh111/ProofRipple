import Mathlib.Order.Lattice
import Mathlib.Data.Set.Lattice
import Lean
open Lean Elab Command

theorem control_goal_00 (A0 A1 A2 A3 A4 A5 : Set Nat) : ((((A5 ∪ (A4 ∩ (A1 ∪ (A4 ∩ A3)))) ∩ ((A5 ∪ (A2 ∩ (A4 ∪ (A4 ∩ A3)))) ∪ (A3 ∩ (A2 ∪ (A4 ∩ (A2 ∪ A1)))))) ∪ ((A2 ∩ (A1 ∪ A5)) ∩ ((A2 ∩ (A2 ∪ A2)) ∪ (A5 ∪ (A1 ∩ A1))))) ∪ (((A4 ∩ (A1 ∪ (A2 ∩ (A1 ∪ A3)))) ∩ ((A1 ∩ (A0 ∪ A4)) ∪ (A0 ∪ (A0 ∩ (A1 ∪ (A3 ∩ A0)))))) ∪ (A1 ∩ (A0 ∪ A4)))) ⊆ ((((A5 ∪ (A2 ∩ (A4 ∪ (A4 ∩ A3)))) ∪ ((A5 ∪ (A4 ∩ (A1 ∪ (A4 ∩ A3)))) ∩ (A3 ∩ (A2 ∪ (A4 ∩ (A2 ∪ A1)))))) ∪ (((A2 ∩ (A1 ∪ A5)) ∩ (A2 ∩ (A2 ∪ A2))) ∪ (A5 ∪ (A1 ∩ A1)))) ∪ ((((A4 ∩ (A1 ∪ (A2 ∩ (A1 ∪ A3)))) ∩ (A1 ∩ (A0 ∪ A4))) ∪ (A0 ∪ (A0 ∩ (A1 ∪ (A3 ∩ A0))))) ∪ (A1 ∩ (A0 ∪ A4)))) := by
  intro x hx
  simp only [Set.mem_union, Set.mem_inter] at *
  aesop

theorem control_goal_01 (A0 A1 A2 A3 A4 A5 : Set Nat) : (((A5 ∪ (A3 ∩ (A4 ∪ (A2 ∩ A1)))) ∩ ((A0 ∪ (A1 ∩ (A3 ∪ (A1 ∩ A3)))) ∪ (A3 ∩ (A0 ∪ (A2 ∩ (A5 ∪ A0)))))) ∩ ((A3 ∪ (A2 ∩ (A1 ∪ (A1 ∩ A3)))) ∩ ((A1 ∪ (A0 ∩ A4)) ∪ (A3 ∪ (A5 ∩ A1))))) ⊆ ((((A5 ∪ (A3 ∩ (A4 ∪ (A2 ∩ A1)))) ∩ (A0 ∪ (A1 ∩ (A3 ∪ (A1 ∩ A3))))) ∪ (A3 ∩ (A0 ∪ (A2 ∩ (A5 ∪ A0))))) ∩ (((A3 ∪ (A2 ∩ (A1 ∪ (A1 ∩ A3)))) ∩ (A1 ∪ (A0 ∩ A4))) ∪ (A3 ∪ (A5 ∩ A1)))) := by
  intro x hx
  simp only [Set.mem_union, Set.mem_inter] at *
  aesop

theorem control_goal_02 (A0 A1 A2 A3 A4 A5 : Set Nat) : ((((A1 ∪ (A1 ∩ (A0 ∪ (A5 ∩ A1)))) ∩ ((A2 ∩ (A0 ∪ A0)) ∪ (A0 ∪ (A5 ∩ A3)))) ∪ ((A3 ∪ (A0 ∩ A2)) ∩ ((A2 ∩ (A2 ∪ A2)) ∪ (A3 ∩ (A1 ∪ (A2 ∩ (A2 ∪ A4))))))) ∩ (((A5 ∪ (A2 ∩ A2)) ∩ ((A0 ∪ (A3 ∩ (A5 ∪ (A1 ∩ A3)))) ∪ (A1 ∩ (A0 ∪ A5)))) ∪ ((A3 ∪ (A4 ∩ A0)) ∩ ((A5 ∪ (A2 ∩ A0)) ∪ (A2 ∪ (A3 ∩ A2)))))) ⊆ (((((A1 ∪ (A1 ∩ (A0 ∪ (A5 ∩ A1)))) ∩ (A2 ∩ (A0 ∪ A0))) ∪ (A0 ∪ (A5 ∩ A3))) ∪ (((A3 ∪ (A0 ∩ A2)) ∩ (A2 ∩ (A2 ∪ A2))) ∪ (A3 ∩ (A1 ∪ (A2 ∩ (A2 ∪ A4)))))) ∩ ((((A5 ∪ (A2 ∩ A2)) ∩ (A0 ∪ (A3 ∩ (A5 ∪ (A1 ∩ A3))))) ∪ (A1 ∩ (A0 ∪ A5))) ∪ ((A5 ∪ (A2 ∩ A0)) ∪ ((A3 ∪ (A4 ∩ A0)) ∩ (A2 ∪ (A3 ∩ A2)))))) := by
  intro x hx
  simp only [Set.mem_union, Set.mem_inter] at *
  aesop

theorem control_goal_03 (A0 A1 A2 A3 A4 A5 : Set Nat) : (((A0 ∩ (A0 ∪ A1)) ∩ ((A3 ∪ (A0 ∩ A4)) ∪ (A5 ∪ (A1 ∩ A1)))) ∪ (((A0 ∪ (A4 ∩ A5)) ∩ ((A3 ∪ (A2 ∩ (A5 ∪ (A0 ∩ A4)))) ∪ (A1 ∪ (A1 ∩ A0)))) ∪ (A2 ∩ (A0 ∪ (A3 ∩ (A5 ∪ A5)))))) ⊆ ((((A0 ∩ (A0 ∪ A1)) ∩ (A3 ∪ (A0 ∩ A4))) ∪ (A5 ∪ (A1 ∩ A1))) ∪ (((A3 ∪ (A2 ∩ (A5 ∪ (A0 ∩ A4)))) ∪ ((A0 ∪ (A4 ∩ A5)) ∩ (A1 ∪ (A1 ∩ A0)))) ∪ (A2 ∩ (A0 ∪ (A3 ∩ (A5 ∪ A5)))))) := by
  intro x hx
  simp only [Set.mem_union, Set.mem_inter] at *
  aesop

theorem control_goal_04 (A0 A1 A2 A3 A4 A5 : Set Nat) : ((((A2 ∩ (A3 ∪ (A4 ∩ (A0 ∪ A5)))) ∩ ((A2 ∪ (A3 ∩ (A4 ∪ (A1 ∩ A1)))) ∪ (A4 ∪ (A3 ∩ (A5 ∪ (A5 ∩ A5)))))) ∪ ((A1 ∩ (A2 ∪ A4)) ∩ ((A5 ∪ (A2 ∩ (A3 ∪ (A1 ∩ A2)))) ∪ (A3 ∩ (A2 ∪ A1))))) ∩ ((A0 ∩ (A0 ∪ A1)) ∩ ((A3 ∪ (A0 ∩ A4)) ∪ (A5 ∪ (A1 ∩ A1))))) ⊆ (((((A2 ∩ (A3 ∪ (A4 ∩ (A0 ∪ A5)))) ∩ (A2 ∪ (A3 ∩ (A4 ∪ (A1 ∩ A1))))) ∪ (A4 ∪ (A3 ∩ (A5 ∪ (A5 ∩ A5))))) ∪ ((A5 ∪ (A2 ∩ (A3 ∪ (A1 ∩ A2)))) ∪ ((A1 ∩ (A2 ∪ A4)) ∩ (A3 ∩ (A2 ∪ A1))))) ∩ (((A0 ∩ (A0 ∪ A1)) ∩ (A3 ∪ (A0 ∩ A4))) ∪ (A5 ∪ (A1 ∩ A1)))) := by
  intro x hx
  simp only [Set.mem_union, Set.mem_inter] at *
  aesop

theorem control_goal_05 (A0 A1 A2 A3 A4 A5 : Set Nat) : ((((A4 ∩ (A1 ∪ (A2 ∩ (A1 ∪ A3)))) ∩ ((A1 ∩ (A0 ∪ A4)) ∪ (A0 ∪ (A0 ∩ (A1 ∪ (A3 ∩ A0)))))) ∪ (A1 ∩ (A0 ∪ A4))) ∪ ((A5 ∪ (A3 ∩ (A4 ∪ (A2 ∩ A1)))) ∩ ((A0 ∪ (A1 ∩ (A3 ∪ (A1 ∩ A3)))) ∪ (A3 ∩ (A0 ∪ (A2 ∩ (A5 ∪ A0))))))) ⊆ (((((A4 ∩ (A1 ∪ (A2 ∩ (A1 ∪ A3)))) ∩ (A1 ∩ (A0 ∪ A4))) ∪ (A0 ∪ (A0 ∩ (A1 ∪ (A3 ∩ A0))))) ∪ (A1 ∩ (A0 ∪ A4))) ∪ (((A5 ∪ (A3 ∩ (A4 ∪ (A2 ∩ A1)))) ∩ (A0 ∪ (A1 ∩ (A3 ∪ (A1 ∩ A3))))) ∪ (A3 ∩ (A0 ∪ (A2 ∩ (A5 ∪ A0)))))) := by
  intro x hx
  simp only [Set.mem_union, Set.mem_inter] at *
  aesop

theorem control_goal_06 (A0 A1 A2 A3 A4 A5 : Set Nat) : ((((A5 ∩ (A5 ∪ (A1 ∩ (A2 ∪ A0)))) ∩ ((A1 ∩ (A5 ∪ A1)) ∪ (A2 ∩ (A3 ∪ A3)))) ∪ ((A1 ∩ (A4 ∪ (A4 ∩ (A4 ∪ A1)))) ∩ ((A0 ∪ (A0 ∩ (A5 ∪ (A4 ∩ A4)))) ∪ (A1 ∩ (A2 ∪ A0))))) ∩ (((A2 ∩ (A3 ∪ (A4 ∩ (A0 ∪ A5)))) ∩ ((A2 ∪ (A3 ∩ (A4 ∪ (A1 ∩ A1)))) ∪ (A4 ∪ (A3 ∩ (A5 ∪ (A5 ∩ A5)))))) ∪ ((A1 ∩ (A2 ∪ A4)) ∩ ((A5 ∪ (A2 ∩ (A3 ∪ (A1 ∩ A2)))) ∪ (A3 ∩ (A2 ∪ A1)))))) ⊆ (((((A5 ∩ (A5 ∪ (A1 ∩ (A2 ∪ A0)))) ∩ (A1 ∩ (A5 ∪ A1))) ∪ (A2 ∩ (A3 ∪ A3))) ∪ (((A1 ∩ (A4 ∪ (A4 ∩ (A4 ∪ A1)))) ∩ (A0 ∪ (A0 ∩ (A5 ∪ (A4 ∩ A4))))) ∪ (A1 ∩ (A2 ∪ A0)))) ∩ ((((A2 ∩ (A3 ∪ (A4 ∩ (A0 ∪ A5)))) ∩ (A2 ∪ (A3 ∩ (A4 ∪ (A1 ∩ A1))))) ∪ (A4 ∪ (A3 ∩ (A5 ∪ (A5 ∩ A5))))) ∪ ((A5 ∪ (A2 ∩ (A3 ∪ (A1 ∩ A2)))) ∪ ((A1 ∩ (A2 ∪ A4)) ∩ (A3 ∩ (A2 ∪ A1)))))) := by
  intro x hx
  simp only [Set.mem_union, Set.mem_inter] at *
  aesop

theorem control_goal_07 (A0 A1 A2 A3 A4 A5 : Set Nat) : ((((A3 ∪ (A2 ∩ A1)) ∩ ((A0 ∩ (A3 ∪ (A1 ∩ (A3 ∪ A1)))) ∪ (A5 ∪ (A2 ∩ (A1 ∪ (A0 ∩ A4)))))) ∪ ((A1 ∩ (A2 ∪ A1)) ∩ ((A4 ∩ (A4 ∪ A1)) ∪ (A0 ∩ (A3 ∪ (A5 ∩ (A4 ∪ A1))))))) ∪ (((A3 ∩ (A4 ∪ A3)) ∩ ((A3 ∩ (A4 ∪ A4)) ∪ (A3 ∪ (A0 ∩ A5)))) ∩ (A4 ∩ (A5 ∪ A3)))) ⊆ (((((A3 ∪ (A2 ∩ A1)) ∩ (A0 ∩ (A3 ∪ (A1 ∩ (A3 ∪ A1))))) ∪ (A5 ∪ (A2 ∩ (A1 ∪ (A0 ∩ A4))))) ∪ (((A1 ∩ (A2 ∪ A1)) ∩ (A4 ∩ (A4 ∪ A1))) ∪ (A0 ∩ (A3 ∪ (A5 ∩ (A4 ∪ A1)))))) ∪ ((((A3 ∩ (A4 ∪ A3)) ∩ (A3 ∩ (A4 ∪ A4))) ∪ (A3 ∪ (A0 ∩ A5))) ∩ (A4 ∩ (A5 ∪ A3)))) := by
  intro x hx
  simp only [Set.mem_union, Set.mem_inter] at *
  aesop

theorem control_goal_08 (A0 A1 A2 A3 A4 A5 : Set Nat) : (((A0 ∩ (A4 ∪ (A3 ∩ (A1 ∪ A2)))) ∩ ((A5 ∩ (A1 ∪ A2)) ∪ (A5 ∩ (A5 ∪ A5)))) ∩ (((A3 ∪ (A2 ∩ A1)) ∩ ((A0 ∩ (A3 ∪ (A1 ∩ (A3 ∪ A1)))) ∪ (A5 ∪ (A2 ∩ (A1 ∪ (A0 ∩ A4)))))) ∪ ((A1 ∩ (A2 ∪ A1)) ∩ ((A4 ∩ (A4 ∪ A1)) ∪ (A0 ∩ (A3 ∪ (A5 ∩ (A4 ∪ A1)))))))) ⊆ (((A5 ∩ (A1 ∪ A2)) ∪ ((A0 ∩ (A4 ∪ (A3 ∩ (A1 ∪ A2)))) ∩ (A5 ∩ (A5 ∪ A5)))) ∩ ((((A3 ∪ (A2 ∩ A1)) ∩ (A0 ∩ (A3 ∪ (A1 ∩ (A3 ∪ A1))))) ∪ (A5 ∪ (A2 ∩ (A1 ∪ (A0 ∩ A4))))) ∪ (((A1 ∩ (A2 ∪ A1)) ∩ (A4 ∩ (A4 ∪ A1))) ∪ (A0 ∩ (A3 ∪ (A5 ∩ (A4 ∪ A1))))))) := by
  intro x hx
  simp only [Set.mem_union, Set.mem_inter] at *
  aesop

theorem control_goal_09 (A0 A1 A2 A3 A4 A5 : Set Nat) : (((A0 ∩ (A0 ∪ A1)) ∩ ((A3 ∪ (A0 ∩ A4)) ∪ (A5 ∪ (A1 ∩ A1)))) ∩ ((A1 ∩ (A5 ∪ (A4 ∩ (A0 ∪ A1)))) ∩ ((A5 ∪ (A4 ∩ (A5 ∪ (A0 ∩ A3)))) ∪ (A3 ∩ (A5 ∪ (A2 ∩ (A5 ∪ A0))))))) ⊆ ((((A0 ∩ (A0 ∪ A1)) ∩ (A3 ∪ (A0 ∩ A4))) ∪ (A5 ∪ (A1 ∩ A1))) ∩ (((A1 ∩ (A5 ∪ (A4 ∩ (A0 ∪ A1)))) ∩ (A5 ∪ (A4 ∩ (A5 ∪ (A0 ∩ A3))))) ∪ (A3 ∩ (A5 ∪ (A2 ∩ (A5 ∪ A0)))))) := by
  intro x hx
  simp only [Set.mem_union, Set.mem_inter] at *
  aesop

theorem control_goal_10 (A0 A1 A2 A3 A4 A5 : Set Nat) : ((((A5 ∪ (A2 ∩ A2)) ∩ ((A0 ∪ (A3 ∩ (A5 ∪ (A1 ∩ A3)))) ∪ (A1 ∩ (A0 ∪ A5)))) ∪ ((A3 ∪ (A4 ∩ A0)) ∩ ((A5 ∪ (A2 ∩ A0)) ∪ (A2 ∪ (A3 ∩ A2))))) ∪ (((A3 ∩ (A0 ∪ A1)) ∩ ((A0 ∩ (A0 ∪ (A3 ∩ (A3 ∪ A2)))) ∪ (A4 ∪ (A0 ∩ A2)))) ∩ ((A0 ∩ (A1 ∪ (A1 ∩ (A2 ∪ A4)))) ∩ ((A2 ∪ (A4 ∩ (A5 ∪ (A1 ∩ A1)))) ∪ (A4 ∩ (A2 ∪ (A5 ∩ (A0 ∪ A2)))))))) ⊆ (((((A5 ∪ (A2 ∩ A2)) ∩ (A0 ∪ (A3 ∩ (A5 ∪ (A1 ∩ A3))))) ∪ (A1 ∩ (A0 ∪ A5))) ∪ ((A5 ∪ (A2 ∩ A0)) ∪ ((A3 ∪ (A4 ∩ A0)) ∩ (A2 ∪ (A3 ∩ A2))))) ∪ ((((A3 ∩ (A0 ∪ A1)) ∩ (A0 ∩ (A0 ∪ (A3 ∩ (A3 ∪ A2))))) ∪ (A4 ∪ (A0 ∩ A2))) ∩ ((A2 ∪ (A4 ∩ (A5 ∪ (A1 ∩ A1)))) ∪ ((A0 ∩ (A1 ∪ (A1 ∩ (A2 ∪ A4)))) ∩ (A4 ∩ (A2 ∪ (A5 ∩ (A0 ∪ A2)))))))) := by
  intro x hx
  simp only [Set.mem_union, Set.mem_inter] at *
  aesop

theorem control_goal_11 (A0 A1 A2 A3 A4 A5 : Set Nat) : ((((A5 ∩ (A5 ∪ (A1 ∩ (A2 ∪ A0)))) ∩ ((A1 ∩ (A5 ∪ A1)) ∪ (A2 ∩ (A3 ∪ A3)))) ∪ ((A1 ∩ (A4 ∪ (A4 ∩ (A4 ∪ A1)))) ∩ ((A0 ∪ (A0 ∩ (A5 ∪ (A4 ∩ A4)))) ∪ (A1 ∩ (A2 ∪ A0))))) ∪ (((A2 ∩ (A3 ∪ (A4 ∩ (A0 ∪ A5)))) ∩ ((A2 ∪ (A3 ∩ (A4 ∪ (A1 ∩ A1)))) ∪ (A4 ∪ (A3 ∩ (A5 ∪ (A5 ∩ A5)))))) ∪ ((A1 ∩ (A2 ∪ A4)) ∩ ((A5 ∪ (A2 ∩ (A3 ∪ (A1 ∩ A2)))) ∪ (A3 ∩ (A2 ∪ A1)))))) ⊆ (((((A5 ∩ (A5 ∪ (A1 ∩ (A2 ∪ A0)))) ∩ (A1 ∩ (A5 ∪ A1))) ∪ (A2 ∩ (A3 ∪ A3))) ∪ (((A1 ∩ (A4 ∪ (A4 ∩ (A4 ∪ A1)))) ∩ (A0 ∪ (A0 ∩ (A5 ∪ (A4 ∩ A4))))) ∪ (A1 ∩ (A2 ∪ A0)))) ∪ ((((A2 ∩ (A3 ∪ (A4 ∩ (A0 ∪ A5)))) ∩ (A2 ∪ (A3 ∩ (A4 ∪ (A1 ∩ A1))))) ∪ (A4 ∪ (A3 ∩ (A5 ∪ (A5 ∩ A5))))) ∪ ((A5 ∪ (A2 ∩ (A3 ∪ (A1 ∩ A2)))) ∪ ((A1 ∩ (A2 ∪ A4)) ∩ (A3 ∩ (A2 ∪ A1)))))) := by
  intro x hx
  simp only [Set.mem_union, Set.mem_inter] at *
  aesop

run_cmd do
  for n in #[`control_goal_00, `control_goal_01, `control_goal_02, `control_goal_03, `control_goal_04, `control_goal_05, `control_goal_06, `control_goal_07, `control_goal_08, `control_goal_09, `control_goal_10, `control_goal_11] do
    let env ← getEnv
    let some ci := env.find? n | throwError "missing declaration"
    let axs ← collectAxioms n
    let ty ← liftTermElabM <| Meta.ppExpr ci.type
    let some value := ci.value? (allowOpaque := true) | throwError "declaration has no checked proof body"
    let deps := value.getUsedConstants.toList.map Name.toString
    logInfo m!"PROOFRIPPLE_AUDIT {Json.compress <| Json.mkObj [("name", toJson n.toString), ("type", toJson ty.pretty), ("axioms", toJson (axs.toList.map Name.toString)), ("constants", toJson deps)]}"
