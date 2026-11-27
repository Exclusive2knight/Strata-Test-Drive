/* v38 traffic minds: 13 determinism. Run twice in fresh pages: the printed fingerprint must be identical */
(async()=>{Traffic.seed(777);window.NOSEMI=1;setTrim("camry25",true);resetCar(STARTS.city);st.power=true;st.started=true;st.gear="P";car.vx=0;cars.length=0;CAR_ID=0;st.clock=0;GT.min=8*60;Traffic.set_density("all",.8);
for(let k=0;k<3000;k++)SIMSTEP(0.1);const A=cars.filter(c=>c.kind==="ai").map(c=>[c.id,c.wx.toFixed(2),c.wy.toFixed(2),c.mind?c.mind.spike.anger.toFixed(3):"-",c.mind?c.mind.stress.toFixed(3):"-"].join(","));
let h=0;for(const s of A)for(let i=0;i<s.length;i++)h=Math.imul(h^s.charCodeAt(i),16777619)>>>0;return `FP ${A.length} cars ${h.toString(16)} first ${A[0]}`})()
