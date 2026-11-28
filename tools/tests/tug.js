/* Exchange Plaza garage: drive down the entrance ramp in the middle of its lane, turn west along the B1 aisle and drive to the far end,
   then back. Logs height and every wall hit; the car must stay on B1 (-3.6) and never sink through it */
(async()=>{const out=[];setTrim("camry_se",true);cars.length=0;const WH=[];const _c2=window.crashFx;window.crashFx=function(v,w){if(v>0.3)WH.push(`${w} @${car.px.toFixed(1)},${car.py.toFixed(1)} z${(car.zb||0).toFixed(2)} v${v.toFixed(1)}`);return _c2.apply(this,arguments)};
const S=SITES.find(s=>s.k==="ugarage");siteLoad(S);resetCar({x:3963,y:-805,h:Math.PI/2});for(let k=0;k<200&&!S.m;k++)await new Promise(r=>setTimeout(r,250));if(!S.m)return "no garage";
resetCar({free:true,x:3963,y:-805,h:Math.PI/2});car.vx=0;st.power=true;sys.epb=false;st.gear="D";st.started=true;
const path=[[3963,-780],[3962,-765],[3959,-757],[3950,-755],[3930,-755],[3900,-755],[3886,-755]];let i=0,zmin=9,zmax=-9;const log=[];
SIM(60,tt=>{const p=path[i];if(Math.hypot(p[0]-car.px,p[1]-car.py)<3&&i<path.length-1)i++;const a=wrapPi(Math.atan2(path[i][1]-car.py,path[i][0]-car.px)-car.psi);inp.steerT=inp.steer=clamp(-a*2,-1,1);
  inp.thrT=inp.thr=car.vx<3.5?0.3:0;inp.brkT=inp.brk=car.vx>5?0.3:0;if(car.py>-760){zmin=Math.min(zmin,car.zb);zmax=Math.max(zmax,car.zb)}
  if(((tt*50)|0)%100===0)log.push(`${car.px.toFixed(0)},${car.py.toFixed(0)} z${(car.zb||0).toFixed(2)}`);if(i===path.length-1&&Math.hypot(path[i][0]-car.px,path[i][1]-car.py)<3)return false});
out.push(`wp ${i}/${path.length-1}; in B1 z ${zmin.toFixed(2)}..${zmax.toFixed(2)}; hits ${WH.length}: ${WH.slice(0,8).join(" | ")}`);out.push(log.join(" | "));
return out.join("\n")})()
