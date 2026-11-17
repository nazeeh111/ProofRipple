"""Render the retained implication witnesses, not a new experiment. Python stdlib only."""
from pathlib import Path
import json,html,hashlib
D=Path(__file__).resolve().parent
r=json.loads((D/'selected/run.json').read_text());n=json.loads((D/'negative/run.json').read_text());c=r['context']
assert r['selected']==['ripple_p4_p11']
a=next(x for x in r['candidates'] if x['id']==r['selected'][0]);assert a['path']==['breakthrough','h6','h7','h8','h9','h10']
assert all(not x['axioms'] for x in r['verification']['audits'])
BG='#101b18';FG='#e9f0e8';DIM='#a9bdb0';MINT='#a9e7c0';GOLD='#e5c989'
def render(phone):
 w,h=(400,960) if phone else (1120,800);o=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc"><title id="title">One checked consequence, four bounded searches</title><desc id="desc">Explicit implication assumptions form p0 through p11. Seed p4 to p6 composes h4 and h5. Selected p4 to p11 composes the seed and h6 through h10. At eight expansions, starting registry solves one of four, adding the selected consequence solves four. Longer chain control solves none.</desc><rect width="100%" height="100%" fill="{BG}"/>']
 def text(x,y,t,size=16,col=FG,weight=400):o.append(f'<text x="{x}" y="{y}" fill="{col}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" font-weight="{weight}">{html.escape(str(t))}</text>')
 def line(x,y,X,Y,col=DIM,width=1):o.append(f'<path d="M{x} {y} L{X} {Y}" fill="none" stroke="{col}" stroke-width="{width}"/>')
 text(28,38,'PROOFRIPPLE / CORE LEAN',13,MINT,700);text(28,79,'Prove once. Reuse under a budget.',19 if phone else 31,FG,700)
 text(28,111,'Known implication composition; explicit assumptions.',13 if phone else 17,DIM)
 if phone:
  text(28,156,'01  THE PREMISES',13,GOLD,700)
  for i in range(4,12):
   y=192+(i-4)*36;text(38,y,f'p{i}',18,FG,700)
   if i<11:line(51,y+6,51,y+22);text(74,y+21,f'h{i} : p{i} → p{i+1}',14,DIM)
  line(204,187,204,259,MINT,3);text(222,220,'Seed',14,MINT,700);text(222,242,'p4 → p6',16,MINT)
  line(190,187,190,440,GOLD,3);text(222,346,'Selected',14,GOLD,700);text(222,370,'p4 → p11',16,GOLD)
  text(28,490,'02  SAME 8-EXPANSION LIMIT',13,GOLD,700);y=528
 else:
  text(28,157,'01  EXPLICIT CONDITIONAL HYPOTHESES',13,GOLD,700)
  for i in range(12):
   x=43+i*92;text(x,211,f'p{i}',18,FG,700)
   if i<11:line(x+28,205,x+76,205);text(x+34,191,f'h{i}',12,DIM)
  x4=43+4*92;x6=43+6*92;x11=43+11*92
  o.append(f'<path d="M{x4+12} 226 V245 H{x6+12} V226" fill="none" stroke="{MINT}" stroke-width="3"/>');text(x4+28,268,'seed p4 → p6',15,MINT)
  o.append(f'<path d="M{x4+12} 286 V307 H{x11+12} V226" fill="none" stroke="{GOLD}" stroke-width="3"/>');text(x4+28,332,'selected p4 → p11 = seed, h6, h7, h8, h9, h10',16,GOLD)
  text(28,385,'02  SAME 8-EXPANSION LIMIT · GRAPH HEURISTIC · 1 SELECTED LEMMA',13,GOLD,700);y=423
 text(28,y,'Goal',14,DIM,700);text(130 if phone else 230,y,'Starting registry',13 if phone else 16,DIM,700);text(270 if phone else 620,y,'+ consequence',13 if phone else 16,MINT,700)
 for i,g in enumerate(r['goals']):
  Y=y+32*(i+1);text(28,Y,f'p{i} → p11',14)
  b=g['baseline'];u=g['augmented'];B=f"{b['expansions']} · "+('solved' if b['solved'] else 'not found');U=f"{u['expansions']} · solved"
  text(130 if phone else 230,Y,B,13 if phone else 16,DIM);text(270 if phone else 620,Y,U,13 if phone else 16,MINT)
 Y=y+168;line(28,Y-15,w-28,Y-15);text(28,Y,'1/4 → 4/4 goals solved in this saved case',15,MINT,700)
 text(28,Y+36,'03  LONGER CHAIN CONTROL',13,GOLD,700)
 text(28,Y+65,'p0…p3 → p17: 0/4 → 0/4 at the same budget.',13 if phone else 16)
 text(28,Y+94,'Not found ≠ false. This is not a new theorem',13 if phone else 15,DIM)
 text(28,Y+115,'or evidence of superiority over Lean automation.',13 if phone else 15,DIM)
 text(28,h-26,'Lean 4.33.1 · empty transitive axiom lists · saved raw runs',11 if phone else 13,DIM)
 o.append('</svg>');return ''.join(o)
for phone in [False,True]:(D/('consequence-phone.svg' if phone else 'consequence.svg')).write_text(render(phone))
manifest={'source':'selected/run.json','control':'negative/run.json','selected':a['id'],'selected_path':a['path'],'rows':r['goals'],'scale':'discrete proposition order; vertical layout is not a measured distance','files':{n:hashlib.sha256((D/n).read_bytes()).hexdigest() for n in ['consequence.svg','consequence-phone.svg']}}
(D/'figure-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
