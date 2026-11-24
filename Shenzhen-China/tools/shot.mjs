// Screenshot a URL after it settles (CDP Page.captureScreenshot).
import { spawn } from 'node:child_process';
import fs from 'node:fs';

const URL_ARG = process.argv[2];
const OUT = process.argv[3] || 'out/shot.png';
const WAIT = Number(process.argv[4] || 9000);
const PORT = 9399;
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

const chrome = spawn(CHROME, ['--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
  '--disable-extensions', '--mute-audio', `--remote-debugging-port=${PORT}`,
  '--user-data-dir=/tmp/trip-tools/profile-shot-' + Date.now(),
  '--window-size=' + (process.env.W||900) + ',' + (process.env.H||1300), 'about:blank'], { stdio: 'ignore' });

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
await send('Emulation.setDeviceMetricsOverride', { width: Number(process.env.W||900), height: Number(process.env.H||1300), deviceScaleFactor: 1, mobile: false });
await send('Page.navigate', { url: URL_ARG });
await sleep(WAIT);
const r = await send('Page.captureScreenshot', { format: 'png' });
fs.writeFileSync(OUT, Buffer.from(r.result.data, 'base64'));
const txt = await send('Runtime.evaluate', { expression: 'document.body.innerText.slice(0,400)', returnByValue: true });
console.log('saved', OUT);
console.log('TEXT:', (txt.result?.result?.value || '').replace(/\n+/g, ' | ').slice(0, 400));
ws.close(); chrome.kill(); process.exit(0);
