(()=>{const out=[];for(const cx of [-2500,-2650,-2800,-2950,-3100,-3250,-3400,-3550]){const X0=cx-470,X1=cx+417,Y0=-339,Y1=324;
  const roads=new Set();for(const e of EDGES){if(e.name==="Grand River Ave")continue;for(let u=0;u<=e.L;u+=10){const p=eAt(e,u);if(p.x>X0-10&&p.x<X1+10&&p.y>Y0-10&&p.y<Y1+10){roads.add(e.name);break}}}
  let nb=0;try{for(const o of (typeof COLLS!=="undefined"?COLLS:[]))if(o.x>X0&&o.x<X1&&o.y>Y0&&o.y<Y1)nb++}catch(e){}
  const prof=[];for(let x=X0;x<=X1;x+=111){const g=groundAt(x,0);prof.push(g.h.toFixed(1))}
  let mn=1e9,mx=-1e9;for(let a=X0;a<=X1;a+=40)for(let b=Y0;b<=Y1;b+=40){const z=terrDrawn(a,b);mn=Math.min(mn,z);mx=Math.max(mx,z)}
  out.push(`cx ${cx}: other roads [${[...roads].join(", ")}] colliders ${nb} road z ${prof.join(",")} terrain ${mn.toFixed(1)}..${mx.toFixed(1)}`)}
 const W=typeof W2C!=="undefined"?W2C:{};return out.join("\n")+"\nkeys "+Object.keys(W).join(",")})()
