// AI cars should move smoothly: no position jumps or heading snaps, especially going from a junction onto the next road
(async()=>{resetCar(STARTS.city||{x:car.px,y:car.py,h:car.psi});st.started=true;st.gear="P";car.vx=0;spawnTraffic(40);TOD.t=1e9;const P=new Map();const J=[];let n=0;
 SIM(40,()=>{for(const c of cars){if(c.kind!=="ai")continue;const q=P.get(c);if(q&&q.id===c.id){const d=Math.hypot(c.wx-q.x,c.wy-q.y),exp=Math.max(c.v,q.v)*0.02,dh=Math.abs(wrapPi(c.wh-q.h));n++;
   if(d>exp+0.25||dh>0.12)J.push(`${d.toFixed(2)}m dh${dh.toFixed(2)} v${c.v.toFixed(1)} ${q.jn?"J":"E"}->${c.jn?"J":"E"} ${q.e}->${c.e.name}${c.errand?" errand":""}${c.robo?" robo":""}${c.stunned>0?" stunned":""}`)}
   P.set(c,{x:c.wx,y:c.wy,h:c.wh,v:c.v,jn:!!c.jn,e:c.e.name,id:c.id})}});
 const k={};for(const j of J){const t=j.split(" ").slice(3,4).join(" ");k[t]=(k[t]||0)+1}return `samples ${n}, jumps ${J.length} by transition ${JSON.stringify(k)}\n`+J.slice(0,14).join("\n")})()
