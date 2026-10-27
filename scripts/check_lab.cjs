/* Optional Playwright development check. Uses a fresh temporary profile and
   only a loopback workbench. Run after both domain artifacts are generated. */
const { chromium } = require('playwright');
const fs = require('node:fs/promises');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');

(async () => {
  const url = process.env.PROOFRIPPLE_URL || 'http://127.0.0.1:8765/lab/';
  assert(['127.0.0.1','localhost','[::1]'].includes(new URL(url).hostname), 'Use a loopback workbench URL');
  const out = path.resolve(process.env.PROOFRIPPLE_BROWSER_OUT || 'outputs/browser-v02-final');
  await fs.mkdir(out, { recursive: true });
  const browser = await chromium.launch({ headless: true, executablePath: process.env.PROOFRIPPLE_CHROME });
  const errors = [], observations = [];
  try {
    const context = await browser.newContext({viewport:{width:1440,height:1080},acceptDownloads:true});
    const page = await context.newPage();
    page.on('pageerror', error => errors.push(error.message));
    const bundle = async relative => {
      const response = await page.request.get(new URL(relative, url).href);
      assert(response.ok(), `${relative} must exist before browser checking`);
      return response.json();
    };
    const natural = await bundle('../artifacts/natural/demo.json');
    const original = await bundle('../artifacts/demo.json');
    const naturalBenchmark = await bundle('../artifacts/natural/benchmark.json');
    const originalBenchmark = await bundle('../artifacts/benchmark.json');
    const verified = value => value.candidates.filter(candidate=>candidate.status==='kernel_verified').length;
    const assertRendered = async value => {
      await page.waitForFunction(expected=>document.querySelector('#context-title').textContent===expected.title && document.querySelector('#verified-count').textContent===String(expected.verified), {title:value.context.title,verified:verified(value)});
      assert.equal(await page.inputValue('#budget'),String(value.budget.search_expansions_per_goal));
      assert.equal(await page.inputValue('#selection-budget'),String(value.budget.selected_lemmas));
      assert.equal(await page.inputValue('#policy-select'),value.metrics.method);
      assert.equal(await page.locator('#baseline-total').textContent(),`${value.metrics.baseline_solved}/${value.goals.length}`);
      assert.equal(await page.locator('#augmented-total').textContent(),`${value.metrics.augmented_solved}/${value.goals.length}`);
    };
    const checkBenchmark = async (expected,key) => {
      await page.waitForFunction(key=>!document.querySelector('#benchmark-section').hidden && document.querySelector('#benchmark-section .experiment-caveat a').getAttribute('href')===key,key);
      const rows=page.locator('#benchmark-rows tr');assert.equal(await rows.count(),Object.keys(expected.summary).length);
      const metrics=expected.summary.learned;
      const learned=Number.isFinite(metrics.total_solved)?`${metrics.total_solved}/${metrics.total_goals}`:metrics.mean_augmented_solved.toFixed(2);
      assert((await page.locator('#benchmark-summary').textContent()).includes(learned));
      if(expected.candidate_coverage?.test){
        assert.match(await page.locator('#benchmark-solved-header').textContent(),/TOTAL/);
        assert((await page.locator('#benchmark-coverage').textContent()).includes(`${expected.candidate_coverage.test.contexts_with_ranking_choice} contexts`));
      } else assert.equal(await page.locator('#benchmark-coverage').isVisible(),false);
      assert.equal(await page.locator('#automation-control').isVisible(),expected.automation_control?.status==='kernel_verified');
    };
    await page.goto(url);
    await assertRendered(natural);
    await checkBenchmark(naturalBenchmark,'../artifacts/natural/benchmark.json');
    assert.equal(natural.context.domain,'list-capacity');
    assert.equal(Number(await page.locator('#candidate-count').textContent()),natural.candidates.length);
    assert.equal(Number(await page.inputValue('#selection-budget')),natural.budget.selected_lemmas);
    assert.equal(natural.metrics.goal_count,natural.goals.length);
    assert.match(await page.locator('#basis-name').textContent(),/List.length_filter_le/);
    assert.equal(await page.locator('#basis-type').textContent(),natural.natural_domain.imported_seed.statement);
    assert.match(await page.locator('#basis-axioms').textContent(),/propext/);
    assert.match(await page.locator('#basis-policy').textContent(),/propext/);
    assert.match(await page.locator('#primitive-legend').textContent(),/Closed/);
    assert.match(await page.locator('#rank-evidence-label').textContent(),/GRAPH HEURISTIC/);
    assert(!(await page.locator('#rank-uncertainty').textContent()).includes('ensemble'));
    // Artifact-level leakage contract: no exact held-out endpoints, identities,
    // duplicate normalized formulas, or candidate lacking normalization evidence.
    const heldOut=new Set(natural.goals.map(goal=>`${goal.source}->${goal.target}`));
    assert(natural.candidates.every(candidate=>candidate.normal_form && candidate.source!==candidate.target && !heldOut.has(`${candidate.source}->${candidate.target}`)));
    assert.equal(new Set(natural.candidates.map(candidate=>candidate.normal_form)).size,natural.candidates.length);
    observations.push({case:'recorded_natural',candidates:natural.candidates.length,budget:natural.budget,metrics:natural.metrics,source_sha256:natural.verification.source_sha256});
    await page.locator('#assumptions-tab').click();
    assert.match(await page.locator('#axioms-list').textContent(),/propext/);
    assert.match(await page.locator('#exact-statement').textContent(),/List Nat/);
    await page.locator('#assumptions-tab').press('ArrowLeft');
    assert.equal(await page.locator('#proof-tab').getAttribute('aria-selected'),'true');
    await page.locator('#candidate-search').fill('no-such-consequence');
    assert.equal(await page.locator('#candidate-empty').isVisible(),true);
    await page.locator('#candidate-search').fill('');
    await page.locator('#example-select').selectOption('implications');
    await assertRendered(original);
    await checkBenchmark(originalBenchmark,'../artifacts/benchmark.json');
    assert.equal(await page.locator('#basis-type-details').isVisible(),false);
    assert.match(await page.locator('#basis-policy').textContent(),/Empty-axiom/);
    assert.equal(await page.locator('#import-declaration').isVisible(),false);
    assert.equal(await page.locator('#automation-control').isVisible(),false);
    await page.locator('#example-select').selectOption('natural');
    await assertRendered(natural);
    await checkBenchmark(naturalBenchmark,'../artifacts/natural/benchmark.json');
    // Loading a missing alternate example must retain both current context and
    // the matching benchmark, rather than leaving stale evidence from a new domain.
    await page.route('**/artifacts/demo.json',route=>route.fulfill({status:503,contentType:'application/json',body:'{}'}));
    await page.locator('#example-select').selectOption('implications');
    await page.waitForFunction(()=>document.querySelector('#notice').textContent.includes('Example loading failed'));
    assert.equal(await page.inputValue('#example-select'),'natural');
    await assertRendered(natural);
    await checkBenchmark(naturalBenchmark,'../artifacts/natural/benchmark.json');
    await page.unroute('**/artifacts/demo.json');
    const rerun = async (method,k) => {
      await page.locator('#policy-select').selectOption(method);
      await page.locator('#selection-budget').fill(String(k));
      const responsePromise=page.waitForResponse(response=>response.url().endsWith('/api/run') && response.request().method()==='POST');
      await page.locator('#run-button').click();
      const response=await responsePromise;assert(response.ok());
      const value=await response.json();
      await page.waitForFunction(()=>document.querySelector('#notice').textContent.startsWith('Local exploration complete.'));
      await assertRendered(value);
      assert.equal(response.request().postDataJSON().method,method);
      assert.equal(response.request().postDataJSON().select,k);
      assert.equal(value.verification.status,'kernel_verified');
      observations.push({case:`fresh_${method}_k${k}`,metrics:value.metrics,budget:value.budget,source_sha256:value.verification.source_sha256});
      return value;
    };
    const larger=await rerun('graph',3);
    assert(larger.metrics.augmented_solved<=natural.metrics.augmented_solved,'The larger-budget control should display its actual bounded-search tradeoff');
    await rerun('learned',natural.budget.selected_lemmas);
    assert.match(await page.locator('#rank-evidence-label').textContent(),/LEARNED/);
    assert.match(await page.locator('#rank-uncertainty').textContent(),/ensemble/);
    await rerun('graph',natural.budget.selected_lemmas);
    const importResponse=page.waitForResponse(response=>response.url().endsWith('/api/import-declaration'));
    await page.locator('#import-declaration').click();
    const importedResponse=await importResponse;assert(importedResponse.ok());
    const imported=await importedResponse.json();
    await page.waitForFunction(()=>document.querySelector('#notice').textContent.startsWith('Local exploration complete.'));
    await assertRendered(imported);
    assert.deepEqual(importedResponse.request().postDataJSON(),{name:'List.length_filter_le',budget:natural.budget.search_expansions_per_goal,select:natural.budget.selected_lemmas,method:'graph'});
    assert.equal(imported.natural_domain.imported_seed.name,'List.length_filter_le');
    assert.equal(imported.verification.status,'kernel_verified');
    observations.push({case:'fresh_registered_import',metrics:imported.metrics,source_sha256:imported.verification.source_sha256});
    const downloadPromise=page.waitForEvent('download');await page.locator('#export-json').click();
    await (await downloadPromise).saveAs(path.join(out,'downloaded-run.json'));
    const downloaded=JSON.parse(await fs.readFile(path.join(out,'downloaded-run.json'),'utf8'));
    assert.equal(crypto.createHash('sha256').update(downloaded.lean_source).digest('hex'),downloaded.verification.source_sha256);
    await page.route('**/api/run',route=>route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({error:'Intentional failure-path test'})}));
    await page.locator('#run-button').click();
    await page.waitForFunction(()=>document.querySelector('#notice').textContent.includes('Exploration failed'));
    await assertRendered(imported);
    await page.unroute('**/api/run');
    // A failed/unrun automation record must never receive a verified badge.
    await page.route('**/artifacts/natural/benchmark.json',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({...naturalBenchmark,automation_control:{...naturalBenchmark.automation_control,status:'not_run',solved:null}})}));
    await page.locator('#example-select').selectOption('implications');await assertRendered(original);
    await page.locator('#example-select').selectOption('natural');await assertRendered(natural);
    await checkBenchmark({...naturalBenchmark,automation_control:{status:'not_run'}},'../artifacts/natural/benchmark.json');
    await page.unroute('**/artifacts/natural/benchmark.json');
    await page.reload();await assertRendered(natural);
    await checkBenchmark(naturalBenchmark,'../artifacts/natural/benchmark.json');
    const sameWidth=()=>page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth);
    assert.equal(await sameWidth(),true);
    await page.screenshot({path:path.join(out,'desktop.png'),fullPage:true});
    await page.evaluate(()=>window.scrollTo({top:0,behavior:'instant'}));
    await page.screenshot({path:path.join(out,'desktop-viewport.png')});
    await page.setViewportSize({width:390,height:844});assert.equal(await sameWidth(),true);
    await page.screenshot({path:path.join(out,'mobile.png'),fullPage:true});
    await page.screenshot({path:path.join(out,'mobile-viewport.png')});
    assert.deepEqual(errors,[]);
    const report={url,checks:['default typed natural evidence','imported theorem exact audit','explicit propext trust policy','normalized candidate evidence','saved search/lemma/policy budgets','typed proof inspector','keyboard tabs','empty filtering','domain switching and matching benchmarks','failed example retention','real graph k3 budget comparison','real learned k1 rerun','real graph k1 rerun','real registered theorem import','complete JSON export/source hash','failed-run retention','automation verified-state guard','desktop/mobile overflow'],observations,pageErrors:errors,source_sha256:natural.verification.source_sha256};
    await fs.writeFile(path.join(out,'checks.json'),JSON.stringify(report,null,2)+'\n');
    console.log(JSON.stringify(report));
  } finally {await browser.close();}
})().catch(error=>{console.error(error);process.exit(1);});
