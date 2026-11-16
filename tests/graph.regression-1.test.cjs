// Regression: ISSUE-001 - interactive proof steps need a non-atomic SVG parent.
// Found by /qa on 2026-11-16.
// Report: research/proofripple-product/qa-report-proofripple-2026-11-16.md
// This DOM boundary checks the actual renderer and keyboard handler, not Lean validity.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const {test} = require('node:test');
const root = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'lab/app.js'), 'utf8');
const html = fs.readFileSync(path.join(root, 'lab/index.html'), 'utf8');

class Element {
  constructor(tag) {this.tag = tag;this.attrs = {};this.children = [];this.style = {};this.listeners = new Map();}
  setAttribute(name, value) {this.attrs[name] = String(value);}
  getAttribute(name) {return this.attrs[name] ?? null;}
  append(...items) {this.children.push(...items);}
  replaceChildren(...items) {this.children = items;}
  addEventListener(name, listener) {this.listeners.set(name, listener);}
  get classList() {
    const tokens = () => (this.attrs.class || '').split(/\s+/).filter(Boolean);
    return {
      add: (...names) => {this.attrs.class = [...new Set([...tokens(), ...names])].join(' ');},
      remove: (...names) => {this.attrs.class = tokens().filter(n => !names.includes(n)).join(' ');},
    };
  }
  querySelectorAll(selector) {
    return this.children.flatMap(child => child instanceof Element ? [
      ...((child.attrs.class || '').split(/\s+/).includes(selector.slice(1)) ? [child] : []),
      ...child.querySelectorAll(selector),
    ] : []);
  }
}

for (const fixture of ['artifacts/mathlib/demo.json', 'artifacts/demo.json']) {
  test(`${fixture} exposes rendered proof controls outside atomic image semantics`, () => {
    const elements = new Map();
    const get = id => {
      if (!elements.has(id)) elements.set(id, new Element('div'));
      return elements.get(id);
    };
    const graph = get('graph');graph.parentElement = get('graph-wrap');
    const markup = html.match(/<svg\b[^>]*\bid="graph"[^>]*>/)[0];
    for (const [, name, value] of markup.matchAll(/([\w-]+)="([^"]*)"/g)) graph.setAttribute(name, value);
    const example = JSON.parse(fs.readFileSync(path.join(root, fixture)));
    const sandbox = vm.createContext({example, document: {
      getElementById: get,
      createElementNS: (_namespace, tag) => new Element(tag),
      createTextNode: text => String(text),
    }});
    const boundary = source.indexOf("\n$('candidate-search').addEventListener");
    assert(boundary > 0);
    vm.runInContext(source.slice(0, boundary), sandbox);
    vm.runInContext('run = example;context = example.context;currentCandidate = example.candidates[0];renderGraph();', sandbox);
    const controls = graph.querySelectorAll(fixture.includes('mathlib') ? '.proof-step' : '.graph-node');
    assert(controls.length > 1, 'production graph must actually contain independently operable controls');
    assert(controls.every(item => item.getAttribute('role') === 'button' && item.getAttribute('tabindex') === '0'));
    assert(['group', 'document', 'graphics-document'].includes(graph.getAttribute('role')),
      'an atomic image role hides its interactive descendants from assistive technology');
    if (fixture.includes('mathlib')) {
      const joint = controls.find(item => item.getAttribute('aria-label').includes('2 premises.'));
      assert(joint, 'the real fixture includes a two-premise proof step');
      let prevented = false;
      joint.listeners.get('keydown')({key:'Enter', preventDefault() {prevented = true;}});
      assert(prevented);
      assert.equal(joint.getAttribute('aria-pressed'), 'true');
      assert.equal(get('proof-step-detail').hidden, false);
      assert.match(get('proof-step-detail').textContent, /All 2 displayed premises are required/);
    }
  });
}
