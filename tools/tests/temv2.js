(async()=>{await loadModel("city_ambulance");const two=EDGES.filter(e=>e.L>900&&!e.ov&&e.n===1).sort((a,b)=>b.L-a.L)[0];
 let s=200;const q=fpt(two,1,s,laneOff(two,0));resetCar({free:true,x:q[0],y:q[1],h:q[2]});st.gear="D";st.started=true;const cash0=ECON.cash;
 emvRun("city_ambulance");const c=EMVR.on.c;let last=performance.now();
 const step=()=>{s+=11/60;const p=fpt(two,1,s,laneOff(two,0));car.px=p[0];car.py=p[1];car.psi=p[2];car.vx=11};SIM(15,step);SIM(15,step);
 const F=me();return `blocking on 2-lane at 11 m/s: off ${F.off.toFixed(2)} blk ${EMVR.on.blk.toFixed(1)} ticket ${EMVR.on.tk} cash ${ECON.cash-cash0} gap ${(F.s-c.s).toFixed(1)} hits ${hits}`})()
