"""Set every model's driver eye height from its own cabin: a little above the dash top (so you see over it),
under the sun visor / windshield header and far enough under the roof that your head fits.
Writes meta.eye[1] and meta.eyeFit=1 (normEye then trusts it).  usage: python3 tools/fix_eye.py [--write] [keys]"""
import json, base64, glob, os, re, sys
import numpy as np
ABOVE_DASH = 0.14   # eye this far over the highest bit of dash in front of you
HEAD = 0.14         # roof at least this far over the eye (head top is ~0.12 above the eyes)
GL = re.compile(r'glass|screen|emi_|headlight|taillight|signal|reverse', re.I)

def pts(o, glass=False):
    P = np.frombuffer(base64.b64decode(o['p']), '<i2').reshape(-1, 3) / 1000.0
    I = np.frombuffer(base64.b64decode(o['i']), '<u2'); keep = np.zeros(len(P), bool)
    for g in o['g']:
        if glass or not GL.search(str(g[0])): keep[I[g[1]:g[1] + g[2]]] = True
    return P[keep]

def fit(d):
    m = d['meta']; E = m['eye']; S = m['steer']
    if 'cabin' not in d['objects']: return None
    ex = E[0]; ez = S[2] + min(max(E[2] - S[2], 0.3), 0.62)
    x, y, z = pts(d['objects']['cabin']).T
    s = (abs(x - S[0]) < 0.25) & (z < S[2] - 0.05) & (z > S[2] - 0.75) & (y < S[1] + 0.5) & (y > S[1] - 0.2)
    if s.sum() < 20: return None
    dash = float(np.percentile(y[s], 99.7))
    if dash > S[1] + 0.42: return None
    A = np.concatenate([pts(d['objects'][k]) for k in ('body', 'cabin') if k in d['objects']]); x, y, z = A.T
    h = (abs(x - ex) < 0.2) & (z > ez - 0.8) & (z < ez - 0.2) & (y > dash + 0.06)
    hdr = float(y[h].min()) if h.any() else 9.0
    if hdr < dash + 0.12: hdr = 9.0
    B = np.concatenate([pts(d['objects'][k], True) for k in ('body', 'cabin') if k in d['objects']]); x, y, z = B.T
    c = (abs(x - ex) < 0.12) & (abs(z - ez) < 0.08) & (y > S[1] + 0.2)
    roof = 9.0
    if c.any(): top = y[c].max(); roof = float(y[c & (y > top - 0.06)].min())
    ey = min(dash + ABOVE_DASH, hdr - 0.06, roof - HEAD)
    ey = max(ey, dash + 0.04, S[1] + 0.12)
    return dict(dash=dash, hdr=hdr, roof=roof, eye=round(ey, 3))

if __name__ == '__main__':
    write = '--write' in sys.argv; keys = [a for a in sys.argv[1:] if not a.startswith('--')]
    for f in ([f'models/{k}.json' for k in keys] or sorted(glob.glob('models/*.json'))):
        d = json.load(open(f)); m = d.get('meta') or {}
        if 'eye' not in m or 'steer' not in m: continue
        r = fit(d); k = os.path.basename(f)[:-5]
        if not r: print(f'{k:30s} no fit, kept'); continue
        S = m['steer']; old = S[1] + min(max(m['eye'][1] - S[1], 0.25), 0.36) if not m.get('eyeFit') else m['eye'][1]
        print(f"{k:30s} {old:.2f} -> {r['eye']:.2f}  (dash {r['dash']:.2f} visor {r['hdr']:.2f} roof {r['roof']:.2f})")
        if write: m['eye'][1] = r['eye']; m['eyeFit'] = 1; json.dump(d, open(f, 'w'), separators=(',', ':'))
