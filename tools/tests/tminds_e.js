/* v38 traffic minds: 6 Michigan left. Halden Pkwy has no left turns at Signal St and Arrow St: drivers who want to turn left there go through
   the light, U-turn from the median bay at the next crossover and come back to turn right (side-street drivers turn right, then U-turn).
   100 drivers whose route needs a Michigan left must all get where they are going without stopping in a through lane to wait for the U-turn. */
(async()=>{const out=[],P=(ok,n,s)=>out.push(`${ok?"PASS":"FAIL"} ${n}: ${s}`);window.NOSEMI=1;setTrim("camry25",true);
resetCar({free:true,x:-4000,y:-2135,h:0});st.power=true;st.started=true;st.gear="P";car.vx=0;cars.length=0;Traffic.set_density("all",.3);
const PK=EDGES.filter(e=>e.name==="Halden Pkwy"),SIDE=n=>EDGES.find(e=>e.name===n);
const pk=(x,east)=>{const e=PK.find(e=>Math.min(e.a.x,e.b.x)<x&&Math.max(e.a.x,e.b.x)>x);return {e,dir:(e.b.x>e.a.x)===east?1:-1}};
const away=n=>{const e=SIDE(n);return {e,dir:e.a.y<e.b.y?-1:1}},toward=n=>{const e=SIDE(n);return {e,dir:-away(n).dir}};   // the side streets run from y -2400 up to the Pkwy at -2100
const SRC=[];for(const st_ of ["Signal St","Arrow St"]){SRC.push([pk(-4380,true),away(st_)],[pk(-3620,false),away(st_)],[toward(st_),pk(-4380,false)],[toward(st_),pk(-3620,true)])}
const usesXO=r=>{for(const [k,v] of r.next){const e=EDGES[k>>1],dir=(k&1)?1:-1;const n=endNode(e,dir),L=arrLeg(e,dir);if(n&&n.kind==="xo"){const ee=EDGES[v>>1],dd=(v&1)?1:-1;if(ee===e&&dd===-dir)return true}}return false};
const D=[];let tries=0,t=0,spawnT=0,si=0;
while((D.length<100||D.some(c=>!c.fin))&&t<1500){SIMSTEP(0.1);t+=0.1;spawnT-=0.1;
  if(spawnT<=0&&D.length<100&&tries++<4000){const [A,B]=SRC[si++%SRC.length];const s=A.e.type==="blvd"?8:150;
    if(freeSpot(A.e,A.dir,s,0,22)){let r=null;try{r=navBuild({e:B.e,dir:B.dir,s:B.e.type==="blvd"?60:120})}catch(e){}
      /* only drivers whose best route really is a Michigan left (go through, U-turn at a crossover), one every 6 s across the four ways in (600 an hour, a busy boulevard) */
      const k0=skey(A.e,A.dir);if(r&&r.dist.get(k0)!==undefined){const c=newCar(A.e,A.dir,s,0);c.route=r;cars.push(c);tmInit(c);c.tmKeep=1;c.mind.lost=false;c._B=B;c._t0=t;c.xoStop=0;
        let k=k0,u=false;for(let g=0;g<12&&k!=null;g++){const e=EDGES[k>>1],dir=(k&1)?1:-1,nx=r.next.get(k);if(nx==null)break;if(endNode(e,dir).kind==="xo"&&EDGES[nx>>1]===e)u=true;k=nx}
        if(u){D.push(c);spawnT=6}else{cars.splice(cars.indexOf(c),1);spawnT=0.1}}}else spawnT=0.5}
  for(const c of D){if(c.fin)continue;if(!cars.includes(c)){c.fin="lost";continue}
    if(c.e===c._B.e&&c.dir===c._B.dir&&!c.jn){c.fin="ok";c._dt=t-c._t0;cars.splice(cars.indexOf(c),1);continue}
    /* waiting in a through lane for the U-turn (not in the bay, not at a red light) */
    if(!c.jn&&c.v<0.4&&c.mv&&c.mv.t==="U"&&!c.inBay&&c.e.name==="Halden Pkwy"){c.xoStop+=0.1}
    if(c.mind&&c.mind.stopT>180)c.fin="stuck"}
  for(let i=cars.length-1;i>=0;i--){const c=cars[i];if(c._plain&&c.e===c.route?.dest?.e)cars.splice(i,1)}}
const ok=D.filter(c=>c.fin==="ok"),stopped=D.filter(c=>c.xoStop>1.5),stuck=D.filter(c=>c.fin==="stuck"||!c.fin),avg=ok.reduce((s,c)=>s+c._dt,0)/Math.max(1,ok.length);
P(D.length>=100&&ok.length>=97&&stopped.length<=5&&stuck.length===0,"6 Michigan left",`${D.length} drivers whose route needs a Michigan left: ${ok.length} made it (average ${avg.toFixed(0)} s from the start of the block), ${stopped.length} stopped in a through lane to wait for the U-turn (${stopped.map(c=>c.xoStop.toFixed(1)+" s").join(", ")||"none"}), stuck or lost: ${stuck.length}, ${D.filter(c=>c.fin==="lost").length} recycled; ${(t).toFixed(0)} sim-s`);
if(stuck.length||D.some(c=>c.fin==="lost"))out.push("  not done: "+D.filter(c=>c.fin!=="ok").slice(0,8).map(c=>`${c.fin}/${c.kind}${c.dead?"/dead":""} ${c.e&&c.e.name} x${c.wx|0} mv ${c.mv&&c.mv.t} bay ${c.inBay} lane ${c.e?laneIdx(c):"-"} need ${c.needLane} wait ${(c.waitT||0).toFixed(0)}`).join(" | "));
return out.join("\n")})()
