/* AI turning over kerbs: traffic runs for 120 s; at every junction drawn with kerb returns, any corner of an AI car that is outside the paved
   junction polygon and off every road's carriageway counts as over the kerb. Reports how often and where (by junction and turn) */
(async()=>{const out=[];window.NOSEMI=1;setTrim("camry25",true);resetCar({free:true,x:-1265,y:-80,h:0});st.power=true;st.started=true;st.gear="P";car.vx=0;Traffic.set_density("all",1);
const inPoly=(P,x,y)=>{let c=false;for(let i=0,j=P.length-1;i<P.length;j=i++){const a=P[i],b=P[j];if((a[1]>y)!==(b[1]>y)&&x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])c=!c}return c};
const onCarriage=(x,y)=>{for(const e of edgesNear(x,y,30)){const p=eProj(e,x,y);if(p.u<-0.5||p.u>e.L+0.5)continue;const a=Math.abs(p.t),m2=mAt(e,Math.max(0,Math.min(e.L,p.u)))/2;if(a<=hwOf(e)+0.15&&(a>=m2-0.15-((e.bay&&(e.bay[1]||e.bay[-1]))?LANE:0)||m2<0.5))return true}return false};
const J=NODES.filter(n=>n.jpoly&&n.legs.length>=3);const near=(x,y)=>{for(const n of J){const d=Math.hypot(n.x-x,n.y-y);if(d<45)return n}return null};
const hit=new Map();let samples=0,over=0;const hl=2.25,hw=0.9;
for(let t=0;t<120;t+=0.1){SIMSTEP(0.1);if(((t*10)|0)%3)continue;
  for(const c of cars){if(c.kind!=="ai"||c.wx===undefined||c.dyn)continue;const n=near(c.wx,c.wy);if(!n)continue;samples++;const co=Math.cos(c.wh),si=Math.sin(c.wh);let bad=0;
    for(const [a,b] of [[hl,hw],[hl,-hw],[-hl,hw],[-hl,-hw]]){const x=c.wx+co*a-si*b,y=c.wy+si*a+co*b;if(!inPoly(n.jpoly,x,y)&&!onCarriage(x,y)&&!(n.xo&&xoHit(n,x,y)))bad++}
    if(bad){over++;const k=`${n.x.toFixed(0)},${n.y.toFixed(0)} ${c.mv?c.mv.t:"-"} ${n.legs.map(l=>l.e.type).join("/")}`;hit.set(k,(hit.get(k)||0)+1)}}}
const top=[...hit.entries()].sort((a,b)=>b[1]-a[1]).slice(0,15);
out.push(`junction samples ${samples}, with a corner over the kerb ${over} (${(100*over/Math.max(1,samples)).toFixed(1)}%)`);out.push(top.map(([k,v])=>k+": "+v).join("\n"));
const byT={};for(const [k,v] of hit){const t=k.split(" ")[1];byT[t]=(byT[t]||0)+v}out.push("by turn "+JSON.stringify(byT));return out.join("\n")})()
