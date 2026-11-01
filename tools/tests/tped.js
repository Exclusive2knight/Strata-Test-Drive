// pedestrians at corners: how long they wait before crossing, and whether any get stuck
(async()=>{resetCar(STARTS.city||{x:car.px,y:car.py,h:car.psi});st.started=true;st.gear="P";car.vx=0;spawnTraffic(30);const W=new Map(),done=[];let peak=0;
 SIM(120,()=>{for(const p of peds){if(p.mode==="waitX")W.set(p,p.wait);else if(W.has(p)){done.push(W.get(p));W.delete(p)}}peak=Math.max(peak,peds.length)});
 done.sort((a,b)=>a-b);const still=[...W.values()].filter(w=>w>40).length;
 return `peds ${peak}, crossings ${done.length}, median wait ${(done[done.length>>1]||0).toFixed(1)} s, max ${(done[done.length-1]||0).toFixed(1)} s, waiting >40 s now ${still} · brain gen ${BRAIN.gen} stops ${BRAIN.stops} cross ${BRAIN.cross} stopWait ${BRAIN.stopWait.toFixed(2)} gapK ${BRAIN.gapK.toFixed(3)} pedPat ${BRAIN.pedPat.toFixed(1)}`})()
