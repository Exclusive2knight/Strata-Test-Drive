"""Import a car from the "All Vehicles GLB Pack" (Wheel_FL/FR/RL/RR, SteeringWheel, Screens, Light_* nodes; Paint,
Light_Head, Screen_Main ... materials; rims without tyres) into models/<key>.json through tools/import_car.py.

    python3 tools/import_pack.py Car.glb key [body_budget cabin_budget]

What it adds on top of import_car:
  * renames the pack's nodes / materials to the names import_car knows
  * builds a tyre round each rim (the pack leaves them out): outer radius = the hub height, the rim's own width
  * a driver camera from the steering wheel, so the screen panels can be found
  * the screens: the cluster panel and the centre panel; one-piece dash screens (Cadillac 33-in. and 55-in., Buick 30-in.)
    are split into a cluster part and a centre part, and their curve is measured and written as meta.arc so the
    game bends its screen pictures the same way.
"""
import sys, json, re
import numpy as np
sys.path.insert(0, "/home/claude/strata")
sys.path.insert(0, "tools")
import import_model as M
import import_car as C

WH = {"Wheel_FL": "wheel_front_left", "Wheel_FR": "wheel_front_right", "Wheel_RL": "wheel_rear_left", "Wheel_RR": "wheel_rear_right"}
NODE = {"Interior": "cabin_interior", "InteriorShell": "cabin_shell", "Dashboard": "dashboard", "Screens": "cabin_screens",
        "Seats": "cabin_seats", "SteeringWheel": "steering_wheel"}
MAT = {"Light_Head": "LED headlights", "Light_Tail": "Red tail light", "Light_Reverse": "Reverse light",
       "Marker_Amber": "Amber turn signal", "Screen_Main": "blank display", "Screen_Aux": "blank display"}


def tyre(cx, cy, cz, R, r_in, half_w, n=40):
    """a tyre round the X axle: tread, rounded shoulders, sidewalls down to the rim"""
    prof = []   # (x offset, radius) from the outer sidewall at the rim round to the inner one
    sh = min(0.04, (R - r_in) * 0.45)
    prof.append((half_w * 0.92, r_in))
    for a in np.linspace(0, np.pi / 2, 4):
        prof.append((half_w - sh + sh * np.cos(a), R - sh + sh * np.sin(a)))
    for a in np.linspace(np.pi / 2, np.pi, 4):
        prof.append((-half_w + sh + sh * np.cos(a), R - sh + sh * np.sin(a)))
    prof.append((-half_w * 0.92, r_in))
    V, F = [], []
    for i in range(n):
        t = 2 * np.pi * i / n
        for (x, r) in prof: V.append([cx + x, cy + r * np.cos(t), cz + r * np.sin(t)])
    m = len(prof)
    for i in range(n):
        j = (i + 1) % n
        for k in range(m - 1):
            a, b, c, d = i * m + k, i * m + k + 1, j * m + k + 1, j * m + k
            F += [[a, b, c], [a, c, d]]
    return np.array(V), np.array(F)


def screen_info(parts):
    """the dash screen panels (GLB space: +X driver side, +Y up, +Z forward)"""
    out = {}
    for p in parts:
        if p["node"] != "Screens": continue
        n = p["mat"]["name"]
        if n in ("Screen_Main", "Screen_Aux"):
            out.setdefault(n, []).append(p["V"][np.unique(p["F"])])
    return {k: np.concatenate(v) for k, v in out.items()}


def main(src, key, *bud):
    M.NODES = {}
    orig = M.load_gltf
    parts, extra = orig(src)
    nodes = dict(M.NODES)
    scr = screen_info(parts)
    sw = [p["V"][np.unique(p["F"])] for p in parts if p["node"] == "SteeringWheel"]
    swc = None
    if sw:
        A = np.concatenate(sw); swc = (A.min(0) + A.max(0)) / 2
    # tyres: one per rim
    add = []
    for wn in WH:
        L = [p for p in parts if p["node"] == wn]
        if not L: continue
        A = np.concatenate([p["V"][np.unique(p["F"])] for p in L]); lo, hi = A.min(0), A.max(0); c = nodes.get(wn, (lo + hi) / 2)
        r_rim = max(hi[1] - lo[1], hi[2] - lo[2]) / 2; R = float(c[1])   # origin on the ground: the hub height is the tyre radius
        if R < r_rim + 0.05: R = r_rim + 0.09
        hw = max((hi[0] - lo[0]) / 2 + 0.01, 0.1)
        V, F = tyre(float(c[0]), float(c[1]), float(c[2]), R, r_rim * 0.97, hw)
        add.append({"V": V, "F": F, "node": wn, "mat": {"name": "Tyre rubber", "color": np.array([0.02, 0.02, 0.022]), "alpha": 1.0,
                    "metal": 0.0, "rough": 0.9, "emissive": np.zeros(3), "transmission": 0}})
    parts += add
    for p in parts:
        if p["node"].startswith("Caliper_"): p["node"] = "body_caliper"
        p["node"] = WH.get(p["node"], NODE.get(p["node"], p["node"]))
        nm = p["mat"]["name"]
        if nm in MAT and not p["mat"].get("_ren"):
            p["mat"] = {**p["mat"], "name": MAT[nm], "_ren": 1}
        if p["node"] == "cabin_seats" and nm == "Screen_Rear": p["mat"] = {**p["mat"], "name": "rear screen"}
    for k, v in WH.items():
        if k in nodes: nodes[v] = nodes[k]
    if swc is not None: nodes["driver_camera"] = [float(swc[0]), float(swc[1] + 0.27), float(swc[2] - 0.55)]

    def fake(path):
        M.NODES = dict(nodes); return parts, extra
    M.load_gltf = fake
    try:
        out = C.main(src, key, *bud)
    finally:
        M.load_gltf = orig
    # one-piece dash screens: split into cluster + centre, and measure the curve
    m = out["meta"]; P = lambda v: [round(-float(v[0]), 4), round(float(v[1]), 4), round(-float(v[2]), 4)]   # GLB -> page (+x right, +y up, -z front)
    shift = None
    try:   # import_car moved the model so the wheels sit at the origin height; read it back from a wheel
        h = nodes["wheel_front_left"]; shift = np.array([0.0, float(h[1]) - out["wheelR"], 0.0])
        zs = [nodes[w][2] for w in WH.values() if w in nodes]; shift[2] = (max(zs) + min(zs)) / 2
    except Exception:
        shift = np.zeros(3)
    main_ = scr.get("Screen_Main"); aux = scr.get("Screen_Aux")
    if main_ is not None and swc is not None:
        W = main_[:, 0].max() - main_[:, 0].min()
        one = aux is None or W > 1.2   # a single panel (or a pillar-to-pillar one with a separate lower screen)
        if one:
            S = main_ - shift; Q = np.array([P(v) for v in S])
            # the panel's curve: depth (page z) against the across position (page x), fitted with a parabola
            x = Q[:, 0]; y = Q[:, 1]; z = Q[:, 2]
            x0, x1 = float(x.min()), float(x.max()); y0, y1 = float(np.percentile(y, 2)), float(np.percentile(y, 98))
            # depth = a curve across (x) plus a lean back (y): the panels are tilted as well as bent
            k2, k1, k0, ky = np.linalg.lstsq(np.c_[x * x, x, np.ones_like(x), y - y0], z, rcond=None)[0]
            zc = lambda xx: k2 * xx * xx + k1 * xx + k0
            # the flat reference quad runs through the two ends; arc = how far the middle sits behind it
            r = lambda q: [round(float(t), 4) for t in q]
            sx = -float(swc[0])   # steering wheel centre, page x
            def quad(a, b):
                za, zb = zc(a), zc(b); n = np.array([-(zb - za), 0, (b - a)]); n /= np.linalg.norm(n)
                if n[2] < 0: n = -n
                dzt = ky * (y1 - y0); n = np.cross(np.array([b - a, 0, zb - za]), np.array([0, y1 - y0, dzt])); n /= np.linalg.norm(n)
                if n[2] < 0: n = -n
                bl = [a, y0, za]; br = [b, y0, zb]; tl = [a, y1, za + dzt]
                mid = (a + b) / 2; sag = zc(mid) - (za + zb) / 2   # + means the middle is further back (toward the driver) than the chord
                return {"bl": r(bl), "br": r(br), "tl": r(tl), "c": r([mid, (y0 + y1) / 2, (za + zb + dzt) / 2]), "n": r(n), "w": round(float(np.hypot(b - a, zb - za)), 4), "h": round(float(np.hypot(y1 - y0, dzt)), 4)}
            arc = {"k2": round(float(k2), 4), "k1": round(float(k1), 4), "k0": round(float(k0), 4)}
            if W > 1.2:   # pillar to pillar (Escalade, Escalade IQ, CELESTIQ): the whole strip, cluster in front of the driver
                m["pano"] = quad(x0, x1); m["pano"]["arc"] = arc
                cx1 = sx + 0.24; m["clu"] = quad(x0 + 0.03 if sx - 0.24 < x0 else sx - 0.24, cx1); m["clu"]["arc"] = arc
                if aux is not None:
                    A = aux - shift; Qa = np.array([P(v) for v in A]); c_ = Qa.mean(0); U_, S_, Vt = np.linalg.svd(Qa - c_); n = Vt[2]
                    if n[2] < 0: n = -n
                    u = np.array([1.0, 0, 0]); u -= n * (u @ n); u /= np.linalg.norm(u); v = np.cross(n, u)
                    if v[1] < 0: v = -v
                    a_ = (Qa - c_) @ u; b_ = (Qa - c_) @ v
                    m["scr"] = {"bl": r(c_ + u * a_.min() + v * b_.min()), "br": r(c_ + u * a_.max() + v * b_.min()), "tl": r(c_ + u * a_.min() + v * b_.max()),
                                "c": r(c_ + u * (a_.min() + a_.max()) / 2 + v * (b_.min() + b_.max()) / 2), "n": r(n), "w": round(float(a_.max() - a_.min()), 4), "h": round(float(b_.max() - b_.min()), 4)}
            else:   # 33-in. / 30-in. one-piece: cluster from the driver's end to just past the wheel's centre, the rest is the centre screen
                cut = min(sx + 0.2, x0 + (x1 - x0) * 0.45)
                m["clu"] = quad(x0, cut); m["scr"] = quad(cut + 0.012, x1)
                m["clu"]["arc"] = arc; m["scr"]["arc"] = arc; m["dashScreen"] = 1
            open(f"models/{key}.json", "w").write(json.dumps(out, separators=(",", ":")))
            print(f"  {key}: one-piece screen {W:.2f} m wide, curve k2={k2:.3f}")
    return out


if __name__ == "__main__":
    nums = [int(a) for a in sys.argv[3:] if a.isdigit()]
    main(sys.argv[1], sys.argv[2], *nums)
    import subprocess
    for t in ("fix_normals", "fix_seats", "fix_eye"):
        subprocess.run([sys.executable, f"tools/{t}.py", "--write", sys.argv[2]])
