/* AI turning over kerbs at the kit's junctions (the pieces drawn at most downtown and suburban corners): the raised parts of every placed
   junction piece (kerbs, sidewalks, islands: anything 7 cm or more above the road) are rasterised at 0.5 m; traffic runs for 150 s and any
   AI car with a corner over a raised cell counts. Reports by junction piece and turn */
(async()=>{const out=[];window.NOSEMI=1;setTrim("camry25",true);resetCar({free:true,x:-1265,y:-80,h:0});st.power=true;st.started=true;st.gear="P";car.vx=0;Traffic.set_density("all",1);
const [J,LAY]=await Promise.all([kitGet("kitold_pieces.json"),kitGet("kitold.json")]);const R=new Map(),RS=0.5,key=(x,y)=>Math.floor(x/RS)+","+Math.floor(y/RS),JX=[];
for(const [name,x,y,h,z0] of LAY.place){if(!name.startsWith("x_"))continue;const d=kitShape(J,name);if(!d)continue;JX.push({name,x,y});const c=Math.cos(h*Math.PI/180),sn=Math.sin(h*Math.PI/180),p=d.p,W=[];
  for(let k=0;k<p.length;k+=3){const ex=p[k]/100,ny=-p[k+2]/100;W.push([x+ex*c+ny*sn,y-ex*sn+ny*c,p[k+1]/100])}
  const I=d.i||d.I;for(let t=0;t<I.length;t+=3){const A=W[I[t]],B=W[I[t+1]],C=W[I[t+2]];if(!(A[2]>0.07&&B[2]>0.07&&C[2]>0.07))continue;
    const x0=Math.min(A[0],B[0],C[0]),x1=Math.max(A[0],B[0],C[0]),y0=Math.min(A[1],B[1],C[1]),y1=Math.max(A[1],B[1],C[1]);if((x1-x0)*(y1-y0)>4000)continue;
    const s=(P,Q,X)=>(Q[0]-P[0])*(X[1]-P[1])-(Q[1]-P[1])*(X[0]-P[0]);
    for(let gx=Math.floor(x0/RS);gx<=Math.floor(x1/RS);gx++)for(let gy=Math.floor(y0/RS);gy<=Math.floor(y1/RS);gy++){const X=[(gx+0.5)*RS,(gy+0.5)*RS],a=s(A,B,X),b=s(B,C,X),cc=s(C,A,X);if((a>=0&&b>=0&&cc>=0)||(a<=0&&b<=0&&cc<=0))R.set(gx+","+gy,name)}}}
out.push(`kit junctions ${JX.length}, raised cells ${R.size}`);
const nearJ=(x,y)=>{for(const j of JX)if(Math.abs(j.x-x)<40&&Math.abs(j.y-y)<40)return j;return null};
const hit=new Map(),seen=new Set();let samples=0,over=0;const hl=2.2,hw=0.88;
for(let t=0;t<150;t+=0.1){SIMSTEP(0.1);if(((t*10)|0)%3)continue;
  for(const c of cars){if(c.kind!=="ai"||c.wx===undefined||c.dyn||(c.wz||0)>1)continue;const j=nearJ(c.wx,c.wy);if(!j)continue;samples++;const co=Math.cos(c.wh),si=Math.sin(c.wh);let bad=0;
    for(const [a,b] of [[hl,hw],[hl,-hw],[-hl,hw],[-hl,-hw]]){const x=c.wx+co*a-si*b,y=c.wy+si*a+co*b;if(R.has(key(x,y)))bad++}
    if(bad){over++;const k=`${j.name} ${j.x.toFixed(0)},${j.y.toFixed(0)} ${c.mv?c.mv.t:"-"}`;hit.set(k,(hit.get(k)||0)+1);if(!seen.has(c.id+k)){seen.add(c.id+k)}}}}
const byT={},byP={};for(const [k,v] of hit){const [p,,t]=k.split(" ");byT[t]=(byT[t]||0)+v;byP[p]=(byP[p]||0)+v}
out.push(`AI samples at kit junctions ${samples}, with a corner on a kerb or sidewalk ${over} (${(100*over/Math.max(1,samples)).toFixed(1)}%), distinct car-junction events ${seen.size}`);
out.push("by turn "+JSON.stringify(byT)+"\nby piece "+JSON.stringify(byP));out.push([...hit.entries()].sort((a,b)=>b[1]-a[1]).slice(0,12).map(([k,v])=>k+": "+v).join("\n"));return out.join("\n")})()
