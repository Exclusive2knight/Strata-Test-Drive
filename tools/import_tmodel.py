"""Textured GLB -> game model JSON (the mall's chunk format), for vehicles and buildings that need their textures.

    python3 tools/import_tmodel.py in.glb out.json [--root NODE] [--texdir props/tx] [--texmax 1024] [--chunk 160]
                                   [--skip REGEX] [--only REGEX] [--yflip]

Full node transforms (rotation / scale / matrix) and EXT_mesh_gpu_instancing are applied.
Each texture is cropped to the part of it the model's UVs use (when they stay inside 0..1), scaled down to --texmax,
written once to --texdir/<hash>.png|jpg (shared between models that use the same picture) and its UVs remapped.
Materials named *_<Role>_lens (truck lights) are merged by role, so the game can light them: role in mats[i].role.
Output: {mats:[{n,f,al,a,t,e,m,r,role}], tex:[{u,clamp}], m:{mat:[{o,k,p,n,i,t,ts}]}, bb:[min,max], nodes:{name:[x,y,z]}}
(model space, metres, +Y up, as in the GLB).
"""
import sys, os, io, re, json, base64, hashlib
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from glbscene import GLB, walk_from

a = sys.argv[1:]; src, out = a[0], a[1]
opt = {"root": None, "texdir": "props/tx", "texmax": 1024, "chunk": 0, "skip": None, "only": None}
i = 2
while i < len(a):
    k = a[i][2:]
    if k in ("yflip",): opt[k] = True; i += 1; continue
    opt[k] = a[i + 1]; i += 2
TEXMAX = int(opt["texmax"]); CS = float(opt["chunk"]); SKIP = re.compile(opt["skip"]) if opt["skip"] else None; ONLY = re.compile(opt["only"]) if opt["only"] else None
G = GLB(src); J = G.J
W = walk_from(G, opt["root"])

ROLE = re.compile(r"_(Headlight|Brake|Turn_Rear|Turn|Marker|Clearance|Reverse|Fog|Beacon|Tail|DRL)(?:_[A-Za-z0-9_-]*)?_lens$")
def role_of(name):
    m = ROLE.search(name)
    if not m: return None
    r = m.group(1).lower()
    side = "L" if re.search(r"_L(_|$)|_-1_|_Left", name) else "R" if re.search(r"_R(_|$)|_1_|_Right", name) else ""
    if r in ("turn", "turn_rear"): return "turn" + side
    if r in ("marker", "clearance"): return "marker"
    return r

# ---- gather triangles per source material
mats_src = J.get("materials", [])
by = {}   # src material -> list of (P, N, UV, I)
uvuse = {}  # image -> list of UV arrays actually used
for ni, path, M, mi in W:
    nm = "/".join(path)
    if SKIP and SKIP.search(nm): continue
    if ONLY and not ONLY.search(nm): continue
    for pr in J["meshes"][mi]["primitives"]:
        if pr.get("mode", 4) != 4: continue
        P = G.acc(pr["attributes"]["POSITION"]).astype(float)
        N = G.acc(pr["attributes"]["NORMAL"]).astype(float) if "NORMAL" in pr["attributes"] else None
        UV = G.acc(pr["attributes"]["TEXCOORD_0"]).astype(float) if "TEXCOORD_0" in pr["attributes"] else None
        I = G.acc(pr["indices"]).reshape(-1).astype(np.int64) if "indices" in pr else np.arange(len(P))
        I = I.reshape(-1, 3)
        Pw = P @ M[:3, :3].T + M[:3, 3]
        if N is None:
            N = np.zeros_like(P); fn = np.cross(Pw[I[:, 1]] - Pw[I[:, 0]], Pw[I[:, 2]] - Pw[I[:, 0]])
            for k in range(3): np.add.at(N, I[:, k], fn)
            Nw = N
        else:
            Nw = N @ np.linalg.inv(M[:3, :3])
        if np.linalg.det(M[:3, :3]) < 0: I = I[:, ::-1]
        nl = np.linalg.norm(Nw, axis=1, keepdims=True); nl[nl == 0] = 1; Nw = Nw / nl
        m = pr.get("material", -1)
        by.setdefault(m, []).append((Pw, Nw, UV, I))
        if m >= 0 and UV is not None:
            pb = mats_src[m].get("pbrMetallicRoughness", {})
            if "baseColorTexture" in pb:
                img = J["textures"][pb["baseColorTexture"]["index"]]["source"]
                uvuse.setdefault(img, []).append(UV[np.unique(I)])

# ---- textures: crop to the used UV box, scale down, write once by content hash
os.makedirs(opt["texdir"], exist_ok=True)
tex = []; tex_of = {}; remap = {}
for img, L in uvuse.items():
    U = np.concatenate(L); raw, mime = G.img(img); im = Image.open(io.BytesIO(raw)); im.load()
    w, h = im.size; u0, v0 = U.min(0); u1, v1 = U.max(0); clamp = True
    if u0 < -0.01 or v0 < -0.01 or u1 > 1.01 or v1 > 1.01: u0, v0, u1, v1 = 0, 0, 1, 1; clamp = False
    px0 = max(0, int(np.floor(u0 * w)) - 3); py0 = max(0, int(np.floor(v0 * h)) - 3); px1 = min(w, int(np.ceil(u1 * w)) + 3); py1 = min(h, int(np.ceil(v1 * h)) + 3)
    if not clamp: px0, py0, px1, py1 = 0, 0, w, h
    crop = im.crop((px0, py0, px1, py1)); cw, ch = crop.size
    s = min(1.0, TEXMAX / max(cw, ch))
    # power-of-two sizes so the game can mipmap and repeat them
    p2 = lambda v: 1 << max(2, int(round(np.log2(max(4, v)))))
    nw, nh = p2(cw * s), p2(ch * s)
    while max(nw, nh) > TEXMAX: nw, nh = max(4, nw // 2), max(4, nh // 2)
    crop = crop.resize((nw, nh), Image.LANCZOS)
    alpha = crop.mode in ("RGBA", "LA", "P") and crop.convert("RGBA").getextrema()[3][0] < 250
    bo = io.BytesIO()
    if alpha: crop.convert("RGBA").save(bo, "PNG", optimize=True); ext = "png"
    else: crop.convert("RGB").save(bo, "JPEG", quality=82); ext = "jpg"
    data = bo.getvalue(); hh = hashlib.md5(data).hexdigest()[:12]; fn = f"{opt['texdir']}/{hh}.{ext}"
    if not os.path.exists(fn): open(fn, "wb").write(data)
    tex_of[img] = len(tex); tex.append({"u": fn, "clamp": clamp})
    remap[img] = (px0 / w, py0 / h, (px1 - px0) / w, (py1 - py0) / h)

# ---- materials: lenses merged by role, others kept
mats = []; mat_of = {}; key_of = {}
for m in by:
    M = mats_src[m] if m >= 0 else {"name": "default"}
    pb = M.get("pbrMetallicRoughness", {}); c = pb.get("baseColorFactor", [0.8, 0.8, 0.8, 1]); nm = M.get("name", "")
    t = -1; img = None
    if "baseColorTexture" in pb: img = J["textures"][pb["baseColorTexture"]["index"]]["source"]; t = tex_of.get(img, -1)
    role = role_of(nm)
    row = {"n": re.sub(r"^truck_", "", nm), "f": [round(v, 3) for v in c[:3]], "al": round(c[3], 3), "a": M.get("alphaMode", "OPAQUE"), "t": t,
           "e": [round(v, 3) for v in M.get("emissiveFactor", [0, 0, 0])], "m": round(pb.get("metallicFactor", 0), 2), "r": round(pb.get("roughnessFactor", 0.7), 2)}
    if role: row["role"] = role; row["n"] = "lens_" + role
    key = (row["n"], tuple(row["f"]), t, row["a"]) if role else ("#" + str(m),)
    if key not in key_of: key_of[key] = len(mats); mats.append(row)
    mat_of[m] = (key_of[key], img)

# ---- geometry
out_m = {}; tris = 0; allP = []
for m, L in by.items():
    mi, img = mat_of[m]; rm = remap.get(img)
    parts = []
    for P, N, UV, I in L:
        if UV is not None and rm:
            UV = UV.copy(); UV[:, 0] = (UV[:, 0] - rm[0]) / rm[2]; UV[:, 1] = (UV[:, 1] - rm[1]) / rm[3]
        used = np.unique(I); r_ = -np.ones(len(P), np.int64); r_[used] = np.arange(len(used))
        parts.append((P[used], N[used], UV[used] if UV is not None else None, r_[I]))
        allP.append(P[used])
    cells = {}
    for P, N, UV, I in parts:
        if CS > 0:
            c = P[I].mean(1); kk = np.floor(c[:, 0] / CS).astype(int) * 1000 + np.floor(c[:, 2] / CS).astype(int)
        else: kk = np.zeros(len(I), int)
        for k in np.unique(kk):
            Ii = I[kk == k]; used = np.unique(Ii); r_ = -np.ones(len(P), np.int64); r_[used] = np.arange(len(used))
            cells.setdefault(int(k), []).append((P[used], N[used], UV[used] if UV is not None else None, r_[Ii]))
    for k, ps in cells.items():
        cur = None; chunks = []
        for P, N, UV, I in ps:
            if cur is None or cur["nv"] + len(P) > 65000: cur = {"P": [], "N": [], "U": [], "I": [], "nv": 0}; chunks.append(cur)
            cur["I"].append(I + cur["nv"]); cur["P"].append(P); cur["N"].append(N); cur["U"].append(UV if UV is not None else np.zeros((len(P), 2))); cur["nv"] += len(P)
        for ch in chunks:
            P = np.concatenate(ch["P"]); N = np.concatenate(ch["N"]); U = np.concatenate(ch["U"]); I = np.concatenate(ch["I"]).reshape(-1)
            lo, hi = P.min(0), P.max(0); ctr = (lo + hi) / 2; ext = float(np.abs(P - ctr).max()) + 0.01; kq = min(2000.0, 32000.0 / ext)
            e = {"o": [round(float(v), 4) for v in ctr], "k": round(kq, 4), "p": base64.b64encode(np.round((P - ctr) * kq).astype("<i2").tobytes()).decode(),
                 "n": base64.b64encode(np.clip(np.round(N * 127), -127, 127).astype("i1").tobytes()).decode(), "i": base64.b64encode(I.astype("<u2").tobytes()).decode()}
            if mats[mi]["t"] >= 0:
                ur = float(np.abs(U).max()) + 1e-6; us = 4096.0 if ur < 7 else 32000.0 / ur; e["ts"] = round(us, 3)
                e["t"] = base64.b64encode(np.clip(np.round(U * us), -32767, 32767).astype("<i2").tobytes()).decode()
            out_m.setdefault(str(mi), []).append(e); tris += len(I) // 3
AP = np.concatenate(allP)
nodes = {}
for ni, path, M, mi in walk_from(G, opt["root"], with_empty=True):
    n = path[-1]
    if n and n not in nodes: nodes[n] = [round(float(v), 3) for v in M[:3, 3]]
res = {"mats": mats, "tex": tex, "m": out_m, "bb": [[round(float(v), 3) for v in AP.min(0)], [round(float(v), 3) for v in AP.max(0)]], "nodes": nodes}
s = json.dumps(res, separators=(",", ":")); open(out, "w").write(s)
print(f"{out}: {tris} tris, {len(mats)} materials, {len(tex)} textures, {len(s)//1024} KB")
