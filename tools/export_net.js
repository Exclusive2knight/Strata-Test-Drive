(async()=>{const E=EDGES.map(e=>{const P=[];for(let u=0;u<=e.L;u+=Math.min(4,e.L)){const p=eAt(e,u);P.push([+p.x.toFixed(2),+p.y.toFixed(2),+(e.hz?ez(e,u):0).toFixed(2)])}const q=eAt(e,e.L);P.push([+q.x.toFixed(2),+q.y.toFixed(2),+(e.hz?ez(e,e.L):0).toFixed(2)]);
  return {i:e.i,t:e.type,nm:e.name,n:e.n,m:e.m,ow:!!e.ow,a:NODES.indexOf(e.a),b:NODES.indexOf(e.b),L:+e.L.toFixed(2),P,u0:+Math.max(e.r0||0,e.p0||0,e.a.pr||0).toFixed(2),u1:+(e.L-Math.max(e.r1||0,e.p1||0,e.b.pr||0)).toFixed(2)}});
 const N=NODES.map(n=>({x:+n.x.toFixed(2),y:+n.y.toFixed(2),z:+(n.z||0).toFixed(2),k:n.kind,c:n.ctrl||"",d:n.legs?n.legs.length:0,pr:+(n.pr||0).toFixed(1)}));
 const s=JSON.stringify({E,N});const a=document.createElement('a');window.__EXP=s;return s.length})()
