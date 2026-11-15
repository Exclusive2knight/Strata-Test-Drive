// v349 cars: Escalade ESV, Escalade IQ / IQL, XT5. Load, launch from rest for 8 s on the freeway start, check speed, no NaN, roll on a 40 m circle
(async()=>{const out=[];for(const k of ["escalade","esv_lux","esv_v","iq_lux","iql_psport","xt5_lux","xt5_sport"]){await loadModel(TRIMS[k].model);setTrim(k,true);resetCar({free:true,x:-3550,y:-12,h:0});
  st.power=true;st.started=true;st.gear="D";car.vx=0;cars=[];let v0=0;const T=TRIMS[k];
  let t60=null;sys.epb=false;SIM(9,(t)=>{inp.thr=1;if(t60===null&&car.vx>26.8)t60=t});
  if(typeof keys!=="undefined")keys.up=false;
  out.push(`${k} (${T.model}, ${PRICE[k]}): ${(car.vx*2.237).toFixed(0)} mph after 9 s, 0-60 ${t60===null?"-":t60.toFixed(1)+" s"}, nan ${isNaN(car.px+car.vx)} sus ${!!(T.sus)} lineup ${ORDER.includes(k)}`)}
 return out.join("\n")})()
