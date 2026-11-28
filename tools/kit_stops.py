"""Where each kit junction piece paints its stop bars: for every leg, the distance from the piece's centre to the stop bar across its
incoming lanes (texture, not geometry, so the road surface is rasterised with its atlas UVs and scanned along each lane).

    python3 tools/kit_stops.py <roadkit folder> piece... > tools/kitmaps/stops.json
"""
import sys, os, json, math
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from kit_pack import piece
from PIL import Image
root = sys.argv[1]; man = {p["name"]: p for p in json.load(open(os.path.join(root, "manifest.json")))["pieces"]}
A = np.asarray(Image.open(os.path.join(root, "textures", "road_atlas.jpg")).convert("L"), dtype=np.float32); AH, AW = A.shape
RES = 0.1
# lane centres right of a leg's centre line for traffic coming in (kit cross sections)
INL = {"CITY2": [1.95], "CITY4": [1.8, 5.25], "CITY5": [3.75, 7.2], "BLVD6D": [9.0, 12.6, 16.2], "CITY6D": [4.2, 7.65, 11.1],
       "RES2": [1.9], "RES2P": [1.6], "RURAL2": [1.9], "ONEWAY3": [-3.4, 0.0, 3.4], "SVC3": [-3.4, 0.0, 3.4], "CITY8D": [4.2, 7.8, 11.4, 15.0]}
out = {}
for name in sys.argv[2:]:
    d = piece(os.path.join(root, man[name]["file"])); P = np.array(d["p"], dtype=np.float32).reshape(-1, 3) / 100; T = np.array(d["t"], dtype=np.float32).reshape(-1, 2) / 10000; I = np.array(d["i"]).reshape(-1, 3)
    x0, z0 = P[:, 0].min(), P[:, 2].min(); W = int((P[:, 0].max() - x0) / RES) + 2; H = int((P[:, 2].max() - z0) / RES) + 2
    img = np.zeros((H, W), np.float32); top = np.full((H, W), -9.0, np.float32)
    for tri in I:
        p = P[tri]; t = T[tri]
        if p[:, 1].max() > 0.05 or p[:, 1].min() < -0.05: continue       # the road surface only
        xs = (p[:, 0] - x0) / RES; zs = (p[:, 2] - z0) / RES
        a, b = int(max(0, xs.min())), int(min(W - 1, xs.max() + 1)); c, e = int(max(0, zs.min())), int(min(H - 1, zs.max() + 1))
        if b < a or e < c: continue
        gx, gz = np.meshgrid(np.arange(a, b + 1) + 0.5, np.arange(c, e + 1) + 0.5)
        den = (zs[1] - zs[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (zs[0] - zs[2])
        if abs(den) < 1e-9: continue
        l0 = ((zs[1] - zs[2]) * (gx - xs[2]) + (xs[2] - xs[1]) * (gz - zs[2])) / den; l1 = ((zs[2] - zs[0]) * (gx - xs[2]) + (xs[0] - xs[2]) * (gz - zs[2])) / den; l2 = 1 - l0 - l1
        m = (l0 >= -1e-4) & (l1 >= -1e-4) & (l2 >= -1e-4)
        if not m.any(): continue
        u = l0 * t[0, 0] + l1 * t[1, 0] + l2 * t[2, 0]; v = l0 * t[0, 1] + l1 * t[1, 1] + l2 * t[2, 1]
        ui = np.clip((u * AW).astype(int), 0, AW - 1); vi = np.clip(((v % 1.0) * AH).astype(int), 0, AH - 1)
        img[c:e + 1, a:b + 1][m] = A[vi, ui][m]
    res = {}
    for cn in man[name]["connectors"]:
        if not cn["name"].startswith("leg_"): continue
        L = math.hypot(cn["pos"][0], cn["pos"][2]); hx, hz = cn["pos"][0] / L, cn["pos"][2] / L      # out along the leg
        rx, rz = hz, -hx                     # right of traffic coming IN (travelling -h): kit X right of -Z
        best = None
        for s in np.arange(L - 0.5, 3.0, -RES):
            ok = 0
            for off in INL.get(cn["profile"], [1.9]):
                px, pz = hx * s + rx * off, hz * s + rz * off
                i, j = int((px - x0) / RES), int((pz - z0) / RES)
                if 0 <= j < H and 0 <= i < W and img[j, i] > 200: ok += 1
            if ok == len(INL.get(cn["profile"], [1.9])): best = round(float(s), 2); break
        res[cn["name"]] = best
    out[name] = res
    print(name, res, file=sys.stderr)
print(json.dumps(out))
