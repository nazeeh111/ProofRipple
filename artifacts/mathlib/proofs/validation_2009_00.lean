import Mathlib.Order.Lattice
import Mathlib.Data.Set.Lattice
import Lean
open Lean Elab Command

theorem pr_distributivity (A B C : Set Nat) : A ∩ (B ∪ C) ⊆ (A ∩ B) ∪ (A ∩ C) :=
  (inf_sup_left A B C).le

run_cmd do
  for n in #[`inf_sup_left, `sup_le, `le_inf, `sup_le_sup, `inf_le_inf, `le_trans, `inf_le_left, `inf_le_right, `le_sup_left, `le_sup_right, `pr_distributivity] do
    let env ← getEnv
    let some ci := env.find? n | throwError "missing declaration"
    let axs ← collectAxioms n
    let ty ← liftTermElabM <| Meta.ppExpr ci.type
    let some value := ci.value? (allowOpaque := true) | throwError "declaration has no checked proof body"
    let deps := value.getUsedConstants.toList.map Name.toString
    logInfo m!"PROOFRIPPLE_AUDIT {Json.compress <| Json.mkObj [("name", toJson n.toString), ("type", toJson ty.pretty), ("axioms", toJson (axs.toList.map Name.toString)), ("constants", toJson deps)]}"
