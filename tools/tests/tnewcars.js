// the previous-generation cars and the Sonata: they load, drive (0-60 time, top speed after 25 s), and nothing goes NaN
(async()=>{const K=Object.keys(TRIMS).filter(k=>/(_18_|camry22|4runner22|chr21|corolla_im|highlander19|lc200|prius20|sequoia21|sienna19|tacoma22|tundra20|gx460|lx570|nx300|rx350_21|xc90_14|xc60_16|v60cc17|hy_sonata)/.test(k));const o=[];
 for(const k of K){try{await loadModel(TRIMS[k].model)}catch(e){o.push(k+" MODEL FAIL "+e)}setTrim(k,true);applyVehicle(TRIMS[k]);resetCar(STARTS.hwy);cars=cars.filter(c=>c.kind!=="ai");st.power=true;st.started=true;st.gear="D";sys.epb=false;car.vx=0;inp.thrT=1;inp.brkT=0;let t60=null,t=0,bad=false;
   SIM(16,()=>{t+=0.02;if(!isFinite(car.vx)||!isFinite(car.px))bad=true;if(t60===null&&car.vx>=26.82)t60=t});inp.thrT=0;
   o.push(`${k.padEnd(22)} ${(TRIMS[k].desc||"").padEnd(52)} 0-60 ${t60?t60.toFixed(1):"--"} s  v25 ${(car.vx*2.237).toFixed(0)} mph ${bad?"NaN!":""} cluster ${cluAnalog()?"needles":"digital"} ${MODELS[TRIMS[k].model]?"":"(no model)"}`)}
 return o.join("\n")})()
