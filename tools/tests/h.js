window.requestAnimationFrame=()=>0;
window.SIMSTEP=(dt)=>{if(st.started){controls(dt);assist(dt);updateTraffic(dt);updatePark(dt);enforcePkgs();acc+=dt;const h=1/G().hz;while(acc>=h){physics(h);acc-=h}if(car.crashed>0)car.crashed-=dt}gtTick(dt);};
window.SIM=(T,fn,dt=0.02)=>{for(let t=0;t<T;t+=dt){SIMSTEP(dt);if(fn&&fn(t)===false)break}};
window.lead=()=>{const M=me();let best=null;for(const c of cars){if(c.kind==="ai"&&!c.test)continue;}return best};
window.gapTo=(c)=>{const M=me();if(!c||c.e!==M.e||c.dir!==M.dir)return Math.hypot(c.wx-car.px,c.wy-car.py);return c.s-M.s};
window.hits=0;const _cf=crashFx;window.crashFx=function(){hits++;return _cf.apply(this,arguments)};
