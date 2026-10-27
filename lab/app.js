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
const EXAMPLES = {
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
const stateName = (status) => ({kernel_verified:'Kernel verified', proposed:'Proposed', failed:'Failed', unavailable:'Unavailable', timeout:'Timed out', rejected:'Rejected'})[status] || String(status || 'Proposed').replaceAll('_', ' ');

function notice(message, kind = '') {
  $('notice').textContent = message;
  $('notice').className = `notice ${kind}`.trim();
}
function setPending(value) {
  pending = value;
  $('run-button').disabled = value || !context;
  $('run-button').replaceChildren(document.createTextNode(value ? 'Exploring…' : 'Explore consequences'), node('span', '', value ? '…' : '→'));
  $('import-button').disabled = value;
  $('budget').disabled = value;
  $('example-select').disabled = value;
  $('policy-select').disabled = value;
  $('selection-budget').disabled = value;
  $('import-declaration').disabled = value;
  $('workspace').setAttribute('aria-busy', String(value));
}
function validContext(value) {
  return value && Array.isArray(value.nodes) && value.nodes.length > 0 && Array.isArray(value.edges) && value.seed && typeof value.seed === 'object';
}
function validateRun(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('The JSON must contain a run object or a supported implication context.');
  if (!validContext(value.context)) throw new Error('This run has no supported context. Expected nodes, edges and a seed theorem.');
  if (!Array.isArray(value.candidates)) throw new Error('This run has no candidates array.');
  if (!Array.isArray(value.goals)) throw new Error('This run has no downstream goals array.');
  if (value.candidates.length > 10000 || value.context.nodes.length > 500) throw new Error('This run is too large for the workbench. Use a context with at most 500 nodes and 10,000 candidates.');
  return value;
}
function loadRun(value, origin = 'recorded') {
  validateRun(value);
  run = value;
  context = value.context;
  activeExample = origin === 'imported' ? null : context.domain === 'list-capacity' ? 'natural' : 'implications';
  $('example-select').value = activeExample || 'imported';
  activeNode = null;
  const selected = selectedIds();
  currentCandidate = candidateList().find((item) => item.id === [...selected][0]) || candidateList()[0] || null;
  $('context-title').textContent = context.title || context.id || 'Imported context';
  $('seed-label').textContent = `${nodeName(context.seed.source)} → ${nodeName(context.seed.target)}`;
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
  $('policy-select').querySelectorAll('[data-recorded-policy]').forEach((item) => item.remove());
  if (!['graph','learned'].includes(rankingMethod)) {
    const option=node('option','',`Recorded: ${rankingMethod.replaceAll('_',' ')}`);option.value=rankingMethod;option.dataset.recordedPolicy='true';$('policy-select').append(option);
  }
  $('policy-select').value = rankingMethod;
  $('budget-caption').textContent = Number.isFinite(Number(budgetValue)) ? `${budgetValue} expansions per goal` : 'Equal search budgets';
  $('export-json').disabled = false;
  $('candidate-search').value = '';
  $('status-filter').value = 'all';
  $('graph-context').textContent = context.domain === 'list-capacity' ? `${context.nodes.length} typed list stages · ${context.edges.length} closed primitive capacity theorems` : `${context.nodes.length} propositions · ${context.edges.length} explicit implication assumptions`;
  $('primitive-legend').textContent = context.domain === 'list-capacity' ? 'Closed capacity theorem' : 'Assumption';
  renderFormalBasis(); renderGraph(); renderCandidates(); renderInspector(); renderGoals(); renderTimeline();
  refreshBenchmark(activeExample);
  setPending(false);
  if (origin === 'imported') notice('Imported recorded evidence. Verification states are reported by this file and have not been rechecked in this session.');
  else if (origin === 'live') notice(`Local exploration complete. ${stateName(run.verification?.status || 'unavailable')} · Inspect the exact proof and assumptions below.`, run.verification?.status === 'failed' ? 'error' : '');
  else notice('Recorded experiment · Every result below comes from the bundled run. Explore consequences to run a fresh local experiment.');
}

function renderFormalBasis() {
  const natural = context.domain === 'list-capacity';
  const basis = run.natural_domain?.imported_seed;
  const badge = $('basis-status');
  badge.textContent = stateName(run.verification?.status || 'unavailable');
  badge.className = `status-badge ${run.verification?.status === 'kernel_verified' ? 'verified' : run.verification?.status === 'failed' ? 'failed' : 'proposed'}`;
  $('basis-domain').textContent = natural ? 'CONCRETE LIST NAT DOMAIN' : 'PROPOSITIONAL IMPLICATION DOMAIN';
  $('basis-name').textContent = natural ? basis?.name || 'List.length_filter_le · audit unavailable' : 'Explicitly quantified implication context';
  $('basis-description').textContent = natural ? 'The imported library theorem bounds a filtered list’s length. The orange graph edge is a composite seed built from closed capacity theorems; it is distinct from this imported declaration.' : 'Every primitive graph edge is an explicit implication hypothesis. The seed and consequences are compositions under those quantified hypotheses.';
  $('basis-type-details').hidden = !natural;
  $('basis-type').textContent = basis?.statement || 'The exact imported statement has not been audited in this recorded run.';
  const allowed = run.natural_domain?.allowed_axioms;
  $('basis-policy').textContent = natural ? `Allowed dependency axiom: ${Array.isArray(allowed) && allowed.length ? allowed.join(', ') : 'not reported'}. Other axiom dependencies must be rejected by the verifier.` : 'Empty-axiom policy. The verifier rejects declarations with any transitive axiom dependency.';
  $('basis-axioms').textContent = natural ? Array.isArray(basis?.axioms) ? basis.axioms.length ? basis.axioms.join(', ') : 'None reported' : 'No audit reported' : 'No imported theorem';
  const dependencyList = $('basis-dependencies');dependencyList.replaceChildren();
  for (const dependency of basis?.dependencies || []) dependencyList.append(node('span','',dependency));
  if (!basis?.dependencies?.length) dependencyList.append(node('span','','No proof constants reported'));
  $('basis-dependency-details').hidden = !natural;
  const templates = run.natural_domain?.registered_templates || [];
  const templateList = $('basis-templates');templateList.replaceChildren();
  for (const template of templates) {
    const item=node('div','registered-template');item.append(node('strong','',template.name || 'Registered template'),node('p','',template.explanation || 'Fixed registered rule, not a discovered inference mechanism.'));templateList.append(item);
  }
  $('basis-template-details').hidden = !templates.length;
  $('import-declaration').hidden = !natural;
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
  const {positions, height} = graphPositions();
  graph.setAttribute('viewBox', `0 0 920 ${height}`);
  const defs = svg('defs');
  [['gray','#a9b0a4'],['seed','#b44b32'],['teal','#194f48']].forEach(([id,color]) => {
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
    const group = svg('g',{class:`graph-node ${item.id === activeNode || connected ? 'selected' : ''} ${item.id === seed.source || item.id === seed.target ? 'seed-node' : ''}`,transform:`translate(${point.x} ${point.y})`,tabindex:0,role:'button','aria-label':`${item.id}: ${item.label || item.id}. Show connected consequences.`,'aria-pressed':String(item.id === activeNode)});
    group.append(svg('title',{},`${item.id}: ${item.label || item.id}`));
    group.append(svg('rect',{x:-27,y:-21,width:54,height:42,rx:21}));
    group.append(svg('text',{'text-anchor':'middle',y:5},String(item.id).length > 6 ? String(item.id).slice(0,5)+'…' : item.id));
    const shortLabel = item.expression?.op || item.label || '';
    group.append(svg('text',{'text-anchor':'middle',y:39,class:'node-label'},String(shortLabel).length > 19 ? String(shortLabel).slice(0,17)+'…' : shortLabel));
    const select = () => {activeNode = activeNode === item.id ? null : item.id; renderGraph(); renderCandidates();};
    group.addEventListener('click',select);
    group.addEventListener('keydown',(event) => {if (event.key === 'Enter' || event.key === ' ') {event.preventDefault();select();}});
    graph.append(group);
  });
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
    const connected = !activeNode || item.source === activeNode || item.target === activeNode;
    const matches = `${item.id} ${item.source} ${item.target} ${labelFor(item.source)} ${labelFor(item.target)}`.toLowerCase().includes(query);
    return connected && matches && (filter === 'all' || (filter === 'selected' ? selected.has(item.id) : (item.status || 'proposed') === filter));
  }).sort((a,b) => Number(selected.has(b.id)) - Number(selected.has(a.id)) || Number(b.score || 0) - Number(a.score || 0) || String(a.id).localeCompare(String(b.id)));
  $('candidate-empty').hidden = candidates.length > 0;
  candidates.forEach((candidate) => {
    const row = node('tr', candidate.id === currentCandidate?.id ? 'active' : '');
    const title = node('td');
    title.append(node('span','candidate-name',`${candidate.source} → ${candidate.target}`));
    const identifier = node('span','candidate-id',candidate.id);
    if (selected.has(candidate.id)) identifier.append(node('span','selected-mark','SELECTED'));
    title.append(identifier);
    const state = node('td'); state.append(node('span',`status-badge ${candidate.status === 'kernel_verified' ? 'verified' : candidate.status === 'failed' ? 'failed' : 'proposed'}`,stateName(candidate.status)));
    const score = node('td');score.append(node('span','candidate-score',formatted(candidate.score)));
    const action = node('td'); const button = node('button','candidate-select','↗');button.setAttribute('aria-label',`Inspect consequence ${candidate.id}`);button.addEventListener('click',(event) => {event.stopPropagation();chooseCandidate(candidate);});action.append(button);
    row.append(title,state,score,action);row.addEventListener('click',() => chooseCandidate(candidate));rows.append(row);
  });
}
function proofText() {
  const proof = currentCandidate?.proof;
  return typeof proof === 'string' ? proof : proof?.source || proof?.lean || '';
}
function renderInspector() {
  const item = currentCandidate;
  $('inspect-id').textContent = item?.id || 'NO CONSEQUENCE SELECTED';
  $('inspect-statement').textContent = item ? `${item.source} → ${item.target}` : 'P → Q';
  const badge = $('inspect-status');badge.textContent = item ? stateName(item.status) : 'Awaiting selection';badge.className = `status-badge ${item?.status === 'kernel_verified' ? 'verified' : item?.status === 'failed' ? 'failed' : 'proposed'}`;
  const explanation = typeof item?.explanation === 'string' ? item.explanation : item?.explanation?.explanation;
  $('inspect-explanation').textContent = explanation || (item ? `An implication from “${labelFor(item.source)}” to “${labelFor(item.target)}” under this context's explicitly quantified assumptions.` : 'Select a consequence to inspect its exact proof and assumptions.');
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
  if (list.length) list.forEach((dependency) => dependencies.append(node('span','',typeof dependency === 'object' ? dependency.id || dependency.name || JSON.stringify(dependency) : dependency)));
  else dependencies.append(node('span','','No dependencies reported'));
  $('rank-score').textContent = formatted(item?.score);
  const actualMethod=run.metrics?.method || rankingMethod;
  $('rank-evidence-label').textContent = actualMethod === 'learned' ? 'LEARNED USEFULNESS ESTIMATE' : actualMethod === 'graph' ? 'GRAPH HEURISTIC SCORE' : `${actualMethod.replaceAll('_',' ').toUpperCase()} SCORE`;
  $('rank-uncertainty').textContent = actualMethod === 'learned' ? item?.uncertainty !== null && item?.uncertainty !== undefined && Number.isFinite(Number(item.uncertainty)) ? `± ${Number(item.uncertainty).toFixed(3)} ensemble spread` : 'No uncertainty reported' : actualMethod === 'graph' ? 'Path saving + goal coverage' : 'Deterministic ranking policy';
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
    const content = node('div');content.append(node('div','goal-title',`${goal.source} → ${goal.target}`));
    const detail = node('details','goal-detail');const summary = node('summary','',`Expansions ${number(goal.baseline?.expansions)} → ${number(goal.augmented?.expansions)} · inspect paths`);detail.append(summary);
    const basePath = (goal.baseline?.path || []).join(' → ');const augmentedPath = (goal.augmented?.path || []).join(' → ');
    detail.append(node('div','',`Starting library: ${basePath || (goal.baseline?.solved ? 'empty path' : 'budget exhausted or no path found')}`));
    detail.append(node('div','',`With consequences: ${augmentedPath || (goal.augmented?.solved ? 'empty path' : 'budget exhausted or no path found')}`));content.append(detail);
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
  setPending(true);notice('Importing List.length_filter_le and auditing its exact declaration in the local Lean process…','loading');
  try {
    const response=await fetch('/api/import-declaration',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:'List.length_filter_le',budget,select:selected,method:$('policy-select').value})});
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

function renderBenchmark(benchmark, key) {
  if (!benchmark.summary || typeof benchmark.summary !== 'object') return;
  const entries = Object.entries(benchmark.summary).filter(([,value]) => value && Number.isFinite(Number(value.mean_augmented_solved)));
  if (!entries.length) return;
  const methodNames = {learned:key === 'natural' ? 'Typed-syntax usefulness ensemble' : 'Usefulness ensemble',structure_only:'Structure-only ensemble',graph:'Graph heuristic',semantic:'Lexical similarity',random:'Random selection',proof_cost:'Shortest proof first'};
  const tbody = $('benchmark-rows');tbody.replaceChildren();
  const decimal = (value) => Number(value).toFixed(2);
  const compact = (value) => String(Number(Number(value).toFixed(2)));
  const hasTotals = entries.every(([,metrics]) => Number.isFinite(metrics.total_solved) && Number.isFinite(metrics.total_goals));
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
  $('benchmark-protocol').textContent=`${entries[0][1].contexts} test contexts · ${protocol.selection_budget ?? '—'} lemma cap · ${protocol.search_expansions_per_goal ?? '—'} expansions / goal`;
  const learned=benchmark.summary.learned;
  const graph=benchmark.summary.graph;
  const comparison=learned&&graph?(hasTotals?`The learned ranker solves ${compact(learned.total_solved)}/${compact(learned.total_goals)} retained queries; the graph heuristic solves ${compact(graph.total_solved)}/${compact(graph.total_goals)}. Starting library: ${compact(learned.total_baseline_solved)}/${compact(learned.total_goals)}.`:`The learned ranker solves ${decimal(learned.mean_augmented_solved)} goals per context; the graph heuristic solves ${decimal(graph.mean_augmented_solved)}.`):'Recorded held-out comparisons from the bundled benchmark.';
  $('benchmark-summary').textContent=`${comparison} ${learned&&graph&&Number(graph.mean_augmented_solved)>=Number(learned.mean_augmented_solved)?'The learned model does not outperform this strong graph baseline.':'The observed differences are specific to this benchmark; inspect the full per-context evidence.'}`;
  const coverage=benchmark.candidate_coverage?.test;
  $('benchmark-coverage').hidden=!coverage;
  if(coverage)$('benchmark-coverage').textContent=`Sparse coverage: ${compact(learned?.total_goals??0)} retained queries across ${coverage.active_goal_contexts}/${coverage.contexts} active contexts; only ${coverage.contexts_with_ranking_choice} contexts offer a choice beyond the lemma cap. ${coverage.empty_contexts} contexts have no eligible candidates. This study does not establish an ML advantage.`;
  $('benchmark-section').querySelector('.experiment-caveat a').href=EXAMPLES[key].benchmark;
  const caveat=$('benchmark-section').querySelector('.experiment-caveat');
  const evidenceLink=caveat.querySelector('a');
  caveat.replaceChildren(document.createTextNode(`${key==='natural' ? 'Registered typed List Nat capacity pipelines.' : 'Procedurally generated implication graphs.'} ${hasTotals?'Random-policy totals average five repetitions; query occurrences need not be globally distinct statements. ':''}Intervals concern mean marginal gain per context. NDCG measures relative ranking quality (0–1). Ensemble disagreement is not calibrated uncertainty. `),evidenceLink);
  $('benchmark-section').hidden=false;
  const control=benchmark.automation_control;
  if (key === 'natural' && control?.status === 'kernel_verified' && Number.isInteger(control.solved) && Number.isInteger(control.total) && control.total > 0 && control.solved >= 0 && control.solved <= control.total) {
    $('automation-score').textContent=`${control.solved}/${control.total}`;
    $('automation-description').textContent=`${control.method || 'Lean automation'} solves the audited showcase goals without the discovered lemmas. ${control.coverage || ''} ${control.interpretation || 'Its resources differ from restricted graph search; this is not evidence of an advantage over Lean automation.'} Allowed axioms for this separate control: ${(control.allowed_axioms || []).join(', ') || 'none reported'}.`;
    $('automation-control').hidden=false;
  }
}

async function refreshBenchmark(key) {
  const request=++benchmarkRequest;
  // Clear stale domain evidence immediately, including a prior automation result.
  $('benchmark-section').hidden=true;
  $('automation-control').hidden=true;
  $('benchmark-rows').replaceChildren();
  if (!key || !EXAMPLES[key]) return;
  try {
    const response=await fetch(EXAMPLES[key].benchmark);
    if(!response.ok)return;
    const benchmark=await response.json();
    if(request===benchmarkRequest)renderBenchmark(benchmark,key);
  } catch {} // Missing recorded benchmark never changes the active run's evidence.
}

loadExample('natural');
