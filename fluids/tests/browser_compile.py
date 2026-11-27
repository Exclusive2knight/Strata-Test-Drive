import asyncio,json,threading,http.server,functools
from pathlib import Path
from playwright.async_api import async_playwright
async def main():
 root=Path(__file__).resolve().parents[2];server=http.server.ThreadingHTTPServer(('127.0.0.1',8765),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(root)));threading.Thread(target=server.serve_forever,daemon=True).start()
 async with async_playwright()as p:
  b=await p.chromium.launch(executable_path='/tmp/chromium',args=['--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']);page=await b.new_page();await page.goto('http://127.0.0.1:8765/fluids/tests/compile.html');await page.wait_for_function('window.result');result=await page.evaluate('result');print(json.dumps(result));Path(__file__).with_name('compile_results.json').write_text(json.dumps(result,indent=2));await b.close()
asyncio.run(main())
