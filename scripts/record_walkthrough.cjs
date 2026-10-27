/* Authentic silent LAB walkthrough of the currently loaded natural artifact.
   Optional Playwright dependency. Use a fresh output directory; no synthetic
   frames, invented proof results, or speed changes are added here. */
const { chromium } = require('playwright');
const fs = require('node:fs/promises');
const path = require('node:path');
const assert = require('node:assert/strict');
(async () => {
  const out=path.resolve(process.env.PROOFRIPPLE_VIDEO_OUT || 'outputs/walkthrough-v02-final');
  const url=process.env.PROOFRIPPLE_URL || 'http://127.0.0.1:8765/lab/';
  assert(['127.0.0.1','localhost','[::1]'].includes(new URL(url).hostname),'Use a loopback workbench URL');
  await fs.mkdir(out,{recursive:true});
  const browser=await chromium.launch({headless:true,executablePath:process.env.PROOFRIPPLE_CHROME});
  const context=await browser.newContext({viewport:{width:1440,height:1000},recordVideo:{dir:out,size:{width:1440,height:1000}}});
  let raw,run;
  const events=[],errors=[];
  try {
    const page=await context.newPage();page.on('pageerror',error=>errors.push(error.message));
    const start=performance.now();
    const mark=action=>events.push({action,elapsed_ms:Math.round(performance.now()-start)});
    const at=async milliseconds=>{const remaining=milliseconds-(performance.now()-start);if(remaining>0)await page.waitForTimeout(remaining);};
    await page.goto(url);
    const response=await page.request.get(new URL('../artifacts/natural/demo.json',url).href);
    assert(response.ok(),'Generate the natural demo before recording');run=await response.json();
    const expectedVerified=run.candidates.filter(candidate=>candidate.status==='kernel_verified').length;
    await page.waitForFunction(count=>document.querySelector('#verified-count').textContent===String(count),expectedVerified);
    assert.equal(run.verification.status,'kernel_verified');
    assert.equal(await page.inputValue('#policy-select'),run.metrics.method);
    assert.equal(await page.inputValue('#selection-budget'),String(run.budget.selected_lemmas));
    await page.waitForSelector('#benchmark-section:not([hidden])');mark('Loaded actual recorded natural run');
    await at(1800);
    await page.locator('#basis-heading').scrollIntoViewIfNeeded();
    await page.locator('#basis-type-details summary').click();mark('Inspected imported theorem exact statement');
    await at(4700);
    await page.locator('#basis-type-details summary').click();
    await page.locator('#graph-heading').scrollIntoViewIfNeeded();mark('Traced actual capacity theorem graph');
    await at(7300);
    if(run.candidates.length>1)await page.locator('#candidate-rows tr').nth(1).locator('button').first().click();
    await page.locator('#assumptions-tab').click();
    await page.locator('#inspector-heading').scrollIntoViewIfNeeded();mark('Inspected typed consequence and transitive axioms');
    await at(10400);
    await page.locator('#experiments-heading').scrollIntoViewIfNeeded();
    await page.locator('#goal-list details').first().locator('summary').click();mark('Compared recorded restricted search paths');
    await at(13300);
    await page.locator('#benchmark-section').scrollIntoViewIfNeeded();mark('Inspected actual held-out ranking comparison');
    await at(16300);
    if(await page.locator('#automation-control').isVisible()) {await page.locator('#automation-control').scrollIntoViewIfNeeded();mark('Inspected verified strong automation control');}
    await at(19000);
    raw=await page.video().path();
    assert.deepEqual(errors,[]);
  } finally {await context.close();await browser.close();}
  const metadata={raw,url,viewport:'1440x1000',audio:false,kind:'Actual browser interactions with recorded Lean-certified natural list domain; not a live verification recording',target_capture_ms:19000,events,pageErrors:errors,artifact:{id:run.context.id,candidates:run.candidates.length,metrics:run.metrics,budget:run.budget,source_sha256:run.verification.source_sha256,imported_theorem:run.natural_domain?.imported_seed?.name},preservation:'Raw Playwright video retained; encoding and playback checks performed separately.'};
  await fs.writeFile(path.join(out,'recording.json'),JSON.stringify(metadata,null,2)+'\n');console.log(JSON.stringify(metadata));
})().catch(error=>{console.error(error);process.exit(1);});
