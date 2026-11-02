// Cybercab robotaxis spawn as traffic only, drive, and pull over for riders
(async()=>{await loadModel("tsl_cybercab");resetCar(STARTS.city||{x:car.px,y:car.py,h:car.psi});st.started=true;st.gear="P";car.vx=0;spawnTraffic(25);GT.min=12*60;let stops=0;const seen=new Set();
 SIM(60,()=>{busTick(0.02);for(const c of cars)if(c.robo){seen.add(c);if(c.tStop>6.9&&!c._st){c._st=1;stops++}if(c.tStop<=0)c._st=0}});
 const R=cars.filter(c=>c.robo);return `robotaxis now ${R.length} (seen ${seen.size}), pull-overs ${stops}, moving ${R.filter(c=>c.v>1).length}, in the dealer: ${LINEUP.some(k=>TRIMS[k].model==="tsl_cybercab")}`})()
