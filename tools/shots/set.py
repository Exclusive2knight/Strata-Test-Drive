import asyncio,sys
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    for i,(vp,mob) in [(1,({"width":874,"height":402},True))]:
      pg=await b.new_page(viewport=vp,has_touch=mob,is_mobile=mob);errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
      await pg.goto("http://127.0.0.1:8765/dev.html",wait_until="domcontentloaded");await pg.wait_for_function("document.getElementById('boot').hidden",timeout=90000)
      await pg.click("#newsGo");await pg.evaluate("st.cfgStep='color';st.cfgTab='acc'");await pg.click("#go");await pg.wait_for_timeout(800)
      for tab in sys.argv[1].split(","):
        await pg.evaluate(f"st.tab='{tab}';openDrawer()");await pg.wait_for_timeout(500);await pg.screenshot(path=f"set_{i}_{tab}.png")
      print(errs[:3]);await pg.close()
    await b.close()
asyncio.run(main())
