(()=>{const C=40;let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;for(const e of EDGES)for(let u=0;u<=e.L;u+=20){const p=eAt(e,u);x0=Math.min(x0,p.x);y0=Math.min(y0,p.y);x1=Math.max(x1,p.x);y1=Math.max(y1,p.y)}
 const nx=Math.ceil((x1-x0)/C)+1,ny=Math.ceil((y1-y0)/C)+1,occ=new Uint8Array(nx*ny);
 for(const e of EDGES)for(let u=0;u<=e.L;u+=8){const p=eAt(e,u);const i=Math.floor((p.x-x0)/C),j=Math.floor((p.y-y0)/C);for(let a=-1;a<=1;a++)for(let b=-1;b<=1;b++){const ii=i+a,jj=j+b;if(ii>=0&&jj>=0&&ii<nx&&jj<ny)occ[jj*nx+ii]=1}}
 // free rectangles of 900x700 m (both orientations), scored by distance to a highway
 const W=Math.ceil(900/C),H=Math.ceil(700/C),res=[];
 const AP=typeof APT!=='undefined'?[APT.cx-2700,APT.cx+2700,APT.cy-1300,APT.cy+1600]:null;for(let j=0;j<ny;j++)for(let i=0;i<nx;i++){const x=x0+i*C,y=y0+j*C;if(AP&&x>AP[0]&&x<AP[1]&&y>AP[2]&&y<AP[3])occ[j*nx+i]=1}
 const hw=EDGES.filter(e=>/^I-|Hwy|Fwy|M-|US-/.test(e.name||""));
 for(const [w,h] of [[W,H],[H,W]])for(let j=0;j+h<ny;j+=2)for(let i=0;i+w<nx;i+=2){let ok=true;for(let b=0;b<h&&ok;b++)for(let a=0;a<w;a++)if(occ[(j+b)*nx+i+a]){ok=false;break}if(!ok)continue;
   const cx=x0+(i+w/2)*C,cy=y0+(j+h/2)*C;let zmin=1e9,zmax=-1e9;for(let b=0;b<=h;b+=2)for(let a=0;a<=w;a+=2){const z=terrDrawn(x0+(i+a)*C,y0+(j+b)*C);zmin=Math.min(zmin,z);zmax=Math.max(zmax,z)}
   let dh=1e9;for(const e of hw)for(let u=0;u<=e.L;u+=60){const p=eAt(e,u);dh=Math.min(dh,Math.hypot(p.x-cx,p.y-cy))}
   res.push({cx:Math.round(cx),cy:Math.round(cy),w:w*C,h:h*C,relief:+(zmax-zmin).toFixed(1),dHwy:Math.round(dh)})}
 res.sort((a,b)=>(a.relief*2+Math.max(0,a.dHwy-250)/60)-(b.relief*2+Math.max(0,b.dHwy-250)/60));
 let nr=r=>{let b=1e9,nm="";for(const e of EDGES)for(let u=0;u<=e.L;u+=25){const q=eAt(e,u),d=Math.hypot(q.x-r.cx,q.y-r.cy);if(d<b){b=d;nm=e.name}}return nm+" "+Math.round(b)};const top=[];for(const r of res){if(top.every(t=>Math.hypot(t.cx-r.cx,t.cy-r.cy)>600))top.push(r);if(top.length>=8)break}
 return `APT ${AP} world x ${x0|0}..${x1|0} y ${y0|0}..${y1|0}; free spots ${res.length}\n`+top.map(r=>JSON.stringify(r)+" nearest: "+nr(r)).join("\n")+"\nhighways: "+[...new Set(hw.map(e=>e.name))].join(", ")})()
