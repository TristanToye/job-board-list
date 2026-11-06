#!/usr/bin/env node
// Read one public page in a headless browser and print JSON: {url, status, title, blocked, text, links}.
// Usage: node scripts/browse.js URL
// It uses the browser as it is. It does not hide itself, solve challenges or log in. If a page shows a
// challenge or refuses access, it reports blocked: true and the caller should record the page as unverifiable.
const { chromium } = require('playwright');
(async () => {
  const url = process.argv[2];
  if (!url || !/^https?:\/\//.test(url)) { console.log(JSON.stringify({ error: 'usage: node scripts/browse.js URL' })); process.exit(2); }
  const b = await chromium.launch(); const p = await (await b.newContext({ locale: 'en-US' })).newPage();
  const out = { url, status: null, title: '', blocked: false, text: '', links: [] };
  try {
    const r = await p.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    out.status = r ? r.status() : null; await p.waitForTimeout(2000);
    out.title = (await p.title()).slice(0, 160);
    out.text = (await p.evaluate(() => document.body ? document.body.innerText : '')).replace(/\n{3,}/g, '\n\n').slice(0, 40000);
    out.links = await p.evaluate(() => Array.from(document.querySelectorAll('a[href]')).slice(0, 120).map(a => ({ t: (a.innerText || '').trim().slice(0, 60), h: a.href })).filter(x => x.t));
    out.final_url = p.url();
    out.blocked = (out.status >= 400) || /verify you are human|captcha|access denied|just a moment|unusual traffic|attention required|blocked/i.test(out.title + ' ' + out.text.slice(0, 500));
  } catch (e) { out.error = String(e.message).split('\n')[0].slice(0, 160); out.blocked = true; }
  await b.close(); console.log(JSON.stringify(out));
})();
