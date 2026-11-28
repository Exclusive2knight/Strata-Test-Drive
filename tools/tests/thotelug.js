/* Harbor Crest: drive from the forecourt down the valet ramp to B1, along the B1 aisle, down the middle ramp to B2 and back up the other lane.
   Logs every wall hit and the height; it must reach B2 (-7.2) and come back to B1 (-3.6) without sticking or climbing out of the floor */
(async()=>{const out=[];setTrim("camry_se",true);cars.length=0;const WH=[];const _c2=window.crashFx;window.crashFx=function(v,w){if(v>0.3)WH.push(`${w} @X${(car.px-S.cx).toFixed(1)},Z${(S.cy-car.py).toFixed(1)} z${(car.zb||0).toFixed(2)} v${v.toFixed(1)}`);return _c2.apply(this,arguments)};
const S=SITES[0],W=(X,Z)=>[S.cx+X,S.cy-Z];siteLoad(S);resetCar({x:S.cx,y:S.cy,h:0});for(let k=0;k<200&&!S.m;k++)await new Promise(r=>setTimeout(r,250));if(!S.m)return "no hotel";
const st0=W(-22.2,46);resetCar({free:true,x:st0[0],y:st0[1],h:Math.PI/2});car.vx=0;st.power=true;sys.epb=false;st.gear="D";st.started=true;
const legs={"down to B1":[W(-22.2,10),W(-22.2,1),W(-24,-4)],"B1 aisle":[W(-10,6.5),W(10,7),W(19.5,8.5)],"ramp down":[W(21.6,4),W(21.6,-8),W(21.6,-19),W(21.6,-24)],"turn":[W(24,-27),W(25.4,-22)],"ramp up":[W(25.4,-12),W(25.4,0),W(25.4,8),W(22,9.5)]};
for(const [nm,path] of Object.entries(legs)){let i=0,zmin=9,zmax=-9,t0=0,ok=false;const h0=WH.length;
  SIM(40,tt=>{t0=tt;const p=path[i];if(Math.hypot(p[0]-car.px,p[1]-car.py)<2.5){if(i<path.length-1)i++;else{ok=true;return false}}const a=wrapPi(Math.atan2(path[i][1]-car.py,path[i][0]-car.px)-car.psi);inp.steerT=inp.steer=clamp(-a*2,-1,1);
    inp.thrT=inp.thr=car.vx<3?0.3:0;inp.brkT=inp.brk=car.vx>4.5?0.3:0;zmin=Math.min(zmin,car.zb);zmax=Math.max(zmax,car.zb)});
  out.push(`${nm}: ${ok?"made it":"STUCK at wp "+i} in ${t0.toFixed(0)} s · at X${(car.px-S.cx).toFixed(1)},Z${(S.cy-car.py).toFixed(1)} z ${car.zb.toFixed(2)} (range ${zmin.toFixed(2)}..${zmax.toFixed(2)}) · wall hits ${WH.length-h0} ${WH.slice(h0,h0+3).join(" | ")}`)}
return out.join("\n")})()
