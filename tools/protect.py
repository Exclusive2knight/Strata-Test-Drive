"""Make the copy-protected build of the game from index.html.

  python3 tools/protect.py            -> index.html  (site lock on: only runs on the official site / app)
  python3 tools/protect.py --nolock   -> dist/artifact.html (for the private Claude artifact)

What it does:
- joins the page's scripts into one closed scope and minifies it with esbuild, so every
  internal name is mangled (no readable source to copy or edit),
- drops the test hook (window.__strata),
- with the lock on, the game refuses to run anywhere except exclusive2knight.github.io
  (and the phone app wrapper), so a downloaded or re-hosted copy shows a notice instead.
dev.html (from build.py) stays readable for development and tests and is never published.
"""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESBUILD = "/opt/npm-tools/node_modules/esbuild/bin/esbuild"
lock = "--nolock" not in sys.argv
src = open(os.path.join(HERE, "dev.html")).read()

spans = [m.span() for m in re.finditer(r"<script>(.*?)</script>", src, re.S)]
codes = [src[a + 8:b - 9] for a, b in spans]
js = "\n;\n".join(codes)
i = js.rfind("window.__strata=")
if i >= 0:
    js = js[:i]

OWNER = "Exclusive2knight"
LOCK = r"""
{const h=location.hostname.toLowerCase(),ok=/(^|\.)exclusive2knight\.github\.io$/.test(h)||/\.discordsays\.com$/.test(h)||(window.Capacitor&&(h==="localhost"||location.protocol==="capacitor:"));
 if(!ok){document.title="Strata Test Drive";document.body.innerHTML='<div style="font:16px system-ui;max-width:520px;margin:15vh auto;padding:24px;color:#ddd;background:#111;border-radius:12px;text-align:center"><h2 style="margin-top:0">Unauthorized copy</h2><p>Strata Test Drive is © """ + OWNER + r""". All rights reserved. This copy is not allowed to run here.</p><p>Play the real game at <a style="color:#7cf" href="https://exclusive2knight.github.io/Strata-Test-Drive/">exclusive2knight.github.io/Strata-Test-Drive</a></p></div>';throw new Error("unauthorized host")}}
"""
body = (LOCK if lock else "") + js
wrapped = "(()=>{\n" + body + "\n})();"

tmp_in = os.path.join(HERE, "dist", "_in.js")
os.makedirs(os.path.dirname(tmp_in), exist_ok=True)
open(tmp_in, "w").write(wrapped)
out_js = subprocess.run([ESBUILD, tmp_in, "--minify", "--target=es2020", "--legal-comments=none", "--charset=utf8", "--log-level=warning"],
                        capture_output=True, text=True)
os.remove(tmp_in)
if out_js.returncode:
    sys.exit(out_js.stderr)
mini = out_js.stdout.replace("</script", "<\\/script")

banner = "<!-- Strata Test Drive. Copyright (c) 2026 " + OWNER + ". All rights reserved. Copying, re-hosting or modifying this game is not permitted. -->\n"
strip = lambda t: re.sub(r"<!--(?!\[).*?-->", "", t, flags=re.S)  # strip HTML comments
html = strip(src[:spans[0][0]]) + "<script>" + mini + "</script>" + strip(src[spans[-1][1]:])
html = html.replace("<!DOCTYPE html>", "<!DOCTYPE html>\n" + banner, 1) if "<!DOCTYPE html>" in html else banner + html
out = os.path.join(HERE, "index.html") if lock else os.path.join(HERE, "dist", "artifact.html")
open(out, "w").write(html)
print(out, os.path.getsize(out) // 1024, "KB", "(site lock on)" if lock else "(no site lock)")
