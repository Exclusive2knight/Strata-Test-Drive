(()=>{setTrim("camry25",true);st.power=true;st.started=true;st.gear="D";sys.epb=false;resetCar(STARTS.city);const o=[];
let t=performance.now();for(let i=0;i<2000;i++)physics(1/400);o.push("physics step "+((performance.now()-t)/2000*1000).toFixed(1)+" µs");
t=performance.now();for(let i=0;i<300;i++){updateTraffic(1/60)}o.push("traffic update "+((performance.now()-t)/300).toFixed(2)+" ms ("+cars.length+" cars)");
t=performance.now();for(let i=0;i<300;i++){controls(1/60);assist(1/60)}o.push("controls+assists "+((performance.now()-t)/300).toFixed(2)+" ms");
t=performance.now();for(let i=0;i<2000;i++)stnWorld("chargers");o.push("stnWorld "+((performance.now()-t)/2000*1000).toFixed(1)+" µs");
t=performance.now();for(let i=0;i<300;i++)hud&&hud(1/60);o.push("hud "+((performance.now()-t)/300).toFixed(2)+" ms");
return o.join("\n")})()
