(async()=>{const out=[];setTrim("camry25",true);cars=[];st.power=true;st.started=true;sys.epb=false;st.gear="D";st.lka=false;
// drive the two-bay dual helix garage with a simple waypoint driver: up thread 1 from Cass Ave to the top, and down thread 2 out to Park Ave
const G=GAR,W=(X,Z)=>[G.cx+X,G.cy+Z];
const ring=(e,from,to)=>{const P=[];for(let k=1;k<=6;k++){const t=from+(to-from)*k/6;P.push(W(e*24+e*12*Math.cos(t),12*Math.sin(t)))}return P};
// thread 1: A0 east, east U-turn to B1 west, west U-turn to A2 east ... up to the top
let up=[W(-50,12),W(-30,12),W(22,12)];for(let n=0;n<5;n++){if(n%2===0){up=up.concat(ring(1,Math.PI/2,-Math.PI/2));up.push(W(-22,-12))}else{up=up.concat(ring(-1,-Math.PI/2,Math.PI/2));up.push(W(22,12))}}
// thread 2 down: from A1 high end westward, west U-turn to B0, east and out through the exit
const down=[W(20,12),W(-22,12),...ring(-1,Math.PI/2,-Math.PI/2),W(22,-12),W(40,-12),W(52,-12)];
const run=(path,tag,z0)=>{GATE.entry.open=true;GATE.exit.open=true;GATE.entry.t=GATE.exit.t=-99;GREF=z0||0;resetCar({free:true,x:path[0][0],y:path[0][1],h:Math.atan2(path[1][1]-path[0][1],path[1][0]-path[0][0]),z:z0||0});car.vx=0;let i=1,zmax=0,h0=hits,t=0,who=[];
  SIM(240,()=>{t+=0.02;let tgt=path[i];if(Math.hypot(tgt[0]-car.px,tgt[1]-car.py)<4.5&&i<path.length-1)i++;tgt=path[i];
    const a=wrapPi(Math.atan2(tgt[1]-car.py,tgt[0]-car.px)-car.psi);inp.steerT=clamp(-a*2.2,-1,1);const v=Math.abs(car.vx);inp.thrT=v<4.5?0.4:0;inp.brkT=v>6?0.3:0;
    zmax=Math.max(zmax,car.zb||0);if(hits>h0+who.length)who.push(`hit at (${(car.px-G.cx).toFixed(0)},${(car.py-G.cy).toFixed(0)}) z ${(car.zb||0).toFixed(1)} wp ${i}`);if(i===path.length-1&&Math.hypot(tgt[0]-car.px,tgt[1]-car.py)<3)return false});
  out.push(`${tag}: wp ${i}/${path.length-1}, top ${zmax.toFixed(2)} m, final z ${(car.zb||0).toFixed(2)}, at (${(car.px-G.cx).toFixed(0)},${(car.py-G.cy).toFixed(0)}), hits ${hits-h0}, ${t.toFixed(0)} s ${who.slice(0,4).join("; ")}`)};
run(up,"up thread 1 (Cass Ave entrance)");
run(down,"down thread 2 (to Park Ave)",garZ(1,1,20));
// a crossover: A2 heading east, switch to B2 through the middle
run([W(-14,12),W(-1,10),W(0,0),W(1,-10),W(-14,-12)],"crossover A2 to B2",garZ(1,2,-14));
out.push("stalls "+garStalls().length+", parked in garage "+parked.filter(p=>p.fixed&&inGarage(p.wx,p.wy)).length);
return out.join("\n")})()
