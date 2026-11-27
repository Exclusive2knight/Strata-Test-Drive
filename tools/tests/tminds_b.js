/* v38 traffic minds: 3 traffic realism. 30 sim-minutes of "weekday rush": no deadlocks, no overlaps, nobody out of their lane except
   while changing lanes, and the flow/density diagram on the freeways (flow should rise with density, then drop) */
(async()=>{const out=[],P=(ok,n,s)=>out.push(`${ok?"PASS":"FAIL"} ${n}: ${s}`);window.NOSEMI=1;setTrim("camry25",true);
resetCar(STARTS.hwy);{const M=me(),q=ePt(M.e,M.s,(hwOf(M.e)+8));resetCar({free:true,x:q[0],y:q[1],h:car.psi})}st.power=true;st.started=true;st.gear="P";car.vx=0;cars.length=0;
Traffic.scenario("weekday rush");spawnTraffic(170);let over=0,overL=new Map(),stuck=new Set(),off=0,offN=0;const FD=[];const T=+(window.TMIN||30)*60;
for(let k=0;k<T*10;k++){SIMSTEP(0.1);
  if(k%10===0){const A=cars.filter(c=>c.kind==="ai"&&c.wx!==undefined);const G=new Map();for(const c of A){const key=Math.floor(c.wx/10)+","+Math.floor(c.wy/10);(G.get(key)||G.set(key,[]).get(key)).push(c)}
    for(const c of A){const [i,j]=[Math.floor(c.wx/10),Math.floor(c.wy/10)];for(let a=-1;a<=1;a++)for(let b=-1;b<=1;b++)for(const o of G.get((i+a)+","+(j+b))||[]){if(o.id<=c.id||Math.abs((o.wz||0)-(c.wz||0))>1.5)continue;
      const H=obbSAT(c.wx,c.wy,c.wh,(c.len||CARLEN)/2-0.25,(c.wid||1.9)/2-0.15,o.wx,o.wy,o.wh,(o.len||CARLEN)/2-0.25,(o.wid||1.9)/2-0.15);if(H&&H.d>0.3){over++;const n=(c.e&&c.e.name)+"/"+(o.e&&o.e.name);overL.set(n,(overL.get(n)||0)+1)}}
      if(c.idle>90)stuck.add(c.id);
      if(!c.jn&&c.e&&!c.lcPending&&c.lcTarget==null&&!c.ovt&&!c.zipT&&!c.emv&&c.v>3){offN++;const lo=loOf(c.e.n);let best=9;for(let q=0;q<c.e.n;q++)best=Math.min(best,Math.abs(c.off-laneOff(c.e,q)));if(best>1.2)off++}}}
  /* like loop detectors: density and flow over 250 m stretches of freeway lane, every 10 s (whole-road averages hide the queues) */
  if(k%100===0){for(const e of EDGES){if(e.type!=="xway"||e.L<300)continue;const L=cars.filter(c=>c.kind==="ai"&&c.e===e&&!c.jn);if(L.length<2)continue;for(const dir of [1,-1]){const S=L.filter(c=>c.dir===dir);if(S.length<2)continue;
    for(let w=0;w+250<=e.L;w+=125){const W_=S.filter(c=>c.s>=w&&c.s<w+250);if(W_.length<2)continue;const dens=W_.length/0.25/e.n,v=W_.reduce((s,c)=>s+c.v,0)/W_.length;FD.push([dens,dens*v*3.6])}}}}}
FD.sort((a,b)=>a[0]-b[0]);const bins={};for(const [d,f] of FD){const b=Math.floor(d/8)*8;(bins[b]=bins[b]||[]).push(f)}const fd=Object.entries(bins).map(([b,F])=>[+b,F.reduce((s,v)=>s+v,0)/F.length,F.length]).filter(r=>r[2]>=3).sort((a,b)=>a[0]-b[0]);
let peak=fd.reduce((m,r)=>r[1]>m[1]?r:m,[0,0]),rises=fd.length>1&&fd[0][1]<peak[1],drops=fd.some(r=>r[0]>peak[0]&&r[1]<peak[1]*0.85);
P(stuck.size===0,"3a no deadlocks",`${T/60} sim-minutes, ${cars.filter(c=>c.kind==="ai").length} cars: cars stopped over 90 s: ${stuck.size}`);
P(over===0,"3b no overlaps",`overlapping pairs (samples) ${over}${over?" · "+[...overL].sort((a,b)=>b[1]-a[1]).slice(0,4).map(([k,v])=>k+":"+v).join(", "):""}`);
P(off/Math.max(1,offN)<0.002,"3c lane discipline",`out of lane (over 1.2 m from any lane centre) when not changing lanes: ${(off/Math.max(1,offN)*100).toFixed(2)}% of ${offN} samples`);
P(rises&&drops,"3d fundamental diagram",`freeway flow by density (veh/km/lane: veh/h/lane, samples): ${fd.map(r=>`${r[0]}:${r[1].toFixed(0)} (${r[2]})`).join(" · ")}`);
return out.join("\n")})()
