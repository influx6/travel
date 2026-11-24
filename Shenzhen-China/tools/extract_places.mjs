// Extract every place from a shared Google Maps list: click each list item,
// wait until a NEW place URL appears, capture name/coords/placeId, then go back.
import { spawn } from 'node:child_process';
import fs from 'node:fs';

const SHARE_URL = process.argv[2];
const OUT = process.argv[3] || './out/places_raw.json';
const PORT = 9366;
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PROFILE = '/tmp/trip-tools/profile-extract2-' + Date.now();
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

const chrome = spawn(CHROME, [
  '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
  '--disable-extensions', '--mute-audio',
  `--remote-debugging-port=${PORT}`, `--user-data-dir=${PROFILE}`,
  '--window-size=1400,1800', 'about:blank',
], { stdio: 'ignore' });

let targets;
for (let i = 0; i < 80; i++) {
  try { targets = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json(); if (targets.length) break; } catch { }
  await sleep(250);
}
const page = targets.find(t => t.type === 'page');
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });

let id = 0;
const pending = new Map();
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
};
const send = (method, params = {}) => new Promise((resolve) => {
  const mid = ++id; pending.set(mid, resolve);
  ws.send(JSON.stringify({ id: mid, method, params }));
});
async function ev(expr, awaitPromise = false) {
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise });
  if (r.result?.exceptionDetails) throw new Error(r.result.exceptionDetails.exception?.description || r.result.exceptionDetails.text);
  return r.result?.result?.value;
}
const waitFor = async (expr, timeoutMs = 20000) => {
  const t0 = Date.now();
  while (Date.now() - t0 < timeoutMs) {
    try { if (await ev(expr)) return true; } catch { }
    await sleep(400);
  }
  return false;
};

await send('Page.enable');
await send('Runtime.enable');
await send('Page.navigate', { url: SHARE_URL });

if (!await waitFor(`!!document.querySelector('button.fHEb6e')`)) {
  console.error('list never appeared'); process.exit(1);
}
await sleep(2500);

// Capture list metadata (rating + category subtitle) straight from the panel.
const items = await ev(`
  Array.from(document.querySelectorAll('button.fHEb6e')).map(b => {
    const t = b.innerText.split('\\n').map(s => s.trim()).filter(Boolean);
    return { name: t[0] || '', meta: t.slice(1).join(' | ') };
  })
`);
console.error('items:', items.length);

const results = [];
let prevHref = await ev('location.href');

for (let i = 0; i < items.length; i++) {
  const clicked = await ev(`(() => {
    const btns = Array.from(document.querySelectorAll('button.fHEb6e'));
    const b = btns[${i}];
    if (!b) return false;
    b.scrollIntoView({ block: 'center' });
    b.click();
    return true;
  })()`);
  if (!clicked) { results.push({ ...items[i], error: 'button missing' }); continue; }

  const fresh = await waitFor(`(() => {
    const h = location.href;
    return /\\/maps\\/place\\//.test(h) && h !== ${JSON.stringify(prevHref)};
  })()`, 25000);
  await sleep(1800);

  const href = await ev('location.href');
  const panel = await ev(`(() => {
    const clean = s => (s || '').replace(/^Address:\\s*/, '').trim();
    const addr = document.querySelector('button[data-item-id="address"]');
    const rating = document.querySelector('div.F7nice span[aria-hidden="true"]');
    const cat = document.querySelector('button[jsaction*="category"]');
    const h1 = document.querySelector('h1');
    return {
      urlName: decodeURIComponent((location.href.match(/\\/maps\\/place\\/([^/]+)/)||[])[1]||'').replace(/\\+/g,' '),
      h1: h1 ? h1.textContent.trim() : null,
      address: addr ? clean(addr.getAttribute('aria-label') || addr.innerText) : null,
      rating: rating ? rating.textContent.trim() : null,
      category: cat ? cat.textContent.trim() : null,
      coords: (location.href.match(/!3d(-?\\d+\\.\\d+)!4d(-?\\d+\\.\\d+)/)||[]).slice(1).map(Number),
      placeId: (location.href.match(/!1s(0x[0-9a-f]+:0x[0-9a-f]+)/)||[])[1] || null,
    };
  })()`);

  results.push({ ...items[i], fresh, href, ...panel });
  console.error(`${i + 1}. ${items[i].name.slice(0, 45)} -> ${panel.urlName.slice(0, 45)} [${panel.coords}]`);
  prevHref = href;

  await ev('history.back()');
  await waitFor(`!!document.querySelector('button.fHEb6e') && !/\\/maps\\/place\\//.test(location.href)`, 20000);
  await sleep(1500);
}

fs.mkdirSync('./out', { recursive: true });
fs.writeFileSync(OUT, JSON.stringify(results, null, 2));
console.error('wrote', OUT, results.length);
ws.close();
chrome.kill();
process.exit(0);
