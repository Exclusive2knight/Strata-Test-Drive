"""Apply batch 11 (Genesis / Chevrolet / Nissan full lineups + 2022 F-150) to src/app_template.html."""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import f150_22
tmp = "/tmp/b11.json"; subprocess.run([sys.executable, os.path.join(HERE, "new_batch11.py"), tmp], check=True)
B = json.load(open(tmp)); fa, fdm, fsu, fbd, fkeys = f150_22.build()
p = os.path.join(ROOT, "src", "app_template.html"); s = open(p).read()
lines = s.split("\n"); pat = re.compile(r'^ add\("(gen_|chv_bolt|chv_malibu|nissan_altima27|f150_22)'); idx = [i for i, l in enumerate(lines) if pat.match(l)]
assert idx, "batch 10 lines not found"
first = idx[0]; lines = [l for i, l in enumerate(lines) if i not in set(idx)]
lines[first:first] = B["adds"] + fa
s = "\n".join(lines)
def merge(prefix, upd):
    global s
    i = s.index(prefix); j = s.index("\n", i); body = s[i + len(prefix):j].rstrip().rstrip(";")
    D = json.loads(body); D.update(upd); s = s[:i] + prefix + json.dumps(D, separators=(",", ":")) + ";" + s[j:]
merge("const DMODES=", {**B["dmodes"], **fdm}); merge("const SUSR=", {**B["susr"], **fsu}); merge("var BDATA=", {**B["bdata"], **fbd})
a = 'const LAZY=new Set(["gen_g70",'
if a in s: s = s.replace(a, 'const LAZY=new Set(["f150_22","gen_g70",', 1)
open(p, "w").write(s); print("applied", len(B["adds"]) + len(fa), "trims")
