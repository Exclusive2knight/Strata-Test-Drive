import asyncio,sys,json
from playwright.async_api import async_playwright
# usage: multi.py out_prefix '[["name","x,y,h","yaw,pitch,dist",cam,"extraJS"],...]'
async def main():
  SH=json.loads(sys.argv[2])
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    pg=await b.new_page(viewport={"width":1000,"height":560});errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
    await pg.goto("http://127.0.0.1:8765/dev.html",wait_until="domcontentloaded",timeout=120000);await pg.wait_for_function("document.getElementById('boot').hidden",timeout=120000)
    await pg.click("#newsGo");await pg.evaluate("st.cfgStep='color';st.cfgTab='acc'");await pg.click("#go");await pg.wait_for_timeout(800)
    await pg.add_style_tag(content="#u2msg,.toast,#toast,#ui2,#hud{display:none!important}")
    for n,pos,lk,cam,ex in SH:
      x,y,h=pos.split(",");yw,pt,ds=lk.split(",")
      await pg.evaluate(f"(()=>{{st.walk=null;resetCar({{free:true,x:{x},y:{y},h:{h}}});car.vx=0;st.gear='P';st.cam={cam};look.yaw={yw};look.pitch={pt};look.dist={ds};{ex}}})()")
      await pg.wait_for_timeout(2200);await pg.screenshot(path=f"{sys.argv[1]}_{n}.png")
    print(errs[:3]);await b.close()
asyncio.run(main())
