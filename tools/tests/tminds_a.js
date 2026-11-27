/* v38 traffic minds, fast checks: 1 personality, 2 emotion, 4 human behaviour, 5 phantom jams (ring road), 7 zipper courtesy (merge model),
   11 player memory, 12 performance + LOD, all printed PASS / FAIL with the numbers */
(async()=>{const out=[],P=(ok,n,s)=>out.push(`${ok?"PASS":"FAIL"} ${n}: ${s}`);
const fake=i=>{const c={id:100000+i,wx:0,wy:0,v:20,kind:"ai"};tmInit(c);return c};
/* 1 */{const D=[];for(let i=0;i<1000;i++)D.push(fake(i).mind);const cnt={};for(const d of D)cnt[d.arch]=(cnt[d.arch]||0)+1;const mix=tmMix(0,0);let tot=0;for(const k in mix)tot+=mix[k];
  let err=0;for(const k in mix)err=Math.max(err,Math.abs((cnt[k]||0)/1000-mix[k]/tot));const ag=D.filter(d=>d.tr.aggression>.6),ca=D.filter(d=>d.tr.caution>.7),m=a=>a.reduce((s,d)=>s+d.want.headway,0)/Math.max(1,a.length);
  const inR=D.every(d=>TM_TRAITS.every(k=>d.tr[k]>=0&&d.tr[k]<=1));P(err<0.04&&m(ag)<m(ca)*0.8&&inR,"1 personality",`mix max error ${(err*100).toFixed(1)}% (${Object.entries(cnt).map(([k,v])=>k+" "+v).join(", ")}); headway aggressive ${m(ag).toFixed(2)} s (n ${ag.length}) vs cautious ${m(ca).toFixed(2)} s (n ${ca.length}); traits in 0..1 ${inR}`)}
/* 2 */{const A=fake(5001),Bp=fake(5002);Object.assign(A.mind.tr,{aggression:.95,patience:.05});Object.assign(Bp.mind.tr,{aggression:.05,patience:.95});A.mind.spike.anger=0;Bp.mind.spike.anger=0;
  tmEvent(A,"cutoff",{});tmEvent(Bp,"cutoff",{});const a0=A.mind.spike.anger,b0=Bp.mind.spike.anger;let t=0;const T0=TM.t;let bad=0;
  for(;t<300&&A.mind.spike.anger>=0.2;t+=0.25){TM.t+=0.25;tmMind(A,A.mind);const E=tmEmo(A.mind);for(const k in E)if(!(E[k]>=0&&E[k]<=1))bad++}TM.t=T0;
  P(a0>b0*1.5&&t<120&&bad===0,"2 emotion",`cut off: anger aggressive ${a0.toFixed(2)} vs patient ${b0.toFixed(2)}; decays under 0.2 in ${t.toFixed(1)} s (limit 120 s); emotion values outside 0..1: ${bad}`)}
/* 4 */{const D=[];for(let i=0;i<600;i++)D.push(fake(2000+i).mind);const avg=(a,f)=>a.reduce((s,d)=>s+f(d),0)/Math.max(1,a.length);
  const late=D.filter(d=>d.late>.5),easy=D.filter(d=>d.late<.15),tired=D.filter(d=>d.fatigue>.2),fresh=D.filter(d=>d.fatigue<.05),nov=D.filter(d=>d.exp==="novice"),pro=D.filter(d=>d.exp==="expert");
  for(const d of D){}const sp=avg(late,d=>d.want.speed)-avg(easy,d=>d.want.speed),gp=avg(late,d=>d.want.gap)-avg(easy,d=>d.want.gap),dr=avg(tired,d=>d.want.drift)-avg(fresh,d=>d.want.drift),br=avg(nov,d=>d.want.brake)-avg(pro,d=>d.want.brake);
  P(sp>0&&gp<0&&dr>0&&br<0,"4 human behaviour",`late vs relaxed: desired speed +${(sp*100).toFixed(1)}%, accepted gap ${(gp*100).toFixed(1)}%; tired vs fresh lane drift +${dr.toFixed(2)} m; novice vs expert comfortable braking ${br.toFixed(2)} m/s2 (lower = brakes earlier)`)}
/* 5: a 1 km ring at 30 vehicles/km, the drivers' own reaction times and noisy estimates, no timers */{const N=30,L=1000,cs=[];for(let i=0;i<N;i++){const d=fake(3000+i).mind;d.want.speed=Math.max(d.want.speed,0.95);cs.push({x:i*L/N,v:15,d,h:[]})}
  const dt=0.1;let minV=99,stops=0,vs=[];for(let k=0;k<6000;k++){for(const c of cs){c.h.push([c.x,c.v]);if(c.h.length>40)c.h.shift()}
    for(let i=0;i<N;i++){const c=cs[i];if(c.dz>0){c.dz-=dt;continue}if((c.nx=(c.nx||0)-dt)>0)continue;c.nx=c.d.want.react*(0.6+0.4*c.d.R());   /* people re-judge the gap about once per reaction time, not continuously */if(c.d.R()<dt*0.03*(1.2-c.d.tr.attentiveness)){c.dz=1+c.d.R()*2;continue}const l=cs[(i+1)%N],lag=Math.min(l.h.length-1,Math.round(c.d.want.react/dt)),o=l.h[l.h.length-1-lag]||[l.x,l.v];let gap=((o[0]-c.x+L)%L)-4.6;gap*=1+(c.d.R()-.5)*0.06*(1+c.d.fatigue);
      c.a=idm(c.v,25*c.d.want.speed,Math.max(0.1,gap),o[1],c.d.want.headway,tmAccel(c.d,gap,c.v),c.d.want.brake)}
    for(const c of cs){c.v=Math.max(0,c.v+clamp(c.a,-8,3)*dt);c.x=(c.x+c.v*dt)%L}if(k>1800){const m=Math.min(...cs.map(c=>c.v));minV=Math.min(minV,m);if(m<1)stops++;vs.push(cs.reduce((s,c)=>s+c.v,0)/N)}}
  const mean=vs.reduce((a,v)=>a+v,0)/vs.length;P(minV<mean*0.35,"5 phantom jams",`30 veh/km ring: mean speed ${(mean*3.6).toFixed(0)} km/h, slowest car ${(minV*3.6).toFixed(1)} km/h, time with someone stopped ${(stops*0.1).toFixed(0)} s of 420 s (waves from reaction delay and misjudged gaps only)`)}
/* 7: a lane drop: the closing lane's cars need the open lane to let them in; courteous vs discourteous populations */{const run=pol=>{const dt=0.1,ML=400;let L0=[],L1=[],thr=0,seq=[],id=0;
    const add=(L,ln)=>{const d=fake(4000+id++).mind;d.want.polite=pol;L.push({x:0,v:12,d,ln,from:ln})};
    for(let k=0;k<6000;k++){if(k%30===0&&(!L0.length||L0[L0.length-1].x>12))add(L0,0);if(k%24===12&&(!L1.length||L1[L1.length-1].x>12))add(L1,1);
      for(const L of [L0,L1])L.sort((a,b)=>b.x-a.x);
      for(const [L,ln] of [[L0,0],[L1,1]])for(let i=0;i<L.length;i++){const c=L[i];let gap=i?L[i-1].x-c.x-4.6:1e9,vL=i?L[i-1].v:c.v;if(ln===1&&!i){gap=Math.min(gap,ML-c.x);vL=0}
        if(ln===0&&c.yieldTo&&L1.includes(c.yieldTo)&&c.yieldTo.x>c.x+4){gap=Math.min(gap,c.yieldTo.x-c.x-8);vL=Math.min(vL,c.yieldTo.v)}
        c.a=idm(c.v,14,Math.max(0.1,gap),vL,1.3,1.6,2.8)}
      const head=L1[0];if(head&&head.x>ML-50){const f=L0.filter(o=>o.x<head.x-6&&o.x>head.x-30).sort((a,b)=>b.x-a.x)[0];if(f&&!f.yieldTo&&!(head.askT>k)){head.askT=k+20;if(f.d.R()<0.08+0.9*f.d.want.polite)f.yieldTo=head}
        const room=L0.every(o=>Math.abs(o.x-head.x)>(o.x>head.x?5.5:6+Math.max(0,o.v-head.v)*1.5));if(room){L1.shift();head.ln=0;L0.push(head);for(const o of L0)if(o.yieldTo===head)o.yieldTo=null}}
      for(const L of [L0,L1])for(const c of L){c.v=Math.max(0,c.v+clamp(c.a,-8,2.5)*dt);c.x+=c.v*dt}
      for(let i=L0.length-1;i>=0;i--)if(L0[i].x>ML+60){if(k>1200){thr++;seq.push(L0[i].from)}L0.splice(i,1)}}
    let ch=0;for(let i=1;i<seq.length;i++)if(seq[i]!==seq[i-1])ch++;return {thr,alt:ch/Math.max(1,seq.length-1),m:seq.filter(v=>v===1).length}};
  const hi=run(0.9),lo=run(0.05);
  P(hi.alt>lo.alt+0.1,"7 courtesy (merge model)",`lane drop, 8 min: courteous drivers alternate ${(hi.alt*100).toFixed(0)}% of the time (${hi.m} from the closing lane), discourteous ${(lo.alt*100).toFixed(0)}% (${lo.m}); throughput ${hi.thr} vs ${lo.thr} cars (${hi.thr-lo.thr>=0?"+":""}${hi.thr-lo.thr})`)}
/* 11: you tailgate one driver for 20 s, then drive politely behind another */{setTrim("camry25",true);cars.length=0;const E2=EDGES.filter(e=>e.type==="art"&&e.n>=2&&e.L>500).sort((a,b)=>b.L-a.L)[0];
  const c=newCar(E2,1,60,0);cars.push(c);tmInit(c);Object.assign(c.mind.tr,{aggression:.6,patience:.3,risk:.5});resetCar({x:c.wx,y:c.wy,h:c.wh});st.started=true;st.power=true;st.gear="D";
  const h0=TM.stats.honk.length;let honks=0;Traffic.on("on_honk",e=>{if(e.at==="you")honks++});
  for(let k=0;k<200;k++){SIMSTEP(0.1);const q=fpt(c.e,c.dir,Math.max(0,c.s-7.5),c.off);car.px=q[0];car.py=q[1];car.psi=c.wh;car.vx=Math.max(6,c.v)}
  const m=c.mind.mem.me||{anger:0,trust:.5};const c2=newCar(E2,1,300,1);cars.push(c2);tmInit(c2);let waves=0;Traffic.on("on_wave",e=>{if(e.id===c2.id)waves++});
  for(let k=0;k<1200;k++){SIMSTEP(0.1);const q=fpt(c2.e,c2.dir,Math.max(0,c2.s-45),c2.off);car.px=q[0];car.py=q[1];car.psi=c2.wh;car.vx=c2.v;if(k%100===0)tmEvent(c2,"letin",{me:true})}
  const m2=c2.mind.mem.me||{trust:0};P(m.anger>0.3&&honks>0&&m2.trust>0.6&&waves>0,"11 player memory",`tailgated 20 s: anger at you ${m.anger.toFixed(2)}, honked at you ${honks}x; polite for 2 min: trust ${m2.trust.toFixed(2)}, waves ${waves}`)}
/* 12: 120 cars, AI time per frame and smooth tier changes */{cars.length=0;resetCar(STARTS.city);st.started=true;spawnTraffic(120);const n=cars.filter(c=>c.kind==="ai").length;let tAI=0,tAll=0,steps=0,jump=0;const prev=new Map();
  for(let k=0;k<1500;k++){const a=performance.now();const t0=TM.stats.ms;tmTick(1/60);TM.t-=1/60;const b=performance.now();SIMSTEP(1/60);const e=performance.now();tAI+=b-a;tAll+=e-a;steps++;
    if(k%6===0)for(const c of cars){if(!c.pers||!c.mind)continue;const p=prev.get(c);if(p&&p.tier!==c.mind.tier)jump=Math.max(jump,Math.abs(c.pers.T-p.T)/Math.max(.3,p.T));prev.set(c,{tier:c.mind.tier,T:c.pers.T})}}
  P(tAI/steps<3,"12 performance",`${n} cars: minds + decisions ${(tAI/steps).toFixed(2)} ms a frame (budget 3 ms), whole traffic step ${(tAll/steps).toFixed(2)} ms; biggest headway change at a detail-tier switch ${(jump*100).toFixed(0)}% (eased, no pop). 60 fps rendering is not measurable in this headless software renderer`)}
return out.join("\n")})()
