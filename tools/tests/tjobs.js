// the new gig jobs: repo (rollback), roadside, tow with the wrecker, plow route
(async()=>{const o=[];const go=async(k,svc,extra)=>{await loadModel(TRIMS[k].model);setTrim(k,true);cars=[];CCN.list=null;st.power=true;st.started=true;sys.epb=false;st.gear="D";EQ.load=null;EQ.hooked=false;if(TRL.on)trlSet(null,true);
  GIG.job=null;GIG.offer=null;GIG.svc=svc;GIG.online=true;if(extra)extra();gigOffer();if(!GIG.offer){o.push(svc+": no offer");return}const pay=GIG.offer.pay;gigAccept();const J=GIG.job;if(!J){o.push(svc+": not accepted");return}
  const before=ECON.cash;let steps=0;
  for(let n=0;n<40&&GIG.job;n++){const S=J.stops[J.i];resetCar({free:true,x:S.x+(S.kind==="assist"?3:0),y:S.y,h:S.h||0});car.vx=0;if(S.kind==="plowpt"){EQ.up=0;EQ.upT=0}for(let t=0;t<(S.secs||2)+4&&GIG.job&&J.stops[J.i]===S;t+=0.1){car.vx=0;gigTick(0.1)}steps++}
  o.push(`${svc} (${k}): offer $${pay.toFixed(0)} · ${steps} stops · paid $${(ECON.cash-before).toFixed(2)} · load=${!!EQ.load} trl=${TRL.kind} · job left=${!!GIG.job}`)};
 await go("wk_rollback_m","repo");await go("wk_rollback_m","tow");await go("wk_wrecker_m","tow");await go("wk_van_m","roadside");
 await go("wk_plow_m","plow",()=>{setWeather("snow",true);WXR.snow=0.5});await go("camry25","repo");
 return o.join("\n")})()
