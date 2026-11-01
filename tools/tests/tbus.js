// school bus and transit buses spawn, drive, stop; the school bus swings its arms out
(async()=>{const o=[];await loadModel("city_schoolbus");await loadModel("city_bus");st.started=true;GT.min=8*60;W2L.busT=0;W2L.tbT=0;
 for(let i=0;i<200;i++){W2L.busT=0;W2L.tbT=0;busTick(0.5)}let sb=cars.filter(c=>c.bus),tb=cars.filter(c=>c.transit);o.push(`school buses ${sb.length} (${sb.map(c=>c.mdl)}), transit ${tb.length}`);
 if(sb[0]){const c=sb[0];c.stopIn=0;o.push("type "+c.e.type+" jn "+!!c.jn+" s "+c.s.toFixed(0)+"/"+c.e.L.toFixed(0)+" sbT "+c.sbT);let maxArm=0,stopped=false;SIM(25,()=>{busTick(0.02);maxArm=Math.max(maxArm,c.sbArm||0);if(c.flash&&c.v<0.3)stopped=true});o.push("after: type "+c.e.type+" flash "+c.flash+" stopIn "+(c.stopIn|0)+" stopT "+c.sbT);o.push(`school bus stopped=${stopped} arm out max ${maxArm.toFixed(2)} v=${c.v.toFixed(1)}`)}
 if(tb[0]){const c=tb[0],p0=[c.wx,c.wy];SIM(10,()=>busTick(0.02));o.push(`transit moved ${Math.hypot(c.wx-p0[0],c.wy-p0[1]).toFixed(0)} m`)}
 return o.join("\n")})()
