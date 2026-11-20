// kit world: the ground along every kit ramp and overpass street follows the kit heights (no steps, nothing under the deck)
(async()=>{let worst=0,where="",n=0;
  for(const e of EDGES){if(!e.kitZ)continue;for(let u=8;u<e.L-8;u+=6){const p=eAt(e,u),z=ez(e,u);GREF=z;const g=groundAt(p.x,p.y);const d=Math.abs(g.h-z);n++;if(d>worst){worst=d;where=`${e.type} ${p.x.toFixed(0)},${p.y.toFixed(0)} want ${z.toFixed(2)} got ${g.h.toFixed(2)} ${g.kind}`}}}
  return `kit heights: ${n} samples, worst ${worst.toFixed(2)} m at ${where}`})()
