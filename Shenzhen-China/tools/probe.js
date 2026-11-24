(() => {
  const target = "Ping'an International Financial Center";
  const leaves = [...document.querySelectorAll('div,span,a')].filter(e => e.children.length === 0 && (e.textContent||'').trim() === target);
  if (!leaves.length) return { found: false };
  const chain = [];
  let el = leaves[0];
  for (let i = 0; i < 8 && el; i++) {
    chain.push({ tag: el.tagName, role: el.getAttribute('role'), label: el.getAttribute('aria-label'),
      cls: (el.className || '').toString().slice(0,80), href: el.getAttribute('href'), jsaction: (el.getAttribute('jsaction')||'').slice(0,60) });
    el = el.parentElement;
  }
  return { found: true, count: leaves.length, chain };
})()
