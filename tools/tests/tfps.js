// Full-throttle launch driven through frame() at different frame rates: the car should reach the same speed in the same (game-clock) time.
(()=>{const o=[];window.requestAnimationFrame=()=>0;window.render=()=>{};window.hud=()=>{};
for(const fps of [60,20,12,10]){setTrim("camry25",true);st.power=true;st.started=true;sys.epb=false;resetCar(STARTS.city);st.gear="D";car.vx=0;
  let t=performance.now()+1e6;last=t;acc=0;const ms=1000/fps;let wall=0;
  for(let i=0;i<Math.round(4*fps);i++){inp.thrT=1;inp.brkT=0;inp.steerT=0;t+=ms;const w0=performance.now();frame(t);wall+=performance.now()-w0}
  o.push(fps+" fps: "+(car.vx*2.237).toFixed(1)+" mph after 4 s ("+(wall/Math.round(4*fps)).toFixed(1)+" ms/frame here)")}
return o.join("\n")})()
