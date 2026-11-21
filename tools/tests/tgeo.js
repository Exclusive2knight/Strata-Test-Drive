// ramps, flyovers, freeways and bridges: too-steep grades, sharp crests/dips, steps where roads join, and the drivable floor not matching the road
(async()=>{const out=[],F={grade:[],kink:[],join:[],floor:[]};const lim=e=>e.type==="xway"?0.06:e.type==="ramp"?0.08:0.10;
 const nm=e=>(e.name||e.type)+"#"+EDGES.indexOf(e);
 const R=EDGES.filter(e=>e.type==="xway"||e.type==="ramp"||e.zp||e.hz);
 for(const e of R){let gmax=0,ug=0,kmax=0,uk=0;for(let u=0;u+4<=e.L;u+=2){const g=(ez(e,u+4)-ez(e,u))/4;if(Math.abs(g)>gmax){gmax=Math.abs(g);ug=u}
    if(u+12<=e.L){const g2=(ez(e,u+12)-ez(e,u+8))/4,d=Math.abs(g2-g);if(d>kmax){kmax=d;uk=u}}}
  const p=eAt(e,ug);if(gmax>lim(e))F.grade.push([gmax,`${nm(e)} ${e.type} grade ${(gmax*100).toFixed(1)}% at u${ug|0} (${p.x|0},${p.y|0}) L${e.L|0}`]);
  const q=eAt(e,uk);if(kmax>0.035)F.kink.push([kmax,`${nm(e)} ${e.type} grade jumps ${(kmax*100).toFixed(1)}% within 8 m at u${uk|0} (${q.x|0},${q.y|0})`]);
  // drivable floor vs the road's own height, across each lane
  let fm=0,fu=0,ft=0;for(let u=6;u<e.L-6;u+=6){for(let l=0;l<(e.n||1);l++){const t=laneOff(e,l),pp=ePt(e,u,t);GREF.z=ez(e,u);const G=groundAt(pp[0],pp[1]);const d=Math.abs(G.h-ez(e,u)-(e.tp?0:0));if(d>fm&&d<3){fm=d;fu=u;ft=t}}}
  if(fm>0.12){const pp=ePt(e,fu,ft);F.floor.push([fm,`${nm(e)} ${e.type} floor off by ${fm.toFixed(2)} m at u${fu|0} lane t${ft.toFixed(1)} (${pp[0]|0},${pp[1]|0})`])}}
 // joins: every pair of roads meeting at a node should meet at the same height
 for(const n of NODES){const L=(n.legs||[]).filter(l=>R.includes(l.e));if(L.length<2)continue;const zs=L.map(l=>ez(l.e,l.end?l.e.L:0));const d=Math.max(...zs)-Math.min(...zs);
  if(d>0.15)F.join.push([d,`node (${n.x|0},${n.y|0}) ${L.map((l,i)=>nm(l.e)+"="+zs[i].toFixed(2)).join(" ")} step ${d.toFixed(2)} m`])}
 for(const k in F){F[k].sort((a,b)=>b[0]-a[0]);out.push(`== ${k}: ${F[k].length}`);out.push(...F[k].slice(0,25).map(x=>"  "+x[1]))}
 return `edges ${R.length}\n`+out.join("\n")})()
