"""Read a GLB and walk its scene with full transforms (TRS / matrix) and EXT_mesh_gpu_instancing."""
import json, struct
import numpy as np
CT = {5126: np.float32, 5123: np.uint16, 5125: np.uint32, 5121: np.uint8, 5122: np.int16, 5120: np.int8}
NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}
NORM = {5121: 255.0, 5123: 65535.0, 5120: 127.0, 5122: 32767.0}


class GLB:
    def __init__(s, f):
        b = open(f, "rb").read(); l = struct.unpack("<I", b[12:16])[0]; s.J = json.loads(b[20:20 + l]); o = 20 + l
        bl = struct.unpack("<I", b[o:o + 4])[0]; s.BIN = b[o + 8:o + 8 + bl]

    def acc(s, i):
        J = s.J; a = J["accessors"][i]; bv = J["bufferViews"][a["bufferView"]]; off = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
        n = NC[a["type"]]; dt = CT[a["componentType"]]; cnt = a["count"]; stride = bv.get("byteStride", 0); isz = np.dtype(dt).itemsize * n
        if stride and stride != isz:
            raw = np.frombuffer(s.BIN, dtype=np.uint8, count=stride * (cnt - 1) + isz, offset=off)
            idx = (np.arange(cnt)[:, None] * stride + np.arange(isz)[None, :])
            v = np.frombuffer(raw[idx].tobytes(), dtype=dt).reshape(cnt, n)
        else:
            v = np.frombuffer(s.BIN, dtype=dt, count=cnt * n, offset=off).reshape(cnt, n)
        if a.get("normalized"): v = v.astype(np.float32) / NORM[a["componentType"]]
        return v

    def img(s, i):
        im = s.J["images"][i]; bv = s.J["bufferViews"][im["bufferView"]]; o = bv.get("byteOffset", 0)
        return s.BIN[o:o + bv["byteLength"]], im.get("mimeType", "image/png")


def trs(t, q, sc):
    x, y, z, w = q
    R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                  [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
    M = np.eye(4); M[:3, :3] = R * np.array(sc); M[:3, 3] = t; return M


def lm(n):
    if "matrix" in n: return np.array(n["matrix"], float).reshape(4, 4).T
    return trs(n.get("translation", [0, 0, 0]), n.get("rotation", [0, 0, 0, 1]), n.get("scale", [1, 1, 1]))


def walk_from(G, root=None, with_empty=False):
    """[(node index, [names from the root], world matrix, mesh index)]; root: a node name to start from (its own transform is kept)"""
    J = G.J
    if root:
        par = {}
        for i, n in enumerate(J["nodes"]):
            for c in n.get("children", []): par[c] = i
        ri = [i for i, n in enumerate(J["nodes"]) if n.get("name") == root][0]
        M = np.eye(4); k = ri
        while k in par: k = par[k]; M = lm(J["nodes"][k]) @ M
        st = [(ri, M, [])]
    else:
        st = [(r, np.eye(4), []) for r in J["scenes"][J.get("scene", 0)]["nodes"]]
    out = []
    while st:
        i, PM, path = st.pop(); n = J["nodes"][i]; M = PM @ lm(n); p = path + [n.get("name", "")]
        if "mesh" in n:
            inst = n.get("extensions", {}).get("EXT_mesh_gpu_instancing")
            if inst:
                A = inst["attributes"]; T = G.acc(A["TRANSLATION"]) if "TRANSLATION" in A else None
                R = G.acc(A["ROTATION"]) if "ROTATION" in A else None; S = G.acc(A["SCALE"]) if "SCALE" in A else None
                cnt = len(T if T is not None else R if R is not None else S)
                for k in range(cnt):
                    out.append((i, p, M @ trs(T[k] if T is not None else [0, 0, 0], R[k] if R is not None else [0, 0, 0, 1], S[k] if S is not None else [1, 1, 1]), n["mesh"]))
            else: out.append((i, p, M, n["mesh"]))
        elif with_empty: out.append((i, p, M, None))
        for c in n.get("children", []): st.append((c, M, p))
    return out


def walk(G): return walk_from(G)
