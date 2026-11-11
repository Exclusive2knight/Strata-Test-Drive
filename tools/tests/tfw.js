// freeway test for the current world: I-38 through its sunken stretches, the cross streets over the cut, the service drives, and traffic using the ramps
(async()=>{const out=[];const W_=new Map();const _c=window.crashFx;window.crashFx=function(v,w){W_.set(w+"@"+car.px.toFixed(0)+","+car.py.toFixed(0),1);return _c.apply(this,arguments)};
setTrim("camry25",true);cars=[];st.power=true;st.started=true;sys.epb=false;st.gear="D";st.aeb=false;
const drive=(label,x,y,h,v,T,thr)=>{   /* holds its lane like a driver would */resetCar({free:true,x,y,h});car.vx=v;let zmin=9,zmax=-9;const fr=new Set(),h0=hits;
  let o0=null;SIM(T,()=>{inp.thrT=car.vx<v?thr:0;inp.brkT=0;try{const M=me(),he=wrapPi(car.psi-M.h);if(o0===null)o0=M.off;inp.steerT=clamp(0.25*(M.off-o0)+1.2*he,-0.4,0.4)}catch(e){inp.steerT=0}try{const M=me();fr.add(M.e.name)}catch(e){}zmin=Math.min(zmin,car.zb||0);zmax=Math.max(zmax,car.zb||0)});
  out.push(`${label}: to ${car.px.toFixed(0)},${car.py.toFixed(0)} z ${zmin.toFixed(1)}..${zmax.toFixed(1)} roads ${[...fr].join("|")} hits ${hits-h0}`)};
// 1. I-38 eastbound (right lane) through County Rd 3's cut, then Woodward's, under the bridges
{const e=EDGES.find(e=>e.type==="xway"&&e.a.x===-1420&&e.b.x===-580),p=fpt(e,1,5,laneOff(e,0));drive("I-38 EB through the Woodward cut",-1700,p[1],0,27,40,0.4)}
{const e=EDGES.find(e=>e.type==="xway"&&e.a.x===-4020&&e.b.x===-3180),p=fpt(e,-1,5,laneOff(e,0));drive("I-38 WB through the County Rd 3 cut",p[0],p[1],p[2],27,30,0.4)}
// 2. Woodward Ave northbound across the cut at street level
{const e=EDGES.find(e=>e.name==="Woodward Ave"&&e.ov&&e.a.y<-1400&&e.b.y>-1600||e.name==="Woodward Ave"&&e.ov),p=fpt(e,e.a.y<e.b.y?1:-1,2,laneOff(e,0));drive("Woodward Ave over the cut",p[0],p[1]-60,Math.PI/2,13,16,0.3)}
// 3. the eastbound service drive from Woodward past the river to Maple
{const e=EDGES.find(e=>e.type==="sd"&&e.a.x===-850&&e.b.x===850),p=fpt(e,1,5,laneOff(e,0));drive("Service Dr EB over the river",p[0],p[1],0,17,60,0.3)}
// 4. traffic: ramps, service drives and the freeway, 120 s
cars=[];resetCar({free:true,x:-1000,y:-1300,h:0});car.vx=0;st.gear="P";spawnTraffic(70);const seen=new Map(),stop=new Map();let ov=0;const ovS=new Set();
SIM(120,t=>{for(const c of cars){if(c.kind!=="ai"||!c.e)continue;if(c.e.type==="sd"||c.e.type==="ramp")seen.set(c.e.type+" "+c.e.name,(seen.get(c.e.type+" "+c.e.name)||0)+1);
    if((c.e.type==="sd"||c.e.type==="ramp")&&(c.v||0)<0.2)stop.set(c,(stop.get(c)||0)+0.02);else stop.delete(c)}
  if(Math.round(t*50)%25===0){const A=cars.filter(c=>c.kind==="ai"&&c.wx!==undefined);for(let i=0;i<A.length;i++)for(let j=i+1;j<A.length;j++){const a=A[i],b=A[j];if(Math.abs((a.wz||0)-(b.wz||0))>2)continue;
      if(Math.hypot(a.wx-b.wx,a.wy-b.wy)<4&&obbSAT(a.wx,a.wy,a.wh,2.2,0.85,b.wx,b.wy,b.wh,2.2,0.85)){ov++;ovS.add((a.e&&a.e.name)+"/"+(b.e&&b.e.name)+"@"+(a.wx|0)+","+(a.wy|0))}}}});
out.push("traffic 120 s, frames on ramps / service drives: "+[...seen].sort((a,b)=>b[1]-a[1]).slice(0,10).map(([k,v])=>k+" "+v).join(", "));
out.push("stopped > 25 s on a ramp or service drive: "+([...stop].filter(([c,t])=>t>25).map(([c])=>c.e.name+"@"+(c.wx|0)+","+(c.wy|0)).join(" ")||"none"));
out.push("overlaps "+ov+" "+[...ovS].slice(0,6).join(" "));out.push("crashes: "+([...W_.keys()].slice(0,6).join(" ")||"none"));
return out.join("\n")})()
