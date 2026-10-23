SETUP={"drive":"(async()=>{const k='camry25';setTrim(k,true);st.power=true;st.started=true;st.gear='D';sys.epb=false;resetCar(STARTS.city);})()",
"charge":"(async()=>{const k=Object.keys(TRIMS).find(k=>TRIMS[k].tesla);await loadModel(TRIMS[k].model);setTrim(k,true);st.power=true;st.started=true;st.gear='P';const p=stnWorld('chargers')[5]||stnWorld('chargers')[0];resetCar({free:true,x:p[0]+1.5,y:p[1],h:0});car.hyb.soc=0.2;sys.fuel='plug';})()",
"garage":"(async()=>{setTrim('camry25',true);st.power=true;st.started=true;st.gear='D';resetCar({free:true,x:GAR.cx-18,y:GAR.cy+12,h:0,z:garZ(1,0,-18)});})()",
"proving":"(async()=>{setTrim('camry25',true);st.power=true;st.started=true;st.gear='D';const p=STARTS.proving||STARTS.tc||Object.values(STARTS).find(s=>/prov|test/i.test(s.name));resetCar(p);})()",
"w2rose":"(async()=>{setTrim('camry25',true);st.power=true;st.started=true;st.gear='D';resetCar(STARTS.suburb);for(let i=0;i<40&&!SCN.w2p;i++)await new Promise(r=>setTimeout(r,500));})()",
"w2fair":"(async()=>{setTrim('camry25',true);st.power=true;st.started=true;st.gear='D';resetCar(STARTS.fairhaven);for(let i=0;i<40&&!SCN.w2p;i++)await new Promise(r=>setTimeout(r,500));})()",
"w2city":"(async()=>{setTrim('camry25',true);st.power=true;st.started=true;st.gear='D';resetCar(STARTS.city);for(let i=0;i<40&&!SCN.w2p;i++)await new Promise(r=>setTimeout(r,500));})()"}
