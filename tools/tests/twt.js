// weights: load sag and axle loads (spec test 5), trailer tongue (6), 0-60 / 60-0 with load (7), per-frame cost (13). Prints PASS / FAIL lines.
(async()=>{const o=[],P=(ok,s)=>o.push((ok?"PASS ":"FAIL ")+s),g=9.81,LB=0.45359237;
const reset=(x,y,h)=>{car.zw=null;car.th=car.phi=car.thd=car.phid=0;car.vzb=0;resetCar({free:true,x,y,h});car.zw=null;car.vx=0;inp.steer=0;inp.steerT=0;inp.thrT=0;inp.brkT=0;inp.thr=0;inp.brk=0};
const X=TCL[2]+20,Y0=TC.y0+25;
const use=async k=>{if(!MODELS[TRIMS[k].model])try{await loadModel(TRIMS[k].model)}catch(e){};setTrim(k,true);cars=[];st.power=true;st.started=true;sys.epb=false;st.gear="P";st.cargoKg=0;st.dummies=0;st.roofKg=0;st.cargoAt="auto";if(TRL.on)trlSet(null,true)};
const settle=(s=9)=>{SIM(s)};
const meas=()=>{let f=0,r=0;for(let i=0;i<4;i++)(i<2?0:1)?r+=car.fz[i]:f+=car.fz[i];const hR=car.zb+B*car.th,hF=car.zb-A*car.th;return {f:f/g,r:r/g,hR,hF}};
// ---- 5: 800 lb behind the rear axle
for(const k of ["camry25","f150_xlt","chv_silverado_1500_lt"]){if(!TRIMS[k])continue;await use(k);st.cargoAt="trunk";reset(X,Y0,Math.PI/2);car.cargo=0;settle();const a=meas(),W0f=WT.front,W0r=WT.rear;
  const W=800*LB;car.cargo=W;settle();const b=meas(),x=wtCargoX(),SP=TRIMS[k].sus,ms=WT.curb-2*SP.mw[0]-2*SP.mw[1],L=WB;
  const dF=W*(L-x)/L,dR=W*x/L,fw=WT.curb*B/L,kr=Math.pow(2*Math.PI*SP.f[1],2)*(WT.curb-fw-2*SP.mw[1])/2,kf=Math.pow(2*Math.PI*SP.f[0],2)*(fw-2*SP.mw[0])/2;   // N/m per corner
  const AR=susArch(),TB=SP.tb[1],hs=(F,k)=>{let x=F/k;const x0=0.35*TB;if(AR.helper[1]&&x>x0)x=x0+(F-k*x0)/(k*1.9);return x},sag=hs(dR*g/2,kr)+(dR*g/2)/260000,rise=(-dF*g/2)/kf+(-dF*g/2)/260000;
  const e1=Math.abs(b.f-(a.f+dF))/b.f,e2=Math.abs(b.r-(a.r+dR))/b.r,e3=Math.abs((a.hR-b.hR)-sag)/sag,e4=Math.abs((b.hF-a.hF)-rise)/Math.max(1e-4,rise);
  P(b.hR<a.hR&&b.f<a.f&&e1<0.03&&e2<0.03&&e3<0.03,`T5 ${k}: 800 lb at ${x.toFixed(2)} m behind the front axle (WB ${L.toFixed(2)}): front axle ${(a.f/LB).toFixed(0)}→${(b.f/LB).toFixed(0)} lb (hand ${((a.f+dF)/LB).toFixed(0)}, err ${(e1*100).toFixed(1)}%), rear ${(a.r/LB).toFixed(0)}→${(b.r/LB).toFixed(0)} lb (hand ${((a.r+dR)/LB).toFixed(0)}, err ${(e2*100).toFixed(1)}%), rear sag ${((a.hR-b.hR)*39.37).toFixed(2)} in (hand ${(sag*39.37).toFixed(2)}, err ${(e3*100).toFixed(1)}%), front rise ${((b.hF-a.hF)*39.37).toFixed(2)} in (hand ${(rise*39.37).toFixed(2)}, err ${(e4*100).toFixed(1)}%); WT says ${(W0f/LB).toFixed(0)}/${(W0r/LB).toFixed(0)} → ${(WT.front/LB).toFixed(0)}/${(WT.rear/LB).toFixed(0)} lb`)}
// ---- 6: a trailer with 12% tongue weight
{const k="f150_xlt";await use(k);reset(X,Y0,Math.PI/2);settle();const p0=wtPerf(),a=meas();trlSet("camper",true);TRL.tp=0.12;settle(4);const b=meas(),p1=wtPerf();
 const tw=0.12*TRL.mass,tx=A-car.tongueX,dR=tw*tx/WB,dF=tw*(WB-tx)/WB,e1=Math.abs((b.r-a.r)-dR)/dR,e2=Math.abs((b.f-a.f)-dF)/Math.abs(dF);
 P(e1<0.05&&e2<0.08&&p1.towLeft<p0.towLeft,`T6 ${k} + ${Math.round(TRL.mass/LB)} lb camper, tongue ${Math.round(tw/LB)} lb (12%) at ${tx.toFixed(2)} m: rear axle +${((b.r-a.r)/LB).toFixed(0)} lb (hand ${(dR/LB).toFixed(0)}, err ${(e1*100).toFixed(1)}%), front ${((b.f-a.f)/LB).toFixed(0)} lb (hand ${(dF/LB).toFixed(0)}, err ${(e2*100).toFixed(1)}%); stat bars: tow left ${Math.round(p0.towLeft/LB)}→${Math.round(p1.towLeft/LB)} lb, 0-60 ${p0.t60.toFixed(1)}→${p1.t60.toFixed(1)} s (est.), warnings ${WT_WARN.filter(w=>WT.warn&w[0]).map(w=>w[1]).join(", ")||"none"}`);trlSet(null,true)}
// ---- 7: 0-60 and 60-0 with load, driven in the full physics
const run=(k,kg)=>{car.cargo=kg;reset(X,Y0,Math.PI/2);car.cargo=kg;st.gear="D";SIM(1.5);let t60=null,t=0;SIM(25,(tt)=>{inp.thrT=1;inp.steerT=clamp(-(car.px-X)*0.2-wrapPi(car.psi-Math.PI/2)*1.2,-1,1);t=tt;if(car.vx>=26.82){t60=tt;return false}});
  let d=0,y0=car.py;SIM(15,()=>{inp.thrT=0;inp.brkT=1;inp.steerT=clamp(-(car.px-X)*0.2-wrapPi(car.psi-Math.PI/2)*1.2,-1,1);if(car.vx<0.05)return false});d=car.py-y0;inp.brkT=0;return {t60,d,M:WT.M}};
for(const k of ["camry25","f150_xlt"]){await use(k);const rows=[];for(const lb of [0,400,800,1200]){const r=run(k,lb*LB);rows.push([lb,r])}
  const [b0,b1]=[rows[0][1],rows[3][1]],ratio=b1.t60/b0.t60,mr=b1.M/b0.M;
  P(ratio>1+(mr-1)*0.6&&ratio<1+(mr-1)*1.25&&b1.d>b0.d,`T7 ${k}: `+rows.map(([lb,r])=>`+${lb} lb (${Math.round(r.M/LB)} lb): 0-60 ${r.t60?r.t60.toFixed(2):"—"} s, 60-0 ${(r.d*3.281).toFixed(0)} ft`).join(" · ")+` · 0-60 ratio ${ratio.toFixed(3)} vs mass ratio ${mr.toFixed(3)}`)}
// ---- 13: cost per frame
{await use("camry25");reset(X,Y0,Math.PI/2);car.cargo=200;st.dummies=3;const n=20000,t0=performance.now();for(let i=0;i<n;i++)wtTick();const ms=(performance.now()-t0)/n;P(ms<0.1,`T13 wtTick ${(ms*1000).toFixed(2)} µs per call (budget 100 µs)`)}
return o.join("\n")})()
