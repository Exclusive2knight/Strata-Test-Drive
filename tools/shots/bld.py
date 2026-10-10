import asyncio,sys
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    for i,(vp,mob) in [(0,({"width":1100,"height":620},False)),(1,({"width":874,"height":402},True))]:
      pg=await b.new_page(viewport=vp,has_touch=mob,is_mobile=mob);errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
      await pg.goto("http://127.0.0.1:8765/index.html",wait_until="domcontentloaded",timeout=120000);await pg.wait_for_function("document.getElementById('boot').hidden",timeout=120000)
      await pg.click("#newsGo");await pg.evaluate("st.cfgStep='color';st.cfgTab='acc';renderCfg()");await pg.wait_for_timeout(600);await pg.screenshot(path=f"bld{i}.png")
      if len(sys.argv)>1:
        await pg.click("#go");await pg.wait_for_timeout(500)
        r=await pg.evaluate("(async()=>{resetCar({free:true,x:-2105,y:-30,h:0});await new Promise(r=>setTimeout(r,300));const a=[car.px|0,car.py|0];spawnAnother();await new Promise(r=>setTimeout(r,500));st.cfgStep='color';st.cfgTab='acc';renderCfg();$('go').click();await new Promise(r=>setTimeout(r,500));return JSON.stringify({before:a,after:[car.px|0,car.py|0],parked:st.fleet.length,cash:ECON.cash})})()")
        print(r)
      print(errs[:3]);await pg.close()
    await b.close()
asyncio.run(main())
