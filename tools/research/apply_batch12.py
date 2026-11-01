"""Apply batch 12 (Range Rover, Range Rover Sport, Velar, Evoque, Lincoln Navigator) to src/app_template.html. Re-runnable."""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
tmp = "/tmp/b12.json"; subprocess.run([sys.executable, os.path.join(HERE, "new_batch12.py"), tmp], check=True)
B = json.load(open(tmp)); keys = set(B["keys"])
p = os.path.join(ROOT, "src", "app_template.html"); s = open(p).read()
lines = s.split("\n"); pat = re.compile(r'^ add\("([a-z0-9_]+)"')
lines = [l for l in lines if not (pat.match(l) and pat.match(l).group(1) in keys)]
last = max(i for i, l in enumerate(lines) if pat.match(l))
lines[last + 1:last + 1] = B["adds"]
s = "\n".join(lines)
def merge(prefix, upd):
    global s
    i = s.index(prefix); j = s.index("\n", i); body = s[i + len(prefix):j].rstrip().rstrip(";")
    D = json.loads(body); D.update(upd); s = s[:i] + prefix + json.dumps(D, separators=(",", ":")) + ";" + s[j:]
merge("const DMODES=", B["dmodes"]); merge("const SUSR=", B["susr"]); merge("var BDATA=", B["bdata"])
a = 'const LAZY=new Set(["q5_25",'
if '"rr_rangerover"' not in s[s.index(a):s.index(a) + 3000]: s = s.replace(a, 'const LAZY=new Set(["rr_rangerover","rr_sport","rr_velar","rr_evoque","lin_navigator","q5_25",', 1)
open(p, "w").write(s); print("applied", len(B["adds"]), "trims")
