(() => {
  const m = location.href.match(/!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)/);
  const m2 = location.href.match(/@(-?\d+\.\d+),(-?\d+\.\d+),(\d+\.?\d*)z/);
  return { href: location.href, urlCoord: m ? [Number(m[1]), Number(m[2])] : null,
           center: m2 ? [Number(m2[1]), Number(m2[2]), m2[3]] : null };
})()
