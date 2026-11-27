/* reversing assists (v37.3): rear auto brake should stop you about half a metre to a second short of something in your path, not for things
   beside your path; rear cross traffic braking should brake for a car about to cross right behind you, not one on the far side of the road */
(async()=>{const out=[];setTrim("camry_se",true);st.rAeb=true;st.rcta=true;
const E2=EDGES.filter(e=>!/xway|ramp|dirt|lot|drive/.test(e.type)&&e.n===1&&e.L>400).sort((a,b)=>b.L-a.L)[0];
const start=()=>{const P=fpt(E2,1,E2.L*0.3,0);resetCar({x:P[0],y:P[1],h:P[2]});cars=[];parked.length=0;st.power=true;sys.epb=false;st.gear="R";inp.thrT=0;inp.brkT=0;sys.rAebOv=false;sys.rAebRel=false;sys.hitClk=-99;sys.rctbOn=false;sys.rctbSide=null;sys.rctbHold=0};
// back up at a fixed speed (moving the car by hand) until the brake comes on; returns the gap then
const rev=(v,fn)=>{let firstGap=null,t=0;for(;t<25;t+=0.02){car.vx=-v;car.px-=Math.cos(car.psi)*v*0.02;car.py-=Math.sin(car.psi)*v*0.02;if(fn)fn();inp.thr=0.3;assist(0.02);if(sys.rAebBrake){firstGap=true;break}}return t};
for(const [v,side] of [[0.6,0],[1.5,0],[2.8,0],[1.0,2.6],[1.0,1.9]]){start();const c=Math.cos(car.psi),s=Math.sin(car.psi);
  // a parked car 8 m behind the rear bumper, side metres off to one side (ISO + = left), parallel to us
  const back=BODY_HL+8+CARLEN/2,o={fixed:true,kind:"parked",wx:car.px-c*back-s*side,wy:car.py-s*back+c*side,wh:car.psi,wz:car.zb||0,v:0,mdl:"camry25",paint:"red",len:CARLEN};parked.push(o);
  const g0=()=>{const dx=o.wx-car.px,dy=o.wy-car.py;return -(dx*c+dy*s)-BODY_HL-CARLEN/2};const t=rev(v);
  out.push(`backing at ${v} m/s toward a parked car ${side?side+" m off to the side":"right behind"}: ${sys.rAebBrake?`brakes with ${g0().toFixed(2)} m to go`:"no braking"}`)}
for(const [v,dist] of [[0.5,10],[0.5,3],[1.2,2.2],[1.2,9]]){start();const c=Math.cos(car.psi),s=Math.sin(car.psi),tx=VEH.tail?VEH.tail[2]:2.4;
  // a car crossing behind us from the left at 8 m/s, its centre line `dist` metres behind our rear bumper
  const bx=car.px-c*(tx+dist),by=car.py-s*(tx+dist),o={kind:"ai",v:8,wx:bx-s*18,wy:by+c*18,wh:car.psi-Math.PI/2,mdl:"camry25",paint:"blue"};cars.push(o);let br=false,al=false;
  for(let k=0;k<200;k++){o.wx+=Math.cos(o.wh)*o.v*0.02;o.wy+=Math.sin(o.wh)*o.v*0.02;car.vx=-v;car.px-=c*v*0.02;car.py-=s*v*0.02;inp.thr=0.3;assist(0.02);if(sys.rcta)al=true;if(sys.rAebBrake)br=true}
  out.push(`cross traffic ${dist} m behind, you backing at ${v} m/s: alert ${al?"yes":"no"}, brakes ${br?"YES":"no"}`)}
return out.join("\n")})()
