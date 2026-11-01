"""Move front seats back where an imported model put them so far forward that the driver's eye ends up
behind the headrest (the zip imports place the seat cushion right under the steering wheel).
usage: python3 tools/fix_seats.py [--write] model_key ...   (no keys = scan every model)"""
import json, base64, glob, os, sys
import numpy as np
GAP = 0.15        # headrest front this far behind the eye, like the older models

def load(o):
    P = np.frombuffer(base64.b64decode(o['p']), '<i2').reshape(-1, 3).astype(np.int32)
    I = np.frombuffer(base64.b64decode(o['i']), '<u2').reshape(-1, 3).astype(np.int64)
    return P, I

def comps(P, I):
    _, pid = np.unique(P, axis=0, return_inverse=True); pid = pid.ravel()
    par = np.arange(pid.max() + 1)
    def f(a):
        while par[a] != a: par[a] = par[par[a]]; a = par[a]
        return a
    for t in I:
        a = f(pid[t[0]]); par[f(pid[t[1]])] = a; par[f(pid[t[2]])] = a
    root = np.array([f(x) for x in range(len(par))])
    return root[pid]

def plan(d):
    m = d['meta']; E = m['eye']; S = m['steer']
    P, I = load(d['objects']['cabin']); cid = comps(P, I); X = P / 1000.0
    info = {}
    for c in np.unique(cid):
        v = X[cid == c]; info[c] = (v.min(0), v.max(0))
    def seatlike(lo, hi, side):
        sz = hi - lo; cx = (lo[0] + hi[0]) / 2; cz = (lo[2] + hi[2]) / 2
        return (0.06 <= sz.max() <= 0.9 and 0.12 < abs(cx) < 0.8 and cx * side > 0 and lo[2] > S[2] - 0.12
                and cz > S[2] + 0.05 and hi[2] < E[2] + 0.6 and hi[1] <= E[1] + 0.15 and lo[1] <= E[1] + 0.05)
    side = 1 if E[0] > 0 else -1
    drv = [c for c, (lo, hi) in info.items() if seatlike(lo, hi, side)]
    pas = [c for c, (lo, hi) in info.items() if seatlike(lo, hi, -side)]
    if not drv: return None
    top = max(drv, key=lambda c: info[c][1][1])
    dz = round(E[2] + GAP - info[top][0][2], 3)
    if dz <= GAP + 0.01: return dict(dz=0)   # only where the eye sits behind the headrest
    moved = set(drv) | set(pas)
    zmax = max(info[c][1][2] for c in moved)
    # what sits behind the front seats (rear seats, cab back wall): don't push the seats into it
    behind = [info[c][0][2] for c, (lo, hi) in info.items() if c not in moved and 0.1 < abs((lo[0] + hi[0]) / 2) < 0.8
              and lo[2] > zmax - 0.02 and lo[1] < E[1] and hi[1] > E[1] - 0.6 and (hi - lo).max() > 0.15]
    room = (min(behind) - zmax - 0.05) if behind else 9
    return dict(dz=dz, room=round(float(room), 3), cid=cid, moved=moved, n=len(moved))

def apply(d, p):
    o = d['objects']['cabin']; P, I = load(o); mask = np.isin(p['cid'], list(p['moved']))
    dz = min(p['dz'], max(0.0, p['room'])) if p['room'] < 9 else p['dz']
    P = P.copy(); P[mask, 2] += int(round(dz * 1000))
    o['p'] = base64.b64encode(np.ascontiguousarray(P, dtype='<i2').tobytes()).decode()
    m = d['meta']
    # front-row seat anchors move with the seats, unless they were only the importer's guess (eye + 8 cm)
    if m.get('seats') and abs(min(s[2] for s in m['seats']) - (m['eye'][2] + 0.08)) > 0.012:
        z0 = min(s[2] for s in m['seats'])
        for s in m['seats']:
            if abs(s[2] - z0) < 0.05: s[2] = round(s[2] + dz, 3)
    return dz

if __name__ == '__main__':
    write = '--write' in sys.argv; keys = [a for a in sys.argv[1:] if not a.startswith('--')]
    files = [f'models/{k}.json' for k in keys] or sorted(glob.glob('models/*.json'))
    for f in files:
        d = json.load(open(f)); m = d.get('meta', {})
        if 'eye' not in m or 'steer' not in m or 'cabin' not in d['objects']: continue
        p = plan(d); k = os.path.basename(f)[:-5]
        if not p or not p['dz']: continue
        line = f"{k:30s} move seats back {p['dz']:.2f} m (room behind {p['room']:.2f}, {p['n']} parts)"
        if write:
            dz = apply(d, p); json.dump(d, open(f, 'w'), separators=(',', ':')); line += f" -> moved {dz:.2f}"
        print(line)
