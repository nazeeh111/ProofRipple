import Lean
open Lean Elab Command

theorem norm_all_filter (xs : List Nat) (p : Nat → Bool) : ∀ a ∈ xs.filter p, p a := by
  intro a ha
  exact (List.mem_filter.mp ha).2

theorem norm_all_reverse (xs : List Nat) (p : Nat → Bool) (h : ∀ a ∈ xs, p a) : ∀ a ∈ xs.reverse, p a := by
  intro a ha
  exact h a (List.mem_reverse.mp ha)

theorem norm_all_take (xs : List Nat) (p : Nat → Bool) (k : Nat) (h : ∀ a ∈ xs, p a) : ∀ a ∈ xs.take k, p a := by
  intro a ha
  exact h a (List.mem_of_mem_take ha)

theorem norm_filter_identity (xs : List Nat) (p : Nat → Bool) (h : ∀ a ∈ xs, p a) : xs.filter p = xs :=
  by
    induction xs with
    | nil => rfl
    | cons a xs ih =>
      have ha : p a = true := h a List.mem_cons_self
      have ht : ∀ b ∈ xs, p b := by
        intro b hb
        exact h b (List.mem_cons_of_mem a hb)
      simp only [List.filter_cons, ha, Bool.true_eq, ↓reduceIte]
      exact congrArg (List.cons a) (ih ht)

theorem norm_within_filter (xs : List Nat) (p : Nat → Bool) (k : Nat) (h : xs.length ≤ k) : (xs.filter p).length ≤ k :=
  Nat.le_trans (List.length_filter_le p xs) h

theorem norm_within_map (xs : List Nat) (f : Nat → Nat) (k : Nat) (h : xs.length ≤ k) : (xs.map f).length ≤ k := by
  simpa only [List.length_map] using h

theorem norm_within_reverse (xs : List Nat) (k : Nat) (h : xs.length ≤ k) : xs.reverse.length ≤ k := by
  simpa only [List.length_reverse] using h

theorem norm_within_take (xs : List Nat) (k : Nat) : (xs.take k).length ≤ k :=
  List.length_take_le k xs

theorem norm_take_identity (xs : List Nat) (k : Nat) (h : xs.length ≤ k) : xs.take k = xs :=
  List.take_of_length_le h

theorem norm_reverse_reverse (xs : List Nat) : xs.reverse.reverse = xs :=
  List.reverse_reverse xs

theorem norm_filter_reverse (xs : List Nat) (p : Nat → Bool) : xs.reverse.filter p = (xs.filter p).reverse :=
  List.filter_reverse

theorem norm_map_reverse (xs : List Nat) (f : Nat → Nat) : xs.reverse.map f = (xs.map f).reverse :=
  List.map_reverse

theorem norm_map_take (xs : List Nat) (f : Nat → Nat) (k : Nat) : (xs.take k).map f = (xs.map f).take k :=
  List.map_take
run_cmd do
  for n in #[`norm_all_filter, `norm_all_reverse, `norm_all_take, `norm_filter_identity, `norm_within_filter, `norm_within_map, `norm_within_reverse, `norm_within_take, `norm_take_identity, `norm_reverse_reverse, `norm_filter_reverse, `norm_map_reverse, `norm_map_take] do
    let env ← getEnv
    let some ci := env.find? n | throwError "missing declaration"
    let axs ← collectAxioms n
    let ty ← liftTermElabM <| Meta.ppExpr ci.type
    let some value := ci.value? (allowOpaque := true) | throwError "declaration has no checked proof body"
    let deps := value.getUsedConstants.toList.map Name.toString
    logInfo m!"PROOFRIPPLE_AUDIT {Json.compress <| Json.mkObj [("name", toJson n.toString), ("type", toJson ty.pretty), ("axioms", toJson (axs.toList.map Name.toString)), ("constants", toJson deps)]}"
