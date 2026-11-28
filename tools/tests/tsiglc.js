// #189: hands-free systems with automatic lane change (Super Cruise on the GMC Sierra Denali and HUMMER EV) change lanes on the signal and when passing,
// even on trims whose plain lane centring ignores the signal (noSigLC). Expect "moved 3.7 m" for those; the Model Y (Autopilot, no auto lane change) still stays put.
(async()=>{const out=[];for(const [trim,alc] of [["sierra_den",true],["hummerpu",true],["ty_lrawd",false],["camry25",false]]){try{setTrim(trim,true)}catch(e){out.push("setTrim "+e);continue}
for(const mode of ["signal","pass"]){resetCar(STARTS.hwy);cars=[];st.power=true;sys.epb=false;st.gear="D";st.acc=false;st.pilot=false;car.vx=26;hits=0;inp.thrT=0;inp.brkT=0;inp.steerT=0;EV.t=1e9;sys.pilotLC=null;st.signal=0;
 act("pilot");st.autoLC=alc&&has("autoLC");st.accSet=29;if(mode==="pass"){placeTest("slow")}
 let M0=null,states={},maxD=0,sigT=0;SIM(20,t=>{sys.handsT=0;const M=me();if(M0==null)M0=M.off;if(mode==="signal"&&t>1.5&&t<1.53){st.signal=-1;st.signalT=0;sys.userSig=true}if(st.signal)sigT+=0.02;maxD=Math.max(maxD,Math.abs(M.off-M0));states[sys.pilotState]=(states[sys.pilotState]||0)+1});
 out.push(`${trim} ${mode} noSigLC=${!!TRIMS[trim].noSigLC} autoLC=${st.autoLC}: pilot=${st.pilot} moved ${maxD.toFixed(1)} m, blinker on ${sigT.toFixed(1)} s, end signal ${st.signal}, states ${JSON.stringify(states)} hits ${hits}`)}}
return out.join("\n")})()
