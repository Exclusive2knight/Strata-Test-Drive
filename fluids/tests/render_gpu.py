import asyncio,json,threading,http.server,functools
from pathlib import Path
from playwright.async_api import async_playwright
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
async def main():
 root=Path(__file__).resolve().parents[2];server=http.server.ThreadingHTTPServer(('127.0.0.1',8770),functools.partial(Quiet,directory=str(root)));threading.Thread(target=server.serve_forever,daemon=True).start()
 async with async_playwright()as p:
  b=await p.chromium.launch(executable_path='/tmp/chromium',args=['--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']);page=await b.new_page(viewport={'width':960,'height':600});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));await page.goto('http://127.0.0.1:8770/fluids/lab.html');await page.wait_for_function('window.lab');await page.evaluate('lab.stop()');await page.evaluate('lab.load(1)');r=await page.evaluate('lab.gpuWater()');r['errors']=errors;await page.screenshot(path=str(root/'fluids/previews/gpu_water_surface.png'));print(r,flush=True);(root/'fluids/tests/gpu_render_results.json').write_text(json.dumps(r,indent=2));await b.close()
asyncio.run(main())
