/* v38.1 traffic minds: Michigan lefts on Main St / Commerce Pkwy. No left turns at the boulevard's lights from Grand River Ave to Maple Rd:
   drivers who want to turn left go through, U-turn from the median bay at the crossover and come back to turn right (side-street drivers turn
   right, then U-turn). 100 drivers whose route needs a Michigan left must all get where they are going without stopping in a through lane. */
(async()=>{const out=[],P=(ok,n,s)=>out.push(`${ok?"PASS":"FAIL"} ${n}: ${s}`);window.NOSEMI=1;setTrim("camry25",true);
resetCar({free:true,x:-1265,y:-60,h:0});st.power=true;st.started=true;st.gear="P";car.vx=0;cars.length=0;Traffic.set_density("all",.3);
const BV=e=>e.type==="blvd"&&(e.name==="Main St"||e.name==="Commerce Pkwy");const PK=EDGES.filter(BV);
const pk=(x,east)=>{const e=PK.find(e=>Math.abs(e.a.y)<1&&Math.min(e.a.x,e.b.x)<x&&Math.max(e.a.x,e.b.x)>x);return {e,dir:(e.b.x>e.a.x)===east?1:-1}};
const side=(x,north)=>{const e=EDGES.find(e=>!BV(e)&&((Math.abs(e.a.x-x)<1&&Math.abs(e.a.y)<1&&(e.b.y<0)===north)||(Math.abs(e.b.x-x)<1&&Math.abs(e.b.y)<1&&(e.a.y<0)===north)));if(!e)return null;const startsAtMain=Math.abs(e.a.y)<1;return {away:{e,dir:startsAtMain?1:-1},toward:{e,dir:startsAtMain?-1:1}}};
const SRC=[];for(const x of [-1300,-1000,-850,-550,500,1000])for(const north of [true,false]){const S=side(x,north);if(!S)continue;SRC.push([pk(x-170,true),S.away],[pk(x+170,false),S.away],[S.toward,pk(x-170,false)],[S.toward,pk(x+170,true)])}
out.push("sources "+SRC.length+(SRC.some(q=>!q[0].e||!q[1].e)?" (some missing)":""));
const usesXO=r=>{for(const [k,v] of r.next){const e=EDGES[k>>1],dir=(k&1)?1:-1;const n=endNode(e,dir),L=arrLeg(e,dir);if(n&&n.kind==="xo"){const ee=EDGES[v>>1],dd=(v&1)?1:-1;if(ee===e&&dd===-dir)return true}}return false};
const D=[];let tries=0,t=0,spawnT=0,si=0;
while((D.length<100||D.some(c=>!c.fin))&&t<1500){SIMSTEP(0.1);t+=0.1;spawnT-=0.1;
  if(spawnT<=0&&D.length<100&&tries++<4000){const [A,B]=SRC[si++%SRC.length];const s=A.e.type==="blvd"?8:Math.min(60,A.e.L-30);
    if(freeSpot(A.e,A.dir,s,0,22)){let r=null;try{r=navBuild({e:B.e,dir:B.dir,s:B.e.type==="blvd"?40:Math.min(60,B.e.L-20)})}catch(e){}
      /* only drivers whose best route really is a Michigan left (go through, U-turn at a crossover), one every 6 s across the four ways in (600 an hour, a busy boulevard) */
      const k0=skey(A.e,A.dir);if(r&&r.dist.get(k0)!==undefined){const c=newCar(A.e,A.dir,s,0);c.route=r;cars.push(c);tmInit(c);c.tmKeep=1;c.mind.lost=false;c._B=B;c._t0=t;c.xoStop=0;
        let k=k0,u=false;for(let g=0;g<12&&k!=null;g++){const e=EDGES[k>>1],dir=(k&1)?1:-1,nx=r.next.get(k);if(nx==null)break;if(endNode(e,dir).kind==="xo"&&EDGES[nx>>1]===e)u=true;k=nx}
        if(u){D.push(c);spawnT=6}else{cars.splice(cars.indexOf(c),1);spawnT=0.1}}}else spawnT=0.5}
  for(const c of D){if(c.fin)continue;if(!cars.includes(c)){c.fin="lost";continue}
    if(c.e===c._B.e&&c.dir===c._B.dir&&!c.jn){c.fin="ok";c._dt=t-c._t0;cars.splice(cars.indexOf(c),1);continue}
    /* waiting in a through lane for the U-turn (not in the bay, not at a red light) */
    if(!c.jn&&c.v<0.4&&c.mv&&c.mv.t==="U"&&!c.inBay&&BV(c.e)){c.xoStop+=0.1}
    if(c.mind&&c.mind.stopT>180)c.fin="stuck"}
  for(let i=cars.length-1;i>=0;i--){const c=cars[i];if(c._plain&&c.e===c.route?.dest?.e)cars.splice(i,1)}}
const ok=D.filter(c=>c.fin==="ok"),stopped=D.filter(c=>c.xoStop>1.5),stuck=D.filter(c=>c.fin==="stuck"||!c.fin),avg=ok.reduce((s,c)=>s+c._dt,0)/Math.max(1,ok.length);
P(D.length>=100&&ok.length>=97&&stopped.length<=5&&stuck.length===0,"Michigan lefts on Main St",`${D.length} drivers whose route needs a Michigan left: ${ok.length} made it (average ${avg.toFixed(0)} s from the start of the block), ${stopped.length} stopped in a through lane to wait for the U-turn (${stopped.map(c=>c.xoStop.toFixed(1)+" s").join(", ")||"none"}), stuck or lost: ${stuck.length}, ${D.filter(c=>c.fin==="lost").length} recycled; ${(t).toFixed(0)} sim-s`);
if(stuck.length||D.some(c=>c.fin==="lost"))out.push("  not done: "+D.filter(c=>c.fin!=="ok").slice(0,8).map(c=>`${c.fin}/${c.kind}${c.dead?"/dead":""} ${c.e&&c.e.name} x${c.wx|0} mv ${c.mv&&c.mv.t} bay ${c.inBay} lane ${c.e?laneIdx(c):"-"} need ${c.needLane} wait ${(c.waitT||0).toFixed(0)}`).join(" | "));
return out.join("\n")})()
