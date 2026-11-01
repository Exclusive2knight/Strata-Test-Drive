// find grass near the start, and watch a city plow drive and clear in a blizzard
(async()=>{const o=[];const S=STARTS.suburb||{x:car.px,y:car.py,h:car.psi};let g=null;for(let r=20;r<600&&!g;r+=20)for(let a=0;a<6.28&&!g;a+=0.3){const x=S.x+Math.cos(a)*r,y=S.y+Math.sin(a)*r,q=groundAt(x,y);if(q&&q.kind==="grass"){let n=0;for(let i=-3;i<=3;i++)for(let j=-3;j<=3;j++){const q2=groundAt(x+i*4,y+j*4);if(q2&&q2.kind==="grass")n++}if(n>=40)g=[x,y]}}
 o.push("grass spot "+JSON.stringify(g&&g.map(v=>Math.round(v))));
 await loadModel("wk_plow");st.started=true;st.power=true;st.wxReal=true;st.snowAcc=true;setWeather("blizzard",true);WXR.snow=0.7;resetCar(S);st.gear="P";
 for(let i=0;i<40;i++){weatherTick(0.1);if(cars.some(c=>c.plow))break}
 const p=cars.find(c=>c.plow);if(!p){o.push("no plow spawned");return o.join("\n")}const p0=[p.wx,p.wy];let cl0=0;for(const v of SNM.cl)if(v>0.5)cl0++;
 SIM(15,()=>{weatherTick(0.02)});let cl=0,sa=0;for(let k=0;k<SNM.cl.length;k++){if(SNM.cl[k]>0.5)cl++;if(SNM.sa[k]>0.2)sa++}
 o.push(`plow moved ${Math.hypot(p.wx-p0[0],p.wy-p0[1]).toFixed(0)} m at ${(p.v*2.237).toFixed(0)} mph, still in traffic: ${cars.includes(p)} · plowed cells ${cl0}->${cl} · salted ${sa} · plow at ${Math.round(p.wx)},${Math.round(p.wy)} h ${p.wh.toFixed(2)}`);
 window.PLOWAT=[p.wx,p.wy,p.wh];return o.join("\n")})()
