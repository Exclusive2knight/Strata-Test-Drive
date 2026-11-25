(async()=>{const out=[];setTrim("camry25",true);
const E2=EDGES.filter(e=>!/xway|ramp|dirt|lot|drive/.test(e.type)&&e.n===1&&e.L>400).sort((a,b)=>b.L-a.L)[0],key=`${E2.type} ${E2.name||""} (${Math.round(E2.L)} m)`;
const prep=()=>{const P=fpt(E2,1,E2.L*0.15,0);resetCar({x:P[0],y:P[1],h:P[2]});cars=[];st.power=true;sys.epb=false;st.gear="D";st.acc=false;st.pilot=false;st.lka=true;st.elk=true;st.bsm=true;st.lkaMode="both";car.vx=22;hits=0;inp.thrT=0.22;inp.brkT=0;inp.steerT=0;EV.t=1e9;sys.lkaHold=0;sys.elkT=0;st.signal=0};
for(const dir of [1,-1]){prep();let M0=me();const lane0=M0.off;let pushBack=0,crossedT=0,maxOff=-99,minOff=99,phase="";
 SIM(9,t=>{const M=me();maxOff=Math.max(maxOff,M.off-lane0);minOff=Math.min(minOff,M.off-lane0);
   inp.steerT=t<1.2?0.05*dir:t<4?0:t<5.2?-0.05*dir:0;
   const over=RF&&M.off>(RF.hi+0.5)*LANE-0.25; if(over)crossedT+=0.02; if(over&&Math.abs(sys.lkaDelta)>0.001)pushBack+=0.02;});
 out.push(`steer ${dir>0?"+":"-"}: start lane off ${lane0.toFixed(1)}, moved ${minOff.toFixed(1)}..${maxOff.toFixed(1)} m, time over the centre line ${crossedT.toFixed(1)} s, LKA pushing while over it ${pushBack.toFixed(2)} s, RF ${RF&&RF.lo}..${RF&&RF.hi}, road ${key}`);}
// plain drift with no steering still gets nudged (regression)
prep();let nudged=0;sys.driftT=6;SIM(7,t=>{inp.steerT=0;if(sys.lkaState==="nudge")nudged+=0.02});out.push(`hands-off drift: LKA nudged ${nudged.toFixed(1)} s, max drift ${ftS(sys.lkaLog.maxE)}`);
return out.join("\n")})()
