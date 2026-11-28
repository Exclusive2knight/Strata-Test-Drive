/* hitching a 53-ft semi trailer to a heavy-duty pickup: it loads, follows the fifth wheel round a turn (cutting the corner), adds its weight
   (slower to speed up), jackknifes when you reverse hard into a turn, drops and couples again when you back the fifth wheel under the kingpin */
(async()=>{const out=[],P=(ok,n,s)=>out.push(`${ok?"PASS":"FAIL"} ${n}: ${s}`);window.NOSEMI=1;
const k=Object.keys(TRIMS).find(k=>/Super Duty|F-250|F-350|Silverado HD|Sierra HD|2500/i.test((TRIMS[k].group||"")+" "+TRIMS[k].name)&&TRIMS[k].real);if(!k)return "no heavy-duty pickup";setTrim(k,true);
resetCar({free:true,x:1300,y:-300,h:0});st.power=true;st.started=true;sys.epb=false;cars.length=0;Traffic.set_density("all",0);
const t0=performance.now();trlSet("semi",true);for(let i=0;i<80&&!(TXM["semi_dryvan_wabash"]&&TXM["semi_dryvan_wabash"].ok);i++)await new Promise(r=>setTimeout(r,250));
const K=TRL.on;trlTick(0.02);out.push(`${TRIMS[k].name}: hitched ${!!K} model ${!!(TXM["semi_dryvan_wabash"]||{}).ok} kingpin to axle ${K&&K.Lt.toFixed(1)} m, length ${K&&K.len.toFixed(1)} m`);
/* pull away: 0-30 mph with and without it */
const acc=()=>{resetCar({free:true,x:1300,y:-300,h:0});st.gear="D";let t=0;SIM(40,tt=>{inp.thrT=inp.thr=1;inp.brkT=inp.brk=0;inp.steerT=inp.steer=0;t=tt;if(car.vx>13.4)return false});return t};
const tW=acc();const keep=TRL.on;TRL.on=null;TRL.mass=0;const tN=acc();TRL.on=keep;TRL.mass=keep.mass;
P(K&&tW>tN*1.3,"weight",`0-30 mph ${tW.toFixed(1)} s with it, ${tN.toFixed(1)} s without`);
/* a 90 degree right turn at 4 m/s: the trailer swings behind and straightens out */
resetCar({free:true,x:1300,y:-300,h:0});trlSet(null,true);trlSet("semi",true);st.gear="D";let maxA=0;SIM(25,tt=>{inp.thrT=inp.thr=car.vx<4?0.7:0;inp.brkT=inp.brk=car.vx>5?0.3:0;inp.steerT=inp.steer=tt>3&&tt<9?-0.6:0;trlTick(0.02);maxA=Math.max(maxA,Math.abs(wrapPi(TRL.h-car.psi)))});
const endA=Math.abs(wrapPi(TRL.h-car.psi));out.push(`debug v ${car.vx.toFixed(1)} pos ${car.px.toFixed(0)},${car.py.toFixed(0)} gear ${st.gear} epb ${sys.epb}`);P(maxA>0.2&&endA<0.1&&!TRL.jk,"turn",`truck turned ${(Math.abs(wrapPi(car.psi))*57.3).toFixed(0)}°, trailer angle up to ${(maxA*57.3).toFixed(0)}°, ${(endA*57.3).toFixed(1)}° after straightening`);
/* reverse with full lock: it jackknifes */
let jk=false;st.gear="R";SIM(20,()=>{inp.thrT=inp.thr=Math.abs(car.vx)<2?0.7:0;inp.steerT=inp.steer=0.9;trlTick(0.02);if(TRL.jk){jk=true;return false}});P(jk,"jackknife",`reversing on full lock: ${jk?"jackknifed":"never"}`);
/* drop it, pull ahead 15 m, back straight under it: it couples again */
resetCar({free:true,x:1300,y:-300,h:0});trlSet(null,true);trlSet("semi",true);st.gear="D";car.vx=0;trlDrop();const dropped=!!TRL.parked;
st.gear="D";SIM(8,()=>{inp.thrT=inp.thr=car.vx<2?0.6:0;inp.steerT=inp.steer=0});st.gear="R";let back=false,dmin=99,why='';SIM(30,()=>{if(TRL.parked){const H=trlHitch(TRL.parked.K),C=trlCoupler(TRL.parked);const d=Math.hypot(H[0]-C[0],H[1]-C[1]);if(d<dmin){dmin=d;why=`d ${d.toFixed(2)} v ${car.vx.toFixed(2)} ang ${Math.abs(wrapPi(car.psi-TRL.parked.h)).toFixed(2)} brk ${inp.brk.toFixed(2)} rctb ${sys.rctbOn} aeb ${!!sys.aebR}`}}inp.brkT=inp.brk=0;inp.thrT=inp.thr=Math.abs(car.vx)<0.6?0.45:0;inp.steerT=inp.steer=0;trlParkedTick(0.02);if(TRL.on){back=true;return false}});
P(dropped&&back,"drop and couple",`dropped ${dropped}, coupled again by backing under it: ${back} (closest ${why})`);
trlSet(null,true);return out.join("\n")})()
