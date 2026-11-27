/* ==== Traffic minds (v38) ===================================================================================================
   Every traffic driver gets a person: fixed traits, a mood that changes, a purpose, limited senses, habits and mistakes.
   Three layers, kept apart (each only talks to the next one through a small object):

   MIND      tmMind(c, d)      4 Hz   traits + purpose + appraised events -> mood (valence, arousal, dominance), stress, fatigue,
                                       named emotions, rage ladder, memory of the player.        writes d.want (below), never steers.
   DECISION  tmDecide(c, d)   10 Hz   perception (view cone, mirrors, range, distraction, reaction time, noisy estimates) ->
                                       events for the mind; intent + reason; turns d.want into control parameters.
                                       writes only: c.pers {v,T,a,b,lc,polite,gap}, c.wob (lane position), c.goDl (reaction),
                                       c.distractT (perception gap), c.honkT / aiHonk, c.flashT, c.bcT (brake check), c.passT,
                                       c.fear, c.rageT, c.gest (animation flag: "wave", "fist", "shrug").
   CONTROL   updateTraffic   ~60 Hz   the game's own lane following on the road-kit lane graph, IDM car following, lane changes,
                                       signals, merges, roundabouts. It reads the fields above and nothing else from here.

   d.want = {speed: desired speed factor, headway: s, accel: m/s2, brake: comfortable m/s2, eager: lane-change eagerness 0..1,
             polite: MOBIL politeness 0..1, gap: accepted gap factor, react: s, drift: m, honk, flash, wave, brakeCheck, distract}

   Level of detail: full mind + decision within 150 m of you, a single stress number from 150 to 400 m, preset behaviour beyond.
   Deterministic: one seeded generator per driver (TM.seed ^ id). Clock: TM.t (sim seconds).
   API: window.Traffic (spawn, despawn, set_density, set_time_of_day, set_weather, set_population, set_signal_override,
        get_driver, force_event, scenario, on/off) and events on_honk, on_wave, on_near_miss, on_collision, on_parked,
        on_rage_started, on_rage_ended. Debug: F7 (overlay), click a car (its head), M in the panel for the mood map. */
const TM={seed:20260,t:0,on:true,stats:{honk:[],wave:0,near:0,crash:0,park:0,rage:0,ms:0},ev:{},sel:null,dbg:false,map:false,mixOv:null,dens:{},accidents:false,fender:true};
function tmRng(seed){let s=(seed>>>0)||1;return ()=>{s=(s+0x6D2B79F5)>>>0;let t=s;t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);return ((t^(t>>>14))>>>0)/4294967296}}
const tmC=(v,a=0,b=1)=>v<a?a:v>b?b:v;
/* ---- population: archetypes (trait means) and the mix by area and time ---- */
const TM_ARCH={
  ordinary:{patience:.55,aggression:.3,caution:.55,courtesy:.55,sociability:.5,attentiveness:.65,risk:.35,rules:.65,confidence:.6},
  commuter:{patience:.25,aggression:.55,caution:.4,courtesy:.35,sociability:.35,attentiveness:.6,risk:.55,rules:.5,confidence:.75},
  elder:   {patience:.8,aggression:.12,caution:.85,courtesy:.7,sociability:.55,attentiveness:.5,risk:.12,rules:.85,confidence:.45},
  distracted:{patience:.5,aggression:.3,caution:.4,courtesy:.45,sociability:.75,attentiveness:.25,risk:.45,rules:.5,confidence:.6},
  novice:  {patience:.6,aggression:.2,caution:.75,courtesy:.6,sociability:.5,attentiveness:.55,risk:.25,rules:.8,confidence:.25},
  family:  {patience:.6,aggression:.2,caution:.75,courtesy:.65,sociability:.7,attentiveness:.55,risk:.2,rules:.75,confidence:.6},
  extreme: {patience:.08,aggression:.9,caution:.12,courtesy:.1,sociability:.3,attentiveness:.55,risk:.92,rules:.15,confidence:.9}};
const TM_TRAITS=["patience","aggression","caution","courtesy","sociability","attentiveness","risk","rules","confidence"];
function tmMix(x,y){if(TM.mixOv)return TM.mixOv;const h=typeof hourNow==="function"?hourNow():12,day=((GT.day||1)-1)%7,wkend=day>=5,rush=!wkend&&(Math.abs(h-8)<1.5||Math.abs(h-17.5)<1.5),night=h>=22||h<5;
  const z=typeof zoneName==="function"?zoneName(x,y):"rural",shop=typeof inMall==="function"&&inMall(x,y,600)||W2&&Math.hypot(x-3530,y+444)<500;
  const m={ordinary:55,commuter:rush?30:10,elder:night?2:9,distracted:6,novice:5,family:shop&&(wkend||h>15)?18:4,extreme:night?5:2};
  if(z==="city"&&rush)m.commuter+=10;if(shop&&wkend&&h>12&&h<18){m.family+=12;m.ordinary+=8}if(night){m.distracted+=4}
  return m}
const TM_PURP={commute:{late:.55,base:{v:-.1,a:.15}},school:{late:.4,base:{v:-.05,a:.1}},delivery:{late:.5,base:{v:-.05,a:.05}},shopping:{late:.05,base:{v:.12,a:-.05}},
  hotel:{late:.1,base:{v:.15,a:.05}},valet:{late:.2,base:{v:0,a:0}},tourist:{late:0,base:{v:0,a:.1},lost:.35},taxi:{late:.35,base:{v:0,a:.05}},emergency:{late:1,base:{v:-.2,a:.3}},learner:{late:0,base:{v:-.1,a:.2}}};
const TM_NAMES=["Alex","Sam","Jordan","Taylor","Morgan","Riley","Casey","Jamie","Avery","Drew","Quinn","Reese","Rowan","Sky","Dana","Lee","Pat","Robin","Terry","Chris","Marisol","Deshawn","Aaliyah","Hiro","Priya","Mateo","Ewa","Omar","Grace","Walt","Doris","Earl"];
function tmInit(c){const R=tmRng(TM.seed^Math.imul(c.id||1,2654435761));const mix=tmMix(c.wx||0,c.wy||0);let tot=0;for(const k in mix)tot+=mix[k];let x=R()*tot,arch="ordinary";for(const k in mix){x-=mix[k];if(x<=0){arch=k;break}}
  const A=TM_ARCH[arch],tr={};for(const k of TM_TRAITS)tr[k]=tmC(A[k]+(R()+R()+R()-1.5)*0.22);
  const age=arch==="elder"?"senior":arch==="novice"?(R()<0.7?"teen":"young adult"):["young adult","adult","adult","adult","senior"][Math.floor(R()*5)],exp=arch==="novice"?"novice":arch==="elder"||R()<0.25?"expert":"average";
  if(age==="teen"){tr.risk=tmC(tr.risk+.12);tr.attentiveness=tmC(tr.attentiveness-.1)}if(age==="senior"){tr.caution=tmC(tr.caution+.1)}
  const P=Object.keys(TM_PURP),pw={commute:arch==="commuter"?8:3,school:arch==="family"?3:.6,delivery:1,shopping:arch==="family"?4:2,hotel:.6,valet:.15,tourist:.5,taxi:.6,emergency:0,learner:arch==="novice"?3:0};
  let pt=0;for(const k of P)pt+=pw[k]||0;let y=R()*pt,purpose="commute";for(const k of P){y-=pw[k]||0;if(y<=0){purpose=k;break}}
  const pax=R()<0.35?[["kid","partner","dog","friend","kid"][Math.floor(R()*5)]]:[];
  const lateBase=TM_PURP[purpose].late*(0.5+R());
  const d={R,id:c.id,name:TM_NAMES[Math.floor(R()*TM_NAMES.length)]+" "+String.fromCharCode(65+Math.floor(R()*26))+".",arch,tr,age,exp,purpose,pax,
    late:tmC(lateBase),lost:purpose==="tourist"&&R()<0.6,
    V:.15+.2*tr.patience,A:.25+.25*(1-tr.patience),D:.4+.3*tr.confidence,stress:.15+.2*lateBase,fatigue:R()*.25,
    spike:{anger:0,fear:0,grat:0,emb:0,amuse:0,impat:0},rage:0,rageT:0,mem:{},bel:new Map(),log:[],hist:[],intent:"cruise",why:"",
    want:null,nextM:TM.t+R()*0.25,nextD:TM.t+R()*0.1,tier:2,phase:R()*6.28,bias:(R()-.5)*0.5*(1-tr.attentiveness*.6),distractT:0,distractNext:TM.t+5+R()*40,lastLead:null,stopT:0,lc:0,
    react:tmC(0.4+0.9*(1-tr.attentiveness)*(exp==="novice"?1.2:exp==="expert"?.8:1),0.4,1.5),born:TM.t,trip:0};
  c.mind=d;tmMind(c,d,true);tmApply(c,d);return d}
/* ---- emotions derived from the core state ---- */
function tmEmo(d){const S=d.spike,v=d.V,a=d.A;return {calm:tmC((1-a)*(v+0.5)/1.5-S.anger*.5),content:tmC(v*(1-a*.6)),impatient:tmC(S.impat*.8+d.late*a*.6),frustrated:tmC((1-v)*a*.9+S.impat*.3),
  angry:tmC(S.anger),anxious:tmC((1-d.D)*a*.9+S.fear*.4),scared:tmC(S.fear),embarrassed:tmC(S.emb),grateful:tmC(S.grat),amused:tmC(S.amuse),bored:tmC((1-a)*(1-v)*.8),tired:tmC(d.fatigue)}}
function tmLog(d,s){d.log.push([Math.round(TM.t),s]);if(d.log.length>10)d.log.shift()}
function tmEmit(n,o){TM.stats[n]=(TM.stats[n]||0);const L=TM.ev[n];if(L)for(const f of L)try{f(o)}catch(e){}}
/* ---- appraisal: an event is judged against the driver's goals and traits ---- */
function tmEvent(c,kind,o){const d=c.mind;if(!d)return;const t=d.tr,S=d.spike;
  if(kind==="cutoff"){const k=.25+.75*t.aggression*(1-t.patience*.6);S.anger=tmC(S.anger+0.55*k+0.2*d.stress);d.A=tmC(d.A+.25*k);d.V=tmC(d.V-.15*k);d.stress=tmC(d.stress+.08);tmLog(d,`cut off${o&&o.me?" by you":""}: angry ${S.anger.toFixed(2)}`);if(o&&o.me)tmMem(d,.35*k,-.2)}
  else if(kind==="letin"){S.grat=tmC(S.grat+.5+.4*t.sociability);d.V=tmC(d.V+.15);S.anger*=.6;tmLog(d,"let in: grateful");if(o&&o.me)tmMem(d,-.1,.3);if(t.courtesy>.4||t.sociability>.6){c.gest="wave";c.gestT=2;TM.stats.wave++;tmEmit("on_wave",{id:c.id,me:o&&o.me})}}
  else if(kind==="near"){S.fear=tmC(S.fear+.7);d.A=tmC(d.A+.3);d.D=tmC(d.D-.25);d.stress=tmC(d.stress+.15);d.fearT=TM.t+40+d.R()*30;TM.stats.near++;tmEmit("on_near_miss",{id:c.id});tmLog(d,"near miss: scared, slowing down")}
  else if(kind==="honked"){S.anger=tmC(S.anger+.2*t.aggression+.05);d.A=tmC(d.A+.15);d.stress=tmC(d.stress+.06);if(o&&o.me)tmMem(d,.2,-.1);tmLog(d,"honked at"+(o&&o.me?" by you":""))}
  else if(kind==="tailgated"){S.anger=tmC(S.anger+.08*(.4+t.aggression));d.stress=tmC(d.stress+.04);if(o&&o.me)tmMem(d,.1,-.08)}
  else if(kind==="queue"){S.impat=tmC(S.impat+.06*(1-t.patience)*(.4+d.late));d.stress=tmC(d.stress+.02*(.3+d.late))}
  else if(kind==="siren"){d.stress=tmC(d.stress+.2);d.A=tmC(d.A+.2);if(d.R()<.1+.2*(1-t.confidence))S.fear=tmC(S.fear+.3);tmLog(d,"siren: pulling over")}
  else if(kind==="missed"){S.emb=tmC(S.emb+.4*(1-t.confidence));S.impat=tmC(S.impat+.3*t.aggression);d.stress=tmC(d.stress+.1);tmLog(d,"missed my turn: "+(t.aggression>.5?"annoyed":"embarrassed")+", going round the block")}
  else if(kind==="crash"){S.fear=1;d.stress=1;d.shockT=TM.t+3+d.R()*7;TM.stats.crash++;tmEmit("on_collision",{id:c.id});tmLog(d,"crash: shocked")}
  else if(kind==="parked"){d.fatigue=tmC(d.fatigue-.3);d.stress*=.6;TM.stats.park++;tmEmit("on_parked",{id:c.id})}
  else if(kind==="polite"){if(o&&o.me)tmMem(d,-.15,.25);S.grat=tmC(S.grat+.25)}}
function tmMem(d,anger,trust){const m=d.mem.me||(d.mem.me={anger:0,trust:.5,t:0});m.anger=tmC(m.anger+anger);m.trust=tmC(m.trust+trust);m.t=TM.t}
/* ---- MIND (4 Hz) ---- */
function tmMind(c,d,init){const t=d.tr,dt=init?0:Math.max(0.05,TM.t-(d.lastM||TM.t));d.lastM=TM.t;const S=d.spike;
  // regulation: emotions fade at a rate set by traits; an empty road, music and being parked calm people down
  const calm=(1+t.patience)*(c.v<0.5&&!c.mv?1.5:1)*(d.music?1.3:1),fade=k=>Math.exp(-dt*k*calm);
  S.anger*=fade(.035+.04*t.patience);S.fear*=fade(.05);S.grat*=fade(.1);S.emb*=fade(.06);S.amuse*=fade(.12);S.impat*=fade(.04);
  d.fatigue=tmC(d.fatigue+dt*(c.v>0.5?1/5400:-1/900)*(hourNow()>=22||hourNow()<5?1.8:1));
  d.stress=tmC(d.stress+dt*(-0.006*(1+t.patience)+0.01*S.impat+(d.lost?.004:0)+(d.late>.4&&d.stopT>10?.006:0)));
  // passengers: a crying child raises stress, chatting lowers it, a dog does whatever it likes
  if(d.pax.length&&d.R()<dt*0.02){const p=d.pax[0];if(p==="kid"){d.stress=tmC(d.stress+.08);d.bark="Are we there yet?"}else if(p==="partner"||p==="friend"){d.stress=tmC(d.stress-.05);d.V=tmC(d.V+.05);d.bark=d.R()<.5?"Did you see that?":"Left here. No, the other left."}else{d.bark="Woof";S.amuse=tmC(S.amuse+.2)}d.barkT=TM.t+3}
  if(d.R()<dt*0.01)d.music=!d.music;
  // core state follows the spikes and meters
  const tv=tmC(.6-.5*S.anger-.3*S.fear-.3*S.impat+.4*S.grat+.3*S.amuse-.35*d.stress-.2*d.fatigue),ta=tmC(.2+.6*S.anger+.6*S.fear+.4*S.impat+.4*d.stress-.25*d.fatigue),td=tmC(.3+.5*t.confidence-.4*S.fear+.2*S.anger);
  const k=1-Math.exp(-dt*0.8);d.V+=(tv-d.V)*k;d.A+=(ta-d.A)*k;d.D+=(td-d.D)*k;d.V=tmC(d.V);d.A=tmC(d.A);d.D=tmC(d.D);
  // the rage ladder: annoyed -> tailgating -> honking -> pushy overtakes / a brake check, then it cools off (game-safe: nothing worse)
  const r0=d.rage,heat=S.anger+.3*d.stress-.4*t.patience;d.rage=heat>.85?4:heat>.68?3:heat>.5?2:heat>.32?1:0;
  if(d.rage>=2&&r0<2){TM.stats.rage++;d.rageOn=true;tmEmit("on_rage_started",{id:c.id,level:d.rage});tmLog(d,"getting angry: tailgating")}
  if(d.rage<1&&d.rageOn){d.rageOn=false;tmEmit("on_rage_ended",{id:c.id});tmLog(d,"cooled down")}
  const m=d.mem.me;if(m&&TM.t-m.t>180){m.anger*=.5;if(TM.t-m.t>300)delete d.mem.me}
  // what the mind wants from the driving (the decision layer turns this into numbers for the control)
  const E=tmEmo(d),late=d.late*(1-.5*(d.trip>600?0:0)),fear=Math.max(S.fear,d.fearT>TM.t?.5:0),wet=st.surface!=="dry"||(WX.cur&&WX.cur!=="clear")?1:0,night=typeof GT!=="undefined"&&(hourNow()>=20||hourNow()<6)?1:0;
  const vis=1-.18*wet-.1*night;   /* bad visibility: careful people slow down for it, bad drivers don't */
  d.want={speed:tmC(0.86+0.2*t.risk-0.12*t.rules+0.12*late+0.06*E.angry-0.08*E.anxious-0.1*fear-(1-vis)*(.3*t.caution+.1),0.65,1.32),
    headway:tmC(0.7+1.4*t.caution-0.6*t.aggression-.35*late-.45*E.angry+.8*E.anxious+.9*fear+(1-vis)*t.caution*.8-(d.rage>=2?.35:0),0.45,3.2),
    accel:tmC(1.1+1.4*t.aggression+.8*t.risk+.6*E.angry-.5*E.anxious+(TM_PURP[d.purpose].base.a||0),0.7,3.4),
    brake:tmC(2+1.3*t.aggression+.8*E.angry-(d.exp==="novice"?.6:0),1.6,4.6),   /* comfortable braking: aggressive drivers brake later and harder, novices earlier */
    eager:tmC(.25+.5*t.aggression+.3*late-.25*t.caution+.2*E.impatient),polite:tmC(.15+.7*t.courtesy+.2*E.grateful+.1*E.content-.4*E.angry),
    gap:tmC(1.25-.35*t.risk-.25*late-.25*E.angry+.4*E.anxious+.3*fear,.55,1.9),
    react:d.react*(1+.8*d.fatigue)*(d.distractT>TM.t?2:1),drift:.12+.6*d.fatigue+.15*(1-t.attentiveness),
    honk:d.rage>=3||E.impatient>.7&&t.aggression>.55,brakeCheck:d.rage>=4&&t.risk>.6,indicator:t.rules>.45?1:t.rules>.25?.5:0};
  d.E=E;if(!init&&(!d.hl||TM.t-d.hl>2)){d.hl=TM.t;d.hist.push([E.angry,E.anxious,E.impatient,E.calm,d.stress]);if(d.hist.length>60)d.hist.shift()}}
/* ---- DECISION (10 Hz): perception, events, intent ---- */
function tmPerceive(c,d,grid){const R=d.R,t=d.tr,range=(st.rain||WX.cur==="rain"?120:180)*(hourNow()>=20||hourNow()<6?.7:1),fx=Math.cos(c.wh),fy=Math.sin(c.wh),now=TM.t;
  const distr=d.distractT>now;if(!distr&&now>d.distractNext){const ph=(1-t.attentiveness)*(d.arch==="distracted"?2.5:1);if(R()<.2+.6*ph){d.distractT=now+1+R()*2;d.dCause=d.pax.length&&R()<.5?"talking to the "+d.pax[0]:R()<.5?"phone":"radio"}d.distractNext=now+15+R()*60*(1.2-ph)}
  const mirror=Math.floor(now*0.5+d.phase)%3===0;   /* a glance in the mirrors every couple of seconds */
  const seen=new Set();for(const o of tmNear(grid,c.wx,c.wy,range)){if(o===c)continue;const dx=o.x-c.wx,dy=o.y-c.wy,dist=Math.hypot(dx,dy);if(dist>range||dist<0.5)continue;
    const cos=(dx*fx+dy*fy)/dist,ahead=cos>0.5,blind=!ahead&&cos>-0.6&&dist<9&&!mirror;   /* 120 degree cone; mirrors behind; the blind spot beside */
    if(distr&&ahead&&dist>8)continue;if(!ahead&&!mirror&&dist>6)continue;if(blind)continue;
    let occ=false;for(const s of grid.trucks){if(s===o.o||s===c)continue;const sx=s.wx-c.wx,sy=s.wy-c.wy,sd=Math.hypot(sx,sy);if(sd<dist-6&&sd>4&&(sx*dx+sy*dy)/(sd*dist)>0.985){occ=true;break}}if(occ)continue;
    seen.add(o.o);let b=d.bel.get(o.o);const err=(0.03+0.0025*dist)*(1+d.fatigue)*(1+(1-t.attentiveness));
    if(!b){b={x:o.x,y:o.y,v:o.v*(1+(R()-.5)*err*4),n:0};d.bel.set(o.o,b)}b.n++;const w=Math.min(0.8,0.25+b.n*0.08);b.x+=(o.x-b.x)*w;b.y+=(o.y-b.y)*w;b.v+=(o.v*(1+(R()-.5)*err)-b.v)*w;b.t=now;b.d=dist;b.ahead=ahead;b.me=o.me}
  for(const [k,b] of d.bel)if(now-b.t>4)d.bel.delete(k);return seen}
function tmDecide(c,d,grid){const now=TM.t,t=d.tr,W=d.want;if(!W)return;d.trip+=0.1;
  if(d.shockT>now){d.intent="frozen";d.why="in shock after the crash";return}
  tmPerceive(c,d,grid);
  // events from what it sees
  const lw=c.lw,lg=c.lg??1e9;if(lw&&lw!=="ctrl"&&lw!==d.lastLead&&lg<Math.max(4,c.v*W.headway*.55)&&c.v>4){const me=lw==="me";if(me||(lw.mind&&(lw.lcPending>0||lw.lcTarget!=null)))tmEvent(c,"cutoff",{me})}d.lastLead=lw;
  if(lw&&lw!=="ctrl"&&c.v>3){const vL=lw==="me"?car.vx:lw.v||0,ttc=lg/Math.max(0.1,c.v-vL);if(ttc<1.1&&lg<c.v*0.7&&!(d.nearT>now)){tmEvent(c,"near");d.nearT=now+8}}
  if(c.v<0.5){d.stopT+=0.1;if(d.stopT>8&&((d.stopT*10)|0)%20===0)tmEvent(c,"queue")}else d.stopT=0;
  /* you, behind me: tailgating, honking; or ahead and polite */
  const me=d.bel.get(undefined);void me;const pdx=car.px-c.wx,pdy=car.py-c.wy,pd=Math.hypot(pdx,pdy),behind=(pdx*Math.cos(c.wh)+pdy*Math.sin(c.wh))<0;
  if(!st.walk&&pd<35&&behind&&car.vx>5&&Math.abs(wrapPi(car.psi-c.wh))<0.5){const hw=(pd-4.6)/Math.max(1,car.vx);d.tailT=(hw<0.8?(d.tailT||0)+0.1:Math.max(0,(d.tailT||0)-0.05));if(d.tailT>3&&((d.tailT*10)|0)%10===0)tmEvent(c,"tailgated",{me:true});if(hw>2.2&&c.v>8&&((now*10)|0)%50===0)tmEvent(c,"polite",{me:true})}
  if(d.tailT>6&&d.mem.me&&d.mem.me.anger>.3&&!(d.honkT>now)){d.honkT=now+8;try{aiHonk(c,.5)}catch(e){}TM.stats.honk.push(now);tmEmit("on_honk",{id:c.id,at:"you"});c.gest=d.mem.me.anger>.6?"fist":"shrug";c.gestT=2;tmLog(d,"honked at you: you're right on my bumper");if(d.tr.risk>.6&&d.mem.me.anger>.7&&!(d.bcT>now)){c.bcT=0.6;d.bcT=now+40;tmLog(d,"tapped the brakes at you")}}
  if(st.hornAt&&st.clock-st.hornAt<0.4&&pd<30&&!(d.hornT>now)){d.hornT=now+3;tmEvent(c,"honked",{me:true})}
  if(typeof SAFE!=="undefined"&&SAFE.emvList&&SAFE.emvList.length&&!(d.sirT>now)){for(const e of SAFE.emvList)if(e&&Math.hypot((e.wx??e.x)-c.wx,(e.wy??e.y)-c.wy)<160){tmEvent(c,"siren");d.sirT=now+30;break}}
  /* intent and the reason, in plain English */
  const E=d.E||tmEmo(d);let intent="cruise",why=`${d.purpose}${d.late>.4?", running late":""}`;
  if(d.distractT>now){intent="distracted";why=`looking at the ${d.dCause||"phone"}`}
  else if(c.v<0.5&&lw){intent="waiting";why=(E.impatient>.5?"impatient"+(d.late>.4?" because late":""):"waiting")+(lg<6?", queued":", gap too small")}
  else if(d.rage>=2){intent=d.rage>=4?"pushing past":d.rage>=3?"honking":"tailgating";why=`angry (${E.angry.toFixed(2)})${d.mem.me&&d.mem.me.anger>.3?" at you":""}`}
  else if(E.scared>.4){intent="careful";why="scared after a close call: slowing down, wide gap"}
  else if(c.ovt||c.lcT>0){intent="changing lanes";why=W.eager>.6?"wants to get past":"lane needed for the turn"}
  else if(lw&&lg<c.v*W.headway*1.2){intent="following";why=`keeping ${W.headway.toFixed(1)} s back`}
  if(intent!==d.intent){tmLog(d,`${intent}: ${why}`)}d.intent=intent;d.why=why;
  /* actions: honk, flash, wave, brake check (game-safe) */
  if(W.honk&&lw&&lw!=="ctrl"&&lg<25&&c.v<12&&!(d.honkT>now)&&d.R()<.25){d.honkT=now+6+d.R()*6;try{aiHonk(c,.3+.4*E.angry)}catch(e){}TM.stats.honk.push(now);tmEmit("on_honk",{id:c.id,at:lw==="me"?"you":lw.id});c.gest=E.angry>.6?"fist":"shrug";c.gestT=2;tmLog(d,"honked"+(lw==="me"?" at you":""))}
  if(W.brakeCheck&&lw===undefined&&!(d.bcT>now)){const B=[...d.bel.entries()].find(([o,b])=>!b.ahead&&b.d<10);if(B&&d.R()<.15){c.bcT=0.8;d.bcT=now+40;tmLog(d,"brake-checked the car behind")}}
  if(d.mem.me&&d.mem.me.trust>.75&&pd<60&&!(d.waveT>now)&&d.R()<.1){d.waveT=now+60;c.gest="wave";c.gestT=2;TM.stats.wave++;tmEmit("on_wave",{id:c.id,to:"you"});tmLog(d,"waved at you")}
  if(d.gestTick)void 0;if(c.gestT>0){c.gestT-=0.1;if(c.gestT<=0)c.gest=null}
  tmApply(c,d)}
/* in a dense queue people pull away gently (they see the next brake lights coming): the source of stop-and-go waves, with reaction time */
function tmAccel(d,gap,v){const dense=gap<45&&v<22;return dense?Math.max(0.4,d.want.accel*(0.22+0.004*gap)):d.want.accel}
/* the decision -> control interface: only these fields */
function tmApply(c,d){const W=d.want;if(!W)return;const p=c.pers||(c.pers={k:"normal",v:1,T:1.3,lc:1,a:1.6,b:2.8});
  const ez=(o,v)=>p[o]==null||!isFinite(p[o])?v:p[o]+(v-p[o])*0.35;   /* eased: a mood swing or a change of detail tier never makes the car jump */
  p.k=d.rage>=2||W.accel>2.6?"aggr":d.tr.caution>.7?"calm":"normal";p.v=ez("v",W.speed);p.T=ez("T",W.headway);p.a=ez("a",tmAccel(d,c.lg??1e9,c.v||0));p.b=ez("b",W.brake);p.lc=tmC(1.6-1.3*W.eager,0.25,2);p.polite=W.polite;p.gap=W.gap;p.reck=d.tr.risk>.85&&d.rage>=3;
  c.fear=Math.max(d.spike.fear,d.fearT>TM.t?.4:0);c.rageT=d.rage>=2?1:0;
  c.wob=Math.sin(TM.t*(0.25+0.1*d.tr.attentiveness)+d.phase)*Math.min(0.55,W.drift*0.45)+d.bias;   /* lane position: some hug the line, tired ones wander */
  if(c.v<0.2&&c.goDl===undefined)c.goDl=W.react+(d.distractT>TM.t?1.5:0);
  if(d.distractT>TM.t&&(c.lg??1e9)>Math.max(12,c.v*2.6))c.distractT=Math.max(c.distractT||0,0.12)}
/* simplified mind (150-400 m): one stress number; preset beyond */
function tmLite(c,d,dt){d.spike.anger*=Math.exp(-dt*.05);d.stress=tmC(d.stress+dt*(c.v<0.5?.004:-.004));c.wob=d.bias*.5;
  const p=c.pers;if(p&&d.want){p.T+=(d.want.headway*(1+.15*d.stress)-p.T)*0.35;p.v+=(d.want.speed-p.v)*0.35}}
/* ---- the per-frame driver: fixed clock, staggered layers, level of detail by distance ---- */
function tmNear(G,x,y,r){const out=[],k=G.k,i0=Math.floor((x-r)/k),i1=Math.floor((x+r)/k),j0=Math.floor((y-r)/k),j1=Math.floor((y+r)/k);for(let i=i0;i<=i1;i++)for(let j=j0;j<=j1;j++){const L=G.m.get(i*100003+j);if(L)for(const o of L)out.push(o)}return out}
function tmTick(dt){if(!TM.on||!st.started)return;const t0=performance.now();TM.t+=dt;
  const G={k:60,m:new Map(),trucks:[]};const put=o=>{const key=Math.floor(o.x/60)*100003+Math.floor(o.y/60);let L=G.m.get(key);if(!L)G.m.set(key,L=[]);L.push(o)};
  for(const c of cars){if(c.wx===undefined)continue;put({x:c.wx,y:c.wy,v:c.v||0,o:c});if(c.semi||c.len>8)G.trucks.push(c)}if(!st.walk)put({x:car.px,y:car.py,v:car.vx,o:"me",me:true});
  const px=plX(),py=plY();
  for(const c of cars){if(c.kind!=="ai"||c.wx===undefined||c.emv||c.robo)continue;const d=c.mind||tmInit(c),dist=Math.hypot(c.wx-px,c.wy-py),tier=dist<150?2:dist<400?1:0;
    if(tier!==d.tier){d.tier=tier}   /* parameters ease between tiers (the control reads the same fields), so nothing jumps */
    if(tier===0){if(TM.t>=d.nextM){d.nextM=TM.t+1;tmLite(c,d,1)}continue}
    if(tier===1){if(TM.t>=d.nextM){tmLite(c,d,TM.t-(d.lastL||TM.t-0.5));d.lastL=TM.t;d.nextM=TM.t+0.5}continue}
    if(TM.t>=d.nextM){d.nextM+=0.25;if(d.nextM<TM.t)d.nextM=TM.t+0.25;tmMind(c,d)}
    if(TM.t>=d.nextD){d.nextD+=0.1;if(d.nextD<TM.t)d.nextD=TM.t+0.1;tmDecide(c,d,G)}}
  const n=performance.now()-t0;TM.stats.ms=TM.stats.ms*0.95+n*0.05;while(TM.stats.honk.length&&TM.stats.honk[0]<TM.t-60)TM.stats.honk.shift()}
/* ---- API ---- */
function tmSnap(c){const d=c.mind;if(!d)return null;return {id:c.id,name:d.name,archetype:d.arch,age:d.age,experience:d.exp,purpose:d.purpose,passengers:d.pax.slice(),late:d.late,lost:d.lost,
  traits:{...d.tr},mood:{valence:d.V,arousal:d.A,dominance:d.D},stress:d.stress,fatigue:d.fatigue,emotions:{...(d.E||tmEmo(d))},rage:d.rage,
  intent:d.intent,reason:d.why,decisions:d.log.slice(),player:d.mem.me?{...d.mem.me}:null,want:{...d.want},road:c.e&&c.e.name,speed:c.v,tier:d.tier,
  perceives:[...d.bel.entries()].map(([o,b])=>({id:o==="me"?"you":o&&o.id,dist:+b.d.toFixed(1),speed:+b.v.toFixed(1),ahead:b.ahead}))}}
function tmWant(){return TM.want==null?null:Math.min(130,Math.round(TM.want*todMul()))}
const Traffic={
  spawn(purpose,vehicle,lane){const p=lane||randomSpot(60,400);if(!p)return null;const c=newCar(p.e,p.dir,p.s,p.i||0);if(vehicle)c.mdl=vehicle;cars.push(c);const d=tmInit(c);if(purpose&&TM_PURP[purpose]){d.purpose=purpose;d.late=TM_PURP[purpose].late}return c.id},
  despawn(id){const i=cars.findIndex(c=>c.id===id);if(i>=0){cars.splice(i,1);return true}return false},
  /* the "all" density sets how many traffic cars live around you: 10 + 80 x density, times the time-of-day curve (rush hour x1.45), at most 130 */
  set_density(cls,v){TM.dens[cls]=tmC(v);if(cls==="all"||cls==="*"){TM.want=Math.round(10+tmC(v)*80);const want=tmWant(),n=cars.filter(c=>c.kind==="ai").length;if(want>n)spawnTraffic(want-n);else{let k=n-want;for(let i=cars.length-1;i>=0&&k>0;i--)if(cars[i].kind==="ai"&&!poolKeep(cars[i])&&Math.hypot(cars[i].wx-plX(),cars[i].wy-plY())>200){cars.splice(i,1);k--}}}},
  set_time_of_day(h){GT.min=Math.round(((h%24)+24)%24*60)+Math.floor(GT.min/1440)*1440},
  set_weather(w){try{WX.cur=w;WX.next=w;st.rain=w==="rain"||w==="storm";st.surface=w==="rain"||w==="storm"?"wet":w==="snow"||w==="ice"?"snow":"dry"}catch(e){}},
  set_population(mix){TM.mixOv=mix||null},
  set_signal_override(n,state){const N=typeof n==="number"?NODES[n]:n;if(N)N.sigOv=state||null},
  get_driver(id){const c=cars.find(c=>c.id===id);return c?tmSnap(c):null},
  force_event(id,ev,o){const c=cars.find(c=>c.id===id);if(c){if(!c.mind)tmInit(c);tmEvent(c,ev,o);tmMind(c,c.mind);tmApply(c,c.mind);return true}return false},
  /* deterministic runs (config): one seed for the traffic dice, the drivers' minds and everything else that rolls dice in the sim */
  seed(s){TM.seed=s;TM.det=true;TM.mdl0=Object.keys(MODELS).filter(k=>MODELS[k]&&MODELS[k].objects&&!LAZY_ALL.has(k)).sort();TM.new0=[];   /* only the built-in models: the on-demand ones arrive at different times */seedR=(s%2147483646)+1;TM.t=0;if(!TM.mr0)TM.mr0=Math.random;Math.random=tmRng(s*7919+13);try{TM.brain0=JSON.stringify(BRAIN);Object.assign(BRAIN,{gapK:1,stopWait:6,pedPat:45,pedGapK:1})}catch(e){}},unseed(){TM.det=false;if(TM.mr0)Math.random=TM.mr0},
  on(n,f){(TM.ev[n]=TM.ev[n]||[]).push(f)},off(n,f){TM.ev[n]=(TM.ev[n]||[]).filter(g=>g!==f)},
  scenario(k){const S=TM_SCEN[k];if(!S)return false;this.set_time_of_day(S.hour);GT.day=S.day||GT.day;this.set_weather(S.weather);this.set_population(S.mix||null);this.set_density("all",S.density);if(S.cars){TM.want=Math.round(S.cars/Math.max(0.3,todMul()));const n=cars.filter(c=>c.kind==="ai").length;if(tmWant()>n)spawnTraffic(tmWant()-n)}TM.accidents=!!S.accidents;return S},
  stats(){const A=cars.filter(c=>c.kind==="ai"),by={};for(const c of A){const k=c.e&&c.e.type||"?";(by[k]=by[k]||[]).push(c.v)}const avg={};for(const k in by)avg[k]=+(by[k].reduce((a,v)=>a+v,0)/by[k].length*2.237).toFixed(1);
    return {cars:A.length,avgMph:avg,jams:A.filter(c=>c.mind&&c.mind.stopT>20).length,honksPerMin:TM.stats.honk.length,nearMisses:TM.stats.near,accidents:TM.stats.crash,parked:TM.stats.park,rages:TM.stats.rage,aiMs:+TM.stats.ms.toFixed(3)}}};
window.Traffic=Traffic;
/* scenario presets (JSON-shaped) */
const TM_SCEN={"weekday rush":{hour:8,day:2,weather:"clear",density:.9,mix:null},"quiet night":{hour:2.5,day:3,weather:"clear",density:.15,mix:{ordinary:40,distracted:15,extreme:10,elder:2,commuter:3,novice:5,family:0}},
  "saturday mall":{hour:14,day:6,weather:"clear",density:.7,mix:{ordinary:45,family:30,elder:10,commuter:3,distracted:6,novice:4,extreme:2}},"rainy rush hour":{hour:17.5,day:4,weather:"rain",density:.9,mix:null},
  "event traffic":{hour:19,day:5,weather:"clear",density:.85,mix:{ordinary:50,family:20,commuter:10,distracted:8,novice:6,elder:4,extreme:2},surge:[3530,-444]},"stress test":{hour:12,day:2,weather:"clear",density:1,mix:null,cars:120}};
/* ---- debug: overlay, the driver panel, the mood map ---- */
const TM_COL={calm:"#3ec46d",impatient:"#f2c230",angry:"#e6392f",anxious:"#3a7bf2",tired:"#8b8f96"};
function tmMoodCol(d){const E=d.E||tmEmo(d);if(E.angry>.45||d.rage>=2)return TM_COL.angry;if(E.anxious>.45||E.scared>.35)return TM_COL.anxious;if(E.impatient>.45)return TM_COL.impatient;if(E.tired>.6)return TM_COL.tired;return TM_COL.calm}
function tmScreen(x,y,z){if(typeof VP==="undefined"||!VP)return null;const m=VP,X=x,Y=z,Z=-y,cx=m[0]*X+m[4]*Y+m[8]*Z+m[12],cy=m[1]*X+m[5]*Y+m[9]*Z+m[13],cw=m[3]*X+m[7]*Y+m[11]*Z+m[15];if(cw<0.1)return null;return [(cx/cw*0.5+0.5)*innerWidth,(1-(cy/cw*0.5+0.5))*innerHeight]}
function tmDebug(on){TM.dbg=on??!TM.dbg;let cv=document.getElementById("tmCv");if(!cv){cv=document.createElement("canvas");cv.id="tmCv";cv.style.cssText="position:fixed;inset:0;pointer-events:none;z-index:35";document.body.appendChild(cv);
    addEventListener("pointerdown",e=>{if(!TM.dbg||e.target.closest&&e.target.closest("#tmPanel,button,#ph2"))return;let best=null,bd=40;for(const c of cars){if(!c.mind)continue;const p=tmScreen(c.wx,c.wy,(c.wz||0)+2.2);if(!p)continue;const d=Math.hypot(p[0]-e.clientX,p[1]-e.clientY);if(d<bd){bd=d;best=c}}if(best){TM.sel=best.id;tmPanel()}},true)}
  cv.hidden=!TM.dbg;if(TM.dbg){if(!TM.raf){const loop=()=>{TM.raf=TM.dbg?requestAnimationFrame(loop):0;tmDraw()};loop()}toast("Traffic minds: F7 to hide · click a car's dot for its mind")}else{const P=document.getElementById("tmPanel");if(P)P.hidden=true}}
function tmDraw(){const cv=document.getElementById("tmCv");if(!cv)return;if(cv.width!==innerWidth)cv.width=innerWidth;if(cv.height!==innerHeight)cv.height=innerHeight;const g=cv.getContext("2d");g.clearRect(0,0,cv.width,cv.height);g.font="600 11px system-ui";
  for(const c of cars){const d=c.mind;if(!d||Math.hypot(c.wx-car.px,c.wy-car.py)>220)continue;const p=tmScreen(c.wx,c.wy,(c.wz||0)+2.2);if(!p)continue;g.fillStyle=tmMoodCol(d);g.beginPath();g.arc(p[0],p[1],TM.sel===c.id?7:5,0,6.29);g.fill();
    const ic=c.gest==="wave"?"👋":c.gest==="fist"?"✊":c.gest==="shrug"?"🤷":d.honkT>TM.t+4?"📯":"";if(ic)g.fillText(ic,p[0]+8,p[1]-6);if(d.barkT>TM.t&&d.bark){g.fillStyle="#fff";g.fillText("“"+d.bark+"”",p[0]+8,p[1]+12)}
    if(TM.sel===c.id){g.strokeStyle="rgba(255,255,255,.5)";for(const s of [-1,1]){const a=c.wh+s*Math.PI/3,q=tmScreen(c.wx+Math.cos(a)*40,c.wy+Math.sin(a)*40,(c.wz||0)+1);if(q){g.beginPath();g.moveTo(p[0],p[1]);g.lineTo(q[0],q[1]);g.stroke()}}
      for(const [o,b] of d.bel){const q=tmScreen(b.x,b.y,(c.wz||0)+1.5);if(q){g.strokeStyle="#7fd3ff";g.strokeRect(q[0]-5,q[1]-5,10,10)}}}}
  if(TM.map){const S=200,M=new Map();for(const c of cars){if(!c.mind)continue;const k=Math.floor(c.wx/S)+","+Math.floor(c.wy/S),r=M.get(k)||{s:0,n:0};r.s+=c.mind.stress;r.n++;M.set(k,r)}
    const W=220,x0=12,y0=innerHeight-W-90,sc=W/9600;g.fillStyle="rgba(0,0,0,.55)";g.fillRect(x0,y0,W,W*1.05);for(const [k,r] of M){const [i,j]=k.split(",").map(Number),v=r.s/r.n;g.fillStyle=`rgba(${255*v|0},${255*(1-v)|0},60,.85)`;g.fillRect(x0+(i*S+4800)*sc,y0+W-(j*S+6500)*sc*0.95,S*sc+1,S*sc+1)}
    g.fillStyle="#fff";g.fillText("Mood map (stress)",x0+4,y0+12);const s=Traffic.stats();g.fillText(`${s.cars} cars · ${s.honksPerMin} honks/min · near misses ${s.nearMisses} · AI ${s.aiMs} ms`,x0+4,y0+W*1.05-4)}
  if(TM.sel)tmPanel(true)}
function tmPanel(soft){const c=cars.find(c=>c.id===TM.sel);let P=document.getElementById("tmPanel");if(!P){P=document.createElement("div");P.id="tmPanel";P.style.cssText="position:fixed;right:12px;top:70px;width:290px;max-height:80vh;overflow:auto;z-index:41;background:rgba(12,15,20,.92);color:#e8edf2;font:500 11px system-ui;border-radius:12px;padding:10px;box-shadow:0 8px 30px rgba(0,0,0,.5)";document.body.appendChild(P);
    P.addEventListener("click",e=>{const b=e.target.closest("[data-t]");if(!b)return;if(b.dataset.t==="x"){TM.sel=null;P.hidden=true}else if(b.dataset.t==="map")TM.map=!TM.map})}
  if(!c||!c.mind){P.hidden=true;return}P.hidden=false;if(soft&&P._t&&performance.now()-P._t<250)return;P._t=performance.now();const s=tmSnap(c),bar=(v,col)=>`<i style="display:inline-block;width:110px;height:7px;background:#2a3038;border-radius:4px;vertical-align:middle"><i style="display:block;height:7px;width:${Math.round(tmC(v)*110)}px;background:${col};border-radius:4px"></i></i>`;
  const H=c.mind.hist,ch=H.length?`<svg width="270" height="40" style="background:#1a1f26;border-radius:6px">${[["#e6392f",0],["#3a7bf2",1],["#f2c230",2],["#3ec46d",3]].map(([col,k])=>`<polyline fill="none" stroke="${col}" stroke-width="1.5" points="${H.map((h,i)=>`${i*270/60},${38-h[k]*36}`).join(" ")}"/>`).join("")}</svg>`:"";
  P.innerHTML=`<div style="display:flex;justify-content:space-between"><b style="font-size:13px">${s.name}</b><span><button data-t="map">mood map</button> <button data-t="x">✕</button></span></div>
  <div style="opacity:.8">${s.age}, ${s.experience} · ${s.archetype} · ${s.purpose}${s.late>.4?" (late)":""}${s.lost?" · lost":""}${s.passengers.length?" · with a "+s.passengers[0]:""}</div>
  <div style="margin:6px 0;padding:6px;background:#1a1f26;border-radius:6px"><b>${s.intent}</b>: ${s.reason}</div>
  <b>Traits</b>${TM_TRAITS.map(k=>`<div>${bar(s.traits[k],"#8fb3d9")} ${k}</div>`).join("")}
  <b>Emotions</b>${Object.entries(s.emotions).map(([k,v])=>`<div>${bar(v,TM_COL[k]||"#c9a45a")} ${k}</div>`).join("")}
  <div>${bar(s.stress,"#e6392f")} stress · ${bar(s.fatigue,"#8b8f96")} fatigue</div>${ch}
  <b>Wants</b><div>speed ×${s.want.speed.toFixed(2)} · gap ${s.want.headway.toFixed(1)} s · accel ${s.want.accel.toFixed(1)} · polite ${s.want.polite.toFixed(2)} · reaction ${s.want.react.toFixed(2)} s</div>
  ${s.player?`<div>About you: anger ${s.player.anger.toFixed(2)} · trust ${s.player.trust.toFixed(2)}</div>`:""}
  <b>Sees</b><div>${s.perceives.slice(0,8).map(p=>`${p.id===undefined?"?":p.id} ${p.dist} m ${p.ahead?"ahead":"behind"} ~${(p.speed*2.237).toFixed(0)} mph`).join("<br>")||"nothing"}</div>
  <b>Last decisions</b><div>${s.decisions.slice().reverse().map(([t,x])=>`${t}s ${x}`).join("<br>")}</div>`}
addEventListener("keydown",e=>{if(e.key==="F7"){e.preventDefault();tmDebug()}});
