// Search Google Maps for a query, click the first place result, print its URL + coords.
import { spawn } from 'node:child_process';

const QUERY = process.argv[2];
const PORT = 9377;
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

const chrome = spawn(CHROME, ['--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
  '--disable-extensions', '--mute-audio', `--remote-debugging-port=${PORT}`,
  '--user-data-dir=/tmp/trip-tools/profile-search-' + Date.now(),
  '--window-size=1400,1800', 'about:blank'], { stdio: 'ignore' });

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
const ev = async (expr) => {
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
  return r.result?.result?.value;
};
await send('Page.enable'); await send('Runtime.enable');
await send('Page.navigate', { url: `https://www.google.com/maps/search/${encodeURIComponent(QUERY)}?hl=en` });
await sleep(10000);

const firstHref = await ev(`(() => {
  const a = Array.from(document.querySelectorAll('a[href*="/maps/place/"]'))[0];
  if (a) return a.href;
  const b = Array.from(document.querySelectorAll('button.fHEb6e'))[0];
  if (b) { b.click(); return 'clicked'; }
  return null;
})()`);
await sleep(4000);
const out = await ev(`(() => {
  const m = location.href.match(/!3d(-?\\d+\\.\\d+)!4d(-?\\d+\\.\\d+)/);
  return { firstHref: ${JSON.stringify(firstHref)}, href: location.href,
    coords: m ? [Number(m[1]), Number(m[2])] : null,
    title: document.title };
})()`);
console.log(JSON.stringify(out, null, 2));
ws.close(); chrome.kill(); process.exit(0);
