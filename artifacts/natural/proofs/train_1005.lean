import Lean
open Lean Elab Command

def stage_p24 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  xs

def stage_p2 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p24 xs f p k).take k

def stage_p30 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p2 xs f p k).map f

def stage_p0 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p30 xs f p k).filter p

def stage_p13 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p0 xs f p k).map f

def stage_p12 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p13 xs f p k).take k

def stage_p16 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p12 xs f p k).map f

def stage_p5 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p16 xs f p k).take k

def stage_p28 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p5 xs f p k).reverse

def stage_p17 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p28 xs f p k).take k

def stage_p23 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p17 xs f p k).map f

def stage_p14 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p23 xs f p k).take k

def stage_p37 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p14 xs f p k).map f

def stage_p4 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p37 xs f p k).take k

def stage_p33 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p4 xs f p k).reverse

def stage_p32 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p33 xs f p k).take k

def stage_p8 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p32 xs f p k).map f

def stage_p3 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p8 xs f p k).filter p

def stage_p15 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p3 xs f p k).map f

def stage_p10 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p15 xs f p k).take k

def stage_p35 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p10 xs f p k).reverse

def stage_p9 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p35 xs f p k).take k

def stage_p38 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p9 xs f p k).map f

def stage_p18 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p38 xs f p k).filter p

def stage_p27 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p18 xs f p k).map f

def stage_p21 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p27 xs f p k).filter p

def stage_p1 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p21 xs f p k).map f

def stage_p29 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p1 xs f p k).take k

def stage_p6 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p29 xs f p k).reverse

def stage_p40 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p6 xs f p k).take k

def stage_p39 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p40 xs f p k).reverse

def stage_p20 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p39 xs f p k).take k

def stage_p7 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p20 xs f p k).map f

def stage_p31 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p7 xs f p k).take k

def stage_p11 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p31 xs f p k).map f

def stage_p22 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p11 xs f p k).filter p

def stage_p19 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p22 xs f p k).reverse

def stage_p36 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p19 xs f p k).take k

def stage_p26 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p36 xs f p k).reverse

def stage_p34 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p26 xs f p k).filter p

def stage_p25 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k : Nat) : List Nat :=
  (stage_p34 xs f p k).reverse

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
    (stage_p24 xs f p k).length ≤ cap → (stage_p2 xs f p k).length ≤ cap :=
  fun hx => (prx_step_take (stage_p24 xs f p k) k cap hx)

theorem pr_h1 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p2 xs f p k).length ≤ cap → (stage_p30 xs f p k).length ≤ cap :=
  fun hx => (prx_step_map (stage_p2 xs f p k) f cap hx)

theorem pr_h2 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p2 xs f p k).length ≤ cap → (stage_p12 xs f p k).length ≤ cap :=
  fun hx => (prx_step_take (stage_p13 xs f p k) k cap (prx_step_map (stage_p0 xs f p k) f cap (prx_step_filter (stage_p30 xs f p k) p cap (prx_step_map (stage_p2 xs f p k) f cap hx))))

theorem pr_h3 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p30 xs f p k).length ≤ cap → (stage_p0 xs f p k).length ≤ cap :=
  fun hx => (prx_step_filter (stage_p30 xs f p k) p cap hx)

theorem pr_h4 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p0 xs f p k).length ≤ cap → (stage_p13 xs f p k).length ≤ cap :=
  fun hx => (prx_step_map (stage_p0 xs f p k) f cap hx)

theorem pr_h5 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p0 xs f p k).length ≤ cap → (stage_p23 xs f p k).length ≤ cap :=
  fun hx => (prx_step_map (stage_p17 xs f p k) f cap (prx_step_take (stage_p28 xs f p k) k cap (prx_step_reverse (stage_p5 xs f p k) cap (prx_step_take (stage_p16 xs f p k) k cap (prx_step_map (stage_p12 xs f p k) f cap (prx_step_take (stage_p13 xs f p k) k cap (prx_step_map (stage_p0 xs f p k) f cap hx)))))))

theorem pr_h6 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p13 xs f p k).length ≤ cap → (stage_p12 xs f p k).length ≤ cap :=
  fun hx => (prx_step_take (stage_p13 xs f p k) k cap hx)

theorem pr_h7 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p13 xs f p k).length ≤ cap → (stage_p28 xs f p k).length ≤ cap :=
  fun hx => (prx_step_reverse (stage_p5 xs f p k) cap (prx_step_take (stage_p16 xs f p k) k cap (prx_step_map (stage_p12 xs f p k) f cap (prx_step_take (stage_p13 xs f p k) k cap hx))))

theorem pr_h8 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p12 xs f p k).length ≤ cap → (stage_p16 xs f p k).length ≤ cap :=
  fun hx => (prx_step_map (stage_p12 xs f p k) f cap hx)

theorem pr_h9 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p16 xs f p k).length ≤ cap → (stage_p5 xs f p k).length ≤ cap :=
  fun hx => (prx_step_take (stage_p16 xs f p k) k cap hx)

theorem pr_h10 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p16 xs f p k).length ≤ cap → (stage_p33 xs f p k).length ≤ cap :=
  fun hx => (prx_step_reverse (stage_p4 xs f p k) cap (prx_step_take (stage_p37 xs f p k) k cap (prx_step_map (stage_p14 xs f p k) f cap (prx_step_take (stage_p23 xs f p k) k cap (prx_step_map (stage_p17 xs f p k) f cap (prx_step_take (stage_p28 xs f p k) k cap (prx_step_reverse (stage_p5 xs f p k) cap (prx_step_take (stage_p16 xs f p k) k cap hx))))))))

theorem pr_h11 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p5 xs f p k).length ≤ cap → (stage_p28 xs f p k).length ≤ cap :=
  fun hx => (prx_step_reverse (stage_p5 xs f p k) cap hx)

theorem pr_h12 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p5 xs f p k).length ≤ cap → (stage_p23 xs f p k).length ≤ cap :=
  fun hx => (prx_step_map (stage_p17 xs f p k) f cap (prx_step_take (stage_p28 xs f p k) k cap (prx_step_reverse (stage_p5 xs f p k) cap hx)))

theorem pr_h13 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p28 xs f p k).length ≤ cap → (stage_p17 xs f p k).length ≤ cap :=
  fun hx => (prx_step_take (stage_p28 xs f p k) k cap hx)

theorem pr_h14 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p17 xs f p k).length ≤ cap → (stage_p23 xs f p k).length ≤ cap :=
  fun hx => (prx_step_map (stage_p17 xs f p k) f cap hx)

theorem pr_h15 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p17 xs f p k).length ≤ cap → (stage_p33 xs f p k).length ≤ cap :=
  fun hx => (prx_step_reverse (stage_p4 xs f p k) cap (prx_step_take (stage_p37 xs f p k) k cap (prx_step_map (stage_p14 xs f p k) f cap (prx_step_take (stage_p23 xs f p k) k cap (prx_step_map (stage_p17 xs f p k) f cap hx)))))

theorem pr_h16 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p23 xs f p k).length ≤ cap → (stage_p14 xs f p k).length ≤ cap :=
  fun hx => (prx_step_take (stage_p23 xs f p k) k cap hx)

theorem pr_h17 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p14 xs f p k).length ≤ cap → (stage_p37 xs f p k).length ≤ cap :=
  fun hx => (prx_step_map (stage_p14 xs f p k) f cap hx)

theorem pr_h18 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p14 xs f p k).length ≤ cap → (stage_p33 xs f p k).length ≤ cap :=
  fun hx => (prx_step_reverse (stage_p4 xs f p k) cap (prx_step_take (stage_p37 xs f p k) k cap (prx_step_map (stage_p14 xs f p k) f cap hx)))

theorem pr_h19 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p14 xs f p k).length ≤ cap → (stage_p8 xs f p k).length ≤ cap :=
  fun hx => (prx_step_map (stage_p32 xs f p k) f cap (prx_step_take (stage_p33 xs f p k) k cap (prx_step_reverse (stage_p4 xs f p k) cap (prx_step_take (stage_p37 xs f p k) k cap (prx_step_map (stage_p14 xs f p k) f cap hx)))))

theorem pr_h20 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p37 xs f p k).length ≤ cap → (stage_p4 xs f p k).length ≤ cap :=
  fun hx => (prx_step_take (stage_p37 xs f p k) k cap hx)

theorem pr_h21 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p4 xs f p k).length ≤ cap → (stage_p33 xs f p k).length ≤ cap :=
  fun hx => (prx_step_reverse (stage_p4 xs f p k) cap hx)

theorem pr_h22 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p4 xs f p k).length ≤ cap → (stage_p15 xs f p k).length ≤ cap :=
  fun hx => (prx_step_map (stage_p3 xs f p k) f cap (prx_step_filter (stage_p8 xs f p k) p cap (prx_step_map (stage_p32 xs f p k) f cap (prx_step_take (stage_p33 xs f p k) k cap (prx_step_reverse (stage_p4 xs f p k) cap hx)))))

theorem pr_h23 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p33 xs f p k).length ≤ cap → (stage_p32 xs f p k).length ≤ cap :=
  fun hx => (prx_step_take (stage_p33 xs f p k) k cap hx)

theorem pr_h24 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p32 xs f p k).length ≤ cap → (stage_p8 xs f p k).length ≤ cap :=
  fun hx => (prx_step_map (stage_p32 xs f p k) f cap hx)

theorem pr_h25 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p8 xs f p k).length ≤ cap → (stage_p3 xs f p k).length ≤ cap :=
  fun hx => (prx_step_filter (stage_p8 xs f p k) p cap hx)

theorem pr_h26 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p3 xs f p k).length ≤ cap → (stage_p15 xs f p k).length ≤ cap :=
  fun hx => (prx_step_map (stage_p3 xs f p k) f cap hx)

theorem pr_h27 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p3 xs f p k).length ≤ cap → (stage_p35 xs f p k).length ≤ cap :=
  fun hx => (prx_step_reverse (stage_p10 xs f p k) cap (prx_step_take (stage_p15 xs f p k) k cap (prx_step_map (stage_p3 xs f p k) f cap hx)))

theorem pr_h28 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p3 xs f p k).length ≤ cap → (stage_p21 xs f p k).length ≤ cap :=
  fun hx => (prx_step_filter (stage_p27 xs f p k) p cap (prx_step_map (stage_p18 xs f p k) f cap (prx_step_filter (stage_p38 xs f p k) p cap (prx_step_map (stage_p9 xs f p k) f cap (prx_step_take (stage_p35 xs f p k) k cap (prx_step_reverse (stage_p10 xs f p k) cap (prx_step_take (stage_p15 xs f p k) k cap (prx_step_map (stage_p3 xs f p k) f cap hx))))))))

theorem pr_h29 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p15 xs f p k).length ≤ cap → (stage_p10 xs f p k).length ≤ cap :=
  fun hx => (prx_step_take (stage_p15 xs f p k) k cap hx)

theorem pr_h30 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p10 xs f p k).length ≤ cap → (stage_p35 xs f p k).length ≤ cap :=
  fun hx => (prx_step_reverse (stage_p10 xs f p k) cap hx)

theorem pr_h31 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p10 xs f p k).length ≤ cap → (stage_p18 xs f p k).length ≤ cap :=
  fun hx => (prx_step_filter (stage_p38 xs f p k) p cap (prx_step_map (stage_p9 xs f p k) f cap (prx_step_take (stage_p35 xs f p k) k cap (prx_step_reverse (stage_p10 xs f p k) cap hx))))

theorem pr_h32 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p10 xs f p k).length ≤ cap → (stage_p27 xs f p k).length ≤ cap :=
  fun hx => (prx_step_map (stage_p18 xs f p k) f cap (prx_step_filter (stage_p38 xs f p k) p cap (prx_step_map (stage_p9 xs f p k) f cap (prx_step_take (stage_p35 xs f p k) k cap (prx_step_reverse (stage_p10 xs f p k) cap hx)))))

theorem pr_h33 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p10 xs f p k).length ≤ cap → (stage_p1 xs f p k).length ≤ cap :=
  fun hx => (prx_step_map (stage_p21 xs f p k) f cap (prx_step_filter (stage_p27 xs f p k) p cap (prx_step_map (stage_p18 xs f p k) f cap (prx_step_filter (stage_p38 xs f p k) p cap (prx_step_map (stage_p9 xs f p k) f cap (prx_step_take (stage_p35 xs f p k) k cap (prx_step_reverse (stage_p10 xs f p k) cap hx)))))))

theorem pr_h34 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p35 xs f p k).length ≤ cap → (stage_p9 xs f p k).length ≤ cap :=
  fun hx => (prx_step_take (stage_p35 xs f p k) k cap hx)

theorem pr_h35 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p35 xs f p k).length ≤ cap → (stage_p1 xs f p k).length ≤ cap :=
  fun hx => (prx_step_map (stage_p21 xs f p k) f cap (prx_step_filter (stage_p27 xs f p k) p cap (prx_step_map (stage_p18 xs f p k) f cap (prx_step_filter (stage_p38 xs f p k) p cap (prx_step_map (stage_p9 xs f p k) f cap (prx_step_take (stage_p35 xs f p k) k cap hx))))))

theorem pr_h36 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p9 xs f p k).length ≤ cap → (stage_p38 xs f p k).length ≤ cap :=
  fun hx => (prx_step_map (stage_p9 xs f p k) f cap hx)

theorem pr_h37 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p38 xs f p k).length ≤ cap → (stage_p18 xs f p k).length ≤ cap :=
  fun hx => (prx_step_filter (stage_p38 xs f p k) p cap hx)

theorem pr_h38 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p38 xs f p k).length ≤ cap → (stage_p6 xs f p k).length ≤ cap :=
  fun hx => (prx_step_reverse (stage_p29 xs f p k) cap (prx_step_take (stage_p1 xs f p k) k cap (prx_step_map (stage_p21 xs f p k) f cap (prx_step_filter (stage_p27 xs f p k) p cap (prx_step_map (stage_p18 xs f p k) f cap (prx_step_filter (stage_p38 xs f p k) p cap hx))))))

theorem pr_h39 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p18 xs f p k).length ≤ cap → (stage_p27 xs f p k).length ≤ cap :=
  fun hx => (prx_step_map (stage_p18 xs f p k) f cap hx)

theorem pr_h40 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p18 xs f p k).length ≤ cap → (stage_p39 xs f p k).length ≤ cap :=
  fun hx => (prx_step_reverse (stage_p40 xs f p k) cap (prx_step_take (stage_p6 xs f p k) k cap (prx_step_reverse (stage_p29 xs f p k) cap (prx_step_take (stage_p1 xs f p k) k cap (prx_step_map (stage_p21 xs f p k) f cap (prx_step_filter (stage_p27 xs f p k) p cap (prx_step_map (stage_p18 xs f p k) f cap hx)))))))

theorem pr_h41 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p27 xs f p k).length ≤ cap → (stage_p21 xs f p k).length ≤ cap :=
  fun hx => (prx_step_filter (stage_p27 xs f p k) p cap hx)

theorem pr_h42 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p21 xs f p k).length ≤ cap → (stage_p1 xs f p k).length ≤ cap :=
  fun hx => (prx_step_map (stage_p21 xs f p k) f cap hx)

theorem pr_h43 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p21 xs f p k).length ≤ cap → (stage_p31 xs f p k).length ≤ cap :=
  fun hx => (prx_step_take (stage_p7 xs f p k) k cap (prx_step_map (stage_p20 xs f p k) f cap (prx_step_take (stage_p39 xs f p k) k cap (prx_step_reverse (stage_p40 xs f p k) cap (prx_step_take (stage_p6 xs f p k) k cap (prx_step_reverse (stage_p29 xs f p k) cap (prx_step_take (stage_p1 xs f p k) k cap (prx_step_map (stage_p21 xs f p k) f cap hx))))))))

theorem pr_h44 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p1 xs f p k).length ≤ cap → (stage_p29 xs f p k).length ≤ cap :=
  fun hx => (prx_step_take (stage_p1 xs f p k) k cap hx)

theorem pr_h45 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p29 xs f p k).length ≤ cap → (stage_p6 xs f p k).length ≤ cap :=
  fun hx => (prx_step_reverse (stage_p29 xs f p k) cap hx)

theorem pr_h46 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p6 xs f p k).length ≤ cap → (stage_p40 xs f p k).length ≤ cap :=
  fun hx => (prx_step_take (stage_p6 xs f p k) k cap hx)

theorem pr_h47 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p6 xs f p k).length ≤ cap → (stage_p39 xs f p k).length ≤ cap :=
  fun hx => (prx_step_reverse (stage_p40 xs f p k) cap (prx_step_take (stage_p6 xs f p k) k cap hx))

theorem pr_h48 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p40 xs f p k).length ≤ cap → (stage_p39 xs f p k).length ≤ cap :=
  fun hx => (prx_step_reverse (stage_p40 xs f p k) cap hx)

theorem pr_h49 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p39 xs f p k).length ≤ cap → (stage_p20 xs f p k).length ≤ cap :=
  fun hx => (prx_step_take (stage_p39 xs f p k) k cap hx)

theorem pr_h50 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p20 xs f p k).length ≤ cap → (stage_p7 xs f p k).length ≤ cap :=
  fun hx => (prx_step_map (stage_p20 xs f p k) f cap hx)

theorem pr_h51 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p7 xs f p k).length ≤ cap → (stage_p31 xs f p k).length ≤ cap :=
  fun hx => (prx_step_take (stage_p7 xs f p k) k cap hx)

theorem pr_h52 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p31 xs f p k).length ≤ cap → (stage_p11 xs f p k).length ≤ cap :=
  fun hx => (prx_step_map (stage_p31 xs f p k) f cap hx)

theorem pr_h53 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p11 xs f p k).length ≤ cap → (stage_p22 xs f p k).length ≤ cap :=
  fun hx => (prx_step_filter (stage_p11 xs f p k) p cap hx)

theorem pr_h54 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p22 xs f p k).length ≤ cap → (stage_p19 xs f p k).length ≤ cap :=
  fun hx => (prx_step_reverse (stage_p22 xs f p k) cap hx)

theorem pr_h55 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p22 xs f p k).length ≤ cap → (stage_p34 xs f p k).length ≤ cap :=
  fun hx => (prx_step_filter (stage_p26 xs f p k) p cap (prx_step_reverse (stage_p36 xs f p k) cap (prx_step_take (stage_p19 xs f p k) k cap (prx_step_reverse (stage_p22 xs f p k) cap hx))))

theorem pr_h56 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p22 xs f p k).length ≤ cap → (stage_p25 xs f p k).length ≤ cap :=
  fun hx => (prx_step_reverse (stage_p34 xs f p k) cap (prx_step_filter (stage_p26 xs f p k) p cap (prx_step_reverse (stage_p36 xs f p k) cap (prx_step_take (stage_p19 xs f p k) k cap (prx_step_reverse (stage_p22 xs f p k) cap hx)))))

theorem pr_h57 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p19 xs f p k).length ≤ cap → (stage_p36 xs f p k).length ≤ cap :=
  fun hx => (prx_step_take (stage_p19 xs f p k) k cap hx)

theorem pr_h58 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p36 xs f p k).length ≤ cap → (stage_p26 xs f p k).length ≤ cap :=
  fun hx => (prx_step_reverse (stage_p36 xs f p k) cap hx)

theorem pr_h59 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p26 xs f p k).length ≤ cap → (stage_p34 xs f p k).length ≤ cap :=
  fun hx => (prx_step_filter (stage_p26 xs f p k) p cap hx)

theorem pr_h60 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p34 xs f p k).length ≤ cap → (stage_p25 xs f p k).length ≤ cap :=
  fun hx => (prx_step_reverse (stage_p34 xs f p k) cap hx)

theorem pr_breakthrough (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p18 xs f p k).length ≤ cap → (stage_p21 xs f p k).length ≤ cap :=
  fun hx => (pr_h41 xs f p k cap (pr_h39 xs f p k cap hx))

theorem pr_ripple_p18_p22 (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p18 xs f p k).length ≤ cap → (stage_p22 xs f p k).length ≤ cap :=
  fun hx => (pr_h53 xs f p k cap (pr_h52 xs f p k cap (pr_h43 xs f p k cap (pr_breakthrough xs f p k cap hx))))

theorem pr_goal_0_baseline (xs : List Nat) (f : Nat → Nat) (p : Nat → Bool) (k cap : Nat) :
    (stage_p32 xs f p k).length ≤ cap → (stage_p29 xs f p k).length ≤ cap :=
  fun hx => (pr_h44 xs f p k cap (pr_h42 xs f p k cap (pr_h28 xs f p k cap (pr_h25 xs f p k cap (pr_h24 xs f p k cap hx)))))

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

run_cmd do
  for n in #[`List.length_filter_le, `List.length_map, `List.length_reverse, `List.length_take_le', `List.length_append, `Nat.le_trans, `Nat.add_le_add, `stage_p24, `stage_p2, `stage_p30, `stage_p0, `stage_p13, `stage_p12, `stage_p16, `stage_p5, `stage_p28, `stage_p17, `stage_p23, `stage_p14, `stage_p37, `stage_p4, `stage_p33, `stage_p32, `stage_p8, `stage_p3, `stage_p15, `stage_p10, `stage_p35, `stage_p9, `stage_p38, `stage_p18, `stage_p27, `stage_p21, `stage_p1, `stage_p29, `stage_p6, `stage_p40, `stage_p39, `stage_p20, `stage_p7, `stage_p31, `stage_p11, `stage_p22, `stage_p19, `stage_p36, `stage_p26, `stage_p34, `stage_p25, `prx_step_filter, `prx_step_map, `prx_step_reverse, `prx_step_take, `pr_h0, `pr_h1, `pr_h2, `pr_h3, `pr_h4, `pr_h5, `pr_h6, `pr_h7, `pr_h8, `pr_h9, `pr_h10, `pr_h11, `pr_h12, `pr_h13, `pr_h14, `pr_h15, `pr_h16, `pr_h17, `pr_h18, `pr_h19, `pr_h20, `pr_h21, `pr_h22, `pr_h23, `pr_h24, `pr_h25, `pr_h26, `pr_h27, `pr_h28, `pr_h29, `pr_h30, `pr_h31, `pr_h32, `pr_h33, `pr_h34, `pr_h35, `pr_h36, `pr_h37, `pr_h38, `pr_h39, `pr_h40, `pr_h41, `pr_h42, `pr_h43, `pr_h44, `pr_h45, `pr_h46, `pr_h47, `pr_h48, `pr_h49, `pr_h50, `pr_h51, `pr_h52, `pr_h53, `pr_h54, `pr_h55, `pr_h56, `pr_h57, `pr_h58, `pr_h59, `pr_h60, `pr_breakthrough, `pr_ripple_p18_p22, `pr_goal_0_baseline, `prx_filtered_budget, `prx_paired_budget, `prx_combined_buffer_safe] do
    let env ← getEnv
    let some ci := env.find? n | throwError "missing declaration"
    let axs ← collectAxioms n
    let ty ← liftTermElabM <| Meta.ppExpr ci.type
    let some value := ci.value? (allowOpaque := true) | throwError "declaration has no checked proof body"
    let deps := value.getUsedConstants.toList.map Name.toString
    logInfo m!"PROOFRIPPLE_AUDIT {Json.compress <| Json.mkObj [("name", toJson n.toString), ("type", toJson ty.pretty), ("axioms", toJson (axs.toList.map Name.toString)), ("constants", toJson deps)]}"
