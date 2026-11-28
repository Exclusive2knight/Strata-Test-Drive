/* the Harbor Crest valet shift: start it, a guest pulls up at the kiosk, take the keys, park on B1 (paid), the guest leaves, bring the car
   back up to the kiosk (paid), your own car back afterwards */
(async()=>{const out=[],P=(ok,n,s)=>out.push(`${ok?"PASS":"FAIL"} ${n}: ${s}`);window.NOSEMI=1;setTrim("camry25",true);st.power=true;st.started=true;cars.length=0;Traffic.set_density("all",0);
const S0=SITES[0];siteLoad(S0);for(let i=0;i<120&&!S0.m;i++)await new Promise(r=>setTimeout(r,250));
const K=hvW(HV.stand[0],HV.stand[1]);resetCar({free:true,x:K[0]-20,y:K[1]-25,h:0});st.gear="P";
valetStart("hotel");const S=valetStandPt();for(let i=0;i<60&&!valetPool().length;i++)await new Promise(r=>setTimeout(r,250));
walkAction();if(!st.walk)return "could not get out";st.walk.x=S.x;st.walk.y=S.y;st.walk.z=0;
valetArrive();const T=VALET.task;if(!T)return "no guest";const rec=T.rec;await loadModel(TRIMS[rec.trim].mesh||TRIMS[rec.trim].model);
const cash0=ECON.cash;valetTake(rec);await new Promise(r=>setTimeout(r,300));const inGuest=VALET.cur===rec&&st.trim===rec.trim;
/* drive it down: put it on B1 in a bay away from the ramp, stopped in P, then get out */
const B=hvW(HV.stall[0],HV.stall[1]);GREF=-3.6;resetCar({free:true,x:B[0],y:B[1],h:0,z:-3.6});SIM(1,()=>{car.vx=0});st.gear="P";walkAction();
const parked1=VALET.lot.includes(rec),pay1=ECON.cash-cash0;P(inGuest&&parked1&&pay1>0,"park on B1",`drove ${TRIMS[rec.trim].name}; parked ${parked1} on level ${rec.level} at z ${(rec.z||0).toFixed(1)}; paid ${money2(pay1)}`);
/* the guest leaves: fetch, bring it up to the kiosk */
valetFetch();const F=VALET.task;st.walk.x=rec.x+2;st.walk.y=rec.y;st.walk.z=rec.z;valetTake(rec);await new Promise(r=>setTimeout(r,300));
resetCar({free:true,x:S.cx,y:S.cy,h:S.ch});SIM(1,()=>{car.vx=0});st.gear="P";const c1=ECON.cash;walkAction();
P(F&&F.type==="fetch"&&!VALET.lot.includes(rec)&&ECON.cash>c1&&!VALET.cur,"bring it back",`paid ${money2(ECON.cash-c1)}; your car back: ${st.trim==="camry25"}; shift total ${money2(VALET.earned)} for ${VALET.cars} cars`);
valetEnd();return out.join("\n")})()
