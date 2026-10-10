import asyncio,sys
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    for i,(vp,mob) in [list(enumerate([({"width":1000,"height":560},False),({"width":874,"height":402},True)]))[int(sys.argv[1])]]:
      pg=await b.new_page(viewport=vp,has_touch=mob,is_mobile=mob);errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
      await pg.goto("http://127.0.0.1:8765/index.html",wait_until="domcontentloaded");await pg.wait_for_function("document.getElementById('boot').hidden",timeout=90000)
      await pg.click("#newsGo");await pg.evaluate("st.cfgStep='color';st.cfgTab='acc'");await pg.click("#go");await pg.wait_for_timeout(500)
      await pg.evaluate("(async()=>{const k='toy_4runner_tr';await loadModel(TRIMS[k].model);setTrim(k,true);st.power=true;st.started=true;st.gear='P';st.cam=0;st.walk=null;act('mode');act('mode');act('mode')})()")
      await pg.wait_for_timeout(3000);await pg.screenshot(path=f"hud{i}.png");print(errs[:3])
    await b.close()
asyncio.run(main())
