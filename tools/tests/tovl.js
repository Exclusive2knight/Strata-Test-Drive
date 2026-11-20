// overlapping roads: points on one road's pavement that lie on another road's pavement at the same level, away from any junction they share
(async()=>{const hits=[],seen=new Set();const near=(n,x,y)=>Math.hypot(n.x-x,n.y-y)<(n.pr||0)+hwOf0(n)+6;
  function hwOf0(n){let w=0;for(const {e} of n.E)w=Math.max(w,e.W||0);return w}
  const G=new Map(),C=60;for(const e of EDGES){for(let u=0;u<=e.L;u+=20){const p=eAt(e,u),k=Math.floor(p.x/C)+","+Math.floor(p.y/C);if(!G.has(k))G.set(k,new Set());G.get(k).add(e)}}
  for(const e of EDGES){const hw=e.m>0?e.m/2+e.n*LANE:e.n*LANE*(e.ow?0.5:1);for(let u=4;u<e.L-4;u+=4){const p=eAt(e,u),z=ez(e,u);
    for(const sd of [-1,1]){const q=ePt(e,u,sd*(Math.max(0,hw-0.4)));const k=Math.floor(q[0]/C)+","+Math.floor(q[1]/C);const S=G.get(k);if(!S)continue;
      for(const f of S){if(f===e)continue;if(f.a===e.a||f.a===e.b||f.b===e.a||f.b===e.b)continue;   /* roads that meet at a junction (ramps at their gore, merges) are meant to touch */
        if(f.name&&f.name===e.name)continue;
        const pp=eProj(f,q[0],q[1]);if(pp.u<2||pp.u>f.L-2)continue;const fh=f.m>0?f.m/2+f.n*LANE:f.n*LANE*(f.ow?0.5:1);if(f.m>0&&Math.abs(pp.t)<f.m/2-0.3)continue;
        if(Math.abs(pp.t)>fh-0.3)continue;if(Math.abs(ez(f,pp.u)-z)>2.5)continue;if([f.a,f.b,e.a,e.b].some(n=>near(n,q[0],q[1])))continue;
        const key=[Math.min(e.i,f.i),Math.max(e.i,f.i)].join("-");if(seen.has(key))continue;seen.add(key);
        hits.push(`${e.type}:${e.name}#${e.i} x ${f.type}:${f.name}#${f.i} at ${q[0].toFixed(0)},${q[1].toFixed(0)}`)}}}}
  return hits.length+" overlapping pairs\n"+hits.join("\n")})()
