"""Run a JS test against the built game: python3 tools/run.py tools/tests/t_all.js
Loads index.html in headless Chromium, starts a drive, installs the SIM harness (tests/h.js), prints the test's return value."""
import asyncio,sys,os
from playwright.async_api import async_playwright
HERE=os.path.dirname(os.path.abspath(__file__))
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    pg=await b.new_page(viewport={"width":480,"height":260});errs=[];pg.on("pageerror",lambda e:errs.append(str(e)+" :: "+(e.stack or "")[:300]))
    await pg.goto("http://127.0.0.1:8765/dev.html",timeout=120000);await pg.wait_for_function("document.getElementById('boot').hidden",timeout=120000)
    await pg.click("#newsGo");await pg.evaluate("st.cfgStep='color';st.cfgTab='acc'");await pg.click("#go");await pg.wait_for_timeout(800)
    await pg.evaluate(open(os.path.join(HERE,"tests","h.js")).read())
    src=open(sys.argv[1]).read()
    if os.path.basename(sys.argv[1]).startswith("pa") and "PAT(" in src and "window.PAT" not in src:src=open(os.path.join(HERE,"tests","pa_lib.js")).read()+"\n"+src
    print(await pg.evaluate(src));print(errs[:4]);await b.close()
asyncio.run(main())
