/* Things standing on the kit's roads: the kit's road pieces are rasterised at 0.5 m (their driving surface, kerbs and sidewalks, no verges);
   every building footprint (models and blocks), streetlight, signal / sign pole and parking-lot site that lands on that surface is listed */
(async()=>{const out=[];const [J,LAY]=await Promise.all([kitGet("kitold_pieces.json"),kitGet("kitold.json")]);const R=new Map(),RS=0.5,key=(x,y)=>Math.floor(x/RS)+","+Math.floor(y/RS);
for(const [name,x,y,h,z0] of LAY.place){const d=kitShape(J,name);if(!d)continue;const c=Math.cos(h*Math.PI/180),sn=Math.sin(h*Math.PI/180),p=d.p,W=[];
  for(let k=0;k<p.length;k+=3){const ex=p[k]/100,ny=-p[k+2]/100;W.push([x+ex*c+ny*sn,y-ex*sn+ny*c,p[k+1]/100])}
  const I=d.i||d.I;for(let t=0;t<I.length;t+=3){const A=W[I[t]],B=W[I[t+1]],C=W[I[t+2]];if(Math.min(A[2],B[2],C[2])<-0.06||Math.max(A[2],B[2],C[2])>0.06)continue;   /* (the buried verges don't count) */
    const x0=Math.min(A[0],B[0],C[0]),x1=Math.max(A[0],B[0],C[0]),y0=Math.min(A[1],B[1],C[1]),y1=Math.max(A[1],B[1],C[1]);if((x1-x0)*(y1-y0)>20000)continue;
    const s=(P,Q,X)=>(Q[0]-P[0])*(X[1]-P[1])-(Q[1]-P[1])*(X[0]-P[0]);
    for(let gx=Math.floor(x0/RS);gx<=Math.floor(x1/RS);gx++)for(let gy=Math.floor(y0/RS);gy<=Math.floor(y1/RS);gy++){const X=[(gx+0.5)*RS,(gy+0.5)*RS],a=s(A,B,X),b=s(B,C,X),cc=s(C,A,X);if((a>=0&&b>=0&&cc>=0)||(a<=0&&b<=0&&cc<=0))R.set(gx+","+gy,name)}}}
out.push(`kit surface cells ${R.size}`);
const on=(x,y)=>R.get(key(x,y));const hits=[];
// buildings: models with footprints (inset 0.5 m), checked on a 1 m grid inside
for(const o of W2P){const f=W2_FP[o.k];if(!f||o.off||!/^(lk_|b_|f_|l_|r_|h_|house|w_)/.test(o.k))continue;const cs=fpRect(o.k,o.x,o.y,o.a,0.5);if(!cs)continue;let n=0,where=null;
  for(let u=0;u<=1.0001;u+=0.1)for(let v=0;v<=1.0001;v+=0.1){const x=cs[0][0]+(cs[1][0]-cs[0][0])*u+(cs[3][0]-cs[0][0])*v,y=cs[0][1]+(cs[1][1]-cs[0][1])*u+(cs[3][1]-cs[0][1])*v;const k=on(x,y);if(k){n++;where=where||[x,y,k]}}
  if(n)hits.push(["building",o.k,n,where])}
for(const l of SL.list){const k=on(l.x,l.y);if(k){/* a streetlight on a sidewalk is fine; on the road it isn't: is it within the asphalt (roadDist 0)? */const rd=roadDist(l.x,l.y,2);hits.push([rd<0.3?"light ON ROAD":"light on walk",l.k,1,[l.x,l.y,k]])}}
for(const S of XSITES){const cs=[[-1,-1],[1,-1],[1,1],[-1,1]].map(([a,b])=>[S.x+S.U[0]*a*S.L/2+S.N[0]*b*S.D/2,S.y+S.U[1]*a*S.L/2+S.N[1]*b*S.D/2]);let n=0,where=null;for(let u=0;u<=1;u+=0.125)for(let v=0;v<=1;v+=0.125){const x=cs[0][0]+(cs[1][0]-cs[0][0])*u+(cs[3][0]-cs[0][0])*v,y=cs[0][1]+(cs[1][1]-cs[0][1])*u+(cs[3][1]-cs[0][1])*v;const k=on(x,y);if(k){n++;where=where||[x,y,k]}}if(n)hits.push(["lot "+S.kind,S.e&&S.e.name,n,where])}
for(const S of STORES){const k=on(S.x,S.y);if(k)hits.push(["store",S.store&&S.store.name,1,[S.x,S.y,k]])}
const by={};for(const h of hits){by[h[0]]=(by[h[0]]||0)+1}out.push("counts "+JSON.stringify(by));
hits.filter(h=>h[0]!=="light on walk"&&(h[0]!=="lot lot"||h[2]>8)).sort((a,b)=>b[2]-a[2]).slice(0,40).forEach(h=>out.push(`${h[0]} ${h[1]} cells ${h[2]} at ${h[3][0].toFixed(0)},${h[3][1].toFixed(0)} on ${h[3][2]}`));
return out.join("\n")})()
