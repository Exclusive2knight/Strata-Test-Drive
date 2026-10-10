(async()=>{const out=[];setTrim("camry25",true);cars=[];st.power=true;st.started=true;sys.epb=false;st.gear="D";st.lka=false;
const G=GAR,xw=G.x0+4.6,xe=G.x1-4.6,A=G.ayA,Bq=G.ayB;
const lap=[[xw,A],[G.xa+6,A],[G.xb-2,A],[xe,A-4],[xe,Bq+4],[G.xb-2,Bq],[G.xa+2,Bq],[xw,Bq+4],[xw,A-4],[G.xa+2,A]];
let path=[[G.x0+2,A]];for(let k=0;k<2;k++)path=path.concat(lap.slice(1));
const run=(path,tag)=>{resetCar({free:true,x:path[0][0],y:path[0][1],h:Math.atan2(path[1][1]-path[0][1],path[1][0]-path[0][0])});car.vx=0;let i=1,zmax=0,log=[],h0=hits,t=0;
  SIM(110,()=>{t+=0.04;let tgt=path[i];if(Math.hypot(tgt[0]-car.px,tgt[1]-car.py)<4.5&&i<path.length-1)i++;tgt=path[i];
    const a=wrapPi(Math.atan2(tgt[1]-car.py,tgt[0]-car.px)-car.psi);inp.steerT=clamp(-a*2.2,-1,1);const v=Math.abs(car.vx);inp.thrT=v<4.5?0.35:0;inp.brkT=v>6?0.3:0;
    zmax=Math.max(zmax,car.zb||0);if(Math.round(t*25)%250===0)log.push(`${t.toFixed(0)}s (${car.px.toFixed(0)},${car.py.toFixed(0)}) z ${(car.zb||0).toFixed(2)} wp ${i}`);if(i===path.length-1&&Math.hypot(tgt[0]-car.px,tgt[1]-car.py)<3)return false});
  out.push(`${tag}: reached wp ${i}/${path.length-1}, zmax ${zmax.toFixed(2)} final z ${(car.zb||0).toFixed(2)} hits ${hits-h0} t ${t.toFixed(0)}s\n  `+log.join("\n  "))};
run(path,"thread 1 (west entrance)");
// thread 2 from the east entrance: start at east landing ground heading south then west into the south bay
const lap2=[[xe,A],[xe,Bq+4],[G.xb-2,Bq],[G.xa+2,Bq],[xw,Bq+4],[xw,A-4],[G.xa+2,A],[G.xb-2,A],[xe,A-4],[xe,Bq+4],[G.xb-2,Bq],[G.xa+2,Bq],[xw,Bq+4],[xw,A-4],[G.xa+2,A],[G.xb-2,A],[xe,A-4]];
run([[xe,G.y1-3],...lap2],"thread 2 (east entrance)");
out.push("stalls "+garStalls().length+", parked in garage "+parked.filter(p=>p.fixed&&inGarage(p.wx,p.wy)).length);
return out.join("\n")})()
