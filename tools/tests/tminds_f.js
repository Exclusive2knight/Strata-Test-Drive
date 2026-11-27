/* v38 traffic minds: 9 garage parking. 200 drivers come to the Fort St garage: queue at the entry gate, take a ticket, drive up looking for
   a space, park (with their own mistakes), stay, back out, drive down, pay and leave. No two cars may touch (each other, parked cars or the
   walls' stalls), the entry gate opens once per ticket and closes behind each car (never on one), and the exit gate the same per departure. */
(async()=>{const out=[],P=(ok,n,s)=>out.push(`${ok?"PASS":"FAIL"} ${n}: ${s}`);window.NOSEMI=1;setTrim("camry25",true);
resetCar({free:true,x:-900,y:-120,h:0});st.power=true;st.started=true;st.gear="P";car.vx=0;cars.length=0;Traffic.set_density("all",0);
for(const k in GPK.stats)if(typeof GPK.stats[k]==="number")GPK.stats[k]=0;GPK.stats.open={entry:0,exit:0};GPK.stats.close={entry:0,exit:0};GPK.res.clear();GPK.gone=[];
GPK.test=true;GPK.max=+(window.GN||200);GPK.rate=()=>5+Math.random()*4;GPK.dwell=c=>40+Math.random()*120;GPK.arrT=0;
const pairs=new Map(),pk=new Map();let t=0,maxIn=0,lastNew=0;const ST=GPK.stats;
const shr=o=>[(o.len||CARLEN)/2-0.25,(o.wid||1.9)/2-0.15];
while(t<3600){SIMSTEP(0.1);t+=0.1;const A=cars.filter(c=>c.gpk);if(((t*10)|0)%10===0)for(const a of A){(a._h=a._h||[]).push(`${t.toFixed(0)} ${a.gpk.ph}${a.gpk.resume?'/bk':''}${a.gpk.mv?'/mv'+a.gpk.mv.mi:''} ${(a.wx-GAR.cx).toFixed(1)},${(a.wy-GAR.cy).toFixed(1)} h${a.wh.toFixed(2)}`);if(a._h.length>14)a._h.shift()}maxIn=Math.max(maxIn,A.length);if(ST.arr>lastNew)lastNew=ST.arr;
  if(((t*10)|0)%5===0){for(let i=0;i<A.length;i++){const a=A[i],[al,aw]=shr(a);
      for(let j=i+1;j<A.length;j++){const b=A[j];if(Math.abs(a.wx-b.wx)>7||Math.abs(a.wy-b.wy)>7||Math.abs((a.wz||0)-(b.wz||0))>1.4)continue;const [bl,bw]=shr(b);const H=obbSAT(a.wx,a.wy,a.wh,al,aw,b.wx,b.wy,b.wh,bl,bw);if(H&&H.d>0.05){const k=Math.min(a.id,b.id)+":"+Math.max(a.id,b.id);if(!pairs.has(k))pairs.set(k,`[A ${(a._h||[]).slice(-6).join(' | ')}] [B ${(b._h||[]).slice(-6).join(' | ')}] ${a.gpk.ph}/${b.gpk.ph} at ${(a.wx-GAR.cx).toFixed(0)},${(a.wy-GAR.cy).toFixed(0)} z${(a.wz||0).toFixed(1)} d${H.d.toFixed(2)}`)}}
      for(const p of parked){if(p.wx===undefined||Math.abs(p.wx-a.wx)>6||Math.abs(p.wy-a.wy)>6||Math.abs((p.wz||0)-(a.wz||0))>1.4)continue;const H=obbSAT(a.wx,a.wy,a.wh,al,aw,p.wx,p.wy,p.wh||0,2.1,0.8);if(H&&H.d>0.05){const k=a.id+":p";if(!pk.has(k))pk.set(k,`[${(a._h||[]).join(' | ')}] ${a.gpk.ph} at ${(a.wx-GAR.cx).toFixed(0)},${(a.wy-GAR.cy).toFixed(0)} z${(a.wz||0).toFixed(1)} h${a.wh.toFixed(2)} d${H.d.toFixed(2)} stall ${a.gpk.stall?(a.gpk.stall.x-GAR.cx).toFixed(1)+','+(a.gpk.stall.y-GAR.cy).toFixed(1)+' k'+a.gpk.stall.k:'-'} parked ${(p.wx-GAR.cx).toFixed(1)},${(p.wy-GAR.cy).toFixed(1)} z${(p.wz||0).toFixed(1)}`)}}}
    /* nobody drives through a closed gate */
    for(const a of A){for(const [k,g] of Object.entries(GATE)){const L=[a.wx-GAR.cx,a.wy-GAR.cy],gx=g.gx-GAR.cx;if(Math.abs(L[0]-gx)<0.6&&L[1]>g.ya-GAR.cy&&L[1]<g.yb-GAR.cy&&g.a<0.9&&Math.abs(a.v)>0.3)a._thru=(a._thru||0)+1}}}
  if(ST.arr>=GPK.max&&!cars.some(c=>c.gpk))break}
const A=cars.filter(c=>c.gpk),thru=0;
const gateOK=ST.open.entry===ST.ticket&&ST.close.entry===ST.ticket&&ST.open.exit===ST.left&&ST.close.exit===ST.left&&ST.closeOnCar===0;
P(ST.arr>=GPK.max&&ST.ticket===ST.arr&&ST.park+ST.give===ST.ticket&&ST.left===ST.ticket&&pairs.size===0&&pk.size===0&&gateOK&&A.length===0,"9 garage parking",
  `${ST.arr} arrived, ${ST.ticket} took a ticket, ${ST.park} parked (${ST.second} needed more than one go to get in, ${ST.crooked} ended up a bit crooked), ${ST.give} found no space and left, ${ST.left} paid and left; `+
  `at most ${maxIn} in the garage at once; touching cars: ${pairs.size}${pairs.size?" ("+[...pairs.values()].slice(0,4).join("; ")+")":""}, touching parked cars: ${pk.size}${pk.size?" ("+[...pk.values()].slice(0,3).join("; ")+")":""}; `+
  `entry gate opened ${ST.open.entry} / closed ${ST.close.entry}, exit gate opened ${ST.open.exit} / closed ${ST.close.exit}, closed on a car ${ST.closeOnCar}; still inside ${A.length}${A.length?" ("+A.slice(0,5).map(c=>c.gpk.ph+"@"+(c.wx-GAR.cx).toFixed(0)+","+(c.wy-GAR.cy).toFixed(0)+" w"+c.gpk.wait.toFixed(0)).join(" ")+")":""}; ${t.toFixed(0)} sim-s`);
out.push("  gone: "+GPK.gone.filter(x=>!/: left/.test(x)).slice(0,10).join(" | "));GPK.test=false;GPK.max=null;GPK.rate=null;GPK.dwell=null;return out.join("\n")})()
