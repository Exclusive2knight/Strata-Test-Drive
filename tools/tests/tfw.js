(async()=>{const out=[];const W_=new Map();const _c=window.crashFx;window.crashFx=function(v,w){W_.set(w+"@"+car.px.toFixed(0)+","+car.py.toFixed(0)+" v"+v.toFixed(1),1);return _c.apply(this,arguments)};
// 1. freeway under the Woodward N bridge: drive east on Hwy 7 north straight
setTrim("camry25",true);cars=[];st.power=true;st.started=true;sys.epb=false;st.gear="D";
const fw=EDGES.find(e=>e.type==="xway"&&Math.abs(e.a.y+1100)<1&&Math.abs(e.b.y+1100)<1);out.push("fw edge "+fw.a.x+"->"+fw.b.x+" L "+fw.L.toFixed(0));
let p=fpt(fw,1,30,laneOff(fw,1));resetCar({free:true,x:p[0],y:p[1],h:p[2]});car.vx=26;let zmax=-9,zmin=9,frames=new Set();
SIM(14,t=>{inp.thrT=0.35;inp.steerT=0;const M=me();frames.add(M.e.name);zmax=Math.max(zmax,car.zb||0);zmin=Math.min(zmin,car.zb||0)});
out.push(`under bridge: x ${car.px.toFixed(0)} z ${zmin.toFixed(2)}..${zmax.toFixed(2)} frames ${[...frames].join("|")} hits ${hits}`);
// 2. over the bridge on Woodward northbound
const wd=EDGES.find(e=>e.ov&&e.name==="Woodward Ave"&&e.a.y<-900);p=fpt(wd,1,5,laneOff(wd,1));resetCar({free:true,x:p[0],y:p[1],h:p[2]});car.vx=15;zmax=-9;frames=new Set();
SIM(16,t=>{inp.thrT=0.3;const M=me();frames.add(M.e.name);zmax=Math.max(zmax,car.zb||0)});out.push(`over bridge: y ${car.py.toFixed(0)} zmax ${zmax.toFixed(2)} frames ${[...frames].join("|")} hits ${hits}`);
// 3. traffic: lots of cars, 150 s
cars=[];resetCar(STARTS.hwy);car.vx=0;st.gear="P";spawnTraffic(160);let rampVisits=0,rampDone=0;const seen=new Map();let stuckMax=0;
for(let k=0;k<1500;k++){SIMSTEP(0.1);for(const c of cars){if(c.kind!=="ai")continue;if(c.e&&c.e.ow&&!c.jn){if(!seen.has(c))seen.set(c,0);}if(seen.has(c)&&c.e&&!c.e.ow&&!c.jn&&seen.get(c)===0){seen.set(c,1);rampDone++}}}
let stuck=[];for(const c of cars)if(c.kind==="ai"&&c.idle>40)stuck.push((c.e.name||"?")+"@"+c.s.toFixed(0)+(c.jn?"(jn)":""));
out.push(`traffic: ${cars.length} cars, used a ramp ${seen.size}, finished ramp ${rampDone}, stuck>40s ${stuck.length}: ${stuck.slice(0,8).join(", ")}`);
out.push([...W_.keys()].join(" | "));return out.join("\n")})()
