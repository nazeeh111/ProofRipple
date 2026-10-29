/* Current-source Mathlib LAB checks. Optional Playwright; loopback only.
   Does not generate study data. Run only after the canonical study is frozen. */
const {chromium}=require('playwright');
const fs=require('node:fs/promises');
const path=require('node:path');
const assert=require('node:assert/strict');
const crypto=require('node:crypto');
(async()=>{
  const url=process.env.PROOFRIPPLE_URL||'http://127.0.0.1:8769/lab/';
  assert(['127.0.0.1','localhost','[::1]'].includes(new URL(url).hostname),'Loopback URL required');
  const out=path.resolve(process.env.PROOFRIPPLE_BROWSER_OUT||'outputs/browser-v03-final');
  await fs.mkdir(out,{recursive:true});
  const browser=await chromium.launch({headless:true,executablePath:process.env.PROOFRIPPLE_CHROME});
  const errors=[],observations=[];
  try{
    const session=await browser.newContext({viewport:{width:1440,height:1080},acceptDownloads:true,reducedMotion:'reduce'});
    const page=await session.newPage();page.on('pageerror',e=>errors.push(e.message));
    const read=async relative=>{const r=await page.request.get(new URL(relative,url).href);assert(r.ok(),`${relative} unavailable`);return r.json();};
    const mathlib=await read('../artifacts/mathlib/demo.json');
    const benchmark=await read('../artifacts/mathlib/benchmark.json');
    assert.equal(mathlib.context.domain,'mathlib-set-lattice');
    assert.equal(mathlib.verification.status,'kernel_verified');
    assert.equal(benchmark.formal_verification.status,'kernel_verified');
    const assertRun=async value=>{
      await page.waitForFunction(title=>document.querySelector('#context-title').textContent===title,value.context.title||value.context.id);
      assert.equal(await page.locator('#candidate-count').textContent(),String(value.candidates.length));
      assert.equal(await page.locator('#verified-count').textContent(),String(value.candidates.filter(c=>c.status==='kernel_verified').length));
      assert.equal(await page.inputValue('#policy-select'),value.metrics.method);
      assert.equal(await page.inputValue('#selection-budget'),String(value.budget.selected_lemmas));
      assert.equal(await page.inputValue('#budget'),String(value.budget.search_expansions_per_goal??value.budget.search_expansions));
      assert.equal(await page.locator('#baseline-total').textContent(),`${value.metrics.baseline_solved}/${value.goals.length}`);
      assert.equal(await page.locator('#augmented-total').textContent(),`${value.metrics.augmented_solved}/${value.goals.length}`);
    };
    const checkProfile=async id=>{
      const profile=benchmark.profiles[id];
      await page.locator('#benchmark-profile').selectOption(id);
      assert.match(await page.locator('#benchmark-protocol').textContent(),new RegExp(`${profile.k} lemma cap.*${profile.budget} goal visits`));
      assert.equal(await page.locator('#benchmark-rows tr').count(),Object.keys(profile.summary).length);
      const rows=await page.locator('#benchmark-rows tr').allTextContents();
      const compact=v=>String(Number(Number(v).toFixed(2)));
      for(const metrics of Object.values(profile.summary))assert(rows.some(row=>row.includes(`${compact(metrics.total_solved)} / ${compact(metrics.total_goals)}`)));
      assert(!/NaN|undefined/.test(await page.locator('#benchmark-section').textContent()));
    };
    await page.goto(url);await assertRun(mathlib);
    await page.waitForSelector('#benchmark-section:not([hidden])');
    assert.equal(await page.locator('#policy-select option').count(),10);
    assert.match(await page.locator('#search-budget-label').textContent(),/Goal visits/);
    assert.match(await page.locator('#basis-name').textContent(),/inf_sup_left/);
    const meta=mathlib.mathlib_domain||mathlib.metadata?.mathlib_domain;
    assert.equal(await page.locator('#basis-type').textContent(),meta.imported_seed.statement);
    for(const axiom of meta.allowed_axioms)assert((await page.locator('#basis-policy').textContent()).includes(axiom));
    const walk=p=>[p,...(p.children||[]).flatMap(walk)];
    const first=mathlib.candidates.find(c=>c.id===mathlib.selected[0])||mathlib.candidates[0];
    const original=mathlib.context.candidates.find(c=>c.id===first.id);
    const tree=first.proof_ast||original.proof;
    assert.equal(await page.locator('#graph .proof-step').count(),walk(tree).length);
    assert.equal(await page.locator('#graph .proof-and-joint').count(),walk(tree).filter(p=>(p.children||[]).length>1).length);
    await page.locator('#graph .proof-step').first().focus();await page.keyboard.press('Enter');
    assert.match(await page.locator('#proof-step-detail').textContent(),/not a separately audited declaration/);
    if(Number.isInteger(first.score_stage))assert.match(await page.locator('#rank-context').textContent(),new RegExp(`Round ${first.score_stage+1}`));
    await page.locator('#assumptions-tab').click();assert.equal(await page.locator('#exact-statement').textContent(),first.statement);
    await page.locator('#assumptions-tab').press('ArrowLeft');assert.equal(await page.locator('#proof-tab').getAttribute('aria-selected'),'true');
    await page.locator('#candidate-search').fill('no-such-consequence');assert(await page.locator('#candidate-empty').isVisible());await page.locator('#candidate-search').fill('');
    await page.locator('#benchmark-section').evaluate(el=>el.open=true);
    assert.equal(await page.locator('#benchmark-profile option').count(),Object.keys(benchmark.profiles).length);
    for(const id of Object.keys(benchmark.profiles))await checkProfile(id);
    const primary=benchmark.aggregate_summary.contrasts.learned_minus_greedy_coverage;
    assert((await page.locator('#benchmark-primary').textContent()).includes((primary.mean_context_profile_solve_fraction_difference*100).toFixed(2)));
    for(const key of ['natural','implications','mathlib']){
      await page.locator('#example-select').selectOption(key);
      await page.waitForFunction(key=>document.querySelector('#example-select').value===key&&!document.querySelector('#run-button').disabled,key);
      if(key==='mathlib')await assertRun(mathlib);
      else assert(!(await page.locator('#basis-name').textContent()).includes('inf_sup_left'));
    }
    await page.route('**/artifacts/natural/demo.json',r=>r.fulfill({status:503,body:'{}',contentType:'application/json'}));
    await page.locator('#example-select').selectOption('natural');await page.waitForFunction(()=>document.querySelector('#notice').textContent.includes('Example loading failed'));
    await assertRun(mathlib);assert.equal(await page.inputValue('#example-select'),'mathlib');await page.unroute('**/artifacts/natural/demo.json');
    const rerun=async(method,k,budget)=>{
      await page.locator('#policy-select').selectOption(method);await page.locator('#selection-budget').fill(String(k));await page.locator('#budget').fill(String(budget));
      const response=page.waitForResponse(r=>r.url().endsWith('/api/run')&&r.request().method()==='POST');await page.locator('#run-button').click();
      const r=await response;assert(r.ok(),await r.text());const value=await r.json();await assertRun(value);assert.equal(value.verification.status,'kernel_verified');
      assert.equal(r.request().postDataJSON().method,method);assert.equal(r.request().postDataJSON().select,k);assert.equal(r.request().postDataJSON().budget,budget);
      observations.push({case:`live_${method}_k${k}_b${budget}`,metrics:value.metrics,source_sha256:value.verification.source_sha256});return value;
    };
    // One strong heuristic and one conditional model exercise the actual local API.
    await rerun('greedy_coverage',1,4);const live=await rerun('learned',3,8);
    assert.match(await page.locator('#rank-evidence-label').textContent(),/LEARNED/);assert.match(await page.locator('#rank-context').textContent(),/Round/);
    const download=page.waitForEvent('download');await page.locator('#export-json').click();const file=await download;await file.saveAs(path.join(out,'downloaded-run.json'));
    const exported=JSON.parse(await fs.readFile(path.join(out,'downloaded-run.json'),'utf8'));assert.deepEqual(exported.metrics,live.metrics);
    assert.equal(crypto.createHash('sha256').update(exported.lean_source).digest('hex'),exported.verification.source_sha256);
    const proofDownload=page.waitForEvent('download');await page.locator('#export-proof').click();await(await proofDownload).saveAs(path.join(out,'downloaded-proof.lean'));
    await page.route('**/api/run',r=>r.fulfill({status:503,contentType:'application/json',body:JSON.stringify({error:'Intentional failure-path check'})}));await page.locator('#run-button').click();await page.waitForFunction(()=>document.querySelector('#notice').textContent.includes('Exploration failed'));await assertRun(live);await page.unroute('**/api/run');
    await page.locator('#import-file').setInputFiles({name:'recorded-run.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(mathlib))});await assertRun(mathlib);assert.match(await page.locator('#notice').textContent(),/file-reported.*not been rechecked/);assert.equal(await page.locator('#benchmark-section').isVisible(),false);
    await page.locator('#import-file').setInputFiles({name:'invalid.json',mimeType:'application/json',buffer:Buffer.from('{')});await page.waitForFunction(()=>document.querySelector('#notice').textContent.includes('Import failed'));await assertRun(mathlib);
    await page.locator('#import-file').setInputFiles({name:'malformed-run.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify({...mathlib,candidates:[null]}))});await page.waitForFunction(()=>document.querySelector('#notice').textContent.includes('Import failed'));await assertRun(mathlib);
    // A file with no completed automation audit must not show a verified control.
    await page.route('**/artifacts/mathlib/benchmark.json',r=>r.fulfill({status:200,contentType:'application/json',body:JSON.stringify({...benchmark,automation_control:{status:'not_run',solved:null,total:null}})}));
    await page.reload();await assertRun(mathlib);await page.waitForSelector('#benchmark-section:not([hidden])');assert.equal(await page.locator('#automation-control').isVisible(),false);await page.unroute('**/artifacts/mathlib/benchmark.json');
    await page.reload();await assertRun(mathlib);await page.waitForSelector('#benchmark-section:not([hidden])');await page.evaluate(()=>scrollTo(0,0));
    const noOverflow=()=>page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth);
    for(const viewport of [{width:1440,height:1080},{width:390,height:844}]){
      await page.setViewportSize(viewport);assert(await noOverflow(),`${viewport.width}px overflow`);
      const label=viewport.width===1440?'desktop':'mobile';await page.screenshot({path:path.join(out,`${label}.png`),fullPage:true});await page.screenshot({path:path.join(out,`${label}-viewport.png`)});
      await page.locator('#benchmark-section').evaluate(el=>el.open=true);assert(await noOverflow());await page.locator('#formal-basis').evaluate(el=>el.open=true);assert(await noOverflow());
      await page.locator('#benchmark-section').evaluate(el=>el.open=false);await page.locator('#formal-basis').evaluate(el=>el.open=false);
    }
    assert.deepEqual(errors,[]);
    const sources={};for(const file of ['lab/index.html','lab/style.css','lab/app.js'])sources[file]=crypto.createHash('sha256').update(await fs.readFile(file)).digest('hex');
    const report={url,checks:['canonical kernel evidence','actual AST/AND graph','step scope and keyboard','exact statement/axioms','stage-dependent scores','all benchmark profile totals','primary paired interval','three domains','failed example retention','real budget/policy reruns','JSON/source-hash and Lean downloads','failed rerun retention','file-reported import and malformed JSON retention','desktop/mobile overflow'],observations,pageErrors:errors,artifact_source_sha256:mathlib.verification.source_sha256,benchmark_outcomes_sha256:benchmark.outcomes_sha256,sources};
    await fs.writeFile(path.join(out,'checks.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
