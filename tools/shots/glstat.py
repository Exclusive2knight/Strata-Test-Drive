import asyncio,sys
from playwright.async_api import async_playwright
sys.path.insert(0,__import__('os').path.dirname(__import__('os').path.abspath(__file__)));from scen import SETUP
WRAP="""(()=>{const S=window.__gs={dc:0,tri:0,buf:0,bufB:0,tex:0,texPx:0,frames:0};const P=WebGLRenderingContext.prototype,P2=window.WebGL2RenderingContext&&WebGL2RenderingContext.prototype;
for(const Q of [P,P2]){if(!Q)continue;const de=Q.drawElements,da=Q.drawArrays,bd=Q.bufferData,ti=Q.texImage2D,ts=Q.texSubImage2D;
Q.drawElements=function(m,c,t,o){S.dc++;S.tri+=c/3;if(S.big)S.big.push([c/3,new Error().stack.split(String.fromCharCode(10))[2].trim().slice(0,90)]);return de.apply(this,arguments)};Q.drawArrays=function(m,f,c){S.dc++;S.tri+=c/3;return da.apply(this,arguments)};
Q.bufferData=function(t,d){S.buf++;S.bufB+=d&&d.byteLength||0;return bd.apply(this,arguments)};Q.texImage2D=function(){S.tex++;const a=arguments,el=a[a.length-1];S.texPx+=(el&&el.width?el.width*el.height:(a[3]*a[4]||0));return ti.apply(this,arguments)};
Q.texSubImage2D=function(){S.tex++;return ts.apply(this,arguments)}}})()"""
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    for scen in sys.argv[1:]:
      pg=await b.new_page(viewport={"width":1000,"height":560});await pg.add_init_script(WRAP)
      await pg.goto("http://127.0.0.1:8765/dev.html",wait_until="domcontentloaded",timeout=120000);await pg.wait_for_function("document.getElementById('boot').hidden",timeout=120000)
      await pg.click("#newsGo");await pg.evaluate("st.cfgStep='color';st.cfgTab='acc'");await pg.click("#go");await pg.wait_for_timeout(1500)
      await pg.evaluate(SETUP[scen]);await pg.wait_for_timeout(4000)
      r=await pg.evaluate("""(()=>{const S=__gs;for(const k in S)S[k]=0;S.big=null;const t0=performance.now();let js=0;for(let i=0;i<5;i++){const a=performance.now();render(0.016);js+=performance.now()-a}gl.finish();const T=(performance.now()-t0)/5;S.big=[];render(0.016);const agg={};for(const [n,w] of S.big){agg[w]=(agg[w]||0)+n}const top=Object.entries(agg).sort((a,b)=>b[1]-a[1]).slice(0,12).map(([w,n])=>`\n   ${(n/1000).toFixed(0)}k ${w}`).join('');S.big=null;
        return `draws ${(S.dc/5)|0}/frame · tris ${(S.tri/5/1000).toFixed(0)}k · bufferData ${(S.buf/5).toFixed(0)} (${(S.bufB/5/1024).toFixed(0)} KB) · tex uploads ${(S.tex/5).toFixed(1)} (${(S.texPx/5/1e6).toFixed(2)} Mpx) · quality ${G().label} res ${G().res} · cpu+gpu ${T.toFixed(0)} ms`+top})()""")
      print(scen,":",r);await pg.close()
    await b.close()
asyncio.run(main())
