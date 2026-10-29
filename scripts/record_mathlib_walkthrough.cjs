/* Silent recording of the real Mathlib LAB artifact. No experiment is run,
   invented frame is inserted, or playback speed changed. Keep raw video. */
const {chromium}=require('playwright');
const fs=require('node:fs/promises');
const path=require('node:path');
const crypto=require('node:crypto');
const assert=require('node:assert/strict');
(async()=>{
  const url=process.env.PROOFRIPPLE_URL||'http://127.0.0.1:8769/lab/';
  const out=path.resolve(process.env.PROOFRIPPLE_VIDEO_OUT||'outputs/walkthrough-v03-final');
  assert(['127.0.0.1','localhost','[::1]'].includes(new URL(url).hostname),'Loopback URL required');
  await fs.mkdir(out,{recursive:true});
  const browser=await chromium.launch({headless:true,executablePath:process.env.PROOFRIPPLE_CHROME});
  const context=await browser.newContext({viewport:{width:1440,height:1000},recordVideo:{dir:out,size:{width:1440,height:1000}},reducedMotion:'reduce'});
  const events=[],errors=[];let raw,run,benchmark,elapsed;
  try{
    const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
    const start=performance.now();const mark=action=>events.push({action,elapsed_ms:Math.round(performance.now()-start)});
    const at=async time=>{const left=time-(performance.now()-start);if(left>0)await page.waitForTimeout(left);};
    const read=async relative=>{const response=await page.request.get(new URL(relative,url).href);assert(response.ok());return response.json();};
    run=await read('../artifacts/mathlib/demo.json');benchmark=await read('../artifacts/mathlib/benchmark.json');
    assert.equal(run.verification.status,'kernel_verified');assert.equal(benchmark.formal_verification.status,'kernel_verified');
    await page.goto(url);await page.waitForFunction(title=>document.querySelector('#context-title').textContent===title,run.context.title||run.context.id);await page.waitForSelector('#benchmark-section:not([hidden])');
    mark('Loaded actual saved Mathlib run and recorded Lean audit');
    await at(2200);await page.locator('#graph .proof-step').first().click();mark('Selected actual proof AST step; scope explicitly shown');
    await at(5200);await page.locator('#assumptions-tab').click();await page.locator('#inspector-heading').scrollIntoViewIfNeeded();mark('Inspected exact consequence statement, dependencies and axiom audit');
    await at(8200);await page.locator('#experiments-heading').scrollIntoViewIfNeeded();await page.locator('#goal-list details').first().locator('summary').click();mark('Compared real bounded-search witnesses');
    await at(11000);await page.locator('#formal-basis').evaluate(el=>el.open=true);await page.locator('#basis-type-details').evaluate(el=>el.open=true);await page.locator('#formal-basis').scrollIntoViewIfNeeded();mark('Inspected imported Mathlib theorem, pinned revision and allowed axioms');
    await at(14300);await page.locator('#benchmark-section').evaluate(el=>el.open=true);await page.locator('#benchmark-section').scrollIntoViewIfNeeded();mark('Inspected complete recorded policy comparison and primary paired result');
    await at(17500);const ids=Object.keys(benchmark.profiles);const next=ids.find(id=>id!==(benchmark.summary_profile||'k3_b8'));if(next)await page.locator('#benchmark-profile').selectOption(next);mark('Changed budget profile; repeated-query denominator remains explicit');
    await at(20500);raw=await page.video().path();elapsed=Math.round(performance.now()-start);assert.deepEqual(errors,[]);
  }finally{await context.close();await browser.close();}
  const sources={};for(const file of ['lab/index.html','lab/style.css','lab/app.js'])sources[file]=crypto.createHash('sha256').update(await fs.readFile(file)).digest('hex');
  const metadata={raw,url,viewport:'1440x1000',audio:false,kind:'Actual browser interactions with saved Mathlib set-lattice artifact; not a live verification recording',target_capture_ms:20500,interaction_elapsed_ms:elapsed,events,pageErrors:errors,sources,artifact:{id:run.context.id,candidates:run.candidates.length,metrics:run.metrics,budget:run.budget,source_sha256:run.verification.source_sha256},benchmark_outcomes_sha256:benchmark.outcomes_sha256,preservation:'Raw Playwright video retained. Separate encoding/playback verification required.'};
  await fs.writeFile(path.join(out,'recording.json'),JSON.stringify(metadata,null,2)+'\n');console.log(JSON.stringify(metadata));
})().catch(e=>{console.error(e);process.exit(1);});
