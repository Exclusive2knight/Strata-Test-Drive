"""Bake the freeway sign props (road props v2) for the game: python3 tools/props2/bake.py
Needs the test server (sh tools/serve.sh) and a fresh build (python3 build.py). Loads dev.html in headless Chromium, runs
tools/props2/bake.js there (strata-road-props.js on the three.js stand-in in three-shim.js) and writes props/rp2.json and
props/rp2_atlas.jpg. strata-road-props.js here is the pack's file with its `three` import pointed at the stand-in."""
import asyncio, base64, os, sys
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        pg = await b.new_page(viewport={"width": 480, "height": 260}); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "warning" and "rp2" in m.text and print("warn:", m.text))
        await pg.goto("http://127.0.0.1:8765/dev.html", timeout=120000); await pg.wait_for_function("document.getElementById('boot').hidden", timeout=120000)
        print(await pg.evaluate(open(os.path.join(HERE, "bake.js")).read()))
        d = await pg.evaluate("window.__RP2")
        open(os.path.join(ROOT, "props/rp2.json"), "w").write(d["json"])
        open(os.path.join(ROOT, "props/rp2_atlas.jpg"), "wb").write(base64.b64decode(d["jpg"].split(",", 1)[1]))
        print(f'rp2.json {len(d["json"]) // 1024} KB, atlas {os.path.getsize(os.path.join(ROOT, "props/rp2_atlas.jpg")) // 1024} KB', errs[:3]); await b.close()
asyncio.run(main())
