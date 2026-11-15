"""Somerset Collection (Troy, MI) mall model -> props/mall_somerset.json for the game.

    python3 tools/import_mall.py somerset_collection.glb

Model space: metres, +Y up; the game places it with no rotation (model X -> world x = cx + X, model Z -> world y = -Z).
Output (all base64): per material a list of chunks {o: offset, k: position scale, p: int16 xyz, n: int8 normals,
t: int16 uv (/512) for textured materials, i: uint16 indices}; the textures as data: URIs (the big road photo is
scaled down); the outdoor lamp posts (for colliders and night glow).
The model's own Big Beaver Rd (|Z| < 21) is left out: the game's Grand River Ave runs there.
"""
import sys, json, struct, base64, io
import numpy as np
sys.path.insert(0, "/home/claude/strata")
from PIL import Image

src = sys.argv[1]
b = open(src, "rb").read(); n = struct.unpack("<I", b[12:16])[0]; J = json.loads(b[20:20 + n]); o = 20 + n
bl = struct.unpack("<I", b[o:o + 4])[0]; BIN = b[o + 8:o + 8 + bl]
CT = {5126: np.float32, 5123: np.uint16, 5125: np.uint32, 5121: np.uint8}; NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}


def acc(i):
    a = J["accessors"][i]; bv = J["bufferViews"][a["bufferView"]]; off = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    nc = NC[a["type"]]; dt = CT[a["componentType"]]; cnt = a["count"]; stride = bv.get("byteStride", 0); isz = np.dtype(dt).itemsize * nc
    if stride and stride != isz:
        raw = np.frombuffer(BIN, np.uint8, stride * cnt, off).reshape(cnt, stride)[:, :isz].copy(); return np.frombuffer(raw.tobytes(), dt).reshape(cnt, nc)
    return np.frombuffer(BIN, dt, cnt * nc, off).reshape(cnt, nc)


par = {}
for i, nd in enumerate(J["nodes"]):
    for c in nd.get("children", []): par[c] = i


def wt(i):
    t = np.array(J["nodes"][i].get("translation", [0, 0, 0]), float)
    while i in par: i = par[i]; t += np.array(J["nodes"][i].get("translation", [0, 0, 0]), float)
    return t


# textures -> data URIs (the road photo is big: 1024 px JPEG)
tex = []
for ti, T in enumerate(J["textures"]):
    im = J["images"][T["source"]]; bv = J["bufferViews"][im["bufferView"]]; raw = BIN[bv.get("byteOffset", 0):bv.get("byteOffset", 0) + bv["byteLength"]]
    mime = im.get("mimeType", "image/png")
    if mime == "image/jpeg" and len(raw) > 300000:
        I = Image.open(io.BytesIO(raw)).convert("RGB"); s = 1024 / max(I.size)
        if s < 1: I = I.resize((int(I.size[0] * s), int(I.size[1] * s)), Image.LANCZOS)
        bo = io.BytesIO(); I.save(bo, "JPEG", quality=72); raw = bo.getvalue()
    smp = J["samplers"][T.get("sampler", 0)] if "samplers" in J else {}
    tex.append({"src": f"data:{mime};base64," + base64.b64encode(raw).decode(), "clamp": smp.get("wrapS") == 33071, "name": im.get("name", "")})

mats = []
for M in J["materials"]:
    pb = M.get("pbrMetallicRoughness", {}); c = pb.get("baseColorFactor", [1, 1, 1, 1])
    t = pb["baseColorTexture"]["index"] if "baseColorTexture" in pb else -1
    mats.append({"n": M.get("name", "").replace("somerset_", ""), "f": [round(v, 3) for v in c[:3]], "al": round(c[3], 3), "a": M.get("alphaMode", "OPAQUE"),
                 "t": t, "e": [round(v, 3) for v in M.get("emissiveFactor", [0, 0, 0])], "m": round(pb.get("metallicFactor", 0), 2), "r": round(pb.get("roughnessFactor", 0.8), 2)})

BAND = 21.0   # the game's Grand River Ave (a boulevard here, kerb to kerb with its walks) runs along Z = 0
GROUND_N = {"Site_Ground", "Site_Islands", "Streetscape", "Roads_Mall", "Roads_FromRoadKit"}


def clip_band(P, N, UV, I):
    """cut the strip |Z| < BAND out of a mesh (keeps the two sides, splits the triangles that cross it)"""
    keepP, keepN, keepU, keepI = [P], [N], [UV if UV is not None else np.zeros((len(P), 2))], []
    nv = len(P)
    U0 = keepU[0]
    for t in I:
        z = P[t, 2]
        if (z <= -BAND).all() or (z >= BAND).all(): keepI.append(t); continue
        if (np.abs(z) < BAND).all(): continue
        for sgn in (-1, 1):   # the part on each side: sgn*Z >= BAND
            poly = [(P[v], N[v], U0[v]) for v in t]; outp = []
            for i in range(len(poly)):
                a, b = poly[i], poly[(i + 1) % len(poly)]; da, db = sgn * a[0][2] - BAND, sgn * b[0][2] - BAND
                if da >= 0: outp.append(a)
                if (da >= 0) != (db >= 0):
                    f = da / (da - db); outp.append(tuple(a[j] + (b[j] - a[j]) * f for j in range(3)))
            if len(outp) < 3: continue
            base = nv
            for q in outp:
                keepP.append(q[0][None]); keepN.append(q[1][None]); keepU.append(q[2][None]); nv += 1
            for k in range(1, len(outp) - 1): keepI.append(np.array([base, base + k, base + k + 1]))
    if not keepI: return None
    return np.concatenate(keepP), np.concatenate(keepN), (np.concatenate(keepU) if UV is not None else None), np.array(keepI, np.int64)


by = {}   # material -> list of (P, N, UV, I)
ground = []   # drivable surfaces for the physics height grid
skipped = 0
for i, nd in enumerate(J["nodes"]):
    if "mesh" not in nd: continue
    T = wt(i); name = nd.get("name", "")
    for pr in J["meshes"][nd["mesh"]]["primitives"]:
        P = acc(pr["attributes"]["POSITION"]).astype(float) + T; N = acc(pr["attributes"]["NORMAL"]).astype(float)
        UV = acc(pr["attributes"]["TEXCOORD_0"]).astype(float) if "TEXCOORD_0" in pr["attributes"] else None
        I = acc(pr["indices"]).reshape(-1, 3).astype(np.int64)
        if name in GROUND_N:   # Big Beaver Rd and the site ground under it: the game's own road is drawn there
            n0 = len(I); r = clip_band(P, N, UV, I)
            if r is None: skipped += n0; continue
            P, N, UV, I = r; skipped += max(0, n0 - len(I))
        if not len(I): continue
        by.setdefault(pr.get("material", 0), []).append((P, N, UV, I))
        mn = J["materials"][pr.get("material", 0)].get("name", "")
        if (name in GROUND_N or name.startswith("Lot_")) and not name.startswith("Lot_LightPoles") and not any(w in mn for w in ("glass", "metal", "plant", "wood", "light", "water", "sign")):
            ground.append((P, I))

CS = 160.0   # chunk cells so the far ones can be culled
out_m = {}
tris = 0
for mi, L in by.items():
    cells = {}
    for P, N, UV, I in L:
        c = P[I].mean(1); key = np.floor(c[:, 0] / CS).astype(int) * 1000 + np.floor(c[:, 2] / CS).astype(int)
        for kk in np.unique(key):
            Ii = I[key == kk]; used = np.unique(Ii); rm = -np.ones(len(P), np.int64); rm[used] = np.arange(len(used))
            cells.setdefault(int(kk), []).append((P[used], N[used], UV[used] if UV is not None else None, rm[Ii]))
    chunks = []
    for kk, parts in cells.items():
        cur = None
        for P, N, UV, I in parts:
            if cur is None or cur["nv"] + len(P) > 65000:
                cur = {"P": [], "N": [], "U": [], "I": [], "nv": 0}; chunks.append(cur)
            cur["I"].append(I + cur["nv"]); cur["P"].append(P); cur["N"].append(N); cur["U"].append(UV if UV is not None else np.zeros((len(P), 2))); cur["nv"] += len(P)
    enc = []
    for ch in chunks:
        P = np.concatenate(ch["P"]); N = np.concatenate(ch["N"]); U = np.concatenate(ch["U"]); I = np.concatenate(ch["I"]).reshape(-1)
        lo, hi = P.min(0), P.max(0); ctr = (lo + hi) / 2; ext = float(np.abs(P - ctr).max()) + 0.01; k = min(1000.0, 32000.0 / ext)
        nl = np.linalg.norm(N, axis=1, keepdims=True); nl[nl == 0] = 1; N = N / nl
        e = {"o": [round(float(v), 3) for v in ctr], "k": round(k, 4), "p": base64.b64encode(np.round((P - ctr) * k).astype("<i2").tobytes()).decode(),
             "n": base64.b64encode(np.clip(np.round(N * 127), -127, 127).astype("i1").tobytes()).decode(), "i": base64.b64encode(I.astype("<u2").tobytes()).decode()}
        if mats[mi]["t"] >= 0:
            ur = float(np.abs(U).max()); us = 512.0 if ur < 60 else 32000.0 / ur; e["ts"] = round(us, 3)
            e["t"] = base64.b64encode(np.clip(np.round(U * us), -32767, 32767).astype("<i2").tobytes()).decode()
        enc.append(e); tris += len(I) // 3
    out_m[mi] = enc

lamps = []
for i, nd in enumerate(J["nodes"]):
    if nd.get("name", "").startswith("LightPoint_"):
        t = wt(i); lamps.append([round(float(t[0]), 1), round(float(t[1]), 1), round(float(t[2]), 1), 1 if nd.get("extras", {}).get("light") == "Outdoor" else 0])

# physics: the drivable ground on a 3 m grid (height in cm, -128 = not paved), from the upward-facing ground triangles
G = 3.0; GX0, GX1, GZ0, GZ1 = -480.0, 426.0, -336.0, 345.0
gw, gh = int((GX1 - GX0) / G), int((GZ1 - GZ0) / G); H = np.full((gh, gw), -1e9)
for P, I in ground:
    T = P[I]; nrm = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); up = nrm[:, 1] / (np.linalg.norm(nrm, axis=1) + 1e-9)
    for tri, u in zip(T, up):
        if abs(u) < 0.7 or tri[:, 1].max() > 1.0: continue
        x0, x1 = tri[:, 0].min(), tri[:, 0].max(); z0, z1 = tri[:, 2].min(), tri[:, 2].max()
        i0, i1 = max(0, int((x0 - GX0) / G)), min(gw - 1, int((x1 - GX0) / G)); j0, j1 = max(0, int((z0 - GZ0) / G)), min(gh - 1, int((z1 - GZ0) / G))
        if i1 < i0 or j1 < j0: continue
        xs = GX0 + (np.arange(i0, i1 + 1) + 0.5) * G; zs = GZ0 + (np.arange(j0, j1 + 1) + 0.5) * G; X, Z = np.meshgrid(xs, zs)
        (ax, ay, az), (bx, by_, bz), (cx, cy, cz) = tri
        d = (bz - cz) * (ax - cx) + (cx - bx) * (az - cz)
        if abs(d) < 1e-9: continue
        l1 = ((bz - cz) * (X - cx) + (cx - bx) * (Z - cz)) / d; l2 = ((cz - az) * (X - cx) + (ax - cx) * (Z - cz)) / d; l3 = 1 - l1 - l2
        inside = (l1 >= -0.02) & (l2 >= -0.02) & (l3 >= -0.02); Y = l1 * ay + l2 * by_ + l3 * cy
        sub = H[j0:j1 + 1, i0:i1 + 1]; sub[inside] = np.maximum(sub[inside], Y[inside])
Hc = np.where(H > -1e8, np.clip(np.round(H * 100), -127, 127), -128).astype(np.int8)
print("paved cells", int((Hc > -128).sum()), "of", Hc.size)

out = {"grid": {"x0": GX0, "z0": GZ0, "s": G, "w": gw, "h": gh, "d": base64.b64encode(Hc.tobytes()).decode()}, "band": BAND, "mats": mats, "tex": tex, "m": {str(k): v for k, v in out_m.items()}, "lamps": lamps}
s = json.dumps(out, separators=(",", ":"))
open("props/mall_somerset.json", "w").write(s)
print(f"mall_somerset: {tris} tris ({skipped} Big Beaver triangles left out), {len(mats)} materials, {len(tex)} textures, {len(lamps)} lamps, {len(s)//1024} KB")
