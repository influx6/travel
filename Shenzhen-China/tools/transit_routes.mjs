// Pull Google Maps directions (transit + driving) from the hotel to each place.
import { spawn } from 'node:child_process';
import fs from 'node:fs';

const ORIGIN = process.argv[2] || '22.52147,114.05994';
const PLACES = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const OUT = process.argv[4] || './out/routes.json';
const PORT = 9388;
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

const chrome = spawn(CHROME, ['--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
  '--disable-extensions', '--mute-audio', `--remote-debugging-port=${PORT}`,
  '--user-data-dir=/tmp/trip-tools/profile-routes-' + Date.now(),
  '--window-size=1400,2000', 'about:blank'], { stdio: 'ignore' });

let targets;
for (let i = 0; i < 80; i++) {
  try { targets = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json(); if (targets.length) break; } catch { }
  await sleep(250);
}
const page = targets.find(t => t.type === 'page');
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
let id = 0; const pending = new Map();
ws.onmessage = (e) => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } };
const send = (method, params = {}) => new Promise((resolve) => { const mid = ++id; pending.set(mid, resolve); ws.send(JSON.stringify({ id: mid, method, params })); });
async function ev(expr) {
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
  if (r.result?.exceptionDetails) return null;
  return r.result?.result?.value;
}
const waitFor = async (expr, timeoutMs = 25000) => {
  const t0 = Date.now();
  while (Date.now() - t0 < timeoutMs) { if (await ev(expr)) return true; await sleep(500); }
  return false;
};

await send('Page.enable'); await send('Runtime.enable');

const results = [];
for (const p of PLACES) {
  const [lat, lng] = p.coords;
  const rec = { name: p.name, transit: null, driving: null };

  for (const mode of (process.env.MODES || 'transit,driving').split(',')) {
    await send('Page.navigate', {
      url: `https://www.google.com/maps/dir/?api=1&origin=${ORIGIN}&destination=${lat},${lng}&travelmode=${mode}&hl=en`,
    });
    await sleep(9000);
    // Expand the first route's step list.
    await ev(`(() => {
      const btns = Array.from(document.querySelectorAll('button, div[role="button"]'));
      const d = btns.find(b => (b.innerText || '').trim() === 'Details');
      if (d) { d.click(); return true; }
      return false;
    })()`);
    await sleep(3500);
    const text = await ev('document.body.innerText');
    rec[mode] = (text || '').slice(0, 2500);
  }
  results.push(rec);
  console.error(`${p.name.slice(0, 40)} captured`);
}

fs.writeFileSync(OUT, JSON.stringify(results, null, 2));
console.error('wrote', OUT);
ws.close(); chrome.kill(); process.exit(0);
