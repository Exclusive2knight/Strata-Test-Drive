// police pull over an AI speeder: cop lights up, the speeder stops on the shoulder, both drive on afterwards
(async()=>{try{await loadModel("city_police")}catch(e){}st.started=true;resetCar(STARTS.hwy);cars=cars.filter(c=>c.kind!=="ai");const M=me(),A=aheadOnRoad(M,200);
 const cop=newCar(A.e,A.dir,A.s,0);cop.mdl="city_police";const tg=newCar(A.e,A.dir,A.s+90,0);tg.rageT=60;cars.push(cop,tg);PULL.t=0;PULL.cur=null;SIM(0.1,()=>{});if(PULL.cur){PULL.cur.tg=tg;PULL.cur.cop=cop}const o=[];let ph="";
 SIM(70,()=>{const P=PULL.cur;const p=P?P.ph:"none";if(p!==ph){o.push(`${p} @${(P?P.t:0).toFixed(1)} gap ${Math.hypot(cop.wx-tg.wx,cop.wy-tg.wy).toFixed(0)} tg v ${tg.v.toFixed(1)}`);ph=p}});
 o.push(`end: tg v ${tg.v.toFixed(1)} kind ${tg.kind} pullH ${!!tg.pullH}, cop v ${cop.v.toFixed(1)}`);return o.join("\n")})()
