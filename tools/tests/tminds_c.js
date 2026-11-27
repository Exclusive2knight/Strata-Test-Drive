/* v38 traffic minds: 8 getting lost, 10 accident aftermath, 13 determinism */
(async()=>{const out=[],P=(ok,n,s)=>out.push(`${ok?"PASS":"FAIL"} ${n}: ${s}`);window.NOSEMI=1;setTrim("camry25",true);
const park=()=>{resetCar(STARTS.city);try{const M=me(),q=ePt(M.e,M.s,(hwOf(M.e)+(M.e.T.walk||0)+6)*(M.e.ow?1:-1));resetCar({free:true,x:q[0],y:q[1],h:car.psi})}catch(e){}st.power=true;st.started=true;st.gear="P";car.vx=0};
try{/* 8: 100 drivers with routes across town; tourists on unfamiliar routes miss turns and recover */{park();cars.length=0;spawnTraffic(60);const R=[];let tries=0;
  while(R.length<100&&tries++<600){const a=randomSpot(80,900),b=randomSpot(200,1100);if(!a||!b||a.e===b.e)continue;const c=newCar(a.e,a.dir,a.s,0);try{c.route=navBuild({e:b.e,dir:b.dir,s:b.s})}catch(e){continue}if(!c.route)continue;cars.push(c);tmInit(c);c.tmKeep=1;c.mind.lost=R.length%4===0;c._g=b;R.push(c)}
  TM.lostP=0.05;let stuck=new Set();for(let k=0;k<6000;k++){SIMSTEP(0.1);if(k%10===0)for(const c of R){if(c.mind&&c.mind.stopT>60)stuck.add(c.id);if(c._g&&!c.done&&c.e===c._g.e&&c.dir===c._g.dir)c.done=true}}
  for(const c of R)if(!c.mind)c.mind={lost:false,missed:0};const lost=R.filter(c=>c.mind.lost),missed=lost.filter(c=>(c.mind.missed||0)>0),rec=missed.filter(c=>c.done),ok=R.filter(c=>c.done&&!c.mind.lost);
  const rN=ok.length/Math.max(1,R.length-lost.length),rL=rec.length/Math.max(1,missed.length);P(missed.length>0&&rL>=rN*0.6&&stuck.size<=2,"8 getting lost",`${lost.length} drivers on unfamiliar routes: ${missed.length} missed a turn (${lost.reduce((s,c)=>s+(c.mind.missed||0),0)} wrong turns) and ${rec.length} of them still got there in 10 min (${(rL*100).toFixed(0)}%, vs ${(rN*100).toFixed(0)}% of drivers who knew the way); stuck over 60 s: ${stuck.size}`)}
}catch(e){out.push('ERR 8 '+e.stack.slice(0,300))}
try{/* 10: a crash between two traffic cars: they stop with hazards, others slow and go round, traffic recovers within 3 minutes */{park();cars.length=0;Traffic.set_density("all",.8);for(let k=0;k<300;k++)SIMSTEP(0.1);
  let pair=null;for(const L_ of cars){if(L_.kind!=="ai"||L_.jn||L_.v<4||L_.semi)continue;for(const F of cars){if(F===L_||F.kind!=="ai"||F.jn||F.e!==L_.e||F.dir!==L_.dir||laneIdx(F)!==laneIdx(L_))continue;const g=L_.s-F.s;if(g>8&&g<60&&F.v>4){pair=[L_,F];break}}if(pair)break}
  if(pair){pair[0].hardT=3.2;pair[1].distractT=6;const st0=TM.accidents;TM.accidents=true;for(let k=0;k<100&&!EV.list.some(v=>v.pair&&v.pair.includes(pair[1]));k++)SIMSTEP(0.1);if(!EV.list.some(v=>v.pair&&v.pair.includes(pair[1])))pair=null}
  if(!pair){P(false,"10 accident aftermath","no pair of cars to crash");}else{const E_=pair[0].e;const sp=()=>{const L=cars.filter(c=>c.kind==="ai"&&c.e===E_&&!pair.includes(c));return L.length?L.reduce((s,c)=>s+c.v,0)/L.length:null};
    const base=sp();let hz=false,stopped=false,minS=99,t=0,rec=null;for(let k=0;k<2400;k++){SIMSTEP(0.1);t+=0.1;const ps=pair.filter(c=>cars.includes(c)||parked.includes(c));if(ps.some(c=>c.haz))hz=true;if(ps.some(c=>(c.v||0)<0.3))stopped=true;
      if(k%20===0){const s=sp();if(s!=null){minS=Math.min(minS,s);if(t>20&&rec===null&&s>Math.max(4,(base||8)*0.7)&&minS<(base||8)*0.8)rec=t}}}
    const stuckN=cars.filter(c=>c.kind==="ai"&&c.idle>60).length;P(stopped&&hz&&stuckN<=1&&(rec===null?minS>=(base||0)*0.8:rec<=180),"10 accident aftermath",`crashed cars stopped ${stopped}, hazards ${hz}; speed on that road ${base!=null?(base*2.237).toFixed(0):"?"} mph before, lowest ${(minS*2.237).toFixed(0)} mph (rubbernecking and going round), back to normal after ${rec!=null?rec.toFixed(0)+" s":"-"}; stuck over 60 s: ${stuckN}`)}}
}catch(e){out.push('ERR 10 '+e.stack.slice(0,300))}

return out.join("\n")})()
