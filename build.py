"""Build the game: src/app_template.html + src/mesh_data.js -> dev.html (readable), then tools/protect.py -> index.html (published, locked).
Car models already live in models/<key>.json; this only lists them."""
import glob, json, os
here = os.path.dirname(os.path.abspath(__file__))
t = open(os.path.join(here, "src", "app_template.html")).read()
m = open(os.path.join(here, "src", "mesh_data.js")).read()
keys = sorted(os.path.splitext(os.path.basename(f))[0] for f in glob.glob(os.path.join(here, "models", "*.json")))
models = "const MODELS={};\nconst MODEL_LIST=" + json.dumps(keys) + ";\n"
html = t.replace("/*MESH_DATA*/", m + models)
html = html.replace("<title>Strata Test Drive</title>", '<title>Strata Test Drive</title><meta name="description" content="Strata Test Drive: a realistic driving simulator in your browser with real cars, drive modes, suspension, a city, freeway and traffic.">', 1)
out = os.path.join(here, "dev.html"); open(out, "w").write(html)
print(out, os.path.getsize(out) // 1024, "KB,", len(keys), "car models  (readable build for tests, not published)")
# the published builds are minified and site-locked: index.html (GitHub Pages) and dist/artifact.html (private Claude artifact, no lock)
import subprocess, sys
for a in ([], ["--nolock"]):
    r = subprocess.run([sys.executable, os.path.join(here, "tools", "protect.py")] + a)
    if r.returncode: sys.exit(r.returncode)
