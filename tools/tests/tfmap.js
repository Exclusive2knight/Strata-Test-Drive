(async()=>{const o=[];st.started=true;navTo(null);fmapOpen();const el=$("fmap");o.push("open "+!el.hidden);
/* tap 300 m north-east of the car */
const [sx,sy]=fmS(car.px+250,car.py+200);fmapTap(sx,sy);o.push("sel "+(FM.sel&&(FM.sel.name+" "+(FM.sel.road||""))));
el.querySelector('[data-f="go"]').click();o.push("nav "+!!NAV.dest+" "+(NAV.dest&&NAV.dest.e&&NAV.dest.e.name)+" closed "+el.hidden);
/* tap far from any road */
fmapOpen();const B=fmapBounds();const [ax,ay]=fmS(B.x1+3000,B.y1+3000);FM.k=0.05;fmapTap(innerWidth/2,innerHeight/2);FM.cx=B.x1+3000;FM.cy=B.y1+3000;fmapTap(innerWidth/2,innerHeight/2);o.push("offroad "+(FM.sel&&FM.sel.none?"refused":"picked"));fmapClose();
o.push((NAV.dest?"PASS":"FAIL")+" full map navigation");return o.join("\n")})()
