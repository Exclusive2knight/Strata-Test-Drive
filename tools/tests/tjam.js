// freeway share of traffic, a jam zone slows cars, road work stays off freeways
(async()=>{const o=[];st.started=true;cars=cars.filter(c=>c.kind!=="ai");spawnTraffic(60);const ai=cars.filter(c=>c.kind==="ai"),fw=ai.filter(c=>c.e.type==="xway"||c.e.type==="ramp");
 const fwLen=EDGES.filter(e=>e.type==="xway"||e.type==="ramp").reduce((a,e)=>a+e.L*e.n,0),all=EDGES.reduce((a,e)=>a+e.L*e.n,0);
 o.push(`traffic on freeway/ramps: ${fw.length}/${ai.length} (road share ${(fwLen/all*100).toFixed(0)}%)`);
 JAM.zones=[];JAM.t=0;for(let i=0;i<40&&!JAM.zones.length;i++)jamTick(3);const z=JAM.zones[0];o.push(z?`jam: ${Math.round(z.s1-z.s0)} m at ${(z.m*100).toFixed(0)}% speed, ${Math.round(z.left)} s`:"no jam");
 if(z){const c=newCar(z.e,z.dir,(z.s0+z.s1)/2,0);o.push(`car in jam target ${(jamMul(c)*100).toFixed(0)}% of normal`)}
 RW.day=-1;GT.day=(GT.day||1)+1;rwTick();const bad=RW.zones.filter(q=>q.e.type==="xway"||q.e.type==="ramp");o.push(`road work zones ${RW.zones.length}, closed ${RW.closed.size}, on freeway ${bad.length}`);
 return o.join("\n")})()
