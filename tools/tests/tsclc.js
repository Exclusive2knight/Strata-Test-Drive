(async()=>{const out=[];const ks=ORDER.filter(k=>/Super Cruise/.test(TRIMS[k].pilotName||"")||/Super Cruise/.test(JSON.stringify(TRIMS[k].std||"")));
const k=ks.find(k=>/escalade/.test(k))||ks[0];out.push("super cruise trims: "+ks.length+", testing "+k+" ("+(TRIMS[k].pilotName||"")+")");
await loadModel(TRIMS[k].mesh||TRIMS[k].model);setTrim(k,true);
const prep=v=>{resetCar(STARTS.hwy);cars=[];st.power=true;sys.epb=false;st.gear="D";st.acc=false;st.pilot=false;st.lka=true;car.vx=v;hits=0;inp.thrT=0;inp.brkT=0;inp.steerT=0;EV.t=1e9;for(const x of EV.list)x.t=0;sys.pilotLC=null;sys.slowT=0;sys.rightT=0;sys.rightNeed=0;st.signal=0;st.autoLC=true;try{fsdReset()}catch(e){}};
// 1: centring in the lane over 20 s
prep(29);act("pilot");if(!st.acc)act("acc");st.accSet=29;let sum=0,n=0,mx=0;const M0=me();out.push(`lanes lo ${M0.lo} hi ${M0.hi}, start lane ${laneOf(M0.off)}, has pilot ${has("pilot")}`);
SIM(20,t=>{sys.handsT=0;const M=me(),ce=M.off-laneOf(M.off)*LANE;if(t>3){sum+=ce;n++;mx=Math.max(mx,Math.abs(ce))}});out.push(`centring: mean offset ${(sum/n).toFixed(2)} m (+ = left), max ${mx.toFixed(2)} m, state ${sys.pilotState}`);
// 2: signalled lane change left: signal -> new lane centred
{const l0=laneOf(me().off);st.signal=-1;st.signalT=0;let tS=null,tD=null,lMax=l0,tR=null;SIM(30,t=>{sys.handsT=0;const M=me(),l=laneOf(M.off);if(tS===null&&sys.pilotLC)tS=t;if(tS!==null&&tD===null&&!sys.pilotLC)tD=t;lMax=Math.max(lMax,l);if(tD!==null&&tR===null&&l<lMax)tR=t-tD});
 out.push(`signalled change: lane ${l0} -> ${lMax}, back right ${tR===null?'no':tR.toFixed(1)+' s'} after, starts moving after ${tS===null?"never":tS.toFixed(1)+" s"}, done after ${tD===null?"never":tD.toFixed(1)+" s"} (move took ${tS!==null&&tD!==null?(tD-tS).toFixed(1):"-"} s)`)}
// 4: same with light traffic in the right lane (a car every ~60 m, doing 2 mph less)
{prep(29);act("pilot");if(!st.acc)act("acc");st.accSet=29;SIM(3,()=>{sys.handsT=0});st.signal=-1;st.signalT=0;SIM(15,()=>{sys.handsT=0});const M=me(),l1=laneOf(M.off),lo=M.lo;
 let nT=0;for(let d=-50;d<=400;d+=65){if(M.s+d<2||M.s+d>M.L-2)continue;const c=Object.assign({kind:"test",paint:"graphite",sig:0,lcT:99,spin:0,head:0,jn:null,vf:1,idle:0,e:M.e,dir:M.dir,s:M.s+d,off:lo*LANE,offT:lo*LANE,v:27,v0:27});planMove(c,"S");carPose(c);cars.push(c);nT++}
 let tB=null;SIM(40,t=>{sys.handsT=0;if(tB===null&&laneOf(me().off)<l1)tB=t});out.push(`back to the right with traffic (${nT} cars): ${tB===null?"not within 40 s":tB.toFixed(1)+" s"}, hits ${hits}`)}
return out.join("\n")})()
