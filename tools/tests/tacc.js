(()=>{const r=[];
 // settings buttons: open the drawer on Display and click them
 st.tab="display";try{renderTab()}catch(e){r.push("renderTab err "+e)}
 const q=s=>document.querySelector(s);
 const b4=q('[data-set="clockX:4"]');r.push("clock btn "+!!b4);if(b4)b4.click();r.push("clockX="+st.clockX+" mul="+clockMul());
 const bf=q('[data-set^="rflash:"]');if(bf)bf.click();r.push("rflash="+st.rflash);
 const bm=q('[data-set^="rmot:"]');if(bm)bm.click();r.push("rmot="+st.rmot);
 let P={};try{P=JSON.parse(localStorage.getItem("strata.prefs")||"{}")}catch(e){}r.push("saved "+JSON.stringify({c:P.clockX,f:P.rflash,m:P.rmot}));
 const bf2=q('[data-set^="rflash:"]');if(bf2)bf2.click();r.push("rflash after 2nd tap="+st.rflash);
 const b1=q('[data-set="clockX:1"]');if(b1)b1.click();const bm2=q('[data-set^="rmot:"]');if(bm2)bm2.click();
 r.push("ver strata.ver="+localStorage.getItem("strata.ver")+" APP_VER="+APP_VER+" BUILD="+BUILD_VER+" news="+document.getElementById("newsVer").textContent.slice(0,40));
 return r.join("\n")})()
