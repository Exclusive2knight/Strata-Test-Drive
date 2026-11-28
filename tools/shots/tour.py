# usage: tour.py out_prefix '[["name","x,y,h","yaw,pitch,dist",cam,"extraJS",simSeconds],...]'
# like multi.py, but the test harness (tests/h.js) is loaded and traffic can run for simSeconds (no rendering) before each shot
import asyncio,sys,os,json
from playwright.async_api import async_playwright
HERE=os.path.dirname(os.path.abspath(__file__))
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    pg=await b.new_page(viewport={"width":1000,"height":560});errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
    await pg.goto("http://127.0.0.1:8765/dev.html"+os.environ.get("Q",""),wait_until="domcontentloaded",timeout=120000);await pg.wait_for_function("document.getElementById('boot').hidden",timeout=120000)
    await pg.evaluate("document.getElementById('maint').hidden=true");await pg.evaluate("document.getElementById('newsGo').click()");await pg.evaluate("st.cfgStep='color';st.cfgTab='fin'");await pg.evaluate("window.KIT_SLICE=400");await pg.evaluate("document.getElementById('go').click()");await pg.wait_for_timeout(800)
    try:await pg.wait_for_function("typeof KITOLD==='undefined'||!KITOLD||KIT.ok",timeout=240000)
    except Exception as e:print("kit wait",e)
    await pg.evaluate(open(os.path.join(HERE,"..","tests","h.js")).read().replace("window.requestAnimationFrame=()=>0;",""))   # (keep rendering)
    await pg.add_style_tag(content="#u2msg,.toast,#toast,#hud,#spawnPop,#tutFx,.hud,#dock,#cluster,#mini{display:none!important}")
    for row in json.loads(sys.argv[2]):
      n,pos,lk,cam,ex=row[:5];sim=row[5] if len(row)>5 else 0
      x,y,h=pos.split(",");yw,pt,ds=lk.split(",")
      await pg.evaluate(f"(()=>{{st.walk=null;resetCar({{free:true,x:{x},y:{y},h:{h}}});car.vx=0;st.gear='P';{ex}}})()")
      if sim:await pg.evaluate(f"SIM({sim},()=>{{car.vx=0}})")
      await pg.evaluate(f"(()=>{{st.cam={cam};look.yaw={yw};look.pitch={pt};look.dist={ds}}})()")
      await pg.wait_for_timeout(2200);await pg.screenshot(path=f"{sys.argv[1]}_{n}.png")
    print(errs[:3]);await b.close()
asyncio.run(main())
