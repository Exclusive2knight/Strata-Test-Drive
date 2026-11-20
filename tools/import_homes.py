"""Add the homes pack's house shells (homes/<nn>_<name>/<name>_shell.obj + .mtl) to props/lk_kit.json as kit houses.

    python3 tools/import_homes.py <homes folder> [names...]

Each house becomes lk object "House_Pack<Name>" (one vertex-coloured part on the kit's VC_Matte material), turned so its front
faces +z like the other kit houses (the pack's road frontage is on -Z), centred on x, with the lawn plane left out.
Prints the LKX footprint entries ([x0, x1, z0, z1, height]) to paste into the game's LKX table.
"""
import sys, os, json, re
import numpy as np

SKIP = {"grass"}


def mtl(path):
    M, cur = {}, None
    for ln in open(path):
        t = ln.split()
        if not t: continue
        if t[0] == "newmtl": cur = t[1]; M[cur] = [0.7, 0.7, 0.7]
        elif t[0] == "Kd" and cur: M[cur] = [float(x) for x in t[1:4]]
    return M


def shell(path, M):
    V, P, C = [], [], []
    cur = None
    for ln in open(path):
        t = ln.split()
        if not t: continue
        if t[0] == "v": V.append([float(x) for x in t[1:4]])
        elif t[0] == "usemtl": cur = t[1]
        elif t[0] == "f" and cur not in SKIP:
            idx = [int(x.split("/")[0]) for x in t[1:]]
            idx = [i - 1 if i > 0 else len(V) + i for i in idx]
            for k in range(1, len(idx) - 1):
                tri = [V[idx[0]], V[idx[k]], V[idx[k + 1]]]
                P += tri; C += [M.get(cur, [0.7, 0.7, 0.7])] * 3
    P = np.array(P); C = np.array(C)
    P[:, 0] *= -1; P[:, 2] *= -1                    # turn round: the front (road side) to +z
    P[:, 0] -= (P[:, 0].min() + P[:, 0].max()) / 2   # centred across
    P[:, 1] -= P[:, 1].min()
    # flat normals; triangle winding flips with the turn? (two axes negated = a rotation, winding unchanged)
    T = P.reshape(-1, 3, 3); n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.maximum(1e-9, np.linalg.norm(n, axis=1))[:, None]
    N = np.repeat(n, 3, axis=0)
    return P, N, C


def main(root, names):
    kit = json.load(open("props/lk_kit.json"))
    out = {}
    for d in sorted(os.listdir(root)):
        nm = re.sub(r"^\d+_", "", d)
        if names and nm not in names: continue
        if nm == "apartments": continue          # apartments are on hold
        sh = os.path.join(root, d, f"{nm}_shell.obj")
        if not os.path.exists(sh): continue
        P, N, C = shell(sh, mtl(os.path.join(root, d, f"{nm}.mtl")))
        key = "House_Pack" + "".join(w.capitalize() for w in nm.split("_"))
        part = {"m": 0, "p": [round(float(v), 3) for v in P.ravel()], "n": [round(float(v), 3) for v in N.ravel()],
                "i": list(range(len(P))), "c": [round(float(v), 3) for v in C.ravel()]}
        kit["objs"][key] = [part]
        out[key] = [round(float(P[:, 0].min()), 1), round(float(P[:, 0].max()), 1), round(float(P[:, 2].min()), 1), round(float(P[:, 2].max()), 1), round(float(P[:, 1].max()), 1)]
        print(f"{key}: {len(P) // 3} triangles, footprint {out[key]}")
    json.dump(kit, open("props/lk_kit.json", "w"), separators=(",", ":"))
    print(json.dumps(out, separators=(",", ":")))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
