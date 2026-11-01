// cyclists at junctions: none should sit stuck in or at an intersection
(async()=>{const S0=window.S0||"city";resetCar(STARTS[S0]||STARTS.city);st.started=true;st.gear="P";car.vx=0;cars=cars.filter(c=>c.kind!=="bike");spawnTraffic(30);spawnBikes(25);TOD.t=1e9;
 const T=new Map();let through=0;
 SIM(100,()=>{for(const c of cars){if(c.kind!=="bike")continue;const k=c.jn?"jn":"";if(c.v<0.1){T.set(c,(T.get(c)||0)+0.02)}else T.set(c,0);if(c.jn&&!c._wasJ)through++;c._wasJ=!!c.jn}});
 const st_=[...T].filter(([c,t])=>t>12).map(([c,t])=>`${c.e.name}${c.jn?"(IN junction "+c.jn.n.ctrl+")":" at "+(c.mvNode&&c.mvNode.ctrl)} ${t.toFixed(0)}s who ${c.lw==="me"?"me":c.lw==="ctrl"?"ctrl":c.lw?c.lw.kind+(c.lw.jn?"(jn)":""):"-"} lg ${(c.lg||0).toFixed(1)} cg ${c.cg===Infinity?"go":(c.cg||0).toFixed(1)} wt ${(c.waitT||0).toFixed(0)}`);
 return `bikes ${cars.filter(c=>c.kind==="bike").length}, junction entries ${through}, stuck >12s: ${st_.length}\n`+st_.slice(0,10).join("\n")})()
