// FSD: a crashed car angled into the lane ahead (its back sticking out), on the freeway and on a city street; then a roundabout with traffic
(async()=>{const out=[];await loadModel(TRIMS.ty_lrawd.model);setTrim("ty_lrawd",true);TSL.sub=true;teslaApply();
 const prep=(start,v)=>{resetCar(STARTS[start]);cars=[];st.power=true;sys.epb=false;st.gear="D";st.aeb=true;car.vx=v;hits=0;LOG.length=0;inp.thrT=0;inp.brkT=0;inp.steerT=0;EV.t=1e9;for(const v of EV.list)v.t=0;sys.lead=null;sys.hold=false;try{fsdReset()}catch(e){};st.pilot=true;st.acc=true;st.autoLC=true};
 for(const [start,v,lat,profile] of [["hwy",24,2.3,"standard"],["city",11,2.0,"standard"],["hwy",24,2.3,"madmax"]]){prep(start,v);TSL.profile=profile;
   const h=car.psi,c=Math.cos(h),s=Math.sin(h),d=70,M=me(),off=(M.off||0);   /* right of our lane centre by lat, nose pointing out of the lane, back into it */
   const wx=car.px+c*d+s*lat,wy=car.py+s*d-c*lat,W={kind:"wreck",wx,wy,wz:car.zb||0,wh:h-0.55,v:0,v0:0,len:4.7,wid:1.85,haz:true,paint:"c:#ddd",mdl:"camry25"};cars.push(W);
   let minD=1e9,passed=false,minLat=9;SIM(20,()=>{const dx=W.wx-car.px,dy=W.wy-car.py,f=dx*Math.cos(car.psi)+dy*Math.sin(car.psi);minD=Math.min(minD,Math.hypot(dx,dy));if(f<-6)passed=true});
   out.push(`${start} ${profile}: wreck ${lat} m right, angled in · hits ${hits} closest ${minD.toFixed(1)} m · passed ${passed} · v ${(car.vx*2.237).toFixed(0)} mph · ${sys.fsdWhy||""} · ${LOG.slice(0,3).join(" / ")}`)}
 return out.join("\n")})()
