// Minimal Chrome DevTools Protocol driver: navigate, wait, dump text + links.
import { spawn } from 'node:child_process';
import fs from 'node:fs';

const URL_ARG = process.argv[2];
const PORT = 9333;
const OUT = process.argv[3] || '/tmp/trip-tools/out.json';
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PROFILE = '/tmp/trip-tools/profile-' + Date.now();

const chrome = spawn(CHROME, [
  '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
  '--disable-extensions', '--mute-audio',
  `--remote-debugging-port=${PORT}`, `--user-data-dir=${PROFILE}`,
  '--window-size=1400,1800', 'about:blank',
], { stdio: 'ignore', detached: false });

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

async function getJSON(path, method = 'GET') {
  const res = await fetch(`http://127.0.0.1:${PORT}${path}`, { method });
  return res.json();
}

let targets;
for (let i = 0; i < 60; i++) {
  try { targets = await getJSON('/json/list'); if (targets.length) break; } catch { }
  await sleep(250);
}
if (!targets || !targets.length) { chrome.kill(); throw new Error('Chrome CDP not ready'); }

const page = targets.find(t => t.type === 'page');
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });

let id = 0;
const pending = new Map();
ws.onmessage = (ev) => {
  const msg = JSON.parse(ev.data);
  if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); }
};
function send(method, params = {}) {
  const mid = ++id;
  return new Promise((resolve) => {
    pending.set(mid, resolve);
    ws.send(JSON.stringify({ id: mid, method, params }));
  });
}

async function evaluate(expr, awaitPromise = false) {
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise });
  if (r.result?.exceptionDetails) return { error: JSON.stringify(r.result.exceptionDetails) };
  return r.result?.result?.value;
}

await send('Page.enable');
await send('Runtime.enable');
await send('Page.navigate', { url: URL_ARG });
await sleep(9000);

// Scroll the side panel to force lazy-loaded list items.
const scrollScript = `(async () => {
  const panels = Array.from(document.querySelectorAll('div[role="main"] div, div[role="feed"], div[aria-label]'))
    .filter(el => el.scrollHeight > el.clientHeight + 50 && el.clientHeight > 200);
  const seen = new Set();
  let els = panels.slice(0, 4);
  for (let pass = 0; pass < 12; pass++) {
    for (const el of els) { el.scrollTop = el.scrollHeight; }
    await new Promise(r => setTimeout(r, 900));
  }
  return els.length;
})()`;
const scrolled = await evaluate(scrollScript, true);
await sleep(3000);

const text = await evaluate('document.body.innerText');
const links = await evaluate(`Array.from(document.querySelectorAll('a')).map(a => a.href).filter(h => /maps|place|search/.test(h)).slice(0, 400)`);
const html = await evaluate('document.documentElement.outerHTML.length');

fs.writeFileSync(OUT, JSON.stringify({ url: URL_ARG, finalUrl: await evaluate('location.href'), scrolled, htmlLength: html, text, links }, null, 2));
console.log('wrote', OUT, 'htmlLen', html, 'links', (links || []).length);

ws.close();
chrome.kill();
process.exit(0);
