/* trees in the way: trunks on a road (or within 1 m of the kerb), and canopies hanging well over the lanes, grouped by area */
(async()=>{const out=[];const on=[],near=[],over=[];let n=0;
const ALL=[];for(const [k,T] of TREEP){const [a,b]=k.split(",").map(Number);ALL.push([a/2,b/2,T.r,""])}for(const o of (typeof W2P!=="undefined"?W2P:[]))if(/^t_/.test(o.k))ALL.push([o.x,o.y,3,o.k]);
for(const [x,y,r_,kk] of ALL){const T={r:r_};n++;let best=1e9,be=null;
  for(const e of edgesNear(x,y,40)){const p=eProj(e,x,y);if(!p||p.u<0||p.u>e.L)continue;const at=Math.abs(p.t),m2=(e.m||0)/2,d=at<m2?m2-at-0.0:at-hwOf(e);if(d<best){best=d;be=e}}
  for(const nd of NODES){if(Math.abs(nd.x-x)>40||Math.abs(nd.y-y)>40)continue;const r=(nd.r||0);const d=Math.hypot(nd.x-x,nd.y-y)-r;if(r&&d<best){best=d;be={name:"junction"}}}
  const s=`${kk}${be?be.name:"?"} @${x.toFixed(0)},${y.toFixed(0)} d${best.toFixed(1)} r${T.r.toFixed(1)}`;
  if(best<0)on.push(s);else if(best<1)near.push(s);else if(best<T.r-1.2)over.push(s)}
const grp=L=>{const m={};for(const s of L){const k=s.split(" @")[0];m[k]=(m[k]||0)+1}return Object.entries(m).sort((a,b)=>b[1]-a[1]).slice(0,15).map(([k,v])=>k+":"+v).join(", ")};
out.push(`trees ${n}; trunk on road ${on.length}; trunk within 1 m of kerb ${near.length}; canopy over lanes ${over.length}`);
out.push("on road: "+grp(on));out.push("  e.g. "+on.slice(0,12).join(" | "));out.push("near: "+grp(near));out.push("over: "+grp(over));out.push("  e.g. "+over.slice(0,10).join(" | "));
return out.join("\n")})()
