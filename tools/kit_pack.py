"""Pack road kit pieces (roadkit_fixed: one GLB per section, one shared atlas) into one file the game loads.

    python3 tools/kit_pack.py <roadkit folder> <out.json> [piece names... | --layout props/kitmap.json]

Kit conventions (see the kit README): metres, +Y up, a piece starts at its origin and runs toward -Z, right-hand traffic (+X is right),
empty child nodes conn_<name> sit on each joint facing out of the piece.

Output (compact JSON):
  {"cycle": 12, "pieces": {name: {"p": [x,y,z in cm ...], "n": [nx,ny,nz * 127 ...], "t": [u,v * 10000 ...], "i": [...],
                                  "c": [[name, x, y, z, heading deg, profile, flow], ...], "lod": {same, optional}}}}
heading: 0 = facing -Z, 90 = facing +X (the kit's own convention).
"""
import sys, json, struct, math, os
import numpy as np

CT = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}
NORM = {np.int8: 127.0, np.uint8: 255.0, np.int16: 32767.0, np.uint16: 65535.0}


def glb(path):
    b = open(path, "rb").read()
    n = struct.unpack("<I", b[12:16])[0]
    j = json.loads(b[20:20 + n])
    off = 20 + n
    bin_ = b[off + 8: off + 8 + struct.unpack("<I", b[off:off + 4])[0]] if off < len(b) else b""
    return j, bin_


def acc(j, bin_, i):
    a = j["accessors"][i]; v = j["bufferViews"][a["bufferView"]]
    dt = CT[a["componentType"]]; nc = NC[a["type"]]
    start = v.get("byteOffset", 0) + a.get("byteOffset", 0)
    stride = v.get("byteStride", 0); isz = np.dtype(dt).itemsize * nc
    if stride and stride != isz:
        raw = np.frombuffer(bin_, np.uint8, count=stride * (a["count"] - 1) + isz, offset=start)
        arr = np.stack([np.frombuffer(raw[k * stride:k * stride + isz].tobytes(), dt) for k in range(a["count"])])
    else:
        arr = np.frombuffer(bin_, dt, count=a["count"] * nc, offset=start).reshape(-1, nc) if nc > 1 else np.frombuffer(bin_, dt, count=a["count"], offset=start)
    arr = arr.astype(np.float64)
    if a.get("normalized") and dt in NORM: arr /= NORM[dt]
    return arr


def qmat(t, r, s):
    x, y, z, w = r
    R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                  [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                  [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
    M = np.eye(4); M[:3, :3] = R * np.array(s); M[:3, 3] = t
    return M


def node_m(n):
    if "matrix" in n: return np.array(n["matrix"]).reshape(4, 4).T
    return qmat(n.get("translation", [0, 0, 0]), n.get("rotation", [0, 0, 0, 1]), n.get("scale", [1, 1, 1]))


def piece(path):
    j, b = glb(path)
    P, N, T, I = [], [], [], []
    base = 0
    roots = j["scenes"][j.get("scene", 0)]["nodes"]

    def walk(ni, M):
        nonlocal base
        n = j["nodes"][ni]; M = M @ node_m(n)
        if "mesh" in n:
            for pr in j["meshes"][n["mesh"]]["primitives"]:
                at = pr["attributes"]
                p = acc(j, b, at["POSITION"]); p = (np.c_[p, np.ones(len(p))] @ M.T)[:, :3]
                nr = acc(j, b, at["NORMAL"]) @ M[:3, :3].T if "NORMAL" in at else np.tile([0, 1, 0], (len(p), 1))
                nr = nr / np.maximum(1e-9, np.linalg.norm(nr, axis=1))[:, None]
                uv = acc(j, b, at["TEXCOORD_0"]) if "TEXCOORD_0" in at else np.zeros((len(p), 2))
                ix = acc(j, b, pr["indices"]).astype(np.int64) if "indices" in pr else np.arange(len(p))
                P.append(p); N.append(nr); T.append(uv); I.append(ix + base); base += len(p)
        for c in n.get("children", []): walk(c, M)
    for r in roots: walk(r, np.eye(4))
    P = np.concatenate(P); N = np.concatenate(N); T = np.concatenate(T); I = np.concatenate(I)
    return {"p": np.round(P * 100).astype(int).ravel().tolist(), "n": np.round(N * 127).astype(int).ravel().tolist(),
            "t": np.round(T * 10000).astype(int).ravel().tolist(), "i": I.astype(int).tolist()}


def clip(d, L0, L):
    """a straight cut / stretched to length L: along-road positions and the atlas V (12 m a cycle) scale together, so the texture keeps its size"""
    k = L / L0; p = list(d["p"]); t = list(d["t"])
    for i in range(0, len(p), 3): p[i + 2] = round(p[i + 2] * k)
    # V runs along the road: rescale it about each vertex's own start so a 96 m piece cut to 40 m shows 40 m of markings
    for i in range(1, len(t), 2): t[i] = round(t[i] * k)
    return {**d, "p": p, "t": t}


def slope(d, L, dz):
    """climb dz metres over the piece's length (a straight graded to the road's profile)"""
    if not dz: return d
    p = list(d["p"])
    for i in range(0, len(p), 3): p[i + 1] = round(p[i + 1] + dz * 100 * (-p[i + 2] / 100.0) / L)
    return {**d, "p": p}


def bend(d, R):
    """a straight bent round an arc of signed radius R (+ turns right): the along-road axis (-Z) follows the arc, X stays across it"""
    if not R: return d
    p = list(d["p"]); n = list(d["n"])
    for i in range(0, len(p), 3):
        x, z = p[i] / 100.0, p[i + 2] / 100.0
        th = -z / R                       # distance along / radius (z is negative going forward)
        rr = R - x
        p[i] = round((R - rr * math.cos(th)) * 100); p[i + 2] = round(-rr * math.sin(th) * 100)
        nx, nz = n[i], n[i + 2]
        c, s_ = math.cos(th), math.sin(th)
        n[i] = round(nx * c + nz * s_); n[i + 2] = round(-nx * s_ + nz * c)
    return {**d, "p": p, "n": n}


def main(root, out, names):
    man = {v["name"]: v for v in json.load(open(os.path.join(root, "manifest.json")))["pieces"]}
    res = {"cycle": 12, "pieces": {}}
    for nm in names:
        if "@" in nm:
            base, L = nm.split("@"); R = 0.0; dz = 0.0
            if "^" in L: L, dz = L.split("^"); dz = float(dz)
            if "~" in L: L, R = L.split("~"); R = float(R)
            v = man[base]; L0 = float(base.rsplit("_st", 1)[1])
            d = bend(slope(clip(piece(os.path.join(root, v["file"])), L0, float(L)), float(L), dz), R)
            d["c"] = []; res["pieces"][nm] = d; continue
        v = man[nm]
        d = piece(os.path.join(root, v["file"]))
        if v.get("lod1"): d["lod"] = piece(os.path.join(root, v["lod1"]))
        d["c"] = [[c["name"], round(c["pos"][0], 3), round(c["pos"][1], 3), round(c["pos"][2], 3), round(c["heading"], 2), c["profile"], c.get("flow", "both")] for c in v["connectors"]]
        res["pieces"][nm] = d
    s = json.dumps(res, separators=(",", ":"))
    open(out, "w").write(s)
    print(f"{len(names)} pieces, {sum(len(p['i']) // 3 for p in res['pieces'].values())} triangles, {len(s) // 1024} KB -> {out}")


if __name__ == "__main__":
    root, out = sys.argv[1], sys.argv[2]
    args = sys.argv[3:]
    if args and args[0] == "--layout":
        L = json.load(open(args[1])); names = sorted({p[0] for p in L["place"]})
        if "--base" in args: names = sorted({n.split("@")[0].split("!")[0].split("%")[0] for n in names})   # the game cuts, grades and bends these itself
    elif args:
        names = args
    else:
        names = sorted(v["name"] for v in json.load(open(os.path.join(root, "manifest.json")))["pieces"])
    main(root, out, names)
