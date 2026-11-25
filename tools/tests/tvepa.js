(async()=>{const out=[];
for(const k of ["cad_vistiq_plat","cad_vistiq_lux","escalade"]){await loadModel(TRIMS[k].model);setTrim(k,true);const S=pkSys();out.push(`${k}: ${S?S.name:"none"} has=${has("autopark")}`)}
setTrim("cad_vistiq_plat",true);st.started=true;st.power=true;st.gear="D";paChoose("perp");paPanel();out.push("panel: "+document.getElementById("paHead").textContent+" | "+document.getElementById("paSub").textContent);paChoose(null);
dmgHit(12,"a test barrier");vstOpen();out.push("vst log "+VST.log.length+": "+(VST.log[0]||{}).x);vstClose();
return out.join("\n")})()
