(async()=>{const out=[];setTrim("camry25",true);resetCar(STARTS.city);st.power=true;st.started=true;st.gear="P";car.vx=0;cars=[];spawnTraffic(170);
let over=0,overList=new Map(),stuckMax=0,stuck=new Map(),hardBrakes=0,redRun=0;const t0=performance.now();
for(let k=0;k<3000;k++){SIMSTEP(0.1);
  if(k%5===0){const A=cars.filter(c=>c.kind==="ai"&&c.wx!==undefined);const G=new Map();for(const c of A){const key=Math.floor(c.wx/8)+","+Math.floor(c.wy/8);(G.get(key)||G.set(key,[]).get(key)).push(c)}
    for(const c of A){const i=Math.floor(c.wx/8),j=Math.floor(c.wy/8);for(let a=-1;a<=1;a++)for(let b=-1;b<=1;b++)for(const o of G.get((i+a)+","+(j+b))||[]){if(o===c||o.wx===undefined)continue;if(Math.abs((o.wz||0)-(c.wz||0))>2)continue;
      if(obbSAT(c.wx,c.wy,c.wh,2.2,0.85,o.wx,o.wy,o.wh,2.2,0.85)){over++;const nm=(c.jn?"jn@"+(c.jn.n.ctrl||c.jn.n.kind)+c.jn.mv.t+(c.jn.n.x|0)+","+(c.jn.n.y|0):c.e.name)+"/"+(o.jn?"jn@"+(o.jn.n.ctrl||o.jn.n.kind)+o.jn.mv.t:o.e.name+(o.v<0.5?"(stopped)":""));overList.set(nm,(overList.get(nm)||0)+1)}}}}
  for(const c of cars){if(c.kind!=="ai")continue;if(c.brk&&c.v>8&&c._pv-c.v>0.6)hardBrakes++;c._pv=c.v;if(c.idle>30)stuck.set(c,(c.e&&c.e.name)+(c.jn?"(jn)":"")+"@"+(c.s|0))}}
out.push(`5 min, ${cars.length} cars: overlaps ${over/2} ${[...overList].sort((a,b)=>b[1]-a[1]).slice(0,8).map(x=>x[0]+":"+x[1]).join(", ")}`);
out.push(`stuck >30s: ${stuck.size} ${[...stuck.values()].slice(0,10).join(", ")}  hard brakes ${hardBrakes}  ms ${(performance.now()-t0)|0}`);
return out.join("\n")})()
