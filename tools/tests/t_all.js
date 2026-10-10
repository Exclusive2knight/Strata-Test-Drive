(async()=>{const out=[],trim="camry25";setTrim(trim,true);const prep=(start,v)=>{resetCar(STARTS[start]);cars=[];st.power=true;sys.epb=false;st.gear="D";st.acc=false;st.pilot=false;st.aeb=true;st.lka=true;st.bsm=true;car.vx=v;hits=0;LOG.length=0;inp.thrT=0;inp.brkT=0;inp.steerT=0};
// 1 ACC follow a 20 mph car from 60 mph
prep("hwy",26.8);placeTest("slow");act("acc");st.accSet=26.8;let c=cars.find(x=>x.kind==="test"),minG=999,maxDec=0,pv=car.vx,gaps=[];
SIM(40,t=>{const g=Math.hypot(c.wx-car.px,c.wy-car.py);minG=Math.min(minG,g);const d=(pv-car.vx)/0.02;if(t>0.5)maxDec=Math.max(maxDec,d);pv=car.vx;if(t>30)gaps.push(g)});
out.push(`ACC follow: minGap ${minG.toFixed(1)} maxDec ${maxDec.toFixed(1)} endV ${car.vx.toFixed(1)} lead ${c.v.toFixed(1)} gap@30-40 ${(gaps.reduce((a,b)=>a+b,0)/gaps.length).toFixed(1)} (2s gap = ${(c.v*1.8).toFixed(1)}) hits ${hits} acc=${st.acc}`);
// 2 ACC stop & go: lead stops then goes
prep("hwy",20);placeTest("slow");c=cars.find(x=>x.kind==="test");act("acc");st.accSet=24;minG=999;let stopped=false,resumed=false;
SIM(60,t=>{if(t>15&&t<25){c.v0=0;c.v=Math.max(0,c.v-4*0.02)}else if(t>=25){c.v0=12}const g=Math.hypot(c.wx-car.px,c.wy-car.py);minG=Math.min(minG,g);if(car.vx<0.2&&t>15)stopped=true;if(stopped&&car.vx>5)resumed=true});
out.push(`ACC stop&go: minGap ${minG.toFixed(1)} stopped ${stopped} resumed ${resumed} acc=${st.acc} hits ${hits} v ${car.vx.toFixed(1)}`);
// 3 cut-in at 50 mph with ACC
prep("hwy",22.4);act("acc");st.accSet=22.4;placeTest("cutin");c=cars.find(x=>x.kind==="test");minG=999;
SIM(15,t=>{if(c){const g=Math.hypot(c.wx-car.px,c.wy-car.py);minG=Math.min(minG,g)}});out.push(`Cut-in: minGap ${minG.toFixed(1)} hits ${hits} | ${LOG.slice(0,2).join(" / ")}`);
// 4 Pilot lane centering on hwy 90 s
prep("hwy",26);act("pilot");let maxE=0,sumE=0,n=0,lc=0;const z0=me().e;
SIM(90,t=>{const M=me();const e=Math.abs(M.off-M.lo*LANE+LANE/2*0);const lane=laneOf(M.off),ce=Math.abs(M.off-lane*LANE);if(t>3&&!sys.pilotLC){maxE=Math.max(maxE,ce);sumE+=ce;n++}});
out.push(`Pilot hwy: maxErr ${maxE.toFixed(2)} meanErr ${(sumE/n).toFixed(3)} pilot=${st.pilot} state=${sys.pilotState} v ${car.vx.toFixed(1)} hits ${hits}`);
// 5 Pilot in city (curves/junctions)
prep("city",12);act("pilot");maxE=0;sumE=0;n=0;
SIM(60,t=>{const M=me(),ce=Math.abs(M.off-laneOf(M.off)*LANE);if(t>3&&!sys.pilotLC&&!M.jn){maxE=Math.max(maxE,ce);sumE+=ce;n++}});
out.push(`Pilot city: maxErr ${maxE.toFixed(2)} meanErr ${(sumE/Math.max(1,n)).toFixed(3)} pilot=${st.pilot} state=${sys.pilotState} v ${car.vx.toFixed(1)} hits ${hits} off ${car.offroad}`);
// 6 LKA drift test at 55 mph
prep("hwy",24.6);placeTest("drift");SIM(10,t=>{inp.thrT=0.25});out.push(`LKA drift: ${LOG.slice(0,2).join(" / ")} offroad ${car.offroad}`);
// 7 pedestrian
prep("city",12);placeTest("pedestrian");await new Promise(r=>setTimeout(r,2700));SIM(8,t=>{inp.thrT=0.3});out.push(`Pedestrian: hits ${hits} v ${car.vx.toFixed(1)} | ${LOG.slice(0,3).join(" / ")}`);
// 8 deer
prep("hwy",27);placeTest("deer");await new Promise(r=>setTimeout(r,2400));SIM(10,t=>{inp.thrT=0.4});out.push(`Deer: hits ${hits} v ${car.vx.toFixed(1)} | ${LOG.slice(0,3).join(" / ")}`);
// 9 BSM + ELK: car in blind spot, driver signals & steers toward it
prep("hwy",24);placeTest("bsm");SIM(2,t=>{inp.thrT=0.3});const b0=sys.bsmL||sys.bsmR,side=sys.bsmL?1:-1;let minLat=99;c=cars.find(x=>x.kind==="test");
SIM(4,t=>{inp.thrT=0.3;st.signal=side;inp.steerT=0.25*side;if(c)minLat=Math.min(minLat,Math.hypot(c.wx-car.px,c.wy-car.py))});inp.steerT=0;st.signal=0;
out.push(`BSM: detected ${!!b0} minDist ${minLat.toFixed(2)} hits ${hits} | ${LOG.slice(0,2).join(" / ")}`);
return out.join("\n")})()
