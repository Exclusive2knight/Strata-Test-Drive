/* bump a garage driver in the Fort St garage: it must get pushed off you and carry on (no jitter, no jumps, no teleport, not stuck for ever) */
(async()=>{const out=[];window.NOSEMI=1;setTrim("camry25",true);resetCar({free:true,x:-900,y:-120,h:0});st.power=true;st.started=true;st.gear="P";cars.length=0;Traffic.set_density("all",0);
GPK.test=true;GPK.max=3;GPK.rate=()=>4;GPK.dwell=()=>30;GPK.arrT=0;let c=null;
SIMSTEP(0.1);for(let t=0;t<200&&!c;t+=0.1){SIMSTEP(0.1);c=cars.find(o=>o.gpk&&o.gpk.ph==="up"&&inGarage(o.wx,o.wy)&&(o.wz||0)>1.5)}
if(!c)return "no garage driver got going";GPK.max=1;
/* park the player 7 m ahead of it on its path, nose to nose, and drive into it */
const fx=Math.cos(c.wh),fy=Math.sin(c.wh);GREF=c.wz;resetCar({free:true,x:c.wx+fx*8,y:c.wy+fy*8,h:c.wh+Math.PI,z:c.wz});st.gear="D";sys.epb=false;let maxJ=0,lx=c.wx,ly=c.wy,h0=hits,dynSeen=false,zmin=99,zmax=-99;
SIM(8,t=>{inp.thrT=inp.thr=t<2.5?0.35:0;inp.brkT=inp.brk=t<2.5?0:1;inp.steerT=inp.steer=0;if(!cars.includes(c))return false;const j=Math.hypot(c.wx-lx,c.wy-ly);maxJ=Math.max(maxJ,j);lx=c.wx;ly=c.wy;if(c.dyn)dynSeen=true;zmin=Math.min(zmin,c.wz);zmax=Math.max(zmax,c.wz)});
const ph1=c.gpk.ph;let moved=0;const x1=c.wx,y1=c.wy;resetCar({free:true,x:-900,y:-120,h:0});st.gear="P";
SIM(25,()=>{inp.thrT=inp.thr=0;inp.brkT=inp.brk=1;if(!cars.includes(c))return false});moved=Math.hypot(c.wx-x1,c.wy-y1);
out.push(`hits ${hits-h0}, garage car biggest step ${maxJ.toFixed(2)} m, went dynamic ${dynSeen}, its z ${zmin.toFixed(1)}..${zmax.toFixed(1)}, phase after ${ph1} -> ${cars.includes(c)?c.gpk.ph:"gone"}, then moved ${moved.toFixed(1)} m (in ${cars.includes(c)?"garage":"-"}), dyn now ${!!c.dyn}`);
GPK.test=false;GPK.max=null;GPK.rate=null;GPK.dwell=null;return out.join("\n")})()
