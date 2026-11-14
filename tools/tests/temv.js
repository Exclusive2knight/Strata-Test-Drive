(async()=>{const r=[];await loadModel("city_ambulance");await loadModel("city_fire");
 r.push("models "+!!MODELS.city_ambulance+" "+!!MODELS.city_fire);
 const pick=f=>EDGES.filter(e=>e.L>900&&!e.ov&&!/ramp/i.test(e.name||"")&&f(e)).sort((a,b)=>b.L-a.L)[0];
 const put=(e,s,i)=>{const q=fpt(e,1,s,laneOff(e,i));resetCar({free:true,x:q[0],y:q[1],h:q[2]});st.gear="D";st.started=true;st.power=true;sys.epb=false};
 const clear=()=>{if(EMVR.on){EMVR.on.ev.t=0;EMVR.on=null}SIM(0.1,()=>{})};
 const run=(label,e,i,k,sec,vx,lane)=>{put(e,400,i);const res=emvRun(k);const c=EMVR.on&&EMVR.on.c;const s0=c?c.s:0;let minD=1e9,passed=false;const cash0=ECON.cash;
   SIM(sec,()=>{if(lane!==undefined){const q=fpt(e,1,Math.max(me().s,1),laneOff(e,lane));}car.vx=vx;if(c){minD=Math.min(minD,Math.hypot(c.wx-car.px,c.wy-car.py));if(c.e===me().e&&c.s>me().s+5)passed=true}});
   r.push(`${label} (${e.name}, ${e.n} lanes): run ${res} lane ${c?laneIdx(c):"-"} moved ${c?(c.s-s0).toFixed(0):"-"} m v ${c?c.v.toFixed(1):"-"} minD ${minD.toFixed(1)} passed ${passed} ticket ${EMVR.on&&EMVR.on.tk} cash ${ECON.cash-cash0} hits ${hits}`);clear()};
 const fw=pick(e=>e.n>=2),two=pick(e=>e.n===1);
 run("amb, you cruise in right lane",fw,0,"city_ambulance",16,13);
 run("fire, you stay in its lane",fw,fw.n-1,"city_fire",16,13);
 if(two)run("amb, 2-lane road, you stop",two,0,"city_ambulance",16,0);
 let err="";try{emvBodyInto()}catch(x){err=String(x)}r.push("draw "+(err||"ok"));
 return r.join("\n")})()
