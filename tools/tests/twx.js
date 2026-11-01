// wind: a car driving straight at 65 mph in a storm drifts sideways unless you steer; with wind off it doesn't
(async()=>{const o=[];const reset=(x,y,h)=>{car.zw=null;car.th=car.phi=car.thd=car.phid=0;car.vzb=0;resetCar({free:true,x,y,h});car.zw=null;car.vx=0};
 for(const k of ["camry25","chv_silverado_2500_hd_wt"]){if(!TRIMS[k])continue;try{if(!MODELS[TRIMS[k].model])await loadModel(TRIMS[k].model)}catch(e){}
  for(const on of [false,true]){setTrim(k,true);cars=[];st.power=true;st.started=true;sys.epb=false;st.wind=on;st.wxReal=true;setWeather("storm",true);for(let i=0;i<120;i++)weatherTick(0.1);
   WXR.g=0;WXR.gT=0;WXR.gt=99;WXR.dir=Math.PI/2;weatherTick(0.01);reset(TCL[0],-1300,0);st.gear="D";car.vx=29;const y0=car.py;
   SIM(3,()=>{inp.thrT=car.vx<29?0.5:0;inp.steerT=0;WXR.gt=99});o.push(`${k.padEnd(26)} wind ${on?"on ":"off"} ${WXR.spd.toFixed(1)} m/s · side force ${Math.round(car.windF||0)} N · drift in 3 s ${(car.py-y0).toFixed(2)} m · heading ${(car.psi*57.3).toFixed(1)}°`)}}
 st.wind=true;return o.join("\n")})()
