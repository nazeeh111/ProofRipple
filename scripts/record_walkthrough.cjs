/* Authentic, silent LAB walkthrough. Optional Playwright development dependency.
   Re-run with an empty output directory; raw video is preserved. */
const { chromium } = require('playwright');
const fs = require('node:fs/promises');
const path = require('node:path');
(async () => {
  const out=path.resolve(process.env.PROOFRIPPLE_VIDEO_OUT || 'outputs/walkthrough');
  await fs.mkdir(out,{recursive:true});
  const browser=await chromium.launch({headless:true,executablePath:process.env.PROOFRIPPLE_CHROME});
  const context=await browser.newContext({viewport:{width:1440,height:1000},recordVideo:{dir:out,size:{width:1440,height:1000}}});
  const page=await context.newPage();
  await page.goto(process.env.PROOFRIPPLE_URL || 'http://127.0.0.1:8765/lab/');
  await page.waitForFunction(()=>document.querySelector('#verified-count').textContent==='19');
  await page.waitForTimeout(2500);
  await page.locator('#graph-heading').scrollIntoViewIfNeeded();
  await page.waitForTimeout(2000);
  await page.locator('#candidate-rows tr').nth(1).locator('button').first().click();
  await page.waitForTimeout(2000);
  await page.locator('#assumptions-tab').click();
  await page.waitForTimeout(2500);
  await page.locator('#experiments-heading').scrollIntoViewIfNeeded();
  await page.waitForTimeout(2500);
  await page.locator('#goal-list details').first().locator('summary').click();
  await page.waitForTimeout(2000);
  await page.locator('#benchmark-section').scrollIntoViewIfNeeded();
  await page.waitForTimeout(3000);
  const raw=await page.video().path();
  await context.close();
  await browser.close();
  await fs.writeFile(path.join(out,'recording.json'),JSON.stringify({raw,viewport:'1440x1000',audio:false,kind:'Real browser interactions with recorded Lean-certified run; not a live verification recording'},null,2));
  console.log(raw);
})().catch(error=>{console.error(error);process.exit(1);});
