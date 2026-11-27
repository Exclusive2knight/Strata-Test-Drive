import asyncio,json,threading,http.server,functools
from pathlib import Path
from playwright.async_api import async_playwright
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
async def main():
 root=Path(__file__).resolve().parents[2];server=http.server.ThreadingHTTPServer(('127.0.0.1',8768),functools.partial(Quiet,directory=str(root)));threading.Thread(target=server.serve_forever,daemon=True).start()
 async with async_playwright()as p:
  b=await p.chromium.launch(executable_path='/tmp/chromium',args=['--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']);page=await b.new_page();await page.goto('http://127.0.0.1:8768/fluids/tests/compile.html');await page.wait_for_function('window.result');await page.add_script_tag(url='http://127.0.0.1:8768/fluids/tests/gpu_checks.js');r=await page.evaluate('runGPU()');print(json.dumps(r,indent=2),flush=True);(root/'fluids/tests/gpu_results.json').write_text(json.dumps(r,indent=2));await b.close()
asyncio.run(main())
