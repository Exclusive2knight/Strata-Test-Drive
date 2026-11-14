// the Kestrel Tunnel: drive both carriageways through the cuts and bores at 60 mph holding the lane; no hits, the car stays on the road surface
(async()=>{const out=[];const W_=new Map();const _c=window.crashFx;window.crashFx=function(v,w){W_.set(w+"@"+car.px.toFixed(0)+","+car.py.toFixed(0),1);return _c.apply(this,arguments)};
setTrim("camry25",true);cars=[];st.power=true;st.started=true;sys.epb=false;st.gear="D";st.aeb=false;
out.push(`tunnel ${TUN.on} bores y ${TUN.y0|0}..${TUN.y1|0} cuts ${TUN.yc0|0}..${TUN.yc1|0}`);
const drive=(label,x,y,h,v,T)=>{resetCar({free:true,x,y,h});car.vx=v;let dzMax=0;const h0=hits;let o0=null,lit=0,n=0;
  SIM(T,()=>{inp.thrT=car.vx<v?0.4:0;inp.brkT=0;try{const M=me(),he=wrapPi(car.psi-M.h);if(o0===null)o0=M.off;inp.steerT=clamp(0.25*(M.off-o0)+1.2*he,-0.4,0.4)}catch(e){inp.steerT=0}
    const g=groundAt(car.px,car.py);dzMax=Math.max(dzMax,Math.abs((car.zb||0)-g.h));if(tunAt(car.px,car.py)){n++;if(hlOn())lit++}});
  out.push(`${label}: to ${car.px.toFixed(0)},${car.py.toFixed(0)} v ${car.vx.toFixed(1)} max |body-ground| ${dzMax.toFixed(2)} hits ${hits-h0} auto lights in tunnel ${n?Math.round(lit/n*100):0}%`)};
drive("northbound",TUN.xc+18.6,TUN.yc0-120,Math.PI/2,27,20);
drive("southbound",TUN.xc-18.6,TUN.yc1+120,-Math.PI/2,27,20);
cars=[];resetCar({free:true,x:TUN.xc+60,y:2470,h:0});car.vx=0;st.gear="P";spawnTraffic(60);let inT=0,ov=0;const seen=new Set();
SIM(60,t=>{for(const c of cars){if(c.kind!=="ai"||c.wx===undefined)continue;if(tunAt(c.wx,c.wy)){seen.add(c)}}
  if(Math.round(t*50)%25===0){const A=cars.filter(c=>c.kind==="ai"&&c.wx!==undefined&&tunAt(c.wx,c.wy));for(let i=0;i<A.length;i++)for(let j=i+1;j<A.length;j++){const a=A[i],b=A[j];if(Math.hypot(a.wx-b.wx,a.wy-b.wy)<4&&obbSAT(a.wx,a.wy,a.wh,2.2,0.85,b.wx,b.wy,b.wh,2.2,0.85))ov++}}});
out.push("traffic through the tunnel in 60 s: "+seen.size+" cars, overlaps "+ov);
out.push("crashes: "+([...W_.keys()].slice(0,6).join(" ")||"none"));return out.join("\n")})()
