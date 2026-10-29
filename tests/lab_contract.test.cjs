/* Import-shape regressions use the actual validator without starting a browser,
   contacting a verifier, or mocking a successful proof. */
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const {test} = require('node:test');
const root = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'lab/app.js'), 'utf8');
const boundary = source.indexOf('\nfunction renderFormalBasis(');
assert(boundary > 0, 'Run-loading contract must be available before renderer setup');
const sandbox = vm.createContext({});
vm.runInContext(source.slice(0, boundary), sandbox);
const validate = value => sandbox.validateRun(value);
const read = name => JSON.parse(fs.readFileSync(path.join(root, name)));
const demo = () => read('artifacts/mathlib/demo.json');

for (const name of ['artifacts/demo.json', 'artifacts/natural/demo.json', 'artifacts/mathlib/demo.json']) {
  test(`recorded ${name} remains importable without changing its evidence`, () => {
    const value = read(name), before = JSON.stringify(value);
    assert.equal(validate(value), value);
    assert.equal(JSON.stringify(value), before);
  });
}
const malformed = {
  'null budget': r => r.budget = null,
  'goal expansion object': r => r.goals[0].baseline.expansions = {toString:null},
  'ranking method object': r => r.metrics.method = {},
  'witness path object': r => r.goals[0].baseline.path = {},
  'truthy string solved flag': r => r.goals[0].baseline.solved = 'false',
  'proof children object': r => r.goals[0].augmented.proof.children = {length: 1},
  'candidate status object': r => r.candidates[0].status = {},
  'nontext proof axiom': r => r.candidates[0].axioms = [{toString: null}],
  'unknown selected identifier': r => r.selected = ['missing-candidate'],
  'duplicate candidate identifiers': r => r.candidates[1].id = r.candidates[0].id,
  'out-of-range set variable': r => r.candidates[0].source = {op:'var', index:6},
  'template explanation object': r => (r.mathlib_domain || r.metadata.mathlib_domain).registered_templates = [{name:'bad', explanation:{}}],
  'nontext imported dependency': r => (r.mathlib_domain || r.metadata.mathlib_domain).imported_seed.dependencies = [{}],
  'timeline detail object': r => r.timeline[0].detail = {},
};
for (const [name, mutate] of Object.entries(malformed)) {
  test(`reject ${name} before the active run can change`, () => {
    const value = demo();mutate(value);
    const previous = demo();
    sandbox.previous = previous;
    vm.runInContext('run = previous; context = previous.context;', sandbox);
    assert.throws(() => sandbox.loadRun(value, 'imported'));
    assert.equal(vm.runInContext('run', sandbox), previous);
    assert.equal(vm.runInContext('context', sandbox), previous.context);
  });
}
test('reject overdeep proof trees before recursive presentation', () => {
  const r = demo(), leaf = structuredClone(r.candidates[0].proof_ast);
  let cursor = leaf;
  for (let i=0;i<35;i++) {cursor.children = [structuredClone(r.candidates[0].proof_ast)];cursor=cursor.children[0];}
  r.candidates[0].proof_ast=leaf;
  assert.throws(() => validate(r), /bounded/);
});

for (const [name, mutate] of Object.entries({
  'graph edge identifier': r => r.context.edges[0].id = {toString:null},
  'node expression operator': r => r.context.nodes[0].expression = {op:{toString:null}},
})) {
  test(`reject malformed ${name} through the actual loader`, () => {
    const previous = read('artifacts/natural/demo.json');
    const invalid = structuredClone(previous);mutate(invalid);
    sandbox.previous = previous;
    vm.runInContext('run = previous; context = previous.context;', sandbox);
    assert.throws(() => sandbox.loadRun(invalid, 'imported'));
    assert.equal(vm.runInContext('run', sandbox), previous);
    assert.equal(vm.runInContext('context', sandbox), previous.context);
  });
}

for (const field of ['library revision', 'candidate dependency']) {
  test(`reject excessive JSON nesting in ${field} without replacing the active result`, () => {
    const previous = demo(), invalid = demo();
    const nested = {};let cursor = nested;
    for (let i=0;i<10000;i++) {cursor.a = {};cursor=cursor.a;}
    if (field === 'library revision') (invalid.mathlib_domain || invalid.metadata.mathlib_domain).library_revision = nested;
    else invalid.candidates[0].dependencies = [nested];
    sandbox.previous = previous;
    vm.runInContext('run = previous; context = previous.context;', sandbox);
    assert.throws(() => sandbox.loadRun(invalid, 'imported'), /nesting limit/);
    assert.equal(vm.runInContext('run', sandbox), previous);
    assert.equal(vm.runInContext('context', sandbox), previous.context);
  });
}
