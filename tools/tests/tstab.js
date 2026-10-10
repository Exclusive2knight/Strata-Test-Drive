(async()=>{const o=[];const reset=(x,y,h)=>{car.zw=null;car.th=car.phi=car.thd=car.phid=0;car.vzb=0;resetCar({free:true,x,y,h});car.zw=null;car.vx=0};
for(const k of ["camry25","q5_prest","escalade","ford_ranger_rap","ty_perf","chv_silverado_hd_wt"]){if(!TRIMS[k])continue;try{if(!MODELS[TRIMS[k].model])await loadModel(TRIMS[k].model)}catch(e){}
 for(const use of [false,true]){setTrim(k,true);const sv=TRIMS[k].sus;if(!use)TRIMS[k].sus=null;cars=[];st.power=true;st.started=true;sys.epb=false;st.gear="P";
  reset(TC_SKID.x,TC_SKID.y+30,0);let mx=0;SIM(2,(t)=>{if(t>0.5)mx=Math.max(mx,Math.abs(car.phi||0),Math.abs(car.th||0))});const still=mx;
  st.gear="D";car.vx=15;let r=0,n=0,ay=0;SIM(4,(t)=>{inp.thrT=car.vx<15?0.3:0;inp.steerT=-0.3;if(t>2){r+=car.phi||0;ay+=car.ay||0;n++}});
  reset(TCL[0],-1300,Math.PI/2);car.vx=10;let pk=0,pv=0;SIM(5,()=>{inp.thrT=car.vx<10?0.4:0;inp.steerT=clamp(-(car.px-TCL[0])*0.3-wrapPi(car.psi-Math.PI/2)*1.5,-1,1);if(car.py>-1280){pk=Math.max(pk,Math.abs(((car.vzb||0)-pv)/0.02))}pv=car.vzb||0});
  o.push(`${k.padEnd(20)} ${use?"NEW":"old"} still ${(still*57.3).toFixed(2)}° · turn ${(ay/n/9.81).toFixed(2)} g roll ${(Math.abs(r/n)*57.3).toFixed(1)}° (${(Math.abs(r/n)*57.3/Math.max(0.05,Math.abs(ay/n/9.81))).toFixed(1)}°/g) · whoops ${(pk/9.81).toFixed(2)} g`);TRIMS[k].sus=sv}}
return o.join("\n")})()
