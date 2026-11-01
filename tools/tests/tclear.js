// crash clean-up: police + two tows arrive, the tows take the wrecks away (towed behind / on the deck), police leave, nothing left blocking
(async()=>{const o=[];for(const m of ["wk_rollback","wk_wrecker","city_police"])try{await loadModel(m)}catch(e){o.push("no "+m)}
 st.started=true;st.gear="P";car.vx=0;resetCar(STARTS.hwy||{x:car.px,y:car.py,h:car.psi});cars=cars.filter(c=>c.kind!=="ai");spawnTraffic(30);
 const M=me(),A=aheadOnRoad(M,250);const L_=newCar(A.e,A.dir,A.s+25,0),F=newCar(A.e,A.dir,A.s,0);L_.v=F.v=24;cars.push(L_,F);L_.hardT=3.2;F.distractT=6;
 const v={type:"aicrash",label:"Crash",x:L_.wx,y:L_.wy,t:240,items:[],pair:[L_,F],phase:0,pt:0,quiet:true};EV.list.push(v);
 let ph=-1,hk=-1,ended=null;const tw={};
 SIM(100,t=>{if(v.phase!==ph){o.push(`phase ${v.phase} at ${v.pt.toFixed(1)}`);ph=v.phase}if((v.hooked||0)!==hk){hk=v.hooked||0;o.push(`hooked ${hk} at ${v.pt.toFixed(1)} s, towed now ${cars.filter(c=>c.kind==="towed").length}`)}
   if(!ended&&!EV.list.includes(v)){ended=t;o.push("event over at "+t.toFixed(1))}
   for(const w of cars)if(w.kind==="towed"&&w.towBy){const d=Math.hypot(w.wx-w.towBy.wx,w.wy-w.towBy.wy);tw[w.towBy.mdl]=[d.toFixed(1),w.towBy.v.toFixed(1),w.towBy.kind]}});
 o.push("tows: "+JSON.stringify(tw));o.push("wrecks left: "+cars.filter(c=>c.kind==="wreck").length+", cones left: "+cars.filter(c=>c.kind==="cone").length+", responders still with beacons: "+cars.filter(c=>c.beacon&&c.kind==="wreck").length);
 return o.join("\n")})()
