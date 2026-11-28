/* proving ground: drive every grade hill up and over; report the top height (expected rise), the worst vertical jolt, scrapes and whether it made it */
(async()=>{const o=[];for(const k of ["camry25","jeep_wrangler_rubicon","toy_4runner_tr"]){if(!TRIMS[k])continue;try{if(!MODELS[TRIMS[k].model])await loadModel(TRIMS[k].model)}catch(e){}
  setTrim(k,true);cars=[];st.power=true;st.started=true;sys.epb=false;st.gear="D";
  for(const S of TCS.filter(S=>/grade/.test(S[3]))){const pc=parseInt(S[3]);if(k==="camry25"&&pc>30)continue;resetCar({free:true,x:TCL[2],y:S[1]-12,h:Math.PI/2});car.zw=null;car.vx=pc>=40?4:6;inp.steer=0;let zmax=-9,jerk=0,pz=null,h0=hits;
    SIM(pc>=40?26:18,()=>{const tv=pc>=40?4:6;inp.thrT=car.vx<tv?(pc>=40?0.8:0.5):0;inp.brkT=car.vx>tv+1.5?0.3:0;inp.steerT=clamp(-(car.px-TCL[2])*0.3-wrapPi(car.psi-Math.PI/2)*1.5,-1,1);zmax=Math.max(zmax,car.zb||0);if(pz!==null)jerk=Math.max(jerk,Math.abs((car.vzb||0)-pz)/0.02);pz=car.vzb||0});
    const over=car.py>S[2]-2;o.push(`${k.padEnd(22)} ${S[3].padEnd(10)} rise ${TC_GR[pc][0]} m · top z ${zmax.toFixed(2)} · worst jolt ${(jerk/9.81).toFixed(2)} g · ${over?"over the top":"STOPPED at "+(car.py-S[1]).toFixed(0)+" m"} · hits ${hits-h0}`)}}
// guard rail: steer into it on top of the 10% grade
const S=TCS.find(S=>S[3]==="10% grade");setTrim("camry25",true);resetCar({free:true,x:TCL[2],y:S[1]+45,h:Math.PI/2});car.zw=null;car.vx=4;let h0=hits;SIM(5,()=>{inp.thrT=0.2;inp.steerT=0.6});o.push(`into the rail on top: x ${car.px.toFixed(2)} (lane edge ${(TCL[2]+3.5).toFixed(1)}/${(TCL[2]-3.5).toFixed(1)}) z ${(car.zb||0).toFixed(2)} hits ${hits-h0}`);
return o.join("\n")})()
