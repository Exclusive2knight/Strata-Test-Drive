has=()=>true;
window.PAT=async(name,setup,side,searchT=25)=>{setTrim("camry25",true);cars=[];st.power=true;st.started=true;sys.epb=false;sys.pa=null;sys.paSpot=null;inp.thrT=0;inp.brkT=0;inp.steerT=0;
  setup();st.gear="D";car.vx=0;st.parkAssist=true;PA.mode=PA.mode||"perp";PA.side=side;PA.found=false;PA.last=null;const h0=hits;let found=null;
  SIM(searchT,t=>{inp.thrT=car.vx<1.6?0.18:0;inp.brkT=car.vx>2.3?0.2:0;paScan();if(sys.paSpot&&!found){found=t;return false}});
  if(!sys.paSpot)return `${name}: NO SPOT found (searched ${searchT}s, ended at ${car.px.toFixed(0)},${car.py.toFixed(0)}, spots near ${perpSpots().filter(t=>Math.hypot(t.x-car.px,t.y-car.py)<14).length})`;
  inp.thrT=0;inp.brkT=0;SIM(1.5,()=>{inp.brkT=0.5});inp.brkT=0;const typ=sys.paSpot.type,T=sys.paSpot.t;paStart();let done=null,ph=[];
  SIM(70,t=>{if(!sys.pa){done=t;return false}const p=sys.pa.ph;if(ph[ph.length-1]!==p)ph.push(p)});
  let q="";if(T){const dx=car.px-T.x,dy=car.py-T.y,ang=Math.abs(wrapPi(car.psi-Math.atan2(T.uy,T.ux)));q=` · ${Math.hypot(dx,dy).toFixed(2)} m from stall centre · ${(Math.min(ang,Math.PI-ang)*57.3).toFixed(1)}° off`}
  return `${name}: ${typ} found ${found.toFixed(1)}s · ${done!==null?"finished "+done.toFixed(0)+"s":"NOT finished ("+(sys.pa&&sys.pa.msg)+")"}${q} · hits ${hits-h0} · phases ${ph.join(">")} · ${LOG[0]||""}`};
(async()=>[await PAT("garage S bay level 1, downhill east",()=>{const x=GAR.xa+4;resetCar({free:true,x,y:GAR.ayB-1,h:0,z:garZ(0,1,x)})},1),await PAT("garage S bay level 1, uphill west",()=>{const x=GAR.xb-4;resetCar({free:true,x,y:GAR.ayB+1,h:Math.PI,z:garZ(0,1,x)})},1)].join("\n"))()
