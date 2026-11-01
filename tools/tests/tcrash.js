// live crash: two traffic cars collide, police + tow drive in, traffic nearby slows to look
(async()=>{const o=[];st.started=true;st.gear="P";car.vx=0;resetCar(STARTS.hwy||{x:car.px,y:car.py,h:car.psi});cars=cars.filter(c=>c.kind!=="ai");spawnTraffic(50);
 let v=null;for(let i=0;i<60&&!v;i++){SIM(1,()=>{});if(startEvent("aicrash"))v=EV.list[EV.list.length-1]}
 if(!v){const M=me(),A=aheadOnRoad(M,250);if(!A)return "no road";const L_=newCar(A.e,A.dir,A.s+25,0),F=newCar(A.e,A.dir,A.s,0);L_.v=F.v=24;cars.push(L_,F);L_.hardT=3.2;F.distractT=6;v={type:"aicrash",label:"Crash",x:L_.wx,y:L_.wy,t:240,items:[],pair:[L_,F],phase:0,pt:0,quiet:true};EV.list.push(v);o.push("(forced pair)")}
 o.push("crash set up on "+v.pair[0].e.type);let ph=v.phase;SIM(40,()=>{evTick(0.02);if(v.phase!==ph){o.push(`phase ${ph}->${v.phase} at ${v.pt.toFixed(1)} s`);ph=v.phase}});
 const resp=v.items.filter(c=>c.beacon);o.push(`responders: ${resp.map(c=>c.mdl+(c.emv?" (driving in)":" (on scene)")).join(", ")}`);
 const near=cars.filter(c=>c.kind==="ai"&&EV.crz.length&&Math.hypot(c.wx-v.x,c.wy-v.y)<150);o.push(`traffic within 150 m: ${near.length}, slowed to ${near.map(c=>Math.round(jamMul(c)*100)+"%").slice(0,6).join(" ")}`);
 return o.join("\n")})()
