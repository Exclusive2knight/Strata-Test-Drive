(async()=>{const out=[];setTrim("camry25",true);
const E2=EDGES.filter(e=>!/xway|ramp|dirt|lot|drive/.test(e.type)&&e.n===1&&e.L>400).sort((a,b)=>b.L-a.L)[0];
for(const from of [-1,1]){const P=fpt(E2,1,E2.L*0.3,0);resetCar({x:P[0],y:P[1],h:P[2]});cars=[];st.power=true;sys.epb=false;st.gear="R";st.rcta=true;car.vx=-0.5;inp.thrT=0;inp.brkT=0;
 // a car 6 m behind, 20 m off to one side (ISO: + = left), driving across behind us toward the other side
 const c0=Math.cos(car.psi),s0=Math.sin(car.psi),bx=car.px-c0*6,by=car.py-s0*6,lat=20*from;
 const o={kind:"ai",v:8,wx:bx-s0*lat,wy:by+c0*lat,wh:car.psi+(from>0?-Math.PI/2:Math.PI/2),mdl:"camry25",paint:"red"};cars.push(o);
 let seen=0,cls="",side=0;for(let t=0;t<1.5;t+=0.02){o.wx+=Math.cos(o.wh)*o.v*0.02;o.wy+=Math.sin(o.wh)*o.v*0.02;assist(0.02);if(sys.rcta){seen+=0.02;side=sys.rcta}}
 try{hud(0.1)}catch(e){out.push("hud err "+e.message)};
 out.push(`car coming from the ${from>0?"left":"right"}: RCTA ${seen>0?"on":"off"} (${seen.toFixed(2)} s), side ${side<0?"left":side>0?"right":"-"}, left marker "${$("bsmL").className}", right marker "${$("bsmR").className}"`);cars=[]}
return out.join("\n")})()
