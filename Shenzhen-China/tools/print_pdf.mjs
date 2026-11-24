// Print a local HTML file to PDF via CDP (reliable, unlike --print-to-pdf with timers).
import { spawn } from 'node:child_process';
import fs from 'node:fs';

const URL_ARG = process.argv[2];
const OUT = process.argv[3];
const PORT = 9411;
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

const chrome = spawn(CHROME, ['--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
  `--remote-debugging-port=${PORT}`, '--user-data-dir=/tmp/trip-tools/profile-pdf-' + Date.now(),
  '--window-size=900,1400', 'about:blank'], { stdio: 'ignore' });

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

await send('Page.enable');
await send('Page.navigate', { url: URL_ARG });
await sleep(4000);
const theme = process.env.THEME || 'light';
await send('Runtime.evaluate', { expression: `document.documentElement.dataset.theme='${theme}'` });
await sleep(1500);
const r = await Promise.race([
  send('Page.printToPDF', {
  printBackground: true, preferCSSPageSize: true, marginTop: 0, marginBottom: 0,
  marginLeft: 0, marginRight: 0, paperWidth: 8.27, paperHeight: 11.69,
  }),
  new Promise((_, rej) => setTimeout(() => rej(new Error('printToPDF timeout')), 90000)),
]);
fs.writeFileSync(OUT, Buffer.from(r.result.data, 'base64'));
console.log('wrote', OUT, fs.statSync(OUT).size, 'bytes');
ws.close(); chrome.kill(); process.exit(0);
