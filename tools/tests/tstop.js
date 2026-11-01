// stop signs: how long AI cars sit at the line after stopping, and how often they creep (start, stop again) without going
(async()=>{const o=[];resetCar(STARTS.city||{x:car.px,y:car.py,h:car.psi});st.started=true;st.gear="P";car.vx=0;cars=cars.filter(c=>c.kind!=="ai");spawnTraffic(60);TOD.t=1e9;
 const W=new Map();let creeps=0,goes=0,waits=[],maxW=0,stuckList=[];
 SIM(60,()=>{for(const c of cars){if(c.kind!=="ai")continue;const n=c.mvNode;const ctl=n&&!c.jn&&(n.ctrl==="allstop"||n.ctrl==="minor"&&c.mvLeg&&!c.mvLeg.major&&!n.rbt);let w=W.get(c);
   if(ctl&&c.stopDone){if(!w){w={t:0,moving:false,cr:0};W.set(c,w)}w.t+=0.02;if(c.v>0.6&&!w.moving)w.moving=true;else if(c.v<0.1&&w.moving){w.moving=false;w.cr++;creeps++}}
   else if(w){if(c.jn){goes++;waits.push(w.t);maxW=Math.max(maxW,w.t)}W.delete(c)}}});
 for(const [c,w] of W)if(w.t>15)stuckList.push(`${c.e.name} ${c.mvNode.ctrl} ${w.t.toFixed(0)}s creeps ${w.cr} gap? ${c.cg===Infinity?"go":c.cg&&c.cg.toFixed(1)} v${c.v.toFixed(2)} who ${c.lw==="me"?"me":c.lw==="ctrl"?"ctrl":c.lw?(c.lw.kind+(c.lw.jn?"(jn,v"+c.lw.v.toFixed(1)+")":"")):"-"} lg ${(c.lg||0).toFixed(1)} busy ${boxBusy(c.mvNode,c)} first ${firstInLine(c,c.mvNode)} exit ${exitClear(c)} wt ${(c.waitT||0).toFixed(0)}`);
 waits.sort((a,b)=>a-b);o.push(`went through ${goes}, median wait ${(waits[waits.length>>1]||0).toFixed(1)} s, max ${maxW.toFixed(1)} s, creep cycles ${creeps}`);o.push("still waiting >15s: "+stuckList.slice(0,8).join(" | "));return o.join("\n")})()
