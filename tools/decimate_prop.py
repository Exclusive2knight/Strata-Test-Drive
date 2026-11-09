"""Lighten a prop: vertex-cluster each material group to a grid (cell in metres), keeping the materials.
   python3 tools/decimate_prop.py props/<key>.json cell [out.json]"""
import json, sys, base64
import numpy as np
src = sys.argv[1]; cell = float(sys.argv[2]); out = sys.argv[3] if len(sys.argv) > 3 else src
d = json.load(open(src))
t0 = t1 = 0
for k, o in d['objects'].items():
    P = np.frombuffer(base64.b64decode(o['p']), '<i2').reshape(-1, 3).astype(float) / 1000
    N = np.frombuffer(base64.b64decode(o['n']), 'i1').reshape(-1, 3).astype(float) / 127
    I = np.frombuffer(base64.b64decode(o['i']), '<u2').astype(np.int64)
    # merge runs of the same material, then cluster each material on its own
    bym = {}
    for mi, st, cnt in o['g']: bym.setdefault(mi, []).append(I[st:st + cnt])
    nP, nN, nI, g = [], [], [], []; nv = 0; ni = 0
    for mi, parts in bym.items():
        T = np.concatenate(parts).reshape(-1, 3); t0 += len(T)
        u = np.unique(T); rm = -np.ones(len(P), np.int64); rm[u] = np.arange(len(u)); Pl = P[u]; Nl = N[u]; T = rm[T]
        key = np.floor(Pl / cell).astype(np.int64)
        # split clusters by normal direction too so hard edges survive
        nk = np.round(Nl * 1.5).astype(np.int64)
        _, inv = np.unique(np.concatenate([key, nk], 1), axis=0, return_inverse=True); inv = inv.reshape(-1)
        m = inv.max() + 1; Pc = np.zeros((m, 3)); Nc = np.zeros((m, 3)); c = np.zeros(m)
        np.add.at(Pc, inv, Pl); np.add.at(Nc, inv, Nl); np.add.at(c, inv, 1); Pc /= c[:, None]
        Nc /= np.maximum(1e-9, np.linalg.norm(Nc, axis=1))[:, None]
        T = inv[T]; ok = (T[:, 0] != T[:, 1]) & (T[:, 1] != T[:, 2]) & (T[:, 0] != T[:, 2]); T = T[ok]
        if not len(T): continue
        _, ix = np.unique(np.sort(T, 1), axis=0, return_index=True); T = T[np.sort(ix)]
        uu = np.unique(T); r2 = -np.ones(m, np.int64); r2[uu] = np.arange(len(uu)); T = r2[T]
        if nv + len(uu) > 65000: raise SystemExit('too many vertices after clustering; use a bigger cell')
        nP.append(Pc[uu]); nN.append(Nc[uu]); nI.append(T.reshape(-1) + nv); g.append([mi, ni, len(T) * 3]); nv += len(uu); ni += len(T) * 3; t1 += len(T)
    o['p'] = base64.b64encode(np.round(np.concatenate(nP) * 1000).astype('<i2').tobytes()).decode()
    o['n'] = base64.b64encode(np.clip(np.round(np.concatenate(nN) * 127), -127, 127).astype('i1').tobytes()).decode()
    o['i'] = base64.b64encode(np.concatenate(nI).astype('<u2').tobytes()).decode(); o['g'] = g
json.dump(d, open(out, 'w'), separators=(',', ':'))
print(src, 'tris', t0, '->', t1)
