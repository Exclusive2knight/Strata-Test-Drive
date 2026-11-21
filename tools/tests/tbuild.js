// build-a-car: every package and option offered on every trim must actually switch on what it says (driver assists, HUD, cameras, comfort features)
(async()=>{const fails={},ex={};let nPk=0,nOp=0,nChk=0;const save=[st.trim,JSON.stringify(st.opk||{}),JSON.stringify(st.cfg||{})];
 const chk=(k,src,f)=>{nChk++;let ok;if(BD_ENG.includes(f)||f==="esa"||f==="tech")ok=has(f);else if(f==="hud")ok=hudStd();else ok=ownF(f,k);if(!ok){fails[f]=(fails[f]||0)+1;(ex[f]=ex[f]||[]).length<4&&ex[f].push(k+' ← '+src)}};
 for(const k of ORDER){const T=TRIMS[k];if(!T||!T.real||T.tesla)continue;st.trim=k;st.opk={};st.cfg={};enforcePkgs.k=null;
  for(const p of OPT_PKGS[k]||[]){nPk++;st.opk={[k]:{[p.id]:1}};for(const f of new Set([...(p.adds||[]),...(p.feats||[])]))chk(k,'pkg '+p.name,f);if(p.hud)chk(k,'pkg '+p.name,'hud')}
  st.opk={};const B=bdOf(k);if(B)B.op.forEach((o,i)=>{if(!bdIn(o[3],k))return;nOp++;st.cfg={[k]:{op:{[i]:1}}};for(const f of o[5])chk(k,'opt '+o[1],f)});st.cfg={}}
 st.trim=save[0];st.opk=JSON.parse(save[1]);st.cfg=JSON.parse(save[2]);enforcePkgs.k=null;
 return `packages ${nPk} options ${nOp} checks ${nChk}\nfailing: ${JSON.stringify(fails)}\n`+Object.entries(ex).map(([f,a])=>f+': '+a.join(' | ')).join('\n')})()
