// Somerset Collection: the model loads, the lots are driveable (drive across them, off the boulevard into a lot and out), the buildings are solid
(async()=>{const out=[];mallLoad();for(let i=0;i<200&&!MALL.m;i++)await new Promise(r=>setTimeout(r,100));out.push("loaded "+!!MALL.m+" groups "+(MALL.m?MALL.m.length:0));
  const drive=(x,y,h,T,v)=>{resetCar({free:true,x,y,h});st.gear="D";st.power=true;hits=0;let zMin=1e9,zMax=-1e9,maxPitch=0;SIM(T,()=>{car.vx=v;const g=groundAt(car.px,car.py);zMin=Math.min(zMin,car.zb-g.h);zMax=Math.max(zMax,car.zb-g.h);maxPitch=Math.max(maxPitch,Math.abs(car.th||0))});
    return `from ${x},${y}: to ${car.px.toFixed(0)},${car.py.toFixed(0)} hits ${hits} z-ground ${zMin.toFixed(2)}..${zMax.toFixed(2)} pitch ${maxPitch.toFixed(3)} ground ${groundAt(car.px,car.py).kind}`};
  const clearY=(x0,x1)=>{for(let y=-34;y>-76;y-=0.5){let ok=true;for(let x=Math.min(x0,x1);x<=Math.max(x0,x1)&&ok;x+=2)if(collNear(x,y).some(o=>Math.hypot(o.x-x,o.y-y)<(o.r||2)+1.6))ok=false;if(ok)return y}return -52};
  {const y=clearY(-3270,-3190);out.push("lot east  "+drive(-3270,y,0,8,9))}
  {const y=clearY(-3060,-2980);out.push("lot west  "+drive(-2980,y,Math.PI,8,9))}
  out.push("blvd->lot "+drive(-3150,-12,-Math.PI/2,4,6));
  out.push("lot->north wall "+drive(-3100,-90,-Math.PI/2+0.0001,10,8)+" (expect a hit at the south mall)");
  out.push("coolidge  "+drive(-3420,250,-Math.PI/2,12,12));
  const g=[[-3200,-52],[-3100,-12],[-3420,0],[-3100,200],[-2600,0]].map(([x,y])=>`${x},${y}:${groundAt(x,y).kind} ${groundAt(x,y).h.toFixed(2)}`);out.push(g.join(" | "));
  return out.join("\n")})()
