'use strict';

// All displayed experiment values come from a loaded run. No simulated results.
const $ = (id) => document.getElementById(id);
const SVG = 'http://www.w3.org/2000/svg';
let run = null;
let context = null;
let currentCandidate = null;
let activeNode = null;
let pending = false;
let selectionBudget = 3;
let rankingMethod = 'graph';
let activeExample = 'natural';
let benchmarkRequest = 0;
let loadedBenchmark = null;
let loadedBenchmarkKey = null;
let loadedSupplementalControl = null;
const EXAMPLES = {
  mathlib: {run:'../artifacts/mathlib/demo.json', benchmark:'../artifacts/mathlib/benchmark.json', control:'../artifacts/mathlib/control-repair/summary.json'},
  natural: {run:'../artifacts/natural/demo.json', benchmark:'../artifacts/natural/benchmark.json'},
  implications: {run:'../artifacts/demo.json', benchmark:'../artifacts/benchmark.json'},
};

function node(tag, className, text) {
  const item = document.createElement(tag);
  if (className) item.className = className;
  if (text !== undefined) item.textContent = String(text);
  return item;
}
function svg(tag, attrs, text) {
  const item = document.createElementNS(SVG, tag);
  Object.entries(attrs || {}).forEach(([key, value]) => item.setAttribute(key, String(value)));
  if (text !== undefined) item.textContent = String(text);
  return item;
}
const number = (value, fallback = '—') => Number.isFinite(Number(value)) && value !== null && value !== undefined ? Number(value) : fallback;
const formatted = (value) => typeof number(value) === 'number' ? Number(value).toFixed(3) : '—';
const nodeName = (id) => String(id ?? '?');
const candidateList = () => Array.isArray(run?.candidates) ? run.candidates : [];
const selectedIds = () => new Set((run?.selected || []).map((item) => typeof item === 'object' ? item.id : item));
const labelFor = (id) => context?.nodes?.find((item) => item.id === id)?.label || id;
const isMathlib = (value=context) => value?.domain === 'mathlib-set-lattice';
function termText(term, depth=0) {
  if(!term || typeof term!=='object' || depth>32)return '?';
  if(term.op==='var')return 'A'+String(term.index).replace(/[0-9]/g,digit=>'₀₁₂₃₄₅₆₇₈₉'[Number(digit)]);
  if(!['join','meet'].includes(term.op))return '?';
  const child=(value)=>{
    const text=termText(value,depth+1);
    return value?.op==='join'&&term.op==='meet'?`(${text})`:text;
  };
  return `${child(term.left)} ${term.op==='join'?'∪':'∩'} ${child(term.right)}`;
}
const relationText = (item) => isMathlib()?`${termText(item.source)} ⊆ ${termText(item.target)}`:`${nodeName(item.source)} → ${nodeName(item.target)}`;
const domainMetadata = () => isMathlib()?run?.mathlib_domain || run?.metadata?.mathlib_domain || {}:run?.natural_domain || {};
const stateName = (status) => ({kernel_verified:'Kernel verified', proposed:'Proposed', failed:'Failed', unavailable:'Unavailable', timeout:'Timed out', rejected:'Rejected'})[status] || String(status || 'Proposed').replaceAll('_', ' ');

function notice(message, kind = '') {
  $('notice').textContent = message;
  $('notice').className = `notice ${kind}`.trim();
}
function setPending(value) {
  pending = value;
  $('run-button').disabled = value || !context;
  $('run-button').replaceChildren(document.createTextNode(value ? 'Running…' : 'Run exploration'), node('span', '', value ? '…' : '→'));
  $('import-button').disabled = value;
  $('budget').disabled = value;
  $('example-select').disabled = value;
  $('policy-select').disabled = value;
  $('selection-budget').disabled = value;
  $('import-declaration').disabled = value;
  $('workspace').setAttribute('aria-busy', String(value));
}
function validContext(value) {
  if(isMathlib(value))return Number.isInteger(value.variables)&&value.seed&&Array.isArray(value.candidates)&&Array.isArray(value.goals);
  return value && Array.isArray(value.nodes) && value.nodes.length > 0 && Array.isArray(value.edges) && value.seed && typeof value.seed === 'object';
}
function validateRun(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('The JSON must contain a run object or a supported implication context.');
  if (!validContext(value.context)) throw new Error('This run has no supported context. Expected nodes, edges and a seed theorem.');
  if (!Array.isArray(value.candidates)) throw new Error('This run has no candidates array.');
  if (!Array.isArray(value.goals)) throw new Error('This run has no downstream goals array.');
  const objects=(items)=>Array.isArray(items)&&items.every(item=>item&&typeof item==='object'&&!Array.isArray(item));
  if(!objects(value.candidates)||!objects(value.goals))throw new Error('Candidates and goals must contain objects.');
  if(value.selected!==undefined&&!Array.isArray(value.selected))throw new Error('Selected consequences must be an array.');
  if(value.selected?.some(item=>typeof item!=='string'&&(!item||typeof item!=='object'||typeof item.id!=='string')))throw new Error('Selected consequences must contain identifiers.');
  if(value.timeline!==undefined&&(!Array.isArray(value.timeline)||value.timeline.some(item=>!item||!['string','object'].includes(typeof item))))throw new Error('The run timeline is malformed.');
  if(isMathlib(value.context)&&!objects(value.context.candidates))throw new Error('The Mathlib context has a malformed candidate pool.');
  if(!isMathlib(value.context)){
    if(!objects(value.context.nodes)||!objects(value.context.edges))throw new Error('Graph nodes and edges must contain objects.');
    const ids=new Set(value.context.nodes.map(item=>item.id));
    if([...value.context.edges,value.context.seed,...value.candidates].some(item=>!ids.has(item.source)||!ids.has(item.target)))throw new Error('Graph relations must refer to existing nodes.');
  }
  for(const candidate of value.candidates)for(const field of ['axioms','dependencies','path'])if(candidate[field]!==undefined&&candidate[field]!==null&&!Array.isArray(candidate[field]))throw new Error(`Candidate ${field} must be an array.`);
  const metadata=isMathlib(value.context)?value.mathlib_domain||value.metadata?.mathlib_domain:value.natural_domain;
  if(metadata){
    if(metadata.registered_templates!==undefined&&!objects(metadata.registered_templates))throw new Error('Registered templates must contain objects.');
    for(const field of ['axioms','dependencies'])if(metadata.imported_seed?.[field]!==undefined&&!Array.isArray(metadata.imported_seed[field]))throw new Error(`Imported theorem ${field} must be an array.`);
  }
  if (value.candidates.length > 10000 || (value.context.nodes?.length || 0) > 500) throw new Error('This run is too large for the workbench. Use a context with at most 500 nodes and 10,000 candidates.');
  return value;
}
function loadRun(value, origin = 'recorded') {
  validateRun(value);
  run = value;
  context = value.context;
  activeExample = origin === 'imported' ? null : isMathlib()?'mathlib':context.domain === 'list-capacity' ? 'natural' : 'implications';
  if(isMathlib()){$('example-select').querySelector('[value="mathlib"]').hidden=false;$('example-select').querySelector('[value="mathlib"]').disabled=false;}
  $('example-select').value = activeExample || 'imported';
  activeNode = null;
  const selected = selectedIds();
  currentCandidate = candidateList().find((item) => item.id === [...selected][0]) || candidateList()[0] || null;
  $('context-title').textContent = context.title || context.id || 'Imported context';
  $('seed-label').textContent = isMathlib()?context.seed.declaration || context.seed.id:relationText(context.seed);
  $('seed-label').title = context.seed.id || 'Seed theorem';
  $('candidate-count').textContent = candidateList().length;
  $('verified-count').textContent = candidateList().filter((item) => item.status === 'kernel_verified').length;
  $('selected-count').textContent = `${selected.size} selected`;
  $('toolchain-label').textContent = run.verification?.toolchain || 'No toolchain evidence';
  $('toolchain-label').title = run.verification?.toolchain || '';
  const budgetValue = typeof run.budget === 'object' ? run.budget.search_expansions_per_goal ?? run.budget.search_expansions ?? run.budget.expansions ?? run.budget.search : run.budget;
  if (Number.isFinite(Number(budgetValue))) $('budget').value = Number(budgetValue);
  const loadedSelectionBudget = Number(run.budget?.selected_lemmas);
  if (Number.isInteger(loadedSelectionBudget) && loadedSelectionBudget >= 0 && loadedSelectionBudget <= 16) selectionBudget = loadedSelectionBudget;
  $('selection-budget').value = selectionBudget;
  rankingMethod = run.metrics?.method || (context.domain === 'list-capacity' ? 'graph' : 'learned');
  const methodOptions=isMathlib()?[['greedy_coverage','Greedy coverage'],['branching_aware','AND-aware coverage'],['learned','Learned ensemble'],['learned_no_bonus','Learned · no bonus'],['learned_singleton','Singleton ablation'],['structure_only','Structure-only'],['graph','Static coverage'],['proof_cost','Proof cost'],['semantic','Symbolic cosine'],['random','Random']]:[['graph','Graph heuristic'],['learned','Learned ensemble']];
  $('policy-select').replaceChildren(...methodOptions.map(([value,label])=>{const option=node('option','',label);option.value=value;return option;}));
  if (!methodOptions.some(([value])=>value===rankingMethod)) {
    const option=node('option','',`Recorded: ${rankingMethod.replaceAll('_',' ')}`);option.value=rankingMethod;option.dataset.recordedPolicy='true';$('policy-select').append(option);
  }
  $('policy-select').value = rankingMethod;
  $('budget-caption').textContent = Number.isFinite(Number(budgetValue)) ? `${budgetValue} ${isMathlib()?'goal visits':'expansions'} per goal` : 'Equal search budgets';
  $('search-budget-label').textContent=isMathlib()?'Goal visits':'Search budget';
  $('budget').setAttribute('aria-label',isMathlib()?'Goal visit budget':'Search expansion budget');
  $('search-interpretation').textContent=isMathlib()?'Bounded AND/OR search counts goal visits, including required premise branches. Failure is not mathematical impossibility. Kernel checks and general Lean automation use different resources.':'Restricted graph-search assistance. Bounded failure is not mathematical impossibility or evidence of an advantage over Lean automation.';
  $('export-json').disabled = false;
  $('candidate-search').value = '';
  $('status-filter').value = 'all';
  $('graph-context').textContent = isMathlib()?'Inspecting the actual proof dependency tree':context.domain === 'list-capacity' ? `${context.nodes.length} typed list stages · ${context.edges.length} closed primitive capacity theorems` : `${context.nodes.length} propositions · ${context.edges.length} explicit implication assumptions`;
  $('graph-heading').textContent=isMathlib()?'Proof dependencies':'Implication paths';
  $('primitive-legend').textContent = isMathlib()?'Proof step · AND premises':context.domain === 'list-capacity' ? 'Closed capacity theorem' : 'Assumption';
  $('seed-legend').textContent=isMathlib()?'Seed instance':'Seed';
  $('selection-legend').textContent=isMathlib()?'Conclusion':'Selected / inspected';
  document.querySelector('.graph-hint').textContent=isMathlib()?'SELECT A PROOF STEP':'SELECT A NODE TO FILTER';
  document.querySelector('.graph-legend').classList.toggle('proof-legend',isMathlib());
  renderFormalBasis(); renderGraph(); renderCandidates(); renderInspector(); renderGoals(); renderTimeline();
  refreshBenchmark(activeExample);
  setPending(false);
  if (origin === 'imported') notice('Imported run · Verification is file-reported and has not been rechecked.');
  else if (origin === 'live') notice(`Local exploration complete. ${stateName(run.verification?.status || 'unavailable')}.`, run.verification?.status === 'failed' ? 'error' : '');
  else notice(run.verification?.status==='kernel_verified'?'Recorded experiment · Saved Lean audit. Run locally to refresh verification.':`Recorded experiment · ${stateName(run.verification?.status || 'unavailable')}. No successful saved audit reported.`);
}

function renderFormalBasis() {
  const natural = context.domain === 'list-capacity';
  const mathlib=isMathlib();
  const metadata=domainMetadata();
  const basis = metadata.imported_seed;
  const badge = $('basis-status');
  badge.textContent = stateName(run.verification?.status || 'unavailable');
  badge.className = `status-badge ${run.verification?.status === 'kernel_verified' ? 'verified' : run.verification?.status === 'failed' ? 'failed' : 'proposed'}`;
  $('basis-domain').textContent = mathlib?'MATHLIB · SET LATTICE':natural ? 'CONCRETE LIST NAT DOMAIN' : 'PROPOSITIONAL IMPLICATION DOMAIN';
  const allowed = metadata.allowed_axioms;
  $('active-policy').textContent=mathlib?`axiom policy: ${Array.isArray(allowed)?allowed.length+' allowed':'not reported'}`:natural?'axiom policy: propext':'axiom policy: none';
  $('active-policy').title=Array.isArray(allowed)?allowed.join(', '):'';
  $('basis-name').textContent = mathlib?basis?.name || context.seed.declaration || 'Imported Mathlib declaration':natural ? basis?.name || 'List.length_filter_le · audit unavailable' : 'Explicitly quantified implication context';
  $('basis-description').textContent = mathlib?'Concrete set inclusions derived from the registered lattice rules. Binary proof steps require both displayed premises; the graph is built from the actual proof AST.':natural ? 'This library theorem bounds filtered length. The graph seed composes closed capacity theorems and is a separate declaration.' : 'Primitive edges are explicit implication hypotheses. Consequences hold under those quantified hypotheses.';
  $('basis-type-details').hidden = !(natural||mathlib);
  $('basis-type').textContent = basis?.statement || 'The exact imported statement has not been audited in this recorded run.';
  $('basis-policy').textContent = natural||mathlib ? `Allowed dependency axioms: ${Array.isArray(allowed)?allowed.join(', ') || 'none':'not reported'}. Other axiom dependencies must be rejected by the verifier.` : 'Empty-axiom policy. The verifier rejects declarations with any transitive axiom dependency.';
  $('basis-axioms').textContent = natural||mathlib ? Array.isArray(basis?.axioms) ? basis.axioms.length ? basis.axioms.join(', ') : 'None reported' : 'No audit reported' : 'No imported theorem';
  const revision=metadata.library_revision || metadata.mathlib_revision;
  $('basis-revision').textContent=revision?`Library revision: ${typeof revision==='string'?revision:JSON.stringify(revision)}`:'';
  const dependencyList = $('basis-dependencies');dependencyList.replaceChildren();
  for (const dependency of basis?.dependencies || []) dependencyList.append(node('span','',dependency));
  if (!basis?.dependencies?.length) dependencyList.append(node('span','','No proof constants reported'));
  $('basis-dependency-details').hidden = !(natural||mathlib);
  const templates = metadata.registered_templates || [];
  const templateList = $('basis-templates');templateList.replaceChildren();
  for (const template of templates) {
    const item=node('div','registered-template');item.append(node('strong','',template.name || 'Registered template'),node('p','',template.explanation || 'Fixed registered rule, not a discovered inference mechanism.'));templateList.append(item);
  }
  $('basis-template-details').hidden = !templates.length;
  $('import-declaration').hidden = !(natural||mathlib);
  $('formal-basis').hidden = false;
}

function graphPositions() {
  const nodes = context.nodes;
  const ids = new Set(nodes.map((item) => item.id));
  const incoming = new Map(nodes.map((item) => [item.id, 0]));
  const outgoing = new Map(nodes.map((item) => [item.id, []]));
  for (const edge of context.edges) {
    if (!ids.has(edge.source) || !ids.has(edge.target)) continue;
    incoming.set(edge.target, incoming.get(edge.target) + 1);
    outgoing.get(edge.source).push(edge.target);
  }
  const depths = new Map(nodes.map((item) => [item.id, 0]));
  const queue = nodes.filter((item) => !incoming.get(item.id)).map((item) => item.id);
  const seen = new Set();
  while (queue.length) {
    const id = queue.shift(); seen.add(id);
    outgoing.get(id).forEach((target) => {
      depths.set(target, Math.max(depths.get(target), depths.get(id) + 1));
      incoming.set(target, incoming.get(target) - 1);
      if (!incoming.get(target)) queue.push(target);
    });
  }
  // Cyclic contexts retain a stable visible layout rather than an endless sort.
  nodes.filter((item) => !seen.has(item.id)).forEach((item, index) => depths.set(item.id, index % Math.max(2, Math.ceil(Math.sqrt(nodes.length)))));
  const maximum = Math.max(...depths.values(), 1);
  // Merge adjacent ranks on large graphs to keep labels readable.
  const columns = Math.min(maximum + 1, 8);
  const layers = Array.from({length:columns}, () => []);
  nodes.forEach((item) => layers[Math.min(columns - 1, Math.floor(depths.get(item.id) / (maximum + 1) * columns))].push(item));
  const height = Math.max(440, Math.max(...layers.map((layer) => layer.length)) * 85 + 100);
  const positions = new Map();
  layers.forEach((layer, column) => layer.forEach((item, row) => positions.set(item.id, {x:70 + column * (780 / Math.max(columns - 1, 1)), y:55 + (row + 1) * ((height - 110) / (layer.length + 1))})));
  return {positions, height};
}
function edgePath(from, to, offset = 0) {
  if (!from || !to) return '';
  const direction = to.x >= from.x ? 1 : -1;
  const x1 = from.x + direction * 26;
  const x2 = to.x - direction * 28;
  const distance = Math.max(32, Math.abs(x2 - x1) * .4);
  if (Math.abs(to.x - from.x) < 20) return `M ${x1} ${from.y} C ${x1 + 65} ${from.y}, ${x2 + 65} ${to.y}, ${x2} ${to.y}`;
  return `M ${x1} ${from.y} C ${x1 + direction * distance} ${from.y + offset}, ${x2 - direction * distance} ${to.y + offset}, ${x2} ${to.y}`;
}
function renderGraph() {
  const graph = $('graph'); graph.replaceChildren();
  if (!context) return;
  $('proof-step-detail').hidden=true;
  if(isMathlib()){renderMathlibProofGraph();return;}
  graph.classList.remove('proof-graph');graph.style.minWidth='';graph.parentElement.classList.remove('proof-tree-wrap');
  graph.setAttribute('aria-label','Implication graph. Select a node to inspect connected consequences.');
  const {positions, height} = graphPositions();
  graph.setAttribute('viewBox', `0 0 920 ${height}`);
  const defs = svg('defs');
  [['gray','var(--edge)'],['seed','var(--seed)'],['teal','var(--accent)']].forEach(([id,color]) => {
    const marker = svg('marker',{id:`arrow-${id}`,viewBox:'0 0 8 8',refX:7,refY:4,markerWidth:5,markerHeight:5,orient:'auto-start-reverse'});
    marker.append(svg('path',{d:'M 0 0 L 8 4 L 0 8 z',fill:color})); defs.append(marker);
  }); graph.append(defs);
  const selected = selectedIds();
  const activePath = new Set(currentCandidate?.path || []);
  const primitiveLayer = svg('g',{'aria-hidden':'true'});
  context.edges.forEach((edge) => {
    const path = svg('path',{d:edgePath(positions.get(edge.source),positions.get(edge.target)),class:`graph-edge ${activePath.has(edge.id) ? 'active-edge' : ''}`,'marker-end':'url(#arrow-gray)'});
    path.append(svg('title',{},`${edge.id}: ${edge.source} → ${edge.target}`)); primitiveLayer.append(path);
  }); graph.append(primitiveLayer);
  const consequenceLayer = svg('g',{'aria-hidden':'true'});
  candidateList().filter((item) => selected.has(item.id) || item.id === currentCandidate?.id).forEach((candidate) => {
    const path = svg('path',{d:edgePath(positions.get(candidate.source),positions.get(candidate.target),-45),class:`graph-edge candidate-edge ${candidate.id === currentCandidate?.id ? 'active-edge' : ''}`,'marker-end':'url(#arrow-teal)'});
    path.append(svg('title',{},`${candidate.id}: ${stateName(candidate.status)}`)); consequenceLayer.append(path);
  }); graph.append(consequenceLayer);
  const seed = context.seed;
  const seedPath = svg('path',{d:edgePath(positions.get(seed.source),positions.get(seed.target),35),class:`graph-edge seed-edge ${activePath.has(seed.id) ? 'active-edge' : ''}`,'marker-end':'url(#arrow-seed)','aria-hidden':'true'});
  seedPath.append(svg('title',{},`Seed: ${seed.id}`)); graph.append(seedPath);
  context.nodes.forEach((item, index) => {
    const point = positions.get(item.id);
    const connected = item.id === currentCandidate?.source || item.id === currentCandidate?.target;
    const group = svg('g',{class:`graph-node ${item.id === activeNode || connected ? 'selected' : ''} ${item.id === seed.source || item.id === seed.target ? 'seed-node' : ''}`,transform:`translate(${point.x} ${point.y})`,tabindex:0,role:'button','data-node-id':item.id,'aria-label':`${item.id}: ${item.label || item.id}. Show connected consequences.`,'aria-pressed':String(item.id === activeNode)});
    group.append(svg('title',{},`${item.id}: ${item.label || item.id}`));
    group.append(svg('rect',{x:-33,y:-33,width:66,height:66,rx:30,class:'node-hit'}));
    group.append(svg('rect',{x:-27,y:-21,width:54,height:42,rx:21}));
    group.append(svg('text',{'text-anchor':'middle',y:5},String(item.id).length > 6 ? String(item.id).slice(0,5)+'…' : item.id));
    const shortLabel = item.expression?.op || item.label || '';
    group.append(svg('text',{'text-anchor':'middle',y:39,class:'node-label'},String(shortLabel).length > 19 ? String(shortLabel).slice(0,17)+'…' : shortLabel));
    const select = (restoreFocus=false) => {
      activeNode = activeNode === item.id ? null : item.id; renderGraph(); renderCandidates();
      if(restoreFocus)Array.from(graph.querySelectorAll('.graph-node')).find(element=>element.getAttribute('data-node-id')===String(item.id))?.focus();
    };
    group.addEventListener('click',()=>select());
    group.addEventListener('keydown',(event) => {if (event.key === 'Enter' || event.key === ' ') {event.preventDefault();select(true);}});
    graph.append(group);
  });
}

function renderMathlibProofGraph() {
  const graph=$('graph');graph.classList.add('proof-graph');graph.parentElement.classList.add('proof-tree-wrap');
  const original=context.candidates.find(item=>item.id===currentCandidate?.id);
  const tree=currentCandidate?.proof_ast || original?.proof || (typeof currentCandidate?.proof==='object'?currentCandidate.proof:null);
  if(!tree || typeof tree!=='object'){
    graph.setAttribute('viewBox','0 0 920 360');graph.append(svg('text',{x:460,y:180,'text-anchor':'middle',class:'proof-placeholder'},'No proof AST was included for this consequence.'));
    $('graph-context').textContent='No dependency graph inferred from labels or proof source.';return;
  }
  const steps=[];let leaves=0,maxDepth=0;
  const visit=(proof,depth=0)=>{
    if(!proof || typeof proof!=='object' || depth>16 || steps.length>=120)throw new Error('Proof tree exceeds the interactive graph limit');
    const step={id:steps.length,proof,depth,children:[]};steps.push(step);maxDepth=Math.max(maxDepth,depth);
    step.children=(Array.isArray(proof.children)?proof.children:[]).map(child=>visit(child,depth+1));
    step.slot=step.children.length?step.children.reduce((sum,child)=>sum+child.slot,0)/step.children.length:leaves++;
    return step;
  };
  let root;
  try{root=visit(tree);}catch(error){graph.setAttribute('viewBox','0 0 920 360');graph.append(svg('text',{x:460,y:180,'text-anchor':'middle',class:'proof-placeholder'},error.message));return;}
  const width=Math.max(920,leaves*195+80),height=Math.max(390,maxDepth*125+140);
  graph.setAttribute('viewBox',`0 0 ${width} ${height}`);graph.style.minWidth=(width<=1050?750:Math.min(width,1700))+'px';
  graph.setAttribute('aria-label','Actual proof dependency tree. AND joints require all child premises. Select a proof step for its exact relation.');
  steps.forEach(step=>{step.x=leaves>1?95+step.slot*(width-190)/(leaves-1):width/2;step.y=height-70-step.depth*125;});
  const defs=svg('defs');const marker=svg('marker',{id:'proof-arrow',viewBox:'0 0 8 8',refX:7,refY:4,markerWidth:4,markerHeight:4,orient:'auto'});marker.append(svg('path',{d:'M0 0 L8 4 L0 8 Z',fill:'var(--edge)'}));defs.append(marker);graph.append(defs);
  for(const step of steps){
    if(!step.children.length)continue;
    const joint={x:step.x,y:step.y-49};
    for(const child of step.children){
      const start={x:child.x,y:child.y+29};const middle=(start.y+joint.y)/2;
      graph.append(svg('path',{d:`M${start.x} ${start.y} C${start.x} ${middle},${joint.x} ${middle},${joint.x} ${joint.y}`,class:'proof-dependency-edge','marker-end':'url(#proof-arrow)'}));
    }
    graph.append(svg('path',{d:`M${joint.x} ${joint.y} L${step.x} ${step.y-30}`,class:'proof-dependency-edge','marker-end':'url(#proof-arrow)'}));
    if(step.children.length>1){graph.append(svg('circle',{cx:joint.x,cy:joint.y,r:5,class:'proof-and-joint'}));graph.append(svg('text',{x:joint.x+10,y:joint.y+3,class:'proof-and-label'},'AND'));}
  }
  for(const step of steps){
    const relation=`${termText(step.proof.source)} ⊆ ${termText(step.proof.target)}`;
    const group=svg('g',{class:`proof-step ${step===root?'proof-conclusion':''} ${step.proof.rule==='seed'?'proof-seed':''}`,transform:`translate(${step.x} ${step.y})`,tabindex:0,role:'button','aria-label':`${step.proof.rule}: ${relation}. ${step.children.length} premises.`,'aria-pressed':'false'});
    group.append(svg('title',{},`${step.proof.rule}: ${relation}`));group.append(svg('rect',{x:-90,y:-30,width:180,height:60,rx:4}));
    const rule=step.proof.rule==='lemma'?`lemma · ${step.proof.lemma_id || ''}`:step.proof.rule;
    group.append(svg('text',{x:0,y:-10,'text-anchor':'middle',class:'proof-rule'},rule));
    const split=relation.indexOf(' ⊆ ');const left=relation.slice(0,split);const right=relation.slice(split+3);
    const concise=(text)=>text.length>25?text.slice(0,23)+'…':text;
    group.append(svg('text',{x:0,y:7,'text-anchor':'middle',class:'proof-relation'},concise(left)));
    const targetLine=svg('text',{x:0,y:22,'text-anchor':'middle',class:'proof-relation'});
    targetLine.append(svg('tspan',{class:'proof-inclusion'},'⊆ '),document.createTextNode(concise(right)));group.append(targetLine);
    const select=()=>{
      graph.querySelectorAll('.proof-step').forEach(element=>{element.classList.remove('proof-selected');element.setAttribute('aria-pressed','false');});group.classList.add('proof-selected');group.setAttribute('aria-pressed','true');
      $('proof-step-detail').textContent=`${rule}: ${relation}. ${step.children.length?`All ${step.children.length} displayed premises are required.`:'Leaf rule.'} This is a step in the displayed candidate proof, not a separately audited declaration.`;$('proof-step-detail').hidden=false;
    };
    group.addEventListener('click',select);group.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();select();}});graph.append(group);
  }
  const conjunctions=steps.filter(step=>step.children.length>1).length;
  $('graph-context').textContent=`${steps.length} proof steps · ${conjunctions} AND joints · all joined premises required`;
}
function chooseCandidate(candidate) {
  currentCandidate = candidate;
  renderGraph(); renderCandidates(); renderInspector();
}
function renderCandidates() {
  const rows = $('candidate-rows'); rows.replaceChildren();
  const query = $('candidate-search').value.trim().toLowerCase();
  const filter = $('status-filter').value;
  const selected = selectedIds();
  const candidates = candidateList().filter((item) => {
    const connected = isMathlib() || !activeNode || item.source === activeNode || item.target === activeNode;
    const matches = `${item.id} ${relationText(item)} ${isMathlib()?'':labelFor(item.source)+' '+labelFor(item.target)}`.toLowerCase().includes(query);
    return connected && matches && (filter === 'all' || (filter === 'selected' ? selected.has(item.id) : (item.status || 'proposed') === filter));
  }).sort((a,b) => Number(selected.has(b.id)) - Number(selected.has(a.id)) || (isMathlib() && selected.has(a.id) && selected.has(b.id) ? [...selected].indexOf(a.id)-[...selected].indexOf(b.id) : Number(b.score || 0) - Number(a.score || 0)) || String(a.id).localeCompare(String(b.id)));
  const scoreHeading=document.querySelector('.candidate-table th:nth-child(3)');
  scoreHeading.textContent=isMathlib()?'STAGE SCORE':'SCORE';
  scoreHeading.title=isMathlib()?'Actual score at this candidate’s recorded selection round. Scores from different portfolios are not directly comparable.':'Score under the recorded ranking policy.';
  $('candidate-empty').hidden = candidates.length > 0;
  candidates.forEach((candidate) => {
    const row = node('tr', candidate.id === currentCandidate?.id ? 'active' : '');
    const title = node('td');
    title.append(node('span','candidate-name',relationText(candidate)));
    const identifier = node('span','candidate-id',candidate.id);
    if (selected.has(candidate.id)) identifier.append(node('span','selected-mark','SELECTED'));
    title.append(identifier);
    const state = node('td'); state.append(node('span',`status-badge ${candidate.status === 'kernel_verified' ? 'verified' : candidate.status === 'failed' ? 'failed' : 'proposed'}`,stateName(candidate.status)));
    const score = node('td');score.append(node('span','candidate-score',formatted(candidate.score)));
    if(isMathlib()&&Number.isInteger(candidate.score_stage))score.append(node('span','candidate-score-stage',`round ${candidate.score_stage+1}`));
    const action = node('td'); const button = node('button','candidate-select','↗');button.setAttribute('aria-label',`Inspect consequence ${candidate.id}`);button.addEventListener('click',(event) => {event.stopPropagation();chooseCandidate(candidate);});action.append(button);
    row.append(title,state,score,action);row.addEventListener('click',() => chooseCandidate(candidate));rows.append(row);
  });
}
function proofText() {
  const proof = currentCandidate?.proof;
  if(typeof proof==='string')return proof;
  if(typeof currentCandidate?.lean_source==='string')return currentCandidate.lean_source;
  return typeof proof?.source==='string'?proof.source:typeof proof?.lean==='string'?proof.lean:'';
}
function renderInspector() {
  const item = currentCandidate;
  $('inspect-id').textContent = item?.id || 'NO CONSEQUENCE SELECTED';
  $('inspect-statement').textContent = item ? relationText(item) : isMathlib()?'No consequence selected':'P → Q';
  $('inspect-statement').classList.toggle('set-relation',isMathlib());
  const badge = $('inspect-status');badge.textContent = item ? stateName(item.status) : 'Awaiting selection';badge.className = `status-badge ${item?.status === 'kernel_verified' ? 'verified' : item?.status === 'failed' ? 'failed' : 'proposed'}`;
  const explanation = typeof item?.explanation === 'string' ? item.explanation : item?.explanation?.explanation || item?.explanation?.why_useful || item?.explanation?.summary;
  $('inspect-explanation').textContent = explanation || (item ? isMathlib()?'A set inclusion composed from the displayed proof rules. The exact Lean statement and audit are authoritative.':`An implication from “${labelFor(item.source)}” to “${labelFor(item.target)}” under this context's explicitly quantified assumptions.` : 'Select a consequence to inspect its exact proof and assumptions.');
  $('proof-code').textContent = proofText() || '-- No Lean proof artifact is available for this consequence.';
  $('copy-proof').disabled = !proofText();
  $('export-proof').disabled = !proofText() && !run?.lean_source && !run?.verification?.source;
  const axioms = Array.isArray(item?.axioms) ? item.axioms : null;
  $('audit-status').textContent = item ? stateName(item.status) : 'Unavailable';
  $('axiom-count').textContent = axioms ? axioms.length === 0 ? context.domain === 'list-capacity' ? '0 reported for this theorem' : '0 · empty axiom set' : axioms.length : 'No audit reported';
  $('axioms-list').textContent = axioms?.length ? axioms.join(', ') : '';
  $('exact-statement').textContent = item?.statement || 'No exact statement was reported. Inspect available proof source.';
  const dependencies = $('dependencies-list');dependencies.replaceChildren();
  const list = item?.dependencies || item?.path || [];
  if (list.length) list.forEach((dependency) => dependencies.append(node('span','',dependency && typeof dependency === 'object' ? dependency.id || dependency.name || JSON.stringify(dependency) : dependency ?? 'Unknown dependency')));
  else dependencies.append(node('span','','No dependencies reported'));
  $('rank-score').textContent = formatted(item?.score);
  const actualMethod=run.metrics?.method || rankingMethod;
  const learnedPolicy=['learned','learned_no_bonus','learned_singleton','structure_only'].includes(actualMethod);
  $('rank-evidence-label').textContent = learnedPolicy ? actualMethod==='structure_only'?'STRUCTURE-ONLY ESTIMATE':actualMethod==='learned_singleton'?'SINGLETON ABLATION ESTIMATE':'LEARNED USEFULNESS ESTIMATE' : actualMethod === 'graph' ? isMathlib()?'STATIC COVERAGE SCORE':'GRAPH HEURISTIC SCORE' : `${actualMethod.replaceAll('_',' ').toUpperCase()} SCORE`;
  const policyDescription=isMathlib()?({graph:'Estimated search benefit',greedy_coverage:'Estimated search benefit',branching_aware:'Estimated benefit + AND completion',proof_cost:'Proof AST cost',semantic:'Symbolic AST cosine',random:'Fixed-seed random policy'})[actualMethod] || 'Policy-local heuristic':actualMethod==='graph'?'Path saving + goal coverage':'Ranking policy';
  $('rank-uncertainty').textContent = learnedPolicy ? item?.uncertainty !== null && item?.uncertainty !== undefined && Number.isFinite(Number(item.uncertainty)) ? `± ${Number(item.uncertainty).toFixed(3)} ensemble spread` : 'No uncertainty reported' : policyDescription;
  const prefix=item?.score_portfolio;
  $('rank-context').hidden=!isMathlib();
  $('rank-context').textContent=Number.isInteger(item?.score_stage)&&Array.isArray(prefix)?`Round ${item.score_stage+1} · ${selectedIds().has(item.id)?'score when selected':'last evaluated score'}. Portfolio before scoring: ${prefix.length?prefix.join(', '):'empty'}. Scores from different portfolios are not directly comparable.`:'No selection-stage metadata was included in this file.';
}
function renderGoals() {
  const goals = Array.isArray(run.goals) ? run.goals : [];
  const baseline = goals.filter((goal) => goal.baseline?.solved === true).length;
  const augmented = goals.filter((goal) => goal.augmented?.solved === true).length;
  $('success-summary').textContent = `${baseline} → ${augmented} / ${goals.length}`;
  $('baseline-total').textContent = `${baseline}/${goals.length}`;
  $('augmented-total').textContent = `${augmented}/${goals.length}`;
  $('baseline-meter').style.width = `${goals.length ? baseline / goals.length * 100 : 0}%`;
  $('augmented-meter').style.width = `${goals.length ? augmented / goals.length * 100 : 0}%`;
  const list = $('goal-list'); list.replaceChildren();
  if (!goals.length) list.append(node('p','empty-state','No downstream goals were included in this run.'));
  goals.forEach((goal) => {
    const entry = node('div','goal-row');
    const content = node('div');content.append(node('div','goal-title',relationText(goal)));
    const detail = node('details','goal-detail');const summary = node('summary','',`${isMathlib()?'Goal visits':'Expansions'} ${number(goal.baseline?.expansions)} → ${number(goal.augmented?.expansions)} · inspect ${isMathlib()?'witnesses':'paths'}`);detail.append(summary);
    const basePath = (goal.baseline?.path || []).join(' → ');const augmentedPath = (goal.augmented?.path || []).join(' → ');
    const proofSummary=(proof,depth=0)=>!proof||depth>8?'…':`${proof.rule}${proof.lemma_id?'['+proof.lemma_id+']':''}${proof.children?.length?'('+proof.children.map(child=>proofSummary(child,depth+1)).join(', ')+')':''}`;
    detail.append(node('div','',`Baseline witness: ${isMathlib()&&goal.baseline?.proof?proofSummary(goal.baseline.proof):basePath || (goal.baseline?.solved ? 'empty path' : 'budget exhausted or no witness')}`));
    detail.append(node('div','',`Augmented witness: ${isMathlib()&&goal.augmented?.proof?proofSummary(goal.augmented.proof):augmentedPath || (goal.augmented?.solved ? 'empty path' : 'budget exhausted or no witness')}`));content.append(detail);
    const gain = goal.augmented?.solved && !goal.baseline?.solved;
    const loss = goal.baseline?.solved && !goal.augmented?.solved;
    entry.append(content,node('span',`goal-result ${gain ? 'gain' : ''}`,gain ? 'NEWLY SOLVED' : loss ? 'LOST UNDER BUDGET' : goal.augmented?.solved ? 'SOLVED IN BOTH' : 'UNSOLVED'));
    list.append(entry);
  });
}
function renderTimeline() {
  const list = $('timeline');list.replaceChildren();
  const timeline = Array.isArray(run.timeline) ? run.timeline : [];
  if (!timeline.length) {
    const entry = node('li');const text = node('div');text.append(node('strong','','Recorded run loaded'),node('span','','No event timeline was included in the artifact.'));entry.append(text);list.append(entry);return;
  }
  timeline.forEach((event) => {
    const item = node('li');const content = node('div');
    if (typeof event === 'string') content.append(node('strong','',event));
    else {content.append(node('strong','',event.stage || event.event || event.label || event.action || 'Recorded event'));const detail = [event.detail || event.message || event.description,event.timestamp || event.time].filter(Boolean).join(' · ');if(detail) content.append(node('span','',detail));}
    item.append(content);list.append(item);
  });
}
function download(content, filename, mime) {
  const blob = new Blob([content],{type:mime});const url = URL.createObjectURL(blob);const anchor = node('a');anchor.href=url;anchor.download=filename;document.body.append(anchor);anchor.click();anchor.remove();setTimeout(() => URL.revokeObjectURL(url),1000);
}
async function explore(inputContext = context) {
  if (pending || !inputContext) return;
  const budget = Number($('budget').value);
  const selected = Number($('selection-budget').value);
  if (!Number.isInteger(budget) || budget < 1 || budget > 128) {notice('Choose a whole-number search budget between 1 and 128.','error');return;}
  if (!Number.isInteger(selected) || selected < 0 || selected > 16) {notice('Choose a whole-number lemma budget between 0 and 16.','error');return;}
  setPending(true);notice('Exploring bounded consequence paths and checking proof artifacts with the local verifier…','loading');
  try {
    const response = await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({context:inputContext,budget,select:selected,method:$('policy-select').value})});
    const type = response.headers.get('content-type') || '';
    if (!type.includes('application/json')) throw new Error('Live exploration needs the local ProofRipple server. Start it with “proofripple lab”; recorded runs remain inspectable here.');
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || `The local server returned ${response.status}.`);
    loadRun(result,'live');
  } catch (error) {notice(`Exploration failed: ${error.message} The previous recorded result is preserved.`,'error');}
  finally {setPending(false);}
}

async function loadExample(key) {
  if (pending || !EXAMPLES[key]) return;
  const previous = activeExample;
  setPending(true);notice('Loading the recorded context and its domain-specific evidence…','loading');
  try {
    const response = await fetch(EXAMPLES[key].run);
    if (!response.ok) throw new Error(`Recorded artifact returned ${response.status}.`);
    loadRun(await response.json());
  } catch (error) {
    $('example-select').value = previous || 'imported';
    if (!run) {$('context-title').textContent='Open a research run';$('graph-empty').hidden=false;}
    notice(`Example loading failed: ${error.message} ${run ? 'The previous result is preserved.' : 'Import a run JSON or generate the natural demo with the CLI.'}`,'error');
  } finally {setPending(false);}
}

async function importRegisteredDeclaration() {
  if (pending) return;
  const budget = Number($('budget').value);
  const selected = Number($('selection-budget').value);
  if (!Number.isInteger(budget) || budget < 1 || budget > 128) {notice('Choose a whole-number search budget between 1 and 128.','error');return;}
  if (!Number.isInteger(selected) || selected < 0 || selected > 16) {notice('Choose a whole-number lemma budget between 0 and 16.','error');return;}
  const declaration=isMathlib()?'inf_sup_left':'List.length_filter_le';
  setPending(true);notice(`Importing ${declaration} and auditing its exact declaration…`,'loading');
  try {
    const response=await fetch('/api/import-declaration',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:declaration,budget,select:selected,method:$('policy-select').value})});
    if (!(response.headers.get('content-type') || '').includes('application/json')) throw new Error('Registered theorem import needs the local ProofRipple server.');
    const result=await response.json();if(!response.ok)throw new Error(result.error || `The local server returned ${response.status}.`);
    loadRun(result,'live');
  } catch (error) {notice(`Theorem import failed: ${error.message} The previous result is preserved.`,'error');}
  finally {setPending(false);}
}

$('candidate-search').addEventListener('input',renderCandidates);
$('status-filter').addEventListener('change',renderCandidates);
$('reset-graph').addEventListener('click',() => {activeNode=null;renderGraph();renderCandidates();});
$('run-button').addEventListener('click',() => explore());
$('example-select').addEventListener('change',(event) => loadExample(event.target.value));
$('import-declaration').addEventListener('click',importRegisteredDeclaration);
function openFormalBasis(event) {
  if(event)event.preventDefault();
  $('formal-basis').open=true;
  $('formal-basis').scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'start'});
}
$('basis-shortcut').addEventListener('click',openFormalBasis);
document.querySelector('.header-nav a[href="#formal-basis"]').addEventListener('click',openFormalBasis);
$('import-button').addEventListener('click',() => $('import-file').click());
$('import-file').addEventListener('change',async (event) => {
  const file = event.target.files[0];if(!file)return;
  try {
    if(file.size > 15 * 1024 * 1024) throw new Error('Choose a JSON file smaller than 15 MiB.');
    const value = JSON.parse(await file.text());
    if (validContext(value)) await explore(value); else loadRun(value,'imported');
  } catch(error) {notice(`Import failed: ${error.message} The previous result is preserved.`,'error');}
  finally {event.target.value='';}
});
$('export-json').addEventListener('click',() => {if(run)download(JSON.stringify(run,null,2)+'\n',`${context.id || 'proofripple'}-run.json`,'application/json');});
$('export-proof').addEventListener('click',() => {const source=run?.lean_source || run?.verification?.source || proofText();if(source)download(source,`${context.id || 'proofripple'}.lean`,'text/plain');});
$('copy-proof').addEventListener('click',async () => {
  try {await navigator.clipboard.writeText(proofText());$('copy-proof').textContent='Copied';setTimeout(() => {$('copy-proof').textContent='Copy';},1500);}
  catch {notice('The browser could not access the clipboard. Use Export Lean artifact to save the proof source.','error');}
});
const tabs = [$('proof-tab'),$('assumptions-tab')];
function selectTab(tab) {
  tabs.forEach((item) => {const active=item===tab;item.setAttribute('aria-selected',String(active));item.tabIndex=active?0:-1;$(item.getAttribute('aria-controls')).hidden=!active;});
}
tabs.forEach((tab,index) => {
  tab.addEventListener('click',() => selectTab(tab));
  tab.addEventListener('keydown',(event) => {if(['ArrowLeft','ArrowRight','Home','End'].includes(event.key)){event.preventDefault();const target=tabs[event.key==='Home'?0:event.key==='End'?tabs.length-1:(index+(event.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length];selectTab(target);target.focus();}});
});

function renderBenchmark(benchmark, key, chosenProfile=null) {
  const original=benchmark;
  const profiles=benchmark.profiles&&typeof benchmark.profiles==='object'?Object.entries(benchmark.profiles):[];
  $('benchmark-profile-control').hidden=!profiles.length;
  if(profiles.length){
    loadedBenchmark=original;loadedBenchmarkKey=key;
    const defaultId=benchmark.default_profile || benchmark.summary_profile || profiles.find(([,profile])=>profile.k===benchmark.protocol?.selection_budget&&profile.budget===(benchmark.protocol?.search_expansions_per_goal??benchmark.protocol?.search_expansions))?.[0] || profiles.find(([,profile])=>profile.k===3&&profile.budget===8)?.[0] || profiles[0][0];
    const id=profiles.some(([id])=>id===chosenProfile)?chosenProfile:defaultId;
    const profile=profiles.find(([key])=>key===id)?.[1] || profiles[0][1];
    $('benchmark-profile').replaceChildren(...profiles.map(([id,profile])=>{const option=node('option','',`k=${profile.k} · ${profile.budget} goal visits`);option.value=id;return option;}));$('benchmark-profile').value=id;
    benchmark={...benchmark,summary:profile.summary,protocol:{...benchmark.protocol,selection_budget:profile.k,search_expansions_per_goal:profile.budget},candidate_coverage:profile.candidate_coverage || benchmark.candidate_coverage?.profiles?.[id] || (key==='mathlib'?null:benchmark.candidate_coverage)};
  }
  if (!benchmark.summary || typeof benchmark.summary !== 'object') return;
  const entries = Object.entries(benchmark.summary).filter(([,value]) => value && Number.isFinite(Number(value.mean_augmented_solved)));
  if (!entries.length) return;
  const methodNames = {learned:key === 'natural' ? 'Typed-syntax ensemble' : 'Usefulness ensemble',learned_no_bonus:'Learned · no uncertainty bonus',learned_singleton:'Singleton ablation',structure_only:'Structure-only ensemble',greedy_coverage:'Greedy goal coverage',branching_aware:'AND-aware coverage',graph:key==='mathlib'?'Static goal coverage':'Graph heuristic',semantic:key==='mathlib'?'Symbolic AST cosine':'Lexical similarity',random:'Random selection',proof_cost:key==='mathlib'?'Proof AST cost':'Shortest proof first'};
  const tbody = $('benchmark-rows');tbody.replaceChildren();
  const decimal = (value) => Number(value).toFixed(2);
  const compact = (value) => String(Number(Number(value).toFixed(2)));
  const hasTotals = entries.every(([,metrics]) => Number.isFinite(metrics.total_solved) && Number.isFinite(metrics.total_goals));
  document.querySelector('.benchmark-table').classList.toggle('mathlib-benchmark',key==='mathlib');
  $('benchmark-solved-header').textContent=hasTotals?'TOTAL SOLVED':'MEAN SOLVED';
  $('benchmark-gain-header').textContent=hasTotals?'TOTAL GAIN':'MEAN GAIN';
  entries.sort((a,b) => b[1].mean_augmented_solved - a[1].mean_augmented_solved).forEach(([method,metrics]) => {
    const tr=node('tr',method==='learned'?'learned-method':'');
    const label=node('th','',methodNames[method] || method);label.scope='row';
    const gain=Number(hasTotals?metrics.total_marginal_solved:metrics.mean_marginal_solved);
    const interval=metrics.marginal_95pct_context_bootstrap;
    const solved=hasTotals?`${compact(metrics.total_solved)} / ${compact(metrics.total_goals)}`:`${decimal(metrics.mean_augmented_solved)} / ${compact(metrics.goals_per_context)}`;
    const newly=hasTotals?metrics.total_newly_solved:metrics.mean_newly_solved;
    const lost=hasTotals?metrics.total_regressed:metrics.mean_regressed;
    tr.append(label,node('td','',solved),node('td',gain>0?'gain':'',`${gain>0?'+':''}${compact(gain)}`),node('td','',`${compact(newly)} / ${compact(lost)}`),node('td','',Array.isArray(interval)?`${decimal(interval[0])} to ${decimal(interval[1])}`:'Unavailable'),node('td','',metrics.mean_ndcg_at_k !== null && metrics.mean_ndcg_at_k !== undefined && Number.isFinite(Number(metrics.mean_ndcg_at_k))?decimal(metrics.mean_ndcg_at_k):'—'));
    tbody.append(tr);
  });
  const protocol=benchmark.protocol || {};
  $('benchmark-protocol').textContent=`${entries[0][1].contexts} test contexts · ${protocol.selection_budget ?? '—'} lemma cap · ${protocol.search_expansions_per_goal ?? '—'} ${key==='mathlib'?'goal visits':'expansions'} / goal`;
  const learned=benchmark.summary.learned;
  const baselineMethod=key==='mathlib'&&benchmark.summary.greedy_coverage?'greedy_coverage':'graph';
  const comparator=benchmark.summary[baselineMethod];const baselineName=baselineMethod==='greedy_coverage'?'greedy coverage':'the graph heuristic';
  const primary=original.aggregate_summary?.contrasts?.learned_minus_greedy_coverage;
  const primaryValue=primary?.mean_context_profile_solve_fraction_difference;
  const primaryInterval=primary?.paired_context_bootstrap_95pct;
  $('benchmark-primary').hidden=key!=='mathlib'||!Number.isFinite(primaryValue);
  if(key==='mathlib'&&Number.isFinite(primaryValue))$('benchmark-primary').textContent=`Primary comparison · learned minus greedy coverage: ${(primaryValue*100).toFixed(2)} percentage points in whole-context mean solve fraction, averaged over all ${profiles.length} profiles.${Array.isArray(primaryInterval)?` 95% paired context bootstrap interval: ${(primaryInterval[0]*100).toFixed(2)} to ${(primaryInterval[1]*100).toFixed(2)} percentage points.`:''}`;
  const comparison=learned&&comparator?(hasTotals?`Learned: ${compact(learned.total_solved)}/${compact(learned.total_goals)} retained queries; ${baselineName}: ${compact(comparator.total_solved)}/${compact(comparator.total_goals)}. Baseline: ${compact(learned.total_baseline_solved)}/${compact(learned.total_goals)}.`:`The learned ranker solves ${decimal(learned.mean_augmented_solved)} goals per context; ${baselineName} solves ${decimal(comparator.mean_augmented_solved)}.`):'Recorded held-out comparisons from the bundled benchmark.';
  $('benchmark-summary').textContent=`${comparison} ${learned&&comparator&&Number(comparator.mean_augmented_solved)>=Number(learned.mean_augmented_solved)?'The learned model does not outperform this heuristic in this view.':'Differences apply to this recorded benchmark; inspect per-context evidence.'}${profiles.length?` This is one of ${profiles.length} budget profiles, which reuse goal queries.`:''}`;
  const coverage=benchmark.candidate_coverage?.test;
  $('benchmark-coverage').hidden=!coverage;
  if(coverage){
    const empty=coverage.empty_contexts ?? (coverage.candidate_counts?Object.values(coverage.candidate_counts).filter(count=>count===0).length:null);
    $('benchmark-coverage').textContent=`Coverage: ${compact(learned?.total_goals??0)} retained queries across ${coverage.active_goal_contexts}/${coverage.contexts} active contexts; ${coverage.contexts_with_ranking_choice} contexts offer a choice beyond the lemma cap.${empty===null?'':` ${empty} contexts have no eligible candidates.`} ${key==='natural'?'This sparse study does not establish an ML advantage.':'Selection comparisons require a real ranking choice.'}`;
  }
  $('benchmark-section').querySelector('.experiment-caveat a').href=EXAMPLES[key].benchmark;
  const caveat=$('benchmark-section').querySelector('.experiment-caveat');
  const evidenceLink=caveat.querySelector('a');
  const scope=key==='mathlib'?'Registered Mathlib set-lattice inclusions. Profiles reuse the retained queries; random-policy totals average repeated runs within context. The primary interval resamples paired whole contexts across all profiles. Ensemble disagreement is not calibrated uncertainty. ':`${key==='natural'?'Registered typed List Nat capacity pipelines.':'Procedurally generated implication graphs.'} ${hasTotals?'Random-policy totals average repeated runs; query occurrences need not be globally distinct statements. ':''}Intervals concern mean marginal gain per context. NDCG measures relative ranking quality (0–1). Ensemble disagreement is not calibrated uncertainty. `;
  caveat.replaceChildren(document.createTextNode(scope),evidenceLink);
  $('benchmark-section').hidden=false;
  renderAutomation(original,key,loadedSupplementalControl);
}

function renderAutomation(benchmark,key,supplemental){
  $('automation-control').hidden=true;$('automation-provenance').hidden=true;
  if(!['natural','mathlib'].includes(key))return;
  const original=benchmark.automation_control;
  const countsValid=control=>Number.isInteger(control?.solved)&&Number.isInteger(control?.total)&&control.total>0&&control.solved>=0&&control.solved<=control.total;
  const repaired=key==='mathlib'&&supplemental?.status==='kernel_verified'&&countsValid(supplemental)&&supplemental.phase==='post_study_control_plumbing_repair'&&supplemental.provenance?.data_sha256===benchmark.data_freeze?.data_sha256&&supplemental.total===original?.total&&Object.keys(benchmark.source_sha256||{}).length>0&&Object.entries(benchmark.source_sha256||{}).every(([name,hash])=>supplemental.provenance?.scientific_source_sha256?.[name]===hash);
  const control=repaired?supplemental:original;
  if(!countsValid(control)||(!repaired&&control.status!=='kernel_verified'&&!(key==='mathlib'&&control.status==='failed')))return;
  $('automation-kind').textContent=repaired?'SUPPLEMENTAL CONTROL · POST-STUDY':control.status==='failed'?'CONTROL BUNDLE · FAILED':'AUTOMATION CONTROL';
  $('automation-score').textContent=`${control.solved}/${control.total}`;
  $('automation-status').textContent=stateName(control.status);
  $('automation-status').className=`status-badge ${control.status==='kernel_verified'?'verified':'failed'}`;
  $('automation-description').textContent=repaired?`Post-study preprocessing fix: a no-op simplification can continue into the unchanged aesop tactic. All ${control.total} retained test goals were checked without seed or candidate lemmas. Search and tactic budgets measure different work. Allowed axioms: ${(control.allowed_axioms||[]).join(', ')}.`:`${control.status==='failed'?'Original certification bundle failed during preprocessing; its count is not an aesop solve-rate measurement. ':''}${control.method || 'Lean automation'}. ${control.coverage || ''} ${control.interpretation || 'Its resources differ from restricted search; this is not evidence of an advantage over Lean automation.'}`;
  if(repaired){
    const originalLink=node('a','',`Original control bundle: ${stateName(original.status).toLowerCase()} (${original.solved}/${original.total} certified) ↗`);originalLink.href=EXAMPLES.mathlib.benchmark;
    const repairLink=node('a','','Supplemental repair audit ↗');repairLink.href=EXAMPLES.mathlib.control;
    $('automation-provenance').replaceChildren(originalLink,document.createTextNode(' · '),repairLink,document.createTextNode('. The original preprocessing failure is not an aesop solve-rate measurement. Ranking results and frozen data are unchanged.'));
    $('automation-provenance').hidden=false;
  }
  $('automation-control').hidden=false;
}

async function refreshBenchmark(key) {
  const request=++benchmarkRequest;
  // Clear stale domain evidence immediately, including a prior automation result.
  $('benchmark-section').hidden=true;
  $('automation-control').hidden=true;
  $('benchmark-rows').replaceChildren();
  $('benchmark-profile-control').hidden=true;loadedBenchmark=null;loadedBenchmarkKey=null;loadedSupplementalControl=null;
  $('benchmark-primary').hidden=true;
  if (!key || !EXAMPLES[key]) return;
  try {
    const response=await fetch(EXAMPLES[key].benchmark);
    if(!response.ok)return;
    const benchmark=await response.json();
    let supplemental=null;
    if(EXAMPLES[key].control){try{const response=await fetch(EXAMPLES[key].control);if(response.ok)supplemental=await response.json();}catch{}}
    if(request===benchmarkRequest){loadedSupplementalControl=supplemental;renderBenchmark(benchmark,key);}
  } catch {} // Missing recorded benchmark never changes the active run's evidence.
}
$('benchmark-profile').addEventListener('change',event=>{if(loadedBenchmark&&loadedBenchmarkKey)renderBenchmark(loadedBenchmark,loadedBenchmarkKey,event.target.value);});

async function initializeWorkbench(){
  setPending(true);
  try{
    const response=await fetch(EXAMPLES.mathlib.run);
    if(response.ok){loadRun(await response.json());return;}
  }catch{}
  setPending(false);loadExample('natural');
}
initializeWorkbench();
