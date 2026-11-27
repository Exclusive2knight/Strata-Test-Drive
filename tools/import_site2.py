"""Textured building / garage GLB -> a driveable game site: props/site/<key>.json

    python3 tools/import_site2.py in.glb key [--cell 0.5] [--skip REGEX] [--clipz Z] [--texmax 1024] [--chunk 40] [--nowall REGEX]

Drawing: like import_tmodel (full transforms, GPU instancing, cropped shared textures in props/site/tx), chunked spatially.
Physics (model space, metres, +Y up):
  grid  - drivable floor LAYERS per cell (cm, int16, -32768 = none). Upward faces are rasterised; heights within 2 m in a cell
          are one floor (its lowest surface plus anything up to 0.35 m above it: kerbs, humps); a floor with another less than
          1.8 m above it is dropped (no headroom: the tops of ceiling fittings). So a garage gives roof / B1 / B2 / ramps.
  walls - boxes [x0,x1,z0,z1,y0,y1]: where something upright stands 0.3-1.5 m over a floor (walls, columns, kerbs of islands,
          posts), and round the edge of every floor more than 1 m underground (the garage's outer walls, the helix core).
--clipz drops everything with Z beyond it (the model's own street: the game draws its own there).
"""
import sys, os, io, re, json, base64, hashlib
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from glbscene import GLB, walk

a = sys.argv[1:]; src, key = a[0], a[1]
opt = {"cell": "0.5", "skip": None, "clipz": None, "texmax": "1024", "chunk": "40", "nowall": None, "texdir": "props/site/tx"}
i = 2
while i < len(a): opt[a[i][2:]] = a[i + 1]; i += 2
CELL = float(opt["cell"]); SKIP = re.compile(opt["skip"]) if opt["skip"] else None; CLIPZ = float(opt["clipz"]) if opt["clipz"] else None
NOWALL = re.compile(opt["nowall"]) if opt["nowall"] else None; TEXMAX = int(opt["texmax"]); CS = float(opt["chunk"])
G = GLB(src); J = G.J; W = walk(G); mats_src = J.get("materials", [])

by = {}; uvuse = {}; phys = []   # phys: (P world, I, nowall)
for ni, path, M, mi in W:
    nm = "/".join(path)
    if SKIP and any(SKIP.search(p) for p in path): continue
    for pr in J["meshes"][mi]["primitives"]:
        if pr.get("mode", 4) != 4: continue
        P = G.acc(pr["attributes"]["POSITION"]).astype(float); Pw = P @ M[:3, :3].T + M[:3, 3]
        I = (G.acc(pr["indices"]).reshape(-1).astype(np.int64) if "indices" in pr else np.arange(len(P))).reshape(-1, 3)
        if np.linalg.det(M[:3, :3]) < 0: I = I[:, ::-1]
        if CLIPZ is not None:
            keep = Pw[I][:, :, 2].mean(1) <= CLIPZ; I = I[keep]
            if not len(I): continue
        N = G.acc(pr["attributes"]["NORMAL"]).astype(float) @ np.linalg.inv(M[:3, :3]) if "NORMAL" in pr["attributes"] else np.zeros_like(Pw)
        nl = np.linalg.norm(N, axis=1, keepdims=True); nl[nl == 0] = 1; N = N / nl
        UV = G.acc(pr["attributes"]["TEXCOORD_0"]).astype(float) if "TEXCOORD_0" in pr["attributes"] else None
        m = pr.get("material", -1); by.setdefault(m, []).append((Pw, N, UV, I))
        phys.append((Pw, I, bool(NOWALL and NOWALL.search(nm)), N))
        if m >= 0 and UV is not None:
            pb = mats_src[m].get("pbrMetallicRoughness", {})
            if "baseColorTexture" in pb: uvuse.setdefault(J["textures"][pb["baseColorTexture"]["index"]]["source"], []).append(UV[np.unique(I)])

# ---- textures (cropped, scaled, shared by hash)
os.makedirs(opt["texdir"], exist_ok=True); tex = []; tex_of = {}; remap = {}
for img, L in uvuse.items():
    U = np.concatenate(L); raw, mime = G.img(img); im = Image.open(io.BytesIO(raw)); im.load(); w, h = im.size
    u0, v0 = U.min(0); u1, v1 = U.max(0); clamp = not (u0 < -0.01 or v0 < -0.01 or u1 > 1.01 or v1 > 1.01)
    if clamp: px0, py0, px1, py1 = max(0, int(np.floor(u0 * w)) - 3), max(0, int(np.floor(v0 * h)) - 3), min(w, int(np.ceil(u1 * w)) + 3), min(h, int(np.ceil(v1 * h)) + 3)
    else: px0, py0, px1, py1 = 0, 0, w, h
    crop = im.crop((px0, py0, px1, py1)); cw, ch = crop.size; s = min(1.0, TEXMAX / max(cw, ch))
    p2 = lambda v: 1 << max(2, int(round(np.log2(max(4, v)))))
    nw, nh = p2(cw * s), p2(ch * s)
    while max(nw, nh) > TEXMAX: nw, nh = max(4, nw // 2), max(4, nh // 2)
    crop = crop.resize((nw, nh), Image.LANCZOS); alpha = crop.mode in ("RGBA", "LA", "P") and crop.convert("RGBA").getextrema()[3][0] < 250
    bo = io.BytesIO()
    if alpha: crop.convert("RGBA").save(bo, "PNG", optimize=True); ext = "png"
    else: crop.convert("RGB").save(bo, "JPEG", quality=80); ext = "jpg"
    data = bo.getvalue(); hh = hashlib.md5(data).hexdigest()[:12]; fn = f"{opt['texdir']}/{hh}.{ext}"
    if not os.path.exists(fn): open(fn, "wb").write(data)
    tex_of[img] = len(tex); tex.append({"u": fn, "clamp": clamp}); remap[img] = (px0 / w, py0 / h, (px1 - px0) / w, (py1 - py0) / h)

mats = []; mat_of = {}
for m in by:
    M = mats_src[m] if m >= 0 else {"name": "default"}; pb = M.get("pbrMetallicRoughness", {}); c = pb.get("baseColorFactor", [0.8, 0.8, 0.8, 1])
    img = J["textures"][pb["baseColorTexture"]["index"]]["source"] if "baseColorTexture" in pb else None
    mat_of[m] = (len(mats), img)
    mats.append({"n": M.get("name", ""), "f": [round(v, 3) for v in c[:3]], "al": round(c[3], 3), "a": M.get("alphaMode", "OPAQUE"), "t": tex_of.get(img, -1) if img is not None else -1,
                 "e": [round(v, 3) for v in M.get("emissiveFactor", [0, 0, 0])], "m": round(pb.get("metallicFactor", 0), 2), "r": round(pb.get("roughnessFactor", 0.7), 2)})

out_m = {}; tris = 0; allP = []
for m, L in by.items():
    mi, img = mat_of[m]; rm = remap.get(img); cells = {}
    for P, N, UV, I in L:
        if UV is not None and rm: UV = UV.copy(); UV[:, 0] = (UV[:, 0] - rm[0]) / rm[2]; UV[:, 1] = (UV[:, 1] - rm[1]) / rm[3]
        c = P[I].mean(1); kk = np.floor(c[:, 0] / CS).astype(int) * 1000 + np.floor(c[:, 2] / CS).astype(int)
        for k in np.unique(kk):
            Ii = I[kk == k]; used = np.unique(Ii); r_ = -np.ones(len(P), np.int64); r_[used] = np.arange(len(used))
            cells.setdefault(int(k), []).append((P[used], N[used], UV[used] if UV is not None else None, r_[Ii])); allP.append(P[used])
    for k, ps in cells.items():
        cur = None; chunks = []
        for P, N, UV, I in ps:
            if cur is None or cur["nv"] + len(P) > 65000: cur = {"P": [], "N": [], "U": [], "I": [], "nv": 0}; chunks.append(cur)
            cur["I"].append(I + cur["nv"]); cur["P"].append(P); cur["N"].append(N); cur["U"].append(UV if UV is not None else np.zeros((len(P), 2))); cur["nv"] += len(P)
        for ch in chunks:
            P = np.concatenate(ch["P"]); N = np.concatenate(ch["N"]); U = np.concatenate(ch["U"]); I = np.concatenate(ch["I"]).reshape(-1)
            lo, hi = P.min(0), P.max(0); ctr = (lo + hi) / 2; ext = float(np.abs(P - ctr).max()) + 0.01; kq = min(1000.0, 32000.0 / ext)
            e = {"o": [round(float(v), 3) for v in ctr], "k": round(kq, 4), "p": base64.b64encode(np.round((P - ctr) * kq).astype("<i2").tobytes()).decode(),
                 "n": base64.b64encode(np.clip(np.round(N * 127), -127, 127).astype("i1").tobytes()).decode(), "i": base64.b64encode(I.astype("<u2").tobytes()).decode()}
            if mats[mi]["t"] >= 0:
                ur = float(np.abs(U).max()) + 1e-6; us = 4096.0 if ur < 7 else 32000.0 / ur; e["ts"] = round(us, 3)
                e["t"] = base64.b64encode(np.clip(np.round(U * us), -32767, 32767).astype("<i2").tobytes()).decode()
            out_m.setdefault(str(mi), []).append(e); tris += len(I) // 3
AP = np.concatenate(allP); BB = [AP.min(0), AP.max(0)]

# ---- physics grid
X0 = np.floor(BB[0][0]) - 1; Z0 = np.floor(BB[0][2]) - 1; X1 = np.ceil(BB[1][0]) + 1; Z1 = np.ceil(BB[1][2]) + 1
if CLIPZ is not None: Z1 = min(Z1, CLIPZ)
GW = int(np.ceil((X1 - X0) / CELL)); GH = int(np.ceil((Z1 - Z0) / CELL))
hs = [[[] for _ in range(GW)] for _ in range(GH)]
vert = []   # (i, j, ylo, yhi)
xs_c = X0 + (np.arange(GW) + 0.5) * CELL; zs_c = Z0 + (np.arange(GH) + 0.5) * CELL
for P, I, nowall, NV in phys:
    T = P[I]; n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); nl = np.linalg.norm(n, axis=1) + 1e-12; ny = n[:, 1] / nl
    vn = NV[I][:, :, 1].mean(1) if NV is not None and np.abs(NV).sum() > 0 else ny   # the model's own normals say which side is up (some parts are wound the other way)
    ny = np.where(np.abs(ny) > 0.72, np.sign(vn) * np.abs(ny), ny)
    for t, u in zip(T, ny):
        if u > 0.72:
            x0, x1 = t[:, 0].min(), t[:, 0].max(); z0, z1 = t[:, 2].min(), t[:, 2].max()
            i0, i1 = max(0, int((x0 - X0) / CELL)), min(GW - 1, int((x1 - X0) / CELL)); j0, j1 = max(0, int((z0 - Z0) / CELL)), min(GH - 1, int((z1 - Z0) / CELL))
            if i1 < i0 or j1 < j0: continue
            Xg, Zg = np.meshgrid(xs_c[i0:i1 + 1], zs_c[j0:j1 + 1]); (ax, ay, az), (bx, by_, bz), (cx, cy, cz) = t
            d = (bz - cz) * (ax - cx) + (cx - bx) * (az - cz)
            if abs(d) < 1e-12: continue
            l1 = ((bz - cz) * (Xg - cx) + (cx - bx) * (Zg - cz)) / d; l2 = ((cz - az) * (Xg - cx) + (ax - cx) * (Zg - cz)) / d; l3 = 1 - l1 - l2
            ins = (l1 >= -0.05) & (l2 >= -0.05) & (l3 >= -0.05); Y = l1 * ay + l2 * by_ + l3 * cy
            for jj, ii in zip(*np.nonzero(ins)): hs[j0 + jj][i0 + ii].append(float(Y[jj, ii]))
        elif abs(u) < 0.35 and not nowall:
            yl, yh = t[:, 1].min(), t[:, 1].max()
            if yh - yl < 0.12: continue
            for k in range(3):   # the triangle's footprint is a line: walk its edges
                A, B = t[k], t[(k + 1) % 3]; L_ = np.hypot(B[0] - A[0], B[2] - A[2]); ns = max(1, int(L_ / (CELL * 0.5)))
                for s in range(ns + 1):
                    f = s / ns; x = A[0] + (B[0] - A[0]) * f; z = A[2] + (B[2] - A[2]) * f
                    ii, jj = int((x - X0) / CELL), int((z - Z0) / CELL)
                    if 0 <= ii < GW and 0 <= jj < GH: vert.append((jj, ii, yl, yh))
LAY = 4; D = np.full((LAY, GH, GW), -32768, np.int16)
for j in range(GH):
    for i in range(GW):
        H = sorted(hs[j][i])
        if not H: continue
        # a surface is a floor if nothing lies 0.35-1.8 m over it (no room for a car: the drum under a helix ramp, the top of a ceiling light);
        # what is left within 0.35 m of each other (kerbs, humps on a lane) is one floor at its top
        H = sorted(set(round(v, 2) for v in H)); cand = [v for v in H if not any(v + 0.35 < w <= v + 1.8 for w in H)]; fl = []
        for v in cand:
            if fl and v - fl[-1] <= 0.35: fl[-1] = v
            else: fl.append(v)
        for L_, v in enumerate(fl[-LAY:]): D[L_, j, i] = int(round(v * 100))
# walls: upright things over a floor, and the edges of underground floors
wall = {}   # (j,i) -> list of (y0,y1)
for j, i, yl, yh in vert:
    for L_ in range(LAY):
        v = D[L_, j, i]
        if v == -32768: continue
        h = v / 100
        if yh > h + 0.3 and yl < h + 1.5: wall.setdefault((j, i), []).append((h + 0.05, h + 2.6))
for j in range(GH):
    for i in range(GW):
        for L_ in range(LAY):
            v = D[L_, j, i]
            if v == -32768 or v > -100: continue
            h = v / 100
            for dj, di in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                jj, ii = j + dj, i + di
                if not (0 <= jj < GH and 0 <= ii < GW): continue
                col = D[:, jj, ii]; ok = any(c != -32768 and abs(c / 100 - h) < 1.0 for c in col)
                if not ok: wall.setdefault((jj, ii), []).append((h + 0.05, h + 2.6))
# merge into boxes: by height band, greedy rectangles
bands = {}
for (j, i), L in wall.items():
    for y0, y1 in L:
        b = int(np.floor(y0 / 1.0)); bands.setdefault(b, set()).add((j, i))
boxes = []
for b, S in bands.items():
    S = set(S)
    while S:
        j, i = min(S); i1 = i
        while (j, i1 + 1) in S: i1 += 1
        j1 = j
        while all((j1 + 1, x) in S for x in range(i, i1 + 1)): j1 += 1
        for jj in range(j, j1 + 1):
            for ii in range(i, i1 + 1): S.discard((jj, ii))
        boxes.append([round(X0 + i * CELL, 2), round(X0 + (i1 + 1) * CELL, 2), round(Z0 + j * CELL, 2), round(Z0 + (j1 + 1) * CELL, 2), round(b * 1.0 - 0.05, 2), round(b * 1.0 + 3.6, 2)])
res = {"mats": mats, "tex": tex, "m": out_m, "bb": [[round(float(v), 2) for v in BB[0]], [round(float(v), 2) for v in BB[1]]],
       "grid": {"x0": float(X0), "z0": float(Z0), "s": CELL, "w": GW, "h": GH, "L": LAY, "d": base64.b64encode(D.astype("<i2").tobytes()).decode()}, "walls": boxes}
os.makedirs("props/site", exist_ok=True)
s = json.dumps(res, separators=(",", ":")); open(f"props/site/{key}.json", "w").write(s)
nl = (D != -32768).sum(0); print(f"{key}: {tris} tris, {len(mats)} mats, {len(tex)} tex, grid {GW}x{GH} ({int((nl>0).sum())} floor cells, max {int(nl.max())} layers), {len(boxes)} wall boxes, {len(s)//1024} KB")
np.save(f"/tmp/{key}_D.npy", D)
