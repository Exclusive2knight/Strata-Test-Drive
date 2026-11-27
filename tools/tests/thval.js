/* v38: Harbor Crest valet takes your car down to B1 and brings it back; the casino games pay out */
(async()=>{const out=[];const H=SITES[0];siteLoad(H);for(let k=0;k<200&&!H.m;k++)await new Promise(r=>setTimeout(r,250));if(!H.m)return "hotel did not load";
const [x,y]=hvW(HV.stand[0],HV.stand[1]);resetCar({free:true,x,y:y-1,h:Math.PI});car.vx=0;st.gear="P";st.started=true;st.power=true;
out.push("at stand: "+hvAtStand()+" button: "+(HV.state==="idle"&&hvAtStand()));const c0=ECON.cash;walkAction();out.push(`after tap: walking ${!!st.walk} valet ${HV.state}`);
let zMin=9;for(let i=0;i<600&&HV.state==="in";i++){hvTick(0.1);zMin=Math.min(zMin,car.zb)}out.push(`parked: ${HV.state} car z ${car.zb.toFixed(2)} (B1 -3.6) lowest ${zMin.toFixed(2)}`);
st.walk.x=x+2;st.walk.y=y;const c=walkCtx();out.push("kiosk button: "+(c&&c.label));walkAction();
for(let i=0;i<600&&HV.state==="out";i++)hvTick(0.1);out.push(`back: ${HV.state} at stand ${Math.hypot(car.px-x,car.py-y).toFixed(1)} m z ${car.zb.toFixed(2)} paid ${(c0-ECON.cash).toFixed(0)}`);
st.walk.x=car.px-Math.sin(car.psi)*1.25;st.walk.y=car.py+Math.cos(car.psi)*1.25;walkGetIn();out.push(`got in: ${!st.walk} valet ${HV.state}`);
/* the casino */ECON.cash=1e6;const c1=ECON.cash;casOpen(true);CAS.bet=100;for(let i=0;i<2000;i++)casAct("spin");const sl=(ECON.cash-c1)/(2000*100);
const c2=ECON.cash;for(let i=0;i<2000;i++)casAct("rl","red");const rl=(ECON.cash-c2)/(2000*100);
const c3=ECON.cash;for(let i=0;i<2000;i++){casAct("deal");let g=0;while(CAS.bj&&!CAS.bj.done&&bjSum(CAS.bj.P)<17&&g++<9)casAct("hit");if(CAS.bj&&!CAS.bj.done)casAct("stand")}const bj=(ECON.cash-c3)/(2000*100);
out.push(`casino return per $ bet: slots ${(1+sl).toFixed(3)} roulette red ${(1+rl).toFixed(3)} blackjack ${(1+bj).toFixed(3)} · panel shown ${!$("casino").hidden}`);casOpen(false);
return out.join("\n")})()
