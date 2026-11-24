(() => {
  const t = document.body.innerText;
  return { url: location.href, len: t.length, text: t.slice(0, 1500) };
})()
