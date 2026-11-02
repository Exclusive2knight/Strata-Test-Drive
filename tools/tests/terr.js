// errands: AI drivers turn into store lots, park, and later back out and rejoin traffic; parked cars leave lots
(async()=>{const S0=XSITES.filter(S=>S.kind==="lot"&&S.stalls&&S.stalls.length)[3];resetCar({free:true,x:S0.x+40,y:S0.y+40,h:0});st.started=true;st.gear="P";car.vx=0;spawnTraffic(40);
 let go=0,ins=0,parkedN=0,outs=0,joined=0;const seen=new Set();const P0=parked.length;
 SIM(120,()=>{for(const c of cars){const E=c.errand;if(!E)continue;const k=E.ph+(c.id);if(!seen.has(k)){seen.add(k);if(E.ph==="go")go++;else if(E.ph==="in")ins++;else if(E.ph==="out")outs++}}
   for(const o of parked)if(o.errAt&&!o._c){o._c=1;parkedN++}});
 const stuckOut=cars.filter(c=>c.errand&&c.errand.ph==="out").map(c=>`k${c.errand.k}/${c.errand.P.length} v${c.v.toFixed(1)}`);
 for(const c of cars)if(c._wasOut&&c.kind==="ai")joined++;
 return `errands started ${go}, turned in ${ins}, parked ${parkedN}, pulled out ${outs}, still pulling out: ${stuckOut.join(" ")}, still driving to a store: ${cars.filter(c=>c.errand&&c.errand.ph==="go").length}, parked ${P0}->${parked.length}`})()
