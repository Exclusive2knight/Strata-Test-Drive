(async()=>{const o=[];const keys=Object.keys(TRIMS).filter(k=>/^(mz_|vw_|toy_rav4_26|ct_|ms20|mx20)/.test(k)||["m3_std","ms_awd","mx_awd","av_res","cor_res","rav4h_lim"].includes(k)||TRIMS[k].model==="modely"||TRIMS[k].model==="nautilus");let bad=[];
for(const k of keys){try{await loadModel(TRIMS[k].model);setTrim(k,true);cars=[];st.power=true;st.started=true;sys.epb=false;st.gear="D";resetCar(STARTS.hwy);SIM(3,()=>{inp.thrT=1});const sp=car.vx;
  for(let i=0;i<TRIMS[k].modes;i++){st.mode=i;dmApply&&0}drawCluster();SCR.page="home";drawScreen(0.1);if(!(sp>5))bad.push(k+" slow "+sp.toFixed(1))}catch(e){bad.push(k+": "+e.message)}}
o.push(keys.length+" trims tested; problems: "+(bad.join(" | ")||"none"));
o.push("ORDER has city? "+ORDER.some(k=>TRIMS[k].model.startsWith("city_"))+"; city models loaded: "+Object.keys(MODELS).filter(k=>k.startsWith("city_")).length);
o.push("modes: "+["mz_cx50_tpp","mz_cx90_phpp","vw_tiguan_se","vw_id4_prosa","toy_rav4_26_wood","ct_beast"].map(k=>k+"="+TRIMS[k].modeNames.join("/")+(TRIMS[k].evBtn?"+EV":"")).join("; "));
return o.join("\n")})()
