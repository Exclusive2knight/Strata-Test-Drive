// AI goes round a wreck on a two-lane road (backing up first when it stopped too close), and waits while traffic is coming
(async()=>{st.started=true;resetCar(STARTS.city);const e=EDGES.filter(e=>e.n===1&&!e.ow&&e.L>260&&/res|st|col/.test(e.type)&&!e.br&&!e.ov)[5];const o=[];
 for(const [gap,onc] of [[14,false],[1.6,false],[14,true]]){cars=[];const w=evStatic("wreck",e,1,140,laneOff(e,0),{haz:true});cars.push(w);const c=newCar(e,1,140-CARLEN-gap,0);c.v=0;c.pers={k:"normal",v:1,T:1.3,lc:1,a:1.6,b:2.8};cars.push(c);
   let on=null;if(onc){on=newCar(e,-1,e.L-200,0);on.v=10;cars.push(on)}resetCar({free:true,x:-9999,y:-9999,h:0});
   let backed=false,swung=false,passed=false,minAh=99,tPass=null,t=0;SIM(30,()=>{t+=0.02;if(c.rev)backed=true;if(c.ovt)swung=true;const ah=(w.wx-c.wx)*Math.cos(c.wh)+(w.wy-c.wy)*Math.sin(c.wh);if(!passed&&ah<-6){passed=true;tPass=t}});
   o.push(`gap ${gap}${onc?" with oncoming":""}: backed ${backed}, swung out ${swung}, passed ${passed}${tPass?" at "+tPass.toFixed(1)+" s":""}, back in lane ${Math.abs(c.off-laneOff(e,0))<0.3}, v ${c.v.toFixed(1)}`)}
 return o.join("\n")})()
