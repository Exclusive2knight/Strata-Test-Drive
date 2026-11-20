(async()=>{const out=[];setTrim("camry25",true);st.started=true;RWX_TRY=true;GT.min=10*60;RW.day=-1;rwTick();const Z=RW.xz;if(!Z)return "no crossover zone";{const q=fpt(Z.e,Z.dc,Z.sX0+150,laneOff(Z.e,Z.e.n-1)+LANE/2+8);resetCar({free:true,x:q[0],y:q[1],h:car.psi})}

  st.power=true;st.started=true;st.gear="P";car.vx=0;cars=[];{const q=fpt(Z.e,Z.dc,Z.sX0+150,laneOff(Z.e,Z.e.n-1)+LANE/2+8);resetCar({free:true,x:q[0],y:q[1],h:car.psi})}spawnTraffic(170);RW.day=-1;rwTick();const Z2=RW.xz;   /* the zone again: its drums are cars, and the list was just emptied */
  const passed=new Set();
let over=0,overList=new Map(),stuckMax=0,stuck=new Map(),hardBrakes=0,redRun=0;const t0=performance.now();
for(let k=0;k<1800;k++){SIMSTEP(0.1);
  if(k%5===0&&Z2){for(const c of cars)if(c.kind==="ai"&&c.e===Z2.e&&c.dir===Z2.dc&&c.s>Z2.sW0+50&&c.s<Z2.sW1)passed.add(c)}
  if(k%5===0){const A=cars.filter(c=>c.kind==="ai"&&c.wx!==undefined);const G=new Map();for(const c of A){const key=Math.floor(c.wx/8)+","+Math.floor(c.wy/8);(G.get(key)||G.set(key,[]).get(key)).push(c)}
    for(const c of A){const i=Math.floor(c.wx/8),j=Math.floor(c.wy/8);for(let a=-1;a<=1;a++)for(let b=-1;b<=1;b++)for(const o of G.get((i+a)+","+(j+b))||[]){if(o===c||o.wx===undefined)continue;if(Math.abs((o.wz||0)-(c.wz||0))>2)continue;
      if(obbSAT(c.wx,c.wy,c.wh,2.2,0.85,o.wx,o.wy,o.wh,2.2,0.85)){over++;const nm=(c.jn?"jn@"+(c.jn.n.ctrl||c.jn.n.kind)+c.jn.mv.t+(c.jn.n.x|0)+","+(c.jn.n.y|0):c.e.name)+"/"+(o.jn?"jn@"+(o.jn.n.ctrl||o.jn.n.kind)+o.jn.mv.t:o.e.name+(o.v<0.5?"(stopped)":""));overList.set(nm,(overList.get(nm)||0)+1)}}}}
  for(const c of cars){if(c.kind!=="ai")continue;if(c.brk&&c.v>8&&c._pv-c.v>0.6)hardBrakes++;c._pv=c.v;if(c.idle>60)stuck.set(c,(c.e&&c.e.name)+(c.jn?"(jn)":"")+"@"+(c.s|0))}}
out.push(`5 min, ${cars.length} cars: overlaps ${over/2} ${[...overList].sort((a,b)=>b[1]-a[1]).slice(0,8).map(x=>x[0]+":"+x[1]).join(", ")}`);
out.push(`stuck >60s: ${stuck.size} ${[...stuck.values()].slice(0,10).join(", ")}  hard brakes ${hardBrakes}  ms ${(performance.now()-t0)|0}`);
out.push(`crossover on ${Z2&&Z2.e.name}: ${passed.size} closed-side cars ran through the shared side`);return out.join("\n")})()
