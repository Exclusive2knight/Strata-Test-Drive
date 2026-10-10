(async()=>{const out=[];setTrim("camry25",true);cars=[];st.power=true;st.started=true;sys.epb=false;st.gear="D";
const fw=EDGES.find(e=>e.type==="xway"&&Math.abs(e.a.y+1100)<1&&Math.abs(e.b.y+1100)<1);
// 1. you crawl along at 15 m/s in lane 1; an aggressive driver behind
let p=fpt(fw,1,200,laneOff(fw,1));resetCar({free:true,x:p[0],y:p[1],h:p[2]});car.vx=15;
const c=newCar(fw,1,175,1,"ai");c.pers={k:"aggr",v:1.1,T:0.8,lc:0.4,a:2.6,b:3.8};c.v=15;cars.push(c);carPose(c);
let fl=0,passed=false,maxP=0,maxR=0,log=[];
SIM(25,t=>{const M=me();inp.thrT=0;car.vx=15;inp.steerT=0;if(c.flashT>0)fl++;maxP=Math.max(maxP,Math.abs(c.sus?c.sus.p:0));maxR=Math.max(maxR,Math.abs(c.sus?c.sus.r:0));
  if(Math.round(t*50)%100===0)log.push(`${t.toFixed(0)}s gap ${(c.s-M.s).toFixed(1)} lane ${laneIdx(c)} v ${c.v.toFixed(1)} slow ${(c.slowT||0).toFixed(1)} pass ${(c.passT||0).toFixed(1)}`);if(c.s>M.s+10)passed=true});
out.push(`aggr behind slow player: flash frames ${fl}, passed ${passed}, pitch max ${(maxP*57.3).toFixed(2)}° roll ${(maxR*57.3).toFixed(2)}°\n`+log.join("\n"));
// 2. tailgating an aggressive driver
cars=[];p=fpt(fw,1,200,laneOff(fw,1));resetCar({free:true,x:p[0],y:p[1],h:p[2]});car.vx=25;
const d=newCar(fw,1,212,1,"ai");d.pers={k:"aggr",v:1.0,T:0.8,lc:9,a:2.6,b:3.8};d.v=25;cars.push(d);carPose(d);let bc=0,minV=99;
SIM(10,t=>{car.vx=Math.min(car.vx,25);const M=me();const g=d.s-M.s-CARLEN;inp.thrT=g>6?0.6:0;inp.brkT=g<3?0.6:0;if(d.bcT>0)bc++;minV=Math.min(minV,d.v)});
out.push(`tailgate: brake check frames ${bc} min v ${minV.toFixed(1)} hits ${hits}`);
// 3. horn at a slow car
cars=[];p=fpt(fw,1,200,laneOff(fw,1));resetCar({free:true,x:p[0],y:p[1],h:p[2]});car.vx=10;
const h=newCar(fw,1,220,1,"ai");h.pers={k:"calm",v:0.6,T:1.7,lc:99,a:1.25,b:2.4};h.v=10;cars.push(h);carPose(h);SIM(2,()=>{car.vx=10});const v1=h.v;
hornOn(false);SIM(4,()=>{car.vx=10});out.push(`horn: v before ${v1.toFixed(1)} after 4s ${h.v.toFixed(1)} honkT ${(h.honkT||0).toFixed(1)}`);
return out.join("\n")})()
