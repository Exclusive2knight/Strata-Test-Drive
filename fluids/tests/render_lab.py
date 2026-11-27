import asyncio,json,threading,http.server,functools
from pathlib import Path
from playwright.async_api import async_playwright
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
async def main():
 root=Path(__file__).resolve().parents[2];server=http.server.ThreadingHTTPServer(('127.0.0.1',8767),functools.partial(Quiet,directory=str(root)));threading.Thread(target=server.serve_forever,daemon=True).start()
 out=root/'fluids/previews';out.mkdir(exist_ok=True)
 async with async_playwright()as p:
  b=await p.chromium.launch(executable_path='/tmp/chromium',args=['--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']);page=await b.new_page(viewport={'width':960,'height':600});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));await page.goto('http://127.0.0.1:8767/fluids/lab.html');await page.wait_for_function('window.lab');await page.evaluate('lab.stop()');results=[]
  for i in range(1,10):
   await page.evaluate('(id)=>lab.load(id)',i)
   frames=[]
   for f in range(3):
    r=await page.evaluate('lab.step(60)');await page.screenshot(path=str(out/f'scene_{i:02d}_{f+1}.png'));frames.append(r)
   if i in (5,6,9):
    await page.evaluate('lab.gpuSmoke()');await page.screenshot(path=str(out/f'scene_{i:02d}_gpu.png'))
   print(i,frames[-1],flush=True);results.append({'scene':i,'frames':frames})
  (root/'fluids/tests/preview_results.json').write_text(json.dumps({'errors':errors,'scenes':results},indent=2));print('ERRORS',errors);await b.close()
asyncio.run(main())
