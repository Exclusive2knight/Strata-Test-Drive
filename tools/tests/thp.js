/* v37.5 Harbor Point sites: drive down the Exchange Plaza garage entrance ramp into B1, along the aisle, and check the floor under the car
   (roof 0, B1 -3.6) and that the walls stop you. Needs the site models (they load when you are near) */
(async()=>{const out=[];setTrim("camry_se",true);cars.length=0;const WH={};const _c2=window.crashFx;window.crashFx=function(v,w){WH[w]=(WH[w]||0)+1;return _c2.apply(this,arguments)};
const S=SITES.find(s=>s.k==="ugarage");siteLoad(S);siteLoad(SITES[0]);resetCar({x:3963.5,y:-805,h:Math.PI/2});st.power=true;sys.epb=false;st.gear="D";
for(let k=0;k<200&&!S.m;k++)await new Promise(r=>setTimeout(r,250));if(!S.m)return "garage did not load";
const H=SITES.find(s=>s.k==="hotel");for(let k=0;k<200&&!H.m;k++)await new Promise(r=>setTimeout(r,250));
resetCar({free:true,x:3963.5,y:-805,h:Math.PI/2});car.vx=0;st.gear="D";const log=[];let t=0;
/* steer to hold x=3963.5 heading north at ~4 m/s */
SIM(30,tt=>{t=tt;const ex=car.px-3963.5,eh=wrapPi(car.psi-Math.PI/2);inp.steerT=inp.steer=clamp(-0.08*ex*0-1.2*eh+0.05*ex,-1,1);inp.thrT=inp.thr=car.vx<4?0.35:0;inp.brkT=inp.brk=0;
  if(((tt*50)|0)%50===0)log.push(`t${tt.toFixed(0)} y${car.py.toFixed(1)} z${(car.zb||0).toFixed(2)} v${car.vx.toFixed(1)}`);if(car.py>-700)return false});
out.push("down the entrance ramp: "+log.join(" | "));
out.push(`end: y ${car.py.toFixed(1)} (B1 aisle ~ -755) z ${(car.zb||0).toFixed(2)} hits ${hits}`);
/* drive west along B1 into the far wall: it must stop us */
const h0=hits;GREF=-3.1;resetCar({free:true,x:3925,y:-745,h:Math.PI});GREF=-3.1;car.zb=-3.6;car.vx=0;st.gear="D";
SIM(25,tt=>{inp.thrT=inp.thr=car.vx<6?0.5:0;inp.steerT=inp.steer=clamp(-1.2*wrapPi(car.psi-Math.PI),-1,1)});
out.push(`west along B1: x ${car.px.toFixed(1)} (wall at ${3925-45}) z ${(car.zb||0).toFixed(2)} hits ${hits-h0}`);
/* the hotel forecourt: ground layer under the car */
GREF=0.3;const g=groundAt(3530,-470);out.push(`hotel forecourt ground ${g.h.toFixed(2)} ${g.kind}`);
GREF=-3.6;const g2=groundAt(3925,-760);GREF=0;const g3=groundAt(3925,-760);out.push(`garage B1 ${g2.h.toFixed(2)}, roof ${g3.h.toFixed(2)}`);
out.push(JSON.stringify(WH));return out.join("\n")})()
