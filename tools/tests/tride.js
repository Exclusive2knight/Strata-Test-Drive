// each car should start sitting at its real ride height: body settled (no drop/bounce) and car.height already at the target
(async()=>{const out=[];const ks=Object.keys(TRIMS).filter(k=>SUSR[k]).filter((k,i)=>i%9===0).slice(0,40);
 for(const k of ks){try{await loadModel(TRIMS[k].model)}catch(e){}setTrim(k,true);st.started=true;st.power=true;st.gear="P";car.vx=0;
  let z0=null,zmin=9,zmax=-9,h0=car.height;SIM(2.5,t=>{if(t<0.05)z0=car.zb;zmin=Math.min(zmin,car.zb);zmax=Math.max(zmax,car.zb)});
  out.push(`${k.padEnd(26)} rideH ${st.rideH==null?'-':st.rideH.toFixed(3)} height start ${h0.toFixed(3)} now ${car.height.toFixed(3)} zb swing ${((zmax-zmin)*1000).toFixed(0)}mm air ${airLv(k)?airLv(k).sys:''}`)}
 return out.join("\n")})()
