(async()=>{const o=[];const k="esc_phev";await loadModel(TRIMS[k].model);setTrim(k,true);cars=[];st.power=true;st.started=true;sys.epb=false;st.gear="D";resetCar(STARTS.hwy);const H=car.hyb;
o.push("modes: "+TRIMS[k].modeNames.join("/")+" · battery modes "+TRIMS[k].eModes.map(x=>x[1]).join("/"));
const run=(lbl,soc)=>{H.soc=soc;H.eng=false;let on=0,n=0;SIM(12,()=>{inp.thrT=car.vx<25?0.5:0.15;n++;if(H.eng)on++});return `${lbl}: engine on ${Math.round(on/n*100)}% · soc ${soc.toFixed(2)}→${H.soc.toFixed(2)} · ${(car.vx*2.237).toFixed(0)} mph`};
st.eMode="hyb";o.push(run("Auto EV",0.8));act("evMode");o.push(st.eMode+" "+run("EV Now",0.8));act("evMode");o.push(st.eMode+" "+run("EV Later",0.6));act("evMode");o.push(st.eMode+" "+run("EV Charge",0.4));
const k2="rav4g_adv";setTrim(k2,true);o.push("rav4 adv terrain: "+JSON.stringify(terrList(k2)));return o.join("\n")})()
