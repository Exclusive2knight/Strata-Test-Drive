/* falling through floors: drop the car (at rest and rolling slowly) on random spots of every floor of the Fort St garage and the
   Harbor Point sites, run 3 s, and report any spot where it sinks more than 0.6 m below where it started */
(async()=>{const out=[];setTrim("camry_se",true);cars.length=0;st.power=true;st.started=true;sys.epb=false;
for(const S of SITES){siteLoad(S);resetCar({x:S.cx,y:S.cy-80,h:0})}for(let k=0;k<240&&SITES.some(S=>!S.m);k++)await new Promise(r=>setTimeout(r,250));
let rs=7;const R=()=>(rs=(rs*16807)%2147483647)/2147483647;const bad=[];let n=0;
const tryAt=(tag,x,y,z,h)=>{GREF=z+0.3;resetCar({free:true,x,y,h,z});GREF=z+0.3;car.zb=Math.max(car.zb||0,z);const z0=car.zb;if(Math.abs(z0-z)>1)return;n++;car.vx=1.5;st.gear="D";let zl=z0;
  SIM(3,()=>{inp.thrT=inp.thr=car.vx<1.5?0.15:0;inp.brkT=inp.brk=0;inp.steerT=inp.steer=0;zl=Math.min(zl,car.zb)});if(zl<z0-0.6)bad.push(`${tag} @${(x).toFixed(1)},${(y).toFixed(1)} z ${z0.toFixed(2)} -> ${zl.toFixed(2)}`)};
for(const S of SITES){const g=S.g;if(!g)continue;for(let k=0;k<120;k++){const i=(R()*g.w)|0,j=(R()*g.h)|0,L=(R()*g.L)|0,v=g.d[(L*g.h+j)*g.w+i];if(v===-32768||v/100>1){k--;continue}
  tryAt(S.k,S.cx+g.x0+(i+0.5)*g.s,S.cy-(g.z0+(j+0.5)*g.s),S.z+v/100,R()*6.28)}}
for(let k=0;k<80;k++){const X=(R()-0.5)*96,Z=(R()-0.5)*38;const fl=[];garFloors(X,Z,h=>fl.push(h));if(!fl.length)continue;tryAt("fortst",GAR.cx+X,GAR.cy+Z,fl[(R()*fl.length)|0],R()*6.28)}
out.push(`${n} drops, ${bad.length} sank: ${bad.slice(0,20).join(" | ")}`);return out.join("\n")})()
