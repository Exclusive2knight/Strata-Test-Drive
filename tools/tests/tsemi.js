/* v37.5 semi trucks: spawn several near the freeway and town, run 3 minutes of traffic; none should get stuck, the trailer angle stays sane,
   and nobody drives through a trailer */
(async()=>{const out=[];setTrim("camry25",true);resetCar({x:2600,y:-1300,h:-Math.PI/2});st.power=true;st.started=true;st.gear="P";car.vx=0;cars=[];spawnTraffic(80);
for(const k of [...SEMI.T.slice(0,3),...SEMI.R.slice(0,3)])semiM(k);for(let i=0;i<120&&!SEMI.T.slice(0,3).concat(SEMI.R.slice(0,3)).every(k=>TXM["semi_"+k].ok);i++)await new Promise(r=>setTimeout(r,250));
G().fullCars=12;let n=0;for(let i=0;i<40&&n<4;i++){SEMI.t=0;SEMI.next={t:SEMI.T[i%3],r:SEMI.R[i%3]};semiTick(0.1);n=cars.filter(c=>c.semi).length}
out.push("semis "+n+": "+cars.filter(c=>c.semi).map(c=>c.e.name).join(", "));
let maxA=0,stuck=new Set(),thru=0;
for(let k=0;k<1800;k++){SIMSTEP(0.1);semiTick(0.1);if(k%10)continue;
  for(const c of cars){if(!c.semi||!c.semi.g)continue;maxA=Math.max(maxA,Math.abs(wrapPi(c.wh-c.semi.th)));if(c.idle>60)stuck.add(c.semi.unit+"@"+c.e.name);
    const g=c.semi.g,K=c.semi.K;if(!K)continue;for(const o of cars){if(o===c||o.kind!=="ai"||o.semi)continue;const dx=o.wx-K[0],dy=o.wy-K[1],a=-(dx*Math.cos(c.semi.th)+dy*Math.sin(c.semi.th)),l=Math.abs(-dx*Math.sin(c.semi.th)+dy*Math.cos(c.semi.th));if(a>1&&a<g.r1-1&&l<1.2&&Math.abs((o.wz||0)-(c.wz||0))<2)thru++}}}
out.push(`3 min: semis now ${cars.filter(c=>c.semi).length}, max trailer angle ${(maxA*57.3).toFixed(0)} deg, stuck ${stuck.size} ${[...stuck].join(" ")}, cars inside a trailer ${thru}`);
out.push(cars.filter(c=>c.semi).map(c=>`${c.semi.unit} ${c.e.name} v${c.v.toFixed(0)}`).join(", "));
return out.join("\n")})()
