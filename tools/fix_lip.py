"""Turn the flat plate some imported models have sticking out under the front bumper into a real-looking lip:
thin, tucked under the bumper, sticking out a few cm and following the bumper's curve.
usage: python3 tools/fix_lip.py model_key[:protrude_m] ...   (adds --dry to only report)"""
import json, base64, sys
import numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from fix_seats import load, comps

def fix(d, prot=0.035, thick=0.022, depth=0.12):
    o = d['objects']['body']; P, I = load(o); X = P / 1000.0; cid = comps(P, I)
    mat = np.empty(len(P), object)
    for g in o['g']: mat[I.ravel()[g[1]:g[1] + g[2]]] = g[0]
    paint = mat == 'strata_paint'; zmin = X[:, 2].min()
    lip = None
    for c in np.unique(cid):
        sel = cid == c; v = X[sel]; lo, hi = v.min(0), v.max(0)
        if paint[sel].any() or lo[2] > zmin + 0.02: continue
        if hi[1] - lo[1] < 0.09 and hi[2] - lo[2] > 0.15 and hi[0] - lo[0] > 1.0: lip = sel; break
    if lip is None: return None
    pf = paint & (X[:, 2] < X[paint, 2].min() + 0.3)
    ybot = X[pf, 1].min()
    band = pf & (X[:, 1] < ybot + 0.10)
    hw = np.abs(X[band & (X[:, 1] < ybot + 0.05), 0]).max() * 0.96
    # bumper front line along x
    bins = np.arange(-hw, hw + 0.04, 0.04); zf = []
    for b in bins:
        s = band & (np.abs(X[:, 0] - b) < 0.03)
        zf.append(X[s, 2].min() if s.any() else np.nan)
    zf = np.array(zf); ok = ~np.isnan(zf); zf = np.interp(bins, bins[ok], zf[ok])
    L = X[lip]; lo, hi = L.min(0), L.max(0)
    # rebuild it as a strip that follows the bumper (the original is a box with vertices only at its ends)
    n = 28; xs = np.linspace(-hw, hw, n + 1)
    edge = np.clip((np.abs(xs) - (hw - 0.14)) / 0.14, 0, 1) ** 1.5          # ends sweep back into the bumper corners
    zfr = np.interp(xs, bins, zf) - prot * (1 - edge) + edge * 0.02
    ytop = ybot + 0.006 + edge * 0.01
    # cross-section, front to back: lower front edge (turned down a touch), upper front edge, top back, bottom back
    sec = lambda i: [(zfr[i], ytop[i] - thick - 0.004), (zfr[i] - 0.004, ytop[i] - 0.006), (zfr[i] + depth, ytop[i]), (zfr[i] + depth, ytop[i] - thick)]
    V, T = [], []
    def quad(a, b, c, d):   # flat-shaded quad, a b c d counter-clockwise seen from outside
        nrm = np.cross(np.subtract(b, a), np.subtract(d, a)); l = np.linalg.norm(nrm) or 1; nrm = nrm / l
        k = len(V); V.extend([(p, nrm) for p in (a, b, c, d)]); T.extend([(k, k + 1, k + 2), (k, k + 2, k + 3)])
    for i in range(n):
        A = [(xs[i], y, z) for z, y in sec(i)]; B = [(xs[i + 1], y, z) for z, y in sec(i + 1)]
        for j in range(4):
            j2 = (j + 1) % 4; quad(A[j], B[j], B[j2], A[j2])
    for i, sgn in ((0, -1), (n, 1)):
        C = [(xs[i], y, z) for z, y in sec(i)]
        quad(*C) if sgn < 0 else quad(*C[::-1])
    # check outward orientation using the strip's centre: flip any face whose normal points inward
    cen = np.array([0, ybot - thick / 2, np.interp(0, bins, zf) + depth / 2])
    for t in range(0, len(T), 2):
        a, b, c = T[t]; p = np.array(V[a][0]); nm = V[a][1]
        mid = np.mean([V[q][0] for q in (a, b, c)], axis=0); out = mid - np.array([mid[0] * (abs(nm[0]) < 0.5), cen[1], cen[2]]) if abs(nm[0]) < 0.5 else np.array([np.sign(mid[0]), 0, 0])
        if np.dot(nm, out) < 0:
            for q in (t, t + 1): T[q] = T[q][::-1]
            for q in range(a, a + 4): V[q] = (V[q][0], -V[q][1])
    # write the body back: old triangles minus the lip, the new strip in the lip's material group
    N8 = np.frombuffer(base64.b64decode(o['n']), '<i1').reshape(-1, 3)
    lipv = set(np.nonzero(lip)[0].tolist()); base = len(P)
    newP = np.vstack([X, np.array([v[0] for v in V])]); newN = np.vstack([N8, np.clip(np.round(np.array([v[1] for v in V]) * 127), -127, 127)])
    lipmat = mat[np.nonzero(lip)[0][0]]; Iflat = I.ravel(); groups, outI = [], []
    for g in o['g']:
        tri = Iflat[g[1]:g[1] + g[2]].reshape(-1, 3); tri = [t for t in tri.tolist() if t[0] not in lipv]
        if g[0] == lipmat: tri += [[base + a, base + b, base + c] for a, b, c in T]
        groups.append([g[0], len(outI), len(tri) * 3]); outI.extend(sum(tri, []))
    assert len(newP) < 65536
    enc = lambda a, dt: base64.b64encode(np.ascontiguousarray(a, dtype=dt).tobytes()).decode()
    o['p'] = enc(np.round(newP * 1000), '<i2'); o['n'] = enc(newN, '<i1'); o['i'] = enc(np.array(outI), '<u2'); o['g'] = groups
    N = newP[base:]
    return dict(before=(lo.round(3).tolist(), hi.round(3).tolist()), after=(N.min(0).round(3).tolist(), N.max(0).round(3).tolist()), ybot=round(float(ybot), 3))

if __name__ == '__main__':
    for a in sys.argv[1:]:
        if a.startswith('--'): continue
        k, _, pr = a.partition(':'); f = f'models/{k}.json'; d = json.load(open(f))
        r = fix(d, prot=float(pr) if pr else 0.035); print(k, r)
        if r and '--dry' not in sys.argv: json.dump(d, open(f, 'w'), separators=(',', ':'))
