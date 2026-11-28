"""Build the game: src/app_template.html + src/mesh_data.js -> dev.html (readable), then tools/protect.py -> index.html (published, locked).
Car models already live in models/<key>.json; this only lists them."""
import glob, json, os
here = os.path.dirname(os.path.abspath(__file__))
t = open(os.path.join(here, "src", "app_template.html")).read()
m = open(os.path.join(here, "src", "mesh_data.js")).read()
keys = sorted(os.path.splitext(os.path.basename(f))[0] for f in glob.glob(os.path.join(here, "models", "*.json")))
models = "const MODELS={};\nconst MODEL_LIST=" + json.dumps(keys) + ";\n"
html = t.replace("/*MESH_DATA*/", m + models)
# the artifact copy fetches models and props from jsDelivr: pin them to the last commit that changed them (a branch name like @main is
# cached by the CDN for hours, so new and updated cars wouldn't show up); commit models/props first, then build
import subprocess as _sp
try: ref = _sp.run(["git", "-C", here, "log", "-1", "--format=%H", "--", "models", "props", "acc_out", "sounds"], capture_output=True, text=True).stdout.strip()
except Exception: ref = ""
import os as _os
if _os.path.exists("props/kitmap.json"):
    import json as _json
    _k = _json.load(open("props/kitmap.json"))
    html = html.replace("/*KIT_MAP*/null", _json.dumps({"nodes": _k["nodes"], "edges": _k["edges"], "place": _k["place"]}, separators=(",", ":")))
if _os.path.exists("props/kitold.json"):
    _kj = json.load(open("props/kitold.json")).get("kj", [])
    _j = [round(v, 2) for q in _kj for v in q]
    html = html.replace("/*KIT_J*/[]", json.dumps(_j, separators=(",", ":")))
    _kn = json.load(open("props/kitold.json")).get("knet")
    html = html.replace("/*KIT_NET*/null", json.dumps(_kn, separators=(",", ":")) if _kn else "null")
if _os.path.exists("props/weights.json"):
    html = html.replace("/*WEIGHTS*/{}", open("props/weights.json").read())
html=html.replace("/*TRAFFIC_MIND*/", open(os.path.join(here,"traffic","mind.js")).read()+"\n"+open(os.path.join(here,"traffic","park.js")).read())
html = html.replace("@/*ASSET_REF*/main/", "@" + (ref or "main") + "/")
html = html.replace("<title>Mission Strata</title>", '<title>Mission Strata</title><meta name="description" content="Mission Strata: a realistic driving simulator in your browser with real cars, drive modes, suspension, a city, freeway and traffic.">', 1)
out = os.path.join(here, "dev.html"); open(out, "w").write(html)
print(out, os.path.getsize(out) // 1024, "KB,", len(keys), "car models  (readable build for tests, not published)")
# the published builds are minified and site-locked: index.html (GitHub Pages) and dist/artifact.html (private Claude artifact, no lock)
import subprocess, sys
for a in ([], ["--nolock"]):
    r = subprocess.run([sys.executable, os.path.join(here, "tools", "protect.py")] + a)
    if r.returncode: sys.exit(r.returncode)
