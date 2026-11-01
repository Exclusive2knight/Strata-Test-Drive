// "send help" after a crash: the new rollback comes, loads your car onto its bed and drives off with it
(async()=>{const o=[];await loadModel("wk_rollback");await loadModel("city_ambulance").catch(()=>{});st.started=true;st.power=true;sys.epb=false;st.gear="P";car.vx=0;
 sfCallEnd(true);const tw=TOWH.c;if(!tw){return "no tow sent"}o.push("truck model "+tw.mdl);let ph=TOWH.ph,zmax=0;
 SIM(80,()=>{if(TOWH.ph!==ph){o.push(`phase ${ph} -> ${TOWH.ph}`);ph=TOWH.ph}if(TOWH.ride){const B=towBed(TOWH.c);zmax=Math.max(zmax,car.zb||0);if(!o.bed){o.bed=1;o.push(`on bed: car ${car.px.toFixed(1)},${car.py.toFixed(1)} z ${(car.zb||0).toFixed(2)} · truck ${TOWH.c.wx.toFixed(1)},${TOWH.c.wy.toFixed(1)} dist ${Math.hypot(car.px-TOWH.c.wx,car.py-TOWH.c.wy).toFixed(2)} m`)}}if(TOWH.ph==="drive"&&o.length>6)return false});
 o.push("final phase "+TOWH.ph);return o.join("\n")})()
