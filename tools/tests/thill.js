(async()=>{setTrim("camry25",true);cars=[];st.power=true;st.started=true;sys.epb=false;st.gear="D";const o=[];
for(const [nm,y0] of [["20% hill",-1170],["30% ramp",-1050]]){resetCar({free:true,x:TCL[2],y:y0,h:Math.PI/2});car.vx=6;let zmax=0,jerk=0,pz=null,h0=hits;
  SIM(16,()=>{inp.thrT=car.vx<6?0.5:0;inp.brkT=car.vx>7?0.2:0;inp.steerT=clamp(-(car.px-TCL[2])*0.3-wrapPi(car.psi-Math.PI/2)*1.5,-1,1);zmax=Math.max(zmax,car.zb||0);if(pz!==null)jerk=Math.max(jerk,Math.abs((car.vzb||0)-pz)/0.02);pz=car.vzb||0});
  o.push(`${nm}: top z ${zmax.toFixed(2)} · max vertical accel ${(jerk/9.81).toFixed(2)} g · ended y ${car.py.toFixed(0)} · hits ${hits-h0}`)}
// guard rail: steer into it on top of the 10% hill
resetCar({free:true,x:TCL[2],y:-1248,h:Math.PI/2});car.vx=4;let h0=hits;SIM(5,()=>{inp.thrT=0.2;inp.steerT=0.6});o.push(`into the rail on top: x ${car.px.toFixed(2)} (lane edge ${(TCL[2]+3.5).toFixed(1)}/${(TCL[2]-3.5).toFixed(1)}) z ${(car.zb||0).toFixed(2)} hits ${hits-h0}`);
return o.join("\n")})()
