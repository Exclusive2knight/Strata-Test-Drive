/* ==== v38 traffic: garage parking (the Fort St garage, entry on Cass Ave, exit onto Park Ave) ====
   Control-layer agents for drivers who park in the garage. Each one: queues at the entry gate, takes a ticket (the gate opens for them and
   closes behind them), drives up, looks for a space (lowest free level first; a level that turns out full is passed and the driver goes on up,
   or gives up and leaves), shuffles into it (three- or five-point turns in the narrow aisles, some end up a bit crooked), stays a while,
   shuffles out, drives down, pays at the exit gate and pulls out onto the street as an ordinary traffic car.
   Traffic in the garage is one-way: up the thread that starts at the entrance (bay A ground floor, B1, A2, ...), across to the other thread
   at a crossover in the middle of a level, and down that one (... A3, B2, A1, B0) to the exit. No two cars ever meet head-on in an aisle.
   Agents live in `cars` with kind "errand" (the road traffic loop skips them) and c.gpk holding their state.
   The mind (traffic/mind.js) feeds in: patience (how long they wait before giving up), experience and age (second attempts, crooked parks),
   and gets told about "parked". Occupancy follows the time of day (busy 8:00-18:00, quiet at night).
   GPK.stats counts tickets, gate cycles, parks, give-ups and departures for the tests and the debug panel. */
const GPK={on:true,t:6,arrT:0,stats:{arr:0,ticket:0,park:0,left:0,give:0,second:0,crooked:0,wide:0,open:{entry:0,exit:0},close:{entry:0,exit:0},closeOnCar:0,passClosed:0},
  test:false,rate:null,dwell:null,res:new Set(),gone:[]};
const GPK_SPAWN=[-73,12],GPK_STOP=-49,GPK_PAY=43.2,GPK_OUT=[78,-12];
/* signs that turn a slope into the car's pitch and roll in carMatrix (worked out once from the matrix itself) */
let GPK_SG=null;function gpkSigns(){if(GPK_SG)return GPK_SG;const h=0.4,M0=carMatrix(0,0,h,0,0,0);let F=[0,0,1],L=[1,0,0];
  for(const v of [[1,0,0],[-1,0,0],[0,0,1],[0,0,-1]]){const q=M4.p(M0,v);if(Math.abs(q[0]-Math.cos(h))<1e-3&&Math.abs(q[2]+Math.sin(h))<1e-3)F=v;if(Math.abs(q[0]+Math.sin(h))<1e-3&&Math.abs(q[2]+Math.cos(h))<1e-3)L=v}
  return GPK_SG={p:Math.sign(M4.p(carMatrix(0,0,h,0,0.1,0),F)[1])||1,r:Math.sign(M4.p(carMatrix(0,0,h,0,0,0.1),L)[1])||1}}
function gpkZ(x,y,zr){const g=GREF;GREF=zr;let h=0;try{h=groundAt(x,y).h||0}catch(e){}GREF=g;return h}
function gpkPose(c){const z=gpkZ(c.wx,c.wy,(c.wz||0)+0.5),ch=Math.cos(c.wh),sh=Math.sin(c.wh),S=gpkSigns();
  const zf=gpkZ(c.wx+ch*1.4,c.wy+sh*1.4,z+0.5),zr=gpkZ(c.wx-ch*1.4,c.wy-sh*1.4,z+0.5),zl=gpkZ(c.wx-sh*0.8,c.wy+ch*0.8,z+0.5),zR=gpkZ(c.wx+sh*0.8,c.wy-ch*0.8,z+0.5);
  c.wz=z;c.wp=S.p*Math.atan((zf-zr)/2.8);c.wr=S.r*Math.atan((zl-zR)/1.6)}
const gpkW=P=>P.map(p=>[GAR.cx+p[0],GAR.cy+p[1]]),gpkL=(x,y)=>[x-GAR.cx,y-GAR.cy];
/* ---- one-way routes through the helix (local coordinates: X along the aisles, Z across, aisles at Z = +12 (bay A) and -12 (bay B)) */
const gpkThread=(sd,n)=>((sd>0)===(n%2===0))?1:2,gpkFlow=(sd,n)=>gpkThread(sd,n)===1?(sd>0?1:-1):(sd>0?-1:1);   /* thread 1 goes up, thread 2 comes down; flow: +1 east */
function gpkArcUp(P,sd){if(sd>0)garArc(P,24,Math.PI/2,-Math.PI/2);else garArc(P,-24,-Math.PI/2,-Math.PI*1.5)}
function gpkArcDown(P,sd){if(sd<0)garArc(P,24,-Math.PI/2,Math.PI/2);else garArc(P,-24,Math.PI/2,Math.PI*1.5)}
function gpkCross(P,sd,n){const f1=gpkFlow(sd,n),f2=gpkFlow(-sd,n);garLine(P,-3*f1,12*sd);garLine(P,-1.2*f1,10.8*sd);garLine(P,0,8.5*sd);garLine(P,0,-8.5*sd);garLine(P,1.2*f2,-10.8*sd);garLine(P,3*f2,-12*sd)}
/* from the street to the point E where the shuffle into space t starts (null: not reachable going with the flow) */
function gpkRouteIn(t,E){const sdT=t.bay,nT=t.k,fT=gpkFlow(sdT,nT),P=[[GPK_SPAWN[0],12]];garLine(P,-62,12);let sd=1,n=0,entry;
  const up=m=>{while(n<m){garLine(P,24*gpkFlow(sd,n),12*sd);gpkArcUp(P,sd);sd=-sd;n++}};
  if(gpkThread(sdT,nT)===1){up(nT);entry=-24*fT}
  else{const here=(E[0]-2*fT)*fT>=10,m=here?nT:nT+1;if(m>GAR.T-1)return null;up(m);gpkCross(P,sd,n);sd=-sd;entry=here?2*fT:-24*fT;while(n>nT){garLine(P,24*gpkFlow(sd,n),12*sd);gpkArcDown(P,sd);sd=-sd;n--}}
  if((E[0]-entry)*fT<10)return null;garLine(P,E[0]-10*fT,12*sdT);return P.concat(gpkBlend(P[P.length-1],E,fT))}
/* from a point on an aisle, with the flow, down to the pay station at the exit (null: on the top floor past its crossover) */
function gpkRouteOut(sd,n,X){const P=[[X,12*sd]];
  if(gpkThread(sd,n)===1){const f=gpkFlow(sd,n);if(X*f<-3){gpkCross(P,sd,n);sd=-sd}else{if(n>=GAR.T-1)return null;garLine(P,24*f,12*sd);gpkArcUp(P,sd);sd=-sd;n++;gpkCross(P,sd,n);sd=-sd}}
  for(let k=0;k<12;k++){const f=gpkFlow(sd,n);if(n===0){garLine(P,GPK_PAY,12*sd);break}garLine(P,24*f,12*sd);gpkArcDown(P,sd);sd=-sd;n--}return P}
/* the way out from the end e of a shuffle: drift onto the middle of the aisle along the straight, then the route down */
function gpkOutFrom(e,sd,n){const D=gpkRouteOut(sd,n,e[0]);if(!D)return null;const f=gpkFlow(sd,n);let i0=0;while(i0<D.length-2&&((D[i0][0]-e[0])*f<4||(D[i0][0]-e[0])*f<12&&Math.abs(D[i0+1][1]-D[i0][1])<0.2))i0++;
  return [[e[0],e[1]]].concat(gpkBlend([e[0],e[1]],D[i0],f),D.slice(i0+1))}
/* drift across the aisle smoothly (over about 10 m, not sideways) to a point on it */
function gpkBlend(A,E,dir){const out=[],L=Math.abs(E[0]-A[0]);const n=Math.max(2,Math.ceil(L));for(let i=1;i<=n;i++){const u=i/n,w=u*u*(3-2*u);out.push([A[0]+(E[0]-A[0])*u,A[1]+(E[1]-A[1])*w])}return out}
/* ---- in and out of a space: the aisles here are narrow (5 m) for 90-degree spaces, so like real drivers the cars shuffle: back straight out,
   then turn on full lock forwards and backwards (a three- or five-point turn) inside the aisle, using their own space and any empty space next to it,
   until they face down the aisle. Going in is the same moves played backwards. Planned in the garage's own coordinates (X along the aisle) */
function gpkPlan(t,len,wid,lat,crk,hEnd,me_){const sd=t.bay,inner=Math.abs(t.y-GAR.cy)<12,Xs=t.x-GAR.cx,hl=len/2+0.02,hw=wid/2+0.04;
  const rowIn=[4.3,9.45],rowOut=[14.55,19.7],own=inner?rowIn:rowOut;
  const free=garStalls().filter(u=>u!==t&&u.k===t.k&&u.bay===t.bay&&Math.abs(u.x-t.x)<7&&gpkFree(u,null)).map(u=>[u.x-GAR.cx,Math.abs(u.y-GAR.cy)<12?rowIn:rowOut]);
  const okP=(px,pz)=>{const a=pz*sd;if(Math.abs(px)>23.5)return false;if(a>9.42&&a<14.58)return true;if(Math.abs(px-Xs)<1.32&&a>own[0]&&a<own[1]+0.1)return true;for(const f of free)if(Math.abs(px-f[0])<1.32&&a>f[1][0]&&a<f[1][1]+0.1)return true;return false};
  const SP=[[1,1],[1,-1],[-1,1],[-1,-1],[1,0],[-1,0],[0,1],[0,-1],[0.5,1],[0.5,-1],[-0.5,1],[-0.5,-1]];
  const OB=[];for(const p of parked)if(p.wx!==undefined&&Math.abs(p.wx-t.x)<12&&Math.abs(p.wy-(GAR.cy+12*sd))<10&&Math.abs((p.wz||0)-t.z)<1.6)OB.push([p.wx-GAR.cx,p.wy-GAR.cy,p.wh||0,2.25,0.9]);
  for(const o of cars)if(o.gpk&&o!==me_&&(o.gpk.ph==="park"||o.gpk.ph==="leave0")&&Math.abs(o.wx-t.x)<12&&Math.abs((o.wz||0)-t.z)<1.6)OB.push([o.wx-GAR.cx,o.wy-GAR.cy,o.wh,(o.len||CARLEN)/2,(o.wid||1.9)/2]);
  const ok=(X,Z,h)=>{const c=Math.cos(h),s=Math.sin(h);for(const [a,b] of SP)if(!okP(X+c*hl*a-s*hw*b,Z+s*hl*a+c*hw*b))return false;for(const o of OB)if(Math.abs(o[0]-X)<6&&obbSAT(X,Z,h,hl,hw,o[0],o[1],o[2],o[3],o[4]))return false;return true};
  const h0=Math.atan2(t.uy,t.ux)+crk,X0=Xs+(t.uy!==0?lat:0),Z0=t.y-GAR.cy+(t.ux!==0?lat:0);if(!ok(X0,Z0,h0))return null;
  /* straight back until the front is out of the row of spaces */
  const st0=[[X0,Z0,h0]];let p=[X0,Z0,h0];{const ux=Math.cos(h0),uz=Math.sin(h0);for(let d=0.05;d<7;d+=0.05){const q=[X0-ux*d,Z0-uz*d,h0];if(!ok(q[0],q[1],q[2]))break;st0.push(q);p=q;const fz=(q[1]+uz*hl)*sd;if(fz>9.7&&fz<14.3)break}}
  const turn=(p0,rv,lock)=>{let p=p0.slice();const M=[];let stuck=0;for(let m=0;m<16;m++){const D=wrapPi(hEnd-p[2]);if(Math.abs(D)<0.02)return M;const sg=rv?-1:1,del=Math.sign(D)*sg*lock,pts=[p.slice()];let moved=0;
      for(let i=0;i<200;i++){const ds=0.05,h=p[2]+sg*ds/2.8*Math.tan(del),q=[p[0]+Math.cos(h)*ds*sg,p[1]+Math.sin(h)*ds*sg,h];if(!ok(q[0],q[1],q[2]))break;const D2=wrapPi(hEnd-h);if(Math.sign(D2)!==Math.sign(D))break;p=q;pts.push(q);moved+=ds;if(Math.abs(D2)<0.02)break}
      if(moved>0.1){M.push({pts,rev:rv});stuck=0}else if(++stuck>=2)return null;rv=!rv}return Math.abs(wrapPi(hEnd-p[2]))<0.03?M:null};
  /* a few ways of doing it (how far to back out first, which way first, how hard to turn): keep the one with the fewest moves */
  const laneZ=12*sd;   /* where it should end up: the middle of the (one-way) aisle */
  let best=null,bestK=0,bestS=1e9;for(const cut of [0,6,12,20,30,40])for(const rv of [true,false])for(const lock of [0.6,0.52,0.44,0.36]){const k=st0.length-1-cut;if(k<1)continue;const M=turn(st0[k],rv,lock);if(!M)continue;const L_=M[M.length-1].pts,e=L_[L_.length-1],sc=M.length+Math.abs(e[1]-laneZ)*8;if(sc<bestS){best=M;bestK=k;bestS=sc}}
  if(!best)return null;st0.length=bestK+1;
  const moves=[{pts:st0,rev:true},...best];const last=moves[moves.length-1].pts,end=last[last.length-1];
  /* the move list ends with the car on the aisle, facing hEnd; it must be clear of the aisle ends */
  if(Math.abs(end[0])>21)return null;return {moves,end,turns:best.length}}
/* the same moves backwards: driving in */
function gpkRev(P){const moves=P.moves.slice().reverse().map(m=>({pts:m.pts.slice().reverse(),rev:!m.rev}));return {moves,end:P.moves[0].pts[0],start:P.end,turns:P.turns}}
function gpkMv(c,P){const G=c.gpk;G.mv={moves:P.moves.map(m=>{const w=m.pts.map(q=>[GAR.cx+q[0],GAR.cy+q[1],q[2]]),cum=[0];for(let i=1;i<w.length;i++)cum.push(cum[i-1]+Math.hypot(w[i][0]-w[i-1][0],w[i][1]-w[i-1][1]));return {w,cum,rev:m.rev}}),mi:0,s:0};gpkMvSeg(c)}
function gpkMvSeg(c){const G=c.gpk,m=G.mv.moves[G.mv.mi];if(m)G.seg={path:m.w,rev:m.rev,i:0}}
/* play the planned moves: slow, a stop and a look at every change of direction */
function gpkReplay(c,dt){const G=c.gpk,M=G.mv,m=M.moves[M.mi];if(!m)return true;const L=m.cum[m.cum.length-1],left=L-M.s,vT=Math.min(m.rev?0.85:1.2,Math.sqrt(2*0.7*Math.max(0,left))+0.12);
  c.v=Math.max(0,c.v+clamp(vT-c.v,-1.6*dt,1.0*dt));M.s=Math.min(L,M.s+c.v*dt);let i=1;while(i<m.cum.length-1&&m.cum[i]<M.s)i++;const a=m.w[i-1],b=m.w[i],f=clamp((M.s-m.cum[i-1])/Math.max(1e-6,m.cum[i]-m.cum[i-1]),0,1);
  c.wx=a[0]+(b[0]-a[0])*f;c.wy=a[1]+(b[1]-a[1])*f;c.wh=a[2]+wrapPi(b[2]-a[2])*f;G.seg.i=i-1;c.rev=m.rev;c.spin+=(m.rev?-1:1)*c.v/0.36*dt;gpkPose(c);
  if(M.s>=L-1e-4){M.mi++;M.s=0;c.v=0;if(M.mi<M.moves.length){gpkMvSeg(c);G.look=0.5}else return true}return false}
function gpkBez(A,B,C,D,n){const P=[];for(let i=0;i<=n;i++){const t=i/n,u=1-t;P.push([u*u*u*A[0]+3*u*u*t*B[0]+3*u*t*t*C[0]+t*t*t*D[0],u*u*u*A[1]+3*u*u*t*B[1]+3*u*t*t*C[1]+t*t*t*D[1]])}return P}
const gpkKey=t=>t.k+":"+t.bay+":"+t.x.toFixed(2)+":"+t.y.toFixed(2);
function gpkFree(t,me){if(GPK.res.has(gpkKey(t))&&!(me&&me.gpk.key===gpkKey(t)))return false;
  if(parked.some(p=>p.wx!==undefined&&Math.abs(p.wx-t.x)<1.6&&Math.abs(p.wy-t.y)<2.4&&Math.abs((p.wz||0)-t.z)<1.2))return false;
  return !cars.some(c=>c!==me&&c.wx!==undefined&&Math.abs(c.wx-t.x)<1.8&&Math.abs(c.wy-t.y)<2.6&&Math.abs((c.wz||0)-t.z)<1.2)}
/* which space a driver goes for: the lowest level with room, near the lifts (the aisle ends), with some noise; `from` = only spaces whose
   way up passes where the car is now (so it can carry on to them) */
function gpkPick(c,minK){const d=c.mind,R=()=>d?d.R():Math.random();const L=garStalls().filter(t=>t.k>=(minK||0)&&gpkFree(t,c));if(!L.length)return null;
  const sc=t=>t.k*10+(24-Math.abs(t.x-GAR.cx))*0.12+R()*5;L.sort((a,b)=>sc(a)-sc(b));
  for(const t of L.slice(0,18)){const P=gpkPlanIn(c,t);if(!P||!gpkRouteOut(t.bay,t.k,t.x-GAR.cx))continue;const U=gpkRouteIn(t,P.start);if(!U)continue;if(!c.gpk.seg||c.gpk.ph==="ticket")return t;
    const W=gpkW(U);let best=9;for(let i=0;i<W.length;i++){const dd=Math.hypot(W[i][0]-c.wx,W[i][1]-c.wy);if(dd<best&&gpkPathZ(W,i,c))best=dd}if(best<1.6)return t}   /* (only a way that passes where the car is, on its floor) */
  return null}
function gpkSet(c,ph,P,rev){const G=c.gpk;G.ph=ph;G.seg={path:P,rev:!!rev,i:0,tight:ph==="in"};G.i=0;G.wait=0;G.look=ph==="back"?1+((c.mind&&c.mind.R())||Math.random())*1.4:0}
function gpkLog(c,msg){try{if(c.mind)tmLog(c.mind,msg)}catch(e){}}
/* a new arrival at the entry lane (only when nobody is right there) */
function gpkSpawn(){const P=gpkW([GPK_SPAWN])[0];if(cars.some(o=>o.wx!==undefined&&Math.hypot(o.wx-P[0],o.wy-P[1])<7.5))return null;if(!GPK.test&&aiSeen(P[0],P[1],0))return null;   /* never pops up in front of you */
  const f=findFrame(P[0],P[1],0,null);const c=newCar(f.e,f.dir,f.s,0);trafficModel(c);for(let k=0;k<8&&((c.len||0)>5.2||c.mdl==="city_police");k++){c.mdl=undefined;c.len=undefined;c.wid=undefined;trafficModel(c)}   /* cars and small SUVs: the long trucks and vans do not fit the 5 m spaces */
  Object.assign(c,{kind:"errand",fixed:true,wx:P[0],wy:P[1],wh:0,wz:0,v:2,spin:0,sig:0,head:0,haz:false});
  try{tmInit(c)}catch(e){}c.tmKeep=1;const d=c.mind,R=()=>d?d.R():Math.random();
  const nov=d&&(d.exp==="novice"||d.arch==="novice"),old=d&&(d.age==="senior"||d.arch==="elder");
  c.gpk={ph:"queue",t:0,P:null,i:0,stall:null,key:null,tries:0,dwell:GPK.dwell?GPK.dwell(c):600+R()*3000,
    crooked:R()<(nov||old?0.35:0.12)?(R()-0.5)*0.12:0,latErr:(R()-0.5)*(nov?0.4:0.2),patience:d?d.tr.patience:0.5};
  gpkSet(c,"queue",gpkW([[GPK_SPAWN[0],12],[GPK_STOP,12]]));cars.push(c);GPK.stats.arr++;gpkPose(c);return c}
/* is the way ahead clear of other cars (and you)? a box in front of the bumper, longer when moving faster */
/* is the way ahead clear? the car's own footprint swept along the path it is about to drive (a bend is checked as a bend), out to its
   stopping distance plus a margin, against the other cars (moving or parked) on that floor and you */
function gpkClear(c,rev,ign){if(c.gpk.ph==="in"&&c.gpk.stall&&Math.hypot(c.gpk.stall.x-c.wx,c.gpk.stall.y-c.wy)<3.4)return null;   /* rolling the last bit into its own (reserved) space */
  const G=c.gpk,sg=G.seg,P=sg.path,half=(c.len||CARLEN)/2,hw=(c.wid||1.9)/2+0.06,look=(rev?0.8:1.6)+Math.abs(c.v)*1.2+(G.ph==="in"?0:0.4);
  /* samples: where the car is, then the path points ahead with the path's own heading (a car a little off its line must not look sideways) */
  const S=[[c.wx,c.wy,c.wh]];{let acc=0;const fx=Math.cos(c.wh)*(rev?-1:1),fy=Math.sin(c.wh)*(rev?-1:1);for(let k=Math.max(1,(sg.i||0)+1);k<P.length&&acc<look;k++){const a=P[k-1],b=P[k],d=Math.hypot(b[0]-a[0],b[1]-a[1]);if(d<0.02)continue;
      const h=b.length>2?b[2]:Math.atan2(b[1]-a[1],b[0]-a[0])+(rev?Math.PI:0),n=Math.max(1,Math.ceil(d/0.8));for(let q=1;q<=n&&acc<look;q++){const x=a[0]+(b[0]-a[0])*q/n,y=a[1]+(b[1]-a[1])*q/n;if((x-c.wx)*fx+(y-c.wy)*fy<0.2)continue;acc+=d/n;S.push([x,y,h])}}}
  if(!G.zone&&/^(queue|up|down|out)$/.test(G.ph)){const z=gpkRegAhead(c,S,rev);if(z){G.bw='reg'+(z.gpk.reg?'['+z.gpk.reg.x0.toFixed(0)+','+z.gpk.reg.x1.toFixed(0)+']':'')+' S'+S.length;return z}}G.bw='body S'+S.length;
  /* coming out of a crossover onto an aisle: wait inside the crossover, fully clear of the aisle, until the mouth of the aisle is free
     (nobody coming along it near the crossover, nobody shuffling into a space right there) */
  {const L0=gpkL(c.wx,c.wy),hz=Math.sin(c.wh)*(rev?-1:1);if(!G.mv&&Math.abs(L0[0])<3.5&&Math.abs(L0[1])<7.6&&Math.abs(L0[1])>2.5&&Math.sign(hz)===Math.sign(L0[1])&&Math.abs(hz)>0.5){const sd=Math.sign(L0[1]);
    for(const o of cars){if(o===c||!o.gpk||o.gpk.ph==="park"||o.gpk.ph==="leave0"||Math.abs((o.wz||0)-(c.wz||0))>1.6)continue;const Lo=gpkL(o.wx,o.wy);if(Math.abs(Lo[1]-12*sd)<3.2&&Math.abs(Lo[0])<9)return o;
      const R=o.gpk.reg;if(R&&R.bay===sd&&Math.abs(R.z-(c.wz||0))<1.7&&R.x0<6&&R.x1>-6&&(o.gpk.zone||o.gpk.ph==="up"))return o}}}
  /* single file: in the one-way aisles and the exit lane, anyone ahead of us (along the way we face) within a car length and a bit stops us,
     whatever the path samples say (two cars merging onto the same lane used to see each other only when it was too late); side by side, the
     one with the higher number waits, so two can never wait for each other */
  if(!G.mv&&/^(queue|up|down|out|pay)$/.test(G.ph)){const fx=Math.cos(c.wh)*(rev?-1:1),fy=Math.sin(c.wh)*(rev?-1:1),reach=(c.len||CARLEN)+1.4+Math.abs(c.v)*0.9;
    for(const o of cars){if(o===c||!o.gpk||o.gpk.ph==="park"||o.gpk.ph==="leave0"||o.wx===undefined||Math.abs((o.wz||0)-(c.wz||0))>1.6)continue;const dx=o.wx-c.wx,dy=o.wy-c.wy,lon=dx*fx+dy*fy,lat=Math.abs(-dx*fy+dy*fx);
      const og=o.gpk,parking=og.zone||og.claimWait>0||og.ph==="up"&&og.seg&&og.seg.path&&og.seg.i>og.seg.path.length-14;   /* someone about to shuffle into a space: leave them room to back up */
      if(lat<2.1&&(lon>0.4&&lon<reach+(parking?5.5:0)||Math.abs(lon)<=0.4&&c.id>o.id))return o}}
  const box=function(x,y,h,l,w,z){{if(Math.abs((z||0)-(c.wz||0))>1.6)return false;if((x-c.wx)**2+(y-c.wy)**2>(look+8)**2)return false;
    const st_=arguments[6];for(let q=S.length>1?1:0;q<S.length;q++){const p=S[q];if(st_?obbSAT(p[0],p[1],p[2],half,hw-0.04,x,y,h,l,w):obbSAT(p[0],p[1],p[2],half+0.08,hw,x,y,h,l,w))return true}return false}};
  for(const o of cars){if(o===c||o===ign||o.wx===undefined||o.kind==="cone")continue;if(G.mv&&o.gpk&&(o.gpk.ph==="park"||o.gpk.ph==="leave0"))continue;if(box(o.wx,o.wy,o.wh,(o.len||CARLEN)/2,(o.wid||1.9)/2,o.wz,!!(o.gpk&&(o.gpk.ph==="park"||o.gpk.ph==="leave0"))))return o}
  if(!st.walk&&st.started&&box(car.px,car.py,car.psi,2.4,1,car.zb||0))return "me";if(st.walk&&box(st.walk.x,st.walk.y,0,0.4,0.4,st.walk.z||0))return "me";
  if(G.mv)return null;   /* a planned shuffle already keeps clear of parked cars */
  for(const p of parked){if(p.wx===undefined||Math.abs(p.wx-c.wx)>look+8||Math.abs(p.wy-c.wy)>look+8)continue;if(box(p.wx,p.wy,p.wh||0,2.25,0.9,p.wz,true))return p}
  return null}
/* turning in and backing out need a stretch of the aisle to themselves (from the planned moves: the region R). Cars driving through stop short of
   another car's region while it shuffles, or while it is pulling up to its space; a car only starts once nobody else is in its region */
function gpkRegion(t,P){let x0=1e9,x1=-1e9;for(const m of P.moves)for(const q of m.pts){const e=2.42*Math.abs(Math.cos(q[2]))+1.0*Math.abs(Math.sin(q[2]));x0=Math.min(x0,q[0]-e);x1=Math.max(x1,q[0]+e)}return {x0:x0-0.5,x1:x1+0.5,bay:t.bay,k:t.k,z:t.z,cx:GAR.cx+(x0+x1)/2,cy:GAR.cy+12*t.bay}}
function gpkIn(R,x,y,z,ex){const X=x-GAR.cx,Z=(y-GAR.cy)*R.bay;return X>R.x0-ex&&X<R.x1+ex&&Z>8.4&&Z<15.6&&Math.abs((z||0)-R.z)<1.7}
function gpkZoneFree(c){const R=c.gpk.reg;if(!R)return true;for(const o of cars){if(o===c||!o.gpk)continue;const g=o.gpk;
    if(g.zone&&g.reg&&g.reg.k===R.k&&g.reg.bay===R.bay&&g.reg.x0<R.x1+1&&g.reg.x1>R.x0-1&&Math.abs(g.reg.z-R.z)<1.7)return false;
    if(g.ph!=="park"&&g.ph!=="leave0"&&gpkIn(R,o.wx,o.wy,o.wz,Math.abs(o.v)>0.3?4:2.3))return false}return true}
function gpkRegAhead(c,S,rev){const fx=Math.cos(c.wh)*(rev?-1:1),fy=Math.sin(c.wh)*(rev?-1:1);for(const o of cars){if(o===c||!o.gpk||!o.gpk.reg)continue;const g=o.gpk,R=g.reg;if(!(g.zone||(g.ph==="up"&&!(g.wait>1)&&Math.hypot(o.wx-R.cx,o.wy-R.cy)<16&&Math.hypot(o.wx-R.cx,o.wy-R.cy)<Math.hypot(c.wx-R.cx,c.wy-R.cy)-1)))continue;   /* a car still pulling up only has the region if it is nearer to it than we are */
    if(gpkIn(R,c.wx,c.wy,c.wz,2.2)||(R.cx-c.wx)*fx+(R.cy-c.wy)*fy<0)continue;   /* already in it (it got there first): carry on out */for(let q=1;q<S.length;q++)if(gpkIn(R,S[q][0],S[q][1],c.wz,2.5))return o}return null}
function gpkGate(k,open){const g=GATE[k];if(open&&!g.open){g.open=true;g.t=0;GPK.stats.open[k]++}else if(!open&&g.open){g.open=false;GPK.stats.close[k]++;
    /* closing on a car: count it (the tests want none) */
    for(const o of cars){if(o.wx===undefined)continue;const L=gpkL(o.wx,o.wy);if(Math.abs(L[0]-(g.gx-GAR.cx))<2.6&&L[1]>g.ya-GAR.cy-0.5&&L[1]<g.yb-GAR.cy+0.5)GPK.stats.closeOnCar++}}}
function gpkTick(dt){if(!GPK.on||!W2||!st.started)return;if(GPK.test)for(const g of Object.values(GATE))g.a+=clamp((g.open?1.4:0)-g.a,-1.5*dt,1.5*dt);   /* headless tests do not run gateTick (the render loop) */
  const near=Math.hypot(plX()-GAR.cx,plY()-GAR.cy)<700||GPK.test;
  /* new arrivals: by the time of day (or the test's rate), only while you're near enough to see it */
  if(near){GPK.arrT-=dt;if(GPK.arrT<=0){const h=hourNow(),occ=garStalls().filter(t=>!gpkFree(t,null)).length/garStalls().length,want=h<6?0.12:h<8?0.35:h<18?0.72:h<22?0.45:0.2;
      GPK.arrT=GPK.rate?GPK.rate():(occ<want?14+Math.random()*20:60+Math.random()*60);if((GPK.rate||occ<want+0.05)&&!(GPK.max&&GPK.stats.arr>=GPK.max))gpkSpawn()}}
  for(let i=cars.length-1;i>=0;i--){const c=cars[i];if(!c.gpk)continue;const ph0=c.gpk.ph;try{gpkStep(c,dt)}catch(e){console.error(e);c.gpk.ph="gone";c.gpk.why="error "+e.message}if(c.gpk.ph==="gone"&&GPK.gone.length<40)GPK.gone.push(`${c.id} ${ph0}: ${c.gpk.why||"?"} at ${(c.wx-GAR.cx).toFixed(0)},${(c.wy-GAR.cy).toFixed(0)} z${(c.wz||0).toFixed(1)}`);if(c.gpk.ph==="gone"){if(c.gpk.key)GPK.res.delete(c.gpk.key);cars.splice(cars.indexOf(c),1)}}
  /* the gates close once the car that opened them is through */
  for(const k of ["entry","exit"]){const g=GATE[k];if(!g.open||!g.gpkC)continue;const o=g.gpkC,L=o.wx!==undefined?gpkL(o.wx,o.wy):[999,0];if(L[0]-(o.len||CARLEN)/2>g.gx-GAR.cx+1.2||!cars.includes(o)){g.gpkC=null;gpkGate(k,false)}}}
function gpkStep(c,dt){const G=c.gpk;G.t+=dt;const S=GPK.stats;if(G.noBack>0){G.noBack-=dt/20;if(G.noBack<=0)G.noBack=0}
  if(G.ph==="ticket"){c.v=0;G.wait-=dt;if(G.wait<=0&&!GATE.entry.open){gpkGate("entry",true);GATE.entry.gpkC=c;S.ticket++;gpkLog(c,"took a ticket at the gate")}
    if(GATE.entry.open&&GATE.entry.gpkC===c&&GATE.entry.a>1.25){const t=gpkPick(c,0);if(!t){gpkLog(c,"garage full: leaving");S.give++;G.ph="gone";G.why="full";return}gpkTake(c,t);G.ph="up"}return}
  if(G.ph==="pay"){c.v=0;G.wait-=dt;if(G.wait<=0&&!GATE.exit.open){gpkGate("exit",true);GATE.exit.gpkC=c;gpkLog(c,"paid at the exit")}
    if(GATE.exit.open&&GATE.exit.gpkC===c&&GATE.exit.a>1.25)gpkSet(c,"out",gpkW([gpkL(c.wx,c.wy),[60,-12],GPK_OUT]));return}
  if(G.ph==="park"){c.v=0;G.dwell-=dt;if(G.dwell<=0){G.ph="leave0"}return}
  if(G.ph==="leave0"){const t=G.stall,dd=gpkFlow(t.bay,t.k),P=gpkPlan(t,c.len||CARLEN,c.wid||1.9,G.latErr,G.crooked,dd>0?0:Math.PI,c);   /* backs out and shuffles round to face the way the aisle runs */
    const D=P?gpkOutFrom(P.end,t.bay,t.k):null;
    if(!P||!D){c.v=0;G.wait+=dt;if(G.wait>300){G.ph="gone";G.why="can't get out of the space"}return}G.reg=gpkRegion(t,P);if(!gpkZoneFree(c)){c.v=0;return}G.zone=1;G.wait=0;G.ph="back";gpkMv(c,P);G.look=1+((c.mind&&c.mind.R())||Math.random())*1.2;
    G.down=gpkW(D);return}
  if(G.look>0){G.look-=dt;c.v=0;return}
  /* the space it was going for got taken (by you, or a car backing in): pick another further on, or give up and leave */
  if(G.ph==="up"&&G.stall&&!gpkFree(G.stall,c)){const t=gpkPick(c,G.stall.k);if(t){gpkLog(c,`space taken: trying level ${t.k+1}`);gpkTake(c,t,true)}else{gpkLog(c,"no space: heading for the exit");S.give++;G.giveUp=1;gpkRelease(c);gpkExitFrom(c)}}
  const blk=gpkClear(c,G.seg.rev);
  if(blk){c.v=Math.max(0,c.v-6*dt);if(c.v<0.05)c.v=0;G.wait+=dt;G.blkBy=blk==='me'?'you':blk.gpk?blk.id+':'+blk.gpk.ph:(blk.kind||'parked');
    /* nose to nose with someone who is waiting on us too: the later one backs off for a moment */
    if(G.wait>4&&blk.gpk&&blk.gpk.wait>4&&c.id>blk.id&&!G.seg.rev){G.yield=(G.yield||0)+dt;if(G.yield>1.5){G.wait=0;G.yield=0;G.look=2.5}}
    /* right up against someone shuffling in or out: back up a few metres to give them room */
    /* head to head with another car in the aisle: the one going down (or, both the same, the later one) backs up for the other */
    const mutual=blk.gpk&&blk.gpk.blkBy&&String(blk.gpk.blkBy).startsWith(c.id+":")&&!blk.gpk.zone&&(blk.gpk.noBack&&!G.noBack||!blk.gpk.noBack&&(G.ph==="down"&&blk.gpk.ph!=="down"||G.ph===blk.gpk.ph&&c.id>blk.id||G.ph==="out"));   /* (if they could not back up, we do) */
    if(false&&(blk.gpk&&(blk.gpk.zone||blk.gpk.claimWait>2)||mutual)&&!G.zone&&!G.seg.rev&&G.wait>2&&!G.resume&&!G.noBack&&/^(up|down|queue|out)$/.test(G.ph)){   /* (v38: no backing up in the one-way aisles: it only ever backed into the next car) */const ux=Math.cos(c.wh),uy=Math.sin(c.wh),B=[[c.wx,c.wy]];for(let d=0.5;d<=(mutual?8:4);d+=0.5)B.push([c.wx-ux*d,c.wy-uy*d]);
      G.resume={ph:G.ph,path:G.seg.path,i:G.seg.i||0};G.seg={path:B,rev:true,i:0};G.wait=0;G.look=0.5;gpkLog(c,"backed up to give a car room");return}
    /* backing up for someone and there's a car behind: stop backing and wait where we are */
    if(G.resume&&G.seg.rev&&G.wait>1.5){const R_=G.resume;G.resume=null;let i0=R_.i,b=1e9;for(let i=Math.max(0,R_.i-40);i<Math.min(R_.path.length,R_.i+12);i++){const d=Math.hypot(R_.path[i][0]-c.wx,R_.path[i][1]-c.wy);if(d<b){b=d;i0=i}}   /* (near where we left it: the thread passes the same spot on other floors) */gpkSet(c,R_.ph,R_.path.slice(i0));G.noBack=1;return}
    if(G.wait>150){gpkLog(c,"boxed in: gave up");G.why="boxed in by "+(blk==="me"?"you":blk.gpk?"garage car "+blk.id+" ("+blk.gpk.ph+" zone"+(blk.gpk.zone||0)+" w"+(blk.gpk.wait||0).toFixed(0)+(blk.gpk.blkBy?" by "+blk.gpk.blkBy:"")+")":blk.kind||"parked car")+' '+G.bw+(blk!=="me"?` at ${(blk.wx-GAR.cx).toFixed(1)},${(blk.wy-GAR.cy).toFixed(1)} z${(blk.wz||0).toFixed(1)}`:"")+` me h${c.wh.toFixed(2)} stall ${G.stall?(G.stall.x-GAR.cx).toFixed(1)+","+(G.stall.y-GAR.cy).toFixed(1)+" k"+G.stall.k:"-"} rev${G.seg.rev?1:0} i${G.seg.i}/${G.seg.path.length}`;G.ph="gone"}return}
  G.wait=0;G.blkBy=null;if(G.noBack){G.noBack-=dt*0.2;if(G.noBack<=0)G.noBack=0}
  if(G.mv&&(G.ph==="in"||G.ph==="back")){if(!gpkReplay(c,dt))return;G.mv=null;
    if(G.ph==="in"){G.ph="park";G.zone=0;G.reg=null;c.v=0;S.park++;if(G.crooked)S.crooked++;c.sig=0;gpkLog(c,`parked on level ${G.stall.k+1}`);try{tmEvent(c,"parked")}catch(e){}}
    else{G.zone=0;G.reg=null;gpkRelease(c);gpkSet(c,"down",G.down);G.look=0.6}return}
  let done=lotFollow(c,G.seg,dt);if(done&&(G.seg.i||0)<G.seg.path.length-4){done=false}   /* (the path passes over its own end point a floor higher or lower: only the real end counts) */G.i=G.seg.i||0;gpkPose(c);c.spin+=(G.seg.rev?-1:1)*(c.v||0)/0.36*dt;
  if(G.ph==="up"&&G.stall){const L=gpkL(c.wx,c.wy),Xt=G.stall.x-GAR.cx;c.sig=Math.abs(L[0]-Xt)<14&&Math.abs(L[1]-12*G.stall.bay)<3?(G.stall.uy*G.stall.bay>0?1:-1)*(G.dir>0?1:-1)*(G.stall.bay>0?-1:1):0}
  if(!done)return;c.v=Math.min(c.v,0.8);
  if(G.resume&&G.seg.rev){const R_=G.resume;G.resume=null;let i0=R_.i,b=1e9;for(let i=Math.max(0,R_.i-40);i<Math.min(R_.path.length,R_.i+12);i++){const d=Math.hypot(R_.path[i][0]-c.wx,R_.path[i][1]-c.wy);if(d<b){b=d;i0=i}}   /* (near where we left it: the thread passes the same spot on other floors) */gpkSet(c,R_.ph,R_.path.slice(i0));G.look=3;return}
  if(G.ph==="queue"){G.ph="ticket";c.v=0;G.wait=2.2+Math.random()*2.5+(c.mind&&c.mind.exp==="novice"?2:0)}
  else if(G.ph==="up"){if(!gpkZoneFree(c)){c.v=0;G.claimWait=(G.claimWait||0)+dt;G.seg.i=Math.max(0,G.seg.path.length-2);return}G.claimWait=0;G.zone=1;gpkTurnIn(c)}
  else if(G.ph==="down"){G.ph="pay";c.v=0;G.wait=2+Math.random()*3}
  else if(G.ph==="out"){gpkToRoad(c)}}
/* is path point i on the floor the car is on? (walk the path's heights from the street, so a point on another floor at the same spot is told apart) */
function gpkPathZ(W,i,c){if(!W._z){let z=0;W._z=W.map(p=>z=gpkZ(p[0],p[1],z+0.6))}return Math.abs(W._z[i]-(c.wz||0))<1.2}
function gpkTake(c,t,keepPath,P){const G=c.gpk;if(G.key)GPK.res.delete(G.key);G.stall=t;G.key=gpkKey(t);GPK.res.add(G.key);
  if(!P)P=gpkPlanIn(c,t);G.plan=P;G.reg=P?gpkRegion(t,P):null;G.dir=gpkFlow(t.bay,t.k);const U=P?gpkRouteIn(t,P.start):null;if(!U){G.ph="gone";G.why="no route";return}const W=gpkW(U);
  let i0=0;{let best=1e9;const zr=(c.wz||0)+0.5;for(let i=0;i<W.length;i++){const d=Math.hypot(W[i][0]-c.wx,W[i][1]-c.wy);if(d<best&&gpkPathZ(W,i,c)){best=d;i0=i}}}   /* the nearest point on this floor */
  gpkSet(c,"up",W.slice(i0))}
/* the way into this space for this car, arriving along the aisle the way the thread runs (null: it can't be done from here) */
function gpkPlanIn(c,t){const dir=gpkFlow(t.bay,t.k),G=c.gpk;const P=gpkPlan(t,c.len||CARLEN,c.wid||1.9,G.latErr,G.crooked,dir>0?0:Math.PI,c);return P?gpkRev(P):null}
function gpkRelease(c){if(c.gpk.key){GPK.res.delete(c.gpk.key)}}
function gpkTurnIn(c){const G=c.gpk;const P=gpkPlanIn(c,G.stall);if(P)G.reg=gpkRegion(G.stall,P);
  /* the cars next to it have changed since it picked the space and there is no way in now: wait a bit (they may be leaving), then try another space */
  if(!P){G.zone=0;G.noWay=(G.noWay||0)+1;if(G.noWay>40){const t=gpkPick(c,G.stall.k);G.noWay=0;if(t){gpkLog(c,"can't get into that space: trying another");gpkTake(c,t,true)}else{GPK.stats.give++;G.giveUp=1;gpkRelease(c);gpkExitFrom(c)}}else G.look=0.5;return}G.noWay=0;
  if(P.turns>1){GPK.stats.second++;gpkLog(c,`took ${P.turns+1} goes to get into the space`)}c.v=0;G.ph="in";gpkMv(c,P);G.look=0.4}
function gpkExitFrom(c){const L=gpkL(c.wx,c.wy),sd=L[1]>=0?1:-1,n=clamp(Math.round(((c.wz||0))/GAR.H-(sd>0?garF(L[0]):1-garF(L[0]))),0,GAR.T-1),D=gpkRouteOut(sd,n,L[0]);
  if(!D){c.gpk.ph="gone";c.gpk.why="stuck on the top floor";return}gpkSet(c,"down",gpkW(D))}
/* out of the exit lane onto Park Ave: an ordinary traffic car from here on */
function gpkToRoad(c){const G=c.gpk;GPK.stats.left++;gpkRelease(c);const f=findFrame(c.wx,c.wy,c.wh,null);
  if(GPK.test||!f||!f.e){G.ph="gone";G.why="left";return}
  const i=Math.max(0,Math.min(f.e.n-1,0));Object.assign(c,{kind:"ai",fixed:false,gpk:null,tmKeep:0,e:f.e,dir:f.dir,s:f.s,off:laneOff(f.e,i),offT:laneOff(f.e,i),v:3,head:0,idle:0,jn:null});
  try{planMove(c)}catch(e){}carPose(c)}
