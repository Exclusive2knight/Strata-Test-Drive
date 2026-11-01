"""Fix body panels that face inward in imported models (the lighting hits them from behind, so the paint
looks grey or dark in patches). Per connected piece: make the triangle winding consistent across shared
edges, then point the whole piece outward (closed pieces by signed volume, open sheets by facing away
from the car's centre). Stored normals are flipped with their triangles.
usage: python3 tools/fix_normals.py [--write] key ...   (no keys = report every model)"""
import json, base64, glob, os, sys
from collections import deque, defaultdict
import numpy as np


def dec(o):
    P = np.frombuffer(base64.b64decode(o['p']), '<i2').reshape(-1, 3).astype(np.int32)
    N = np.frombuffer(base64.b64decode(o['n']), '<i1').reshape(-1, 3).astype(np.int16)
    I = np.frombuffer(base64.b64decode(o['i']), '<u2').reshape(-1, 3).astype(np.int64)
    return P, N, I


def inward_share(P, I, L):
    X = P / 1000.0; A, B, C = X[I[:, 0]], X[I[:, 1]], X[I[:, 2]]
    fn = np.cross(B - A, C - A); ar = np.linalg.norm(fn, axis=1); c = (A + B + C) / 3
    out = c - np.stack([np.zeros(len(c)), np.full(len(c), 0.8), np.clip(c[:, 2], -L / 2 + 0.9, L / 2 - 0.9)], 1)
    return float((ar * ((fn * out).sum(1) < 0)).sum() / max(ar.sum(), 1e-9))


def plan(P, I, L):
    X = P / 1000.0; nT = len(I)
    _, pid = np.unique(P, axis=0, return_inverse=True); pid = pid.ravel()
    T = pid[I]                                       # triangles over welded positions
    edges = defaultdict(list)
    for t in range(nT):
        a, b, c = T[t]
        for u, v in ((a, b), (b, c), (c, a)):
            if u != v: edges[(min(u, v), max(u, v))].append((t, u, v))
    flip = np.zeros(nT, bool); seen = np.zeros(nT, bool); comp = np.full(nT, -1)
    nb = defaultdict(list)
    for lst in edges.values():
        if len(lst) == 2:
            (t1, u1, v1), (t2, u2, v2) = lst
            same = (u1 == u2)                        # same direction along the edge = opposite winding
            nb[t1].append((t2, same)); nb[t2].append((t1, same))
    ci = 0
    for s in range(nT):
        if seen[s]: continue
        q = deque([s]); seen[s] = True; comp[s] = ci
        while q:
            t = q.popleft()
            for t2, same in nb[t]:
                if not seen[t2]:
                    seen[t2] = True; comp[t2] = ci; flip[t2] = flip[t] ^ same; q.append(t2)
        ci += 1
    W = I.copy(); W[flip] = W[flip][:, [0, 2, 1]]
    A, B, C = X[W[:, 0]], X[W[:, 1]], X[W[:, 2]]
    fn = np.cross(B - A, C - A); ar = np.linalg.norm(fn, axis=1) / 2; cen = (A + B + C) / 3
    vol = (A * np.cross(B, C)).sum(1) / 6           # signed volume per triangle
    out = cen - np.stack([np.zeros(nT), np.full(nT, 0.8), np.clip(cen[:, 2], -L / 2 + 0.9, L / 2 - 0.9)], 1)
    dp = (fn * out).sum(1)
    # is each piece closed (every edge shared by exactly two of its triangles)?
    openc = set()
    for lst in edges.values():
        if len(lst) == 1: openc.add(comp[lst[0][0]])
    for c in range(ci):
        s = comp == c
        if c in openc:
            bad = (ar[s] * np.sign(dp[s])).sum() < 0
        else:
            v = vol[s].sum(); bad = v < 0 if abs(v) > 1e-7 else (ar[s] * np.sign(dp[s])).sum() < 0
        if bad: flip[s] ^= True
    return flip


def fix(o, L):
    """per material: keep the re-orientation only where it clearly turns that material's panels outward"""
    P, N, I = dec(o); flip = np.zeros(len(I), bool)
    for g in o['g']:
        a, b = g[1] // 3, (g[1] + g[2]) // 3
        if b - a < 4: continue
        sub = I[a:b]; f = plan(P, sub, L); W = sub.copy(); W[f] = W[f][:, [0, 2, 1]]
        if inward_share(P, sub, L) - inward_share(P, W, L) > 0.1: flip[a:b] = f
    if not flip.any(): return 0, 0
    nT = len(I)
    # flip the triangles; a vertex used only by flipped triangles gets its normal negated,
    # one used by both kinds is split
    use = defaultdict(set)
    for t in range(nT):
        for v in I[t]: use[int(v)].add(bool(flip[t]))
    P2, N2 = [P], [N]; extra = {}; nV = len(P); NN = N.copy()
    for v, kinds in use.items():
        if kinds == {True}: NN[v] = -N[v]
    newP, newN = [], []
    I2 = I.copy()
    for t in np.nonzero(flip)[0]:
        for j in range(3):
            v = int(I[t, j])
            if use[v] == {True, False}:
                if v not in extra:
                    extra[v] = nV + len(newP); newP.append(P[v]); newN.append(-N[v])
                I2[t, j] = extra[v]
    I2[flip] = I2[flip][:, [0, 2, 1]]
    P3 = np.vstack([P] + ([np.array(newP)] if newP else [])); N3 = np.vstack([NN] + ([np.array(newN)] if newN else []))
    assert len(P3) < 65536
    enc = lambda a, dt: base64.b64encode(np.ascontiguousarray(a, dtype=dt).tobytes()).decode()
    o['p'] = enc(P3, '<i2'); o['n'] = enc(N3, '<i1'); o['i'] = enc(I2.ravel(), '<u2')
    return int(flip.sum()), len(newP)


if __name__ == '__main__':
    write = '--write' in sys.argv; keys = [a for a in sys.argv[1:] if not a.startswith('--')]
    for f in ([f'models/{k}.json' for k in keys] or sorted(glob.glob('models/*.json'))):
        d = json.load(open(f))
        if 'objects' not in d or 'body' not in d['objects'] or 'meta' not in d: continue
        L = d['meta'].get('length', 4.8); o = d['objects']['body']; P, N, I = dec(o)
        before = inward_share(P, I, L); k = os.path.basename(f)[:-5]
        if not keys and before < 0.2: continue
        nf, ns = fix(o, L); P, N, I = dec(o); after = inward_share(P, I, L)
        print(f"{k:30s} inward {before:.2f} -> {after:.2f}  ({nf} triangles flipped, {ns} vertices split)")
        if write: json.dump(d, open(f, 'w'), separators=(',', ':'))
