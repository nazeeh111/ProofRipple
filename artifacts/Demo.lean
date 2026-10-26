import Lean
open Lean Elab Command

theorem pr_breakthrough (p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 : Prop) (h_h0 : p_p0 → p_p1) (h_h1 : p_p1 → p_p2) (h_h2 : p_p2 → p_p3) (h_h3 : p_p3 → p_p4) (h_h4 : p_p4 → p_p5) (h_h5 : p_p5 → p_p6) (h_h6 : p_p6 → p_p7) (h_h7 : p_p7 → p_p8) (h_h8 : p_p8 → p_p9) (h_h9 : p_p9 → p_p10) (h_h10 : p_p10 → p_p11) : p_p4 → p_p6 :=
  fun hx => (h_h5 (h_h4 hx))

theorem pr_ripple_p3_p6 (p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 : Prop) (h_h0 : p_p0 → p_p1) (h_h1 : p_p1 → p_p2) (h_h2 : p_p2 → p_p3) (h_h3 : p_p3 → p_p4) (h_h4 : p_p4 → p_p5) (h_h5 : p_p5 → p_p6) (h_h6 : p_p6 → p_p7) (h_h7 : p_p7 → p_p8) (h_h8 : p_p8 → p_p9) (h_h9 : p_p9 → p_p10) (h_h10 : p_p10 → p_p11) : p_p3 → p_p6 :=
  fun hx => ((pr_breakthrough p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 h_h0 h_h1 h_h2 h_h3 h_h4 h_h5 h_h6 h_h7 h_h8 h_h9 h_h10) (h_h3 hx))

theorem pr_ripple_p4_p7 (p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 : Prop) (h_h0 : p_p0 → p_p1) (h_h1 : p_p1 → p_p2) (h_h2 : p_p2 → p_p3) (h_h3 : p_p3 → p_p4) (h_h4 : p_p4 → p_p5) (h_h5 : p_p5 → p_p6) (h_h6 : p_p6 → p_p7) (h_h7 : p_p7 → p_p8) (h_h8 : p_p8 → p_p9) (h_h9 : p_p9 → p_p10) (h_h10 : p_p10 → p_p11) : p_p4 → p_p7 :=
  fun hx => (h_h6 ((pr_breakthrough p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 h_h0 h_h1 h_h2 h_h3 h_h4 h_h5 h_h6 h_h7 h_h8 h_h9 h_h10) hx))

theorem pr_ripple_p2_p6 (p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 : Prop) (h_h0 : p_p0 → p_p1) (h_h1 : p_p1 → p_p2) (h_h2 : p_p2 → p_p3) (h_h3 : p_p3 → p_p4) (h_h4 : p_p4 → p_p5) (h_h5 : p_p5 → p_p6) (h_h6 : p_p6 → p_p7) (h_h7 : p_p7 → p_p8) (h_h8 : p_p8 → p_p9) (h_h9 : p_p9 → p_p10) (h_h10 : p_p10 → p_p11) : p_p2 → p_p6 :=
  fun hx => ((pr_breakthrough p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 h_h0 h_h1 h_h2 h_h3 h_h4 h_h5 h_h6 h_h7 h_h8 h_h9 h_h10) (h_h3 (h_h2 hx)))

theorem pr_ripple_p3_p7 (p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 : Prop) (h_h0 : p_p0 → p_p1) (h_h1 : p_p1 → p_p2) (h_h2 : p_p2 → p_p3) (h_h3 : p_p3 → p_p4) (h_h4 : p_p4 → p_p5) (h_h5 : p_p5 → p_p6) (h_h6 : p_p6 → p_p7) (h_h7 : p_p7 → p_p8) (h_h8 : p_p8 → p_p9) (h_h9 : p_p9 → p_p10) (h_h10 : p_p10 → p_p11) : p_p3 → p_p7 :=
  fun hx => (h_h6 ((pr_breakthrough p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 h_h0 h_h1 h_h2 h_h3 h_h4 h_h5 h_h6 h_h7 h_h8 h_h9 h_h10) (h_h3 hx)))

theorem pr_ripple_p4_p8 (p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 : Prop) (h_h0 : p_p0 → p_p1) (h_h1 : p_p1 → p_p2) (h_h2 : p_p2 → p_p3) (h_h3 : p_p3 → p_p4) (h_h4 : p_p4 → p_p5) (h_h5 : p_p5 → p_p6) (h_h6 : p_p6 → p_p7) (h_h7 : p_p7 → p_p8) (h_h8 : p_p8 → p_p9) (h_h9 : p_p9 → p_p10) (h_h10 : p_p10 → p_p11) : p_p4 → p_p8 :=
  fun hx => (h_h7 (h_h6 ((pr_breakthrough p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 h_h0 h_h1 h_h2 h_h3 h_h4 h_h5 h_h6 h_h7 h_h8 h_h9 h_h10) hx)))

theorem pr_ripple_p1_p6 (p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 : Prop) (h_h0 : p_p0 → p_p1) (h_h1 : p_p1 → p_p2) (h_h2 : p_p2 → p_p3) (h_h3 : p_p3 → p_p4) (h_h4 : p_p4 → p_p5) (h_h5 : p_p5 → p_p6) (h_h6 : p_p6 → p_p7) (h_h7 : p_p7 → p_p8) (h_h8 : p_p8 → p_p9) (h_h9 : p_p9 → p_p10) (h_h10 : p_p10 → p_p11) : p_p1 → p_p6 :=
  fun hx => ((pr_breakthrough p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 h_h0 h_h1 h_h2 h_h3 h_h4 h_h5 h_h6 h_h7 h_h8 h_h9 h_h10) (h_h3 (h_h2 (h_h1 hx))))

theorem pr_ripple_p2_p7 (p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 : Prop) (h_h0 : p_p0 → p_p1) (h_h1 : p_p1 → p_p2) (h_h2 : p_p2 → p_p3) (h_h3 : p_p3 → p_p4) (h_h4 : p_p4 → p_p5) (h_h5 : p_p5 → p_p6) (h_h6 : p_p6 → p_p7) (h_h7 : p_p7 → p_p8) (h_h8 : p_p8 → p_p9) (h_h9 : p_p9 → p_p10) (h_h10 : p_p10 → p_p11) : p_p2 → p_p7 :=
  fun hx => (h_h6 ((pr_breakthrough p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 h_h0 h_h1 h_h2 h_h3 h_h4 h_h5 h_h6 h_h7 h_h8 h_h9 h_h10) (h_h3 (h_h2 hx))))

theorem pr_ripple_p3_p8 (p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 : Prop) (h_h0 : p_p0 → p_p1) (h_h1 : p_p1 → p_p2) (h_h2 : p_p2 → p_p3) (h_h3 : p_p3 → p_p4) (h_h4 : p_p4 → p_p5) (h_h5 : p_p5 → p_p6) (h_h6 : p_p6 → p_p7) (h_h7 : p_p7 → p_p8) (h_h8 : p_p8 → p_p9) (h_h9 : p_p9 → p_p10) (h_h10 : p_p10 → p_p11) : p_p3 → p_p8 :=
  fun hx => (h_h7 (h_h6 ((pr_breakthrough p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 h_h0 h_h1 h_h2 h_h3 h_h4 h_h5 h_h6 h_h7 h_h8 h_h9 h_h10) (h_h3 hx))))

theorem pr_ripple_p4_p9 (p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 : Prop) (h_h0 : p_p0 → p_p1) (h_h1 : p_p1 → p_p2) (h_h2 : p_p2 → p_p3) (h_h3 : p_p3 → p_p4) (h_h4 : p_p4 → p_p5) (h_h5 : p_p5 → p_p6) (h_h6 : p_p6 → p_p7) (h_h7 : p_p7 → p_p8) (h_h8 : p_p8 → p_p9) (h_h9 : p_p9 → p_p10) (h_h10 : p_p10 → p_p11) : p_p4 → p_p9 :=
  fun hx => (h_h8 (h_h7 (h_h6 ((pr_breakthrough p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 h_h0 h_h1 h_h2 h_h3 h_h4 h_h5 h_h6 h_h7 h_h8 h_h9 h_h10) hx))))

theorem pr_ripple_p0_p6 (p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 : Prop) (h_h0 : p_p0 → p_p1) (h_h1 : p_p1 → p_p2) (h_h2 : p_p2 → p_p3) (h_h3 : p_p3 → p_p4) (h_h4 : p_p4 → p_p5) (h_h5 : p_p5 → p_p6) (h_h6 : p_p6 → p_p7) (h_h7 : p_p7 → p_p8) (h_h8 : p_p8 → p_p9) (h_h9 : p_p9 → p_p10) (h_h10 : p_p10 → p_p11) : p_p0 → p_p6 :=
  fun hx => ((pr_breakthrough p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 h_h0 h_h1 h_h2 h_h3 h_h4 h_h5 h_h6 h_h7 h_h8 h_h9 h_h10) (h_h3 (h_h2 (h_h1 (h_h0 hx)))))

theorem pr_ripple_p1_p7 (p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 : Prop) (h_h0 : p_p0 → p_p1) (h_h1 : p_p1 → p_p2) (h_h2 : p_p2 → p_p3) (h_h3 : p_p3 → p_p4) (h_h4 : p_p4 → p_p5) (h_h5 : p_p5 → p_p6) (h_h6 : p_p6 → p_p7) (h_h7 : p_p7 → p_p8) (h_h8 : p_p8 → p_p9) (h_h9 : p_p9 → p_p10) (h_h10 : p_p10 → p_p11) : p_p1 → p_p7 :=
  fun hx => (h_h6 ((pr_breakthrough p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 h_h0 h_h1 h_h2 h_h3 h_h4 h_h5 h_h6 h_h7 h_h8 h_h9 h_h10) (h_h3 (h_h2 (h_h1 hx)))))

theorem pr_ripple_p2_p8 (p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 : Prop) (h_h0 : p_p0 → p_p1) (h_h1 : p_p1 → p_p2) (h_h2 : p_p2 → p_p3) (h_h3 : p_p3 → p_p4) (h_h4 : p_p4 → p_p5) (h_h5 : p_p5 → p_p6) (h_h6 : p_p6 → p_p7) (h_h7 : p_p7 → p_p8) (h_h8 : p_p8 → p_p9) (h_h9 : p_p9 → p_p10) (h_h10 : p_p10 → p_p11) : p_p2 → p_p8 :=
  fun hx => (h_h7 (h_h6 ((pr_breakthrough p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 h_h0 h_h1 h_h2 h_h3 h_h4 h_h5 h_h6 h_h7 h_h8 h_h9 h_h10) (h_h3 (h_h2 hx)))))

theorem pr_ripple_p3_p9 (p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 : Prop) (h_h0 : p_p0 → p_p1) (h_h1 : p_p1 → p_p2) (h_h2 : p_p2 → p_p3) (h_h3 : p_p3 → p_p4) (h_h4 : p_p4 → p_p5) (h_h5 : p_p5 → p_p6) (h_h6 : p_p6 → p_p7) (h_h7 : p_p7 → p_p8) (h_h8 : p_p8 → p_p9) (h_h9 : p_p9 → p_p10) (h_h10 : p_p10 → p_p11) : p_p3 → p_p9 :=
  fun hx => (h_h8 (h_h7 (h_h6 ((pr_breakthrough p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 h_h0 h_h1 h_h2 h_h3 h_h4 h_h5 h_h6 h_h7 h_h8 h_h9 h_h10) (h_h3 hx)))))

theorem pr_ripple_p4_p10 (p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 : Prop) (h_h0 : p_p0 → p_p1) (h_h1 : p_p1 → p_p2) (h_h2 : p_p2 → p_p3) (h_h3 : p_p3 → p_p4) (h_h4 : p_p4 → p_p5) (h_h5 : p_p5 → p_p6) (h_h6 : p_p6 → p_p7) (h_h7 : p_p7 → p_p8) (h_h8 : p_p8 → p_p9) (h_h9 : p_p9 → p_p10) (h_h10 : p_p10 → p_p11) : p_p4 → p_p10 :=
  fun hx => (h_h9 (h_h8 (h_h7 (h_h6 ((pr_breakthrough p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 h_h0 h_h1 h_h2 h_h3 h_h4 h_h5 h_h6 h_h7 h_h8 h_h9 h_h10) hx)))))

theorem pr_ripple_p0_p7 (p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 : Prop) (h_h0 : p_p0 → p_p1) (h_h1 : p_p1 → p_p2) (h_h2 : p_p2 → p_p3) (h_h3 : p_p3 → p_p4) (h_h4 : p_p4 → p_p5) (h_h5 : p_p5 → p_p6) (h_h6 : p_p6 → p_p7) (h_h7 : p_p7 → p_p8) (h_h8 : p_p8 → p_p9) (h_h9 : p_p9 → p_p10) (h_h10 : p_p10 → p_p11) : p_p0 → p_p7 :=
  fun hx => (h_h6 ((pr_breakthrough p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 h_h0 h_h1 h_h2 h_h3 h_h4 h_h5 h_h6 h_h7 h_h8 h_h9 h_h10) (h_h3 (h_h2 (h_h1 (h_h0 hx))))))

theorem pr_ripple_p1_p8 (p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 : Prop) (h_h0 : p_p0 → p_p1) (h_h1 : p_p1 → p_p2) (h_h2 : p_p2 → p_p3) (h_h3 : p_p3 → p_p4) (h_h4 : p_p4 → p_p5) (h_h5 : p_p5 → p_p6) (h_h6 : p_p6 → p_p7) (h_h7 : p_p7 → p_p8) (h_h8 : p_p8 → p_p9) (h_h9 : p_p9 → p_p10) (h_h10 : p_p10 → p_p11) : p_p1 → p_p8 :=
  fun hx => (h_h7 (h_h6 ((pr_breakthrough p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 h_h0 h_h1 h_h2 h_h3 h_h4 h_h5 h_h6 h_h7 h_h8 h_h9 h_h10) (h_h3 (h_h2 (h_h1 hx))))))

theorem pr_ripple_p2_p9 (p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 : Prop) (h_h0 : p_p0 → p_p1) (h_h1 : p_p1 → p_p2) (h_h2 : p_p2 → p_p3) (h_h3 : p_p3 → p_p4) (h_h4 : p_p4 → p_p5) (h_h5 : p_p5 → p_p6) (h_h6 : p_p6 → p_p7) (h_h7 : p_p7 → p_p8) (h_h8 : p_p8 → p_p9) (h_h9 : p_p9 → p_p10) (h_h10 : p_p10 → p_p11) : p_p2 → p_p9 :=
  fun hx => (h_h8 (h_h7 (h_h6 ((pr_breakthrough p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 h_h0 h_h1 h_h2 h_h3 h_h4 h_h5 h_h6 h_h7 h_h8 h_h9 h_h10) (h_h3 (h_h2 hx))))))

theorem pr_ripple_p3_p10 (p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 : Prop) (h_h0 : p_p0 → p_p1) (h_h1 : p_p1 → p_p2) (h_h2 : p_p2 → p_p3) (h_h3 : p_p3 → p_p4) (h_h4 : p_p4 → p_p5) (h_h5 : p_p5 → p_p6) (h_h6 : p_p6 → p_p7) (h_h7 : p_p7 → p_p8) (h_h8 : p_p8 → p_p9) (h_h9 : p_p9 → p_p10) (h_h10 : p_p10 → p_p11) : p_p3 → p_p10 :=
  fun hx => (h_h9 (h_h8 (h_h7 (h_h6 ((pr_breakthrough p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 h_h0 h_h1 h_h2 h_h3 h_h4 h_h5 h_h6 h_h7 h_h8 h_h9 h_h10) (h_h3 hx))))))

theorem pr_ripple_p4_p11 (p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 : Prop) (h_h0 : p_p0 → p_p1) (h_h1 : p_p1 → p_p2) (h_h2 : p_p2 → p_p3) (h_h3 : p_p3 → p_p4) (h_h4 : p_p4 → p_p5) (h_h5 : p_p5 → p_p6) (h_h6 : p_p6 → p_p7) (h_h7 : p_p7 → p_p8) (h_h8 : p_p8 → p_p9) (h_h9 : p_p9 → p_p10) (h_h10 : p_p10 → p_p11) : p_p4 → p_p11 :=
  fun hx => (h_h10 (h_h9 (h_h8 (h_h7 (h_h6 ((pr_breakthrough p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 h_h0 h_h1 h_h2 h_h3 h_h4 h_h5 h_h6 h_h7 h_h8 h_h9 h_h10) hx))))))

theorem pr_goal_0_augmented (p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 : Prop) (h_h0 : p_p0 → p_p1) (h_h1 : p_p1 → p_p2) (h_h2 : p_p2 → p_p3) (h_h3 : p_p3 → p_p4) (h_h4 : p_p4 → p_p5) (h_h5 : p_p5 → p_p6) (h_h6 : p_p6 → p_p7) (h_h7 : p_p7 → p_p8) (h_h8 : p_p8 → p_p9) (h_h9 : p_p9 → p_p10) (h_h10 : p_p10 → p_p11) : p_p0 → p_p11 :=
  fun hx => (h_h10 ((pr_ripple_p3_p10 p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 h_h0 h_h1 h_h2 h_h3 h_h4 h_h5 h_h6 h_h7 h_h8 h_h9 h_h10) (h_h2 (h_h1 (h_h0 hx)))))

theorem pr_goal_1_augmented (p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 : Prop) (h_h0 : p_p0 → p_p1) (h_h1 : p_p1 → p_p2) (h_h2 : p_p2 → p_p3) (h_h3 : p_p3 → p_p4) (h_h4 : p_p4 → p_p5) (h_h5 : p_p5 → p_p6) (h_h6 : p_p6 → p_p7) (h_h7 : p_p7 → p_p8) (h_h8 : p_p8 → p_p9) (h_h9 : p_p9 → p_p10) (h_h10 : p_p10 → p_p11) : p_p1 → p_p11 :=
  fun hx => (h_h10 ((pr_ripple_p3_p10 p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 h_h0 h_h1 h_h2 h_h3 h_h4 h_h5 h_h6 h_h7 h_h8 h_h9 h_h10) (h_h2 (h_h1 hx))))

theorem pr_goal_2_augmented (p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 : Prop) (h_h0 : p_p0 → p_p1) (h_h1 : p_p1 → p_p2) (h_h2 : p_p2 → p_p3) (h_h3 : p_p3 → p_p4) (h_h4 : p_p4 → p_p5) (h_h5 : p_p5 → p_p6) (h_h6 : p_p6 → p_p7) (h_h7 : p_p7 → p_p8) (h_h8 : p_p8 → p_p9) (h_h9 : p_p9 → p_p10) (h_h10 : p_p10 → p_p11) : p_p2 → p_p11 :=
  fun hx => (h_h10 ((pr_ripple_p3_p10 p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 h_h0 h_h1 h_h2 h_h3 h_h4 h_h5 h_h6 h_h7 h_h8 h_h9 h_h10) (h_h2 hx)))

theorem pr_goal_3_baseline (p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 : Prop) (h_h0 : p_p0 → p_p1) (h_h1 : p_p1 → p_p2) (h_h2 : p_p2 → p_p3) (h_h3 : p_p3 → p_p4) (h_h4 : p_p4 → p_p5) (h_h5 : p_p5 → p_p6) (h_h6 : p_p6 → p_p7) (h_h7 : p_p7 → p_p8) (h_h8 : p_p8 → p_p9) (h_h9 : p_p9 → p_p10) (h_h10 : p_p10 → p_p11) : p_p3 → p_p11 :=
  fun hx => (h_h10 (h_h9 (h_h8 (h_h7 (h_h6 ((pr_breakthrough p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 h_h0 h_h1 h_h2 h_h3 h_h4 h_h5 h_h6 h_h7 h_h8 h_h9 h_h10) (h_h3 hx)))))))

theorem pr_goal_3_augmented (p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 : Prop) (h_h0 : p_p0 → p_p1) (h_h1 : p_p1 → p_p2) (h_h2 : p_p2 → p_p3) (h_h3 : p_p3 → p_p4) (h_h4 : p_p4 → p_p5) (h_h5 : p_p5 → p_p6) (h_h6 : p_p6 → p_p7) (h_h7 : p_p7 → p_p8) (h_h8 : p_p8 → p_p9) (h_h9 : p_p9 → p_p10) (h_h10 : p_p10 → p_p11) : p_p3 → p_p11 :=
  fun hx => (h_h10 ((pr_ripple_p3_p10 p_p0 p_p1 p_p2 p_p3 p_p4 p_p5 p_p6 p_p7 p_p8 p_p9 p_p10 p_p11 h_h0 h_h1 h_h2 h_h3 h_h4 h_h5 h_h6 h_h7 h_h8 h_h9 h_h10) hx))

run_cmd do
  for n in #[`pr_breakthrough, `pr_ripple_p3_p6, `pr_ripple_p4_p7, `pr_ripple_p2_p6, `pr_ripple_p3_p7, `pr_ripple_p4_p8, `pr_ripple_p1_p6, `pr_ripple_p2_p7, `pr_ripple_p3_p8, `pr_ripple_p4_p9, `pr_ripple_p0_p6, `pr_ripple_p1_p7, `pr_ripple_p2_p8, `pr_ripple_p3_p9, `pr_ripple_p4_p10, `pr_ripple_p0_p7, `pr_ripple_p1_p8, `pr_ripple_p2_p9, `pr_ripple_p3_p10, `pr_ripple_p4_p11, `pr_goal_0_augmented, `pr_goal_1_augmented, `pr_goal_2_augmented, `pr_goal_3_baseline, `pr_goal_3_augmented] do
    let env ← getEnv
    let some ci := env.find? n | throwError "missing declaration"
    let axs ← collectAxioms n
    let ty ← liftTermElabM <| Meta.ppExpr ci.type
    let some value := ci.value? (allowOpaque := true) | throwError "declaration has no checked proof body"
    let deps := value.getUsedConstants.toList.map Name.toString
    logInfo m!"PROOFRIPPLE_AUDIT {Json.compress <| Json.mkObj [("name", toJson n.toString), ("type", toJson ty.pretty), ("axioms", toJson (axs.toList.map Name.toString)), ("constants", toJson deps)]}"
