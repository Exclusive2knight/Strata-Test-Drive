"""Import a structured car GLB (nodes: body, roof, glazing, wheel_front_left..., interior / cabin_*, steering_wheel,
driver_cluster or panoramic_display, center_touchscreen, driver_camera) into models/<key>.json.

    python3 tools/import_car.py Car.glb key

Meters, Y up, Z forward in the GLB. Uses the mesh helpers in /home/claude/strata (import_model, strata_mesh, web_export).
"""
import json, sys, re, colorsys
import numpy as np
sys.path.insert(0, "/home/claude/strata")
import import_model as M
from strata_mesh import clean, auto_smooth
from web_export import pack

WHEEL = {"wheel_front_left": "FL", "wheel_front_right": "FR", "wheel_rear_left": "RL", "wheel_rear_right": "RR"}
CABIN = re.compile(r"^(interior|headliner|cabin_.*|driver_cluster|cluster_information_display|panoramic_display|center_touchscreen|steering_wheel)$")
SCREEN_M = re.compile(r"blank display surface|display glass|display graphics|navigation", re.I)


def srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


def hexcol(c, pre="col_"):
    return pre + "".join(f"{int(round(v * 255)):02x}" for v in np.clip(c, 0, 1))   # linear, like the earlier imports


def main(src, key, budget=60000, cab_budget=42000):
    M.NODES = {}
    parts, _ = M.load_gltf(src)
    # GLB (X left, Y up, Z forward)  ->  vehicle space for pack(): +X left, -Y front, Z up
    for p in parts:
        V = p["V"]; p["V"] = np.stack([V[:, 0], -V[:, 2], V[:, 1]], 1)
    cam = M.NODES.get("driver_camera"); cam = np.array([cam[0], -cam[2], cam[1]]) if cam is not None else None
    wheels = {WHEEL[p["node"]]: [] for p in parts if p["node"] in WHEEL}
    for p in parts:
        if p["node"] in WHEEL: wheels[WHEEL[p["node"]]].append(p)
    if len(wheels) != 4: sys.exit("needs the four wheel_* nodes")
    hubs, R = {}, []
    for w, L in wheels.items():
        P = np.concatenate([q["V"] for q in L]); lo, hi = P.min(0), P.max(0); hubs[w] = (lo + hi) / 2; R.append((hi[2] - lo[2]) / 2)
    R = float(np.mean(R))
    allV = np.concatenate([p["V"] for p in parts])
    midY = float(np.mean([h[1] for h in hubs.values()])); dz = float(np.mean([h[2] for h in hubs.values()]) - R)
    shift = np.array([0.0, midY, dz])
    for p in parts: p["V"] = p["V"] - shift
    for w in hubs: hubs[w] = hubs[w] - shift
    if cam is not None: cam = cam - shift
    allV = allV - shift

    def mname(p, tri_c):
        n = p["mat"]["name"]; nl = n.lower(); node = p["node"]
        if node in WHEEL: return "strata_tire" if "rubber" in nl else "strata_rim"
        if CABIN.match(node):
            if SCREEN_M.search(n): return "strata_screen"
            return hexcol(p["mat"]["color"])
        if nl == "paint": return "strata_paint"
        if "glass" in nl and "edge" not in nl: return "strata_glass"
        if "led headlight" in nl: return "strata_headlight"
        if "brake light" in nl or "red light guide" in nl or "ruby lens" in nl: return "strata_taillight"
        if "indicator" in nl: return np.where(tri_c[:, 0] > 0, "strata_signal_L", "strata_signal_R")
        if "machined alloy" in nl: return "strata_chrome"
        if np.max(p["mat"]["emissive"]) > 0.4: return hexcol(p["mat"]["emissive"], "emi_")
        return hexcol(p["mat"]["color"])

    def collect(sel):
        Vs, Fs, Ms = [], [], []; o = 0
        for p in parts:
            if not sel(p): continue
            V, F = p["V"], p["F"]; tc = V[F].mean(1); nm = mname(p, tc)
            names = nm if isinstance(nm, np.ndarray) else np.array([nm] * len(F), dtype=object)
            Vs.append(V); Fs.append(F + o); Ms.extend(list(names)); o += len(V)
        if not Vs: return None
        return np.concatenate(Vs), np.concatenate(Fs), np.array(Ms, dtype=object)

    def build(data, bud, ctr=None):
        V, F, Ms = data
        if ctr is not None: V = V - ctr
        groups = []
        for n in sorted(set(Ms)):
            Fg = F[Ms == n]; used = np.unique(Fg); rm = -np.ones(len(V), int); rm[used] = np.arange(len(used)); groups.append((V[used], rm[Fg], n))
        groups = M.decimate(groups, bud)
        Vs, Fs, Mm = [], [], []; o = 0
        for Vg, Fg, n in groups: Vs.append(Vg); Fs.append(Fg + o); Mm += [n] * len(Fg); o += len(Vg)
        Vc, Fc, Mc = clean(np.concatenate(Vs), np.concatenate(Fs), Mm)
        while True:
            try: return pack(Vc, Fc, auto_smooth(Vc, Fc), Mc)
            except AssertionError:   # too many corners for 16-bit indices: thin it out a bit more
                bud = int(bud * 0.8); return build(data, bud, ctr)

    out = {"wheelZ": R, "wheelR": R, "wheels": {}, "objects": {}, "meta": {}}
    out["objects"]["body"] = build(collect(lambda p: p["node"] not in WHEEL and not CABIN.match(p["node"]) and p["node"] != "driver_camera"), budget)
    cab = collect(lambda p: CABIN.match(p["node"]) and p["node"] != "steering_wheel")
    if cab: out["objects"]["cabin"] = build(cab, cab_budget)
    sw = collect(lambda p: p["node"] == "steering_wheel"); steer_c = None
    if sw:
        steer_c = (sw[0][np.unique(sw[1])].min(0) + sw[0][np.unique(sw[1])].max(0)) / 2
        out["objects"]["steer"] = build(sw, 6000, steer_c)
    for w in ("FL", "RL", "FR", "RR"):
        h = hubs[w]; tire = collect(lambda p, w=w: p["node"] in WHEEL and WHEEL[p["node"]] == w and "rubber" in p["mat"]["name"].lower())
        rim = collect(lambda p, w=w: p["node"] in WHEEL and WHEEL[p["node"]] == w and "rubber" not in p["mat"]["name"].lower())
        out["objects"]["tire_" + w] = build(tire, 2500, h)
        out["objects"]["rim_" + w] = build(rim if rim else tire, 3000, h)
        out["wheels"][w] = [round(-float(h[0]), 4), round(float(h[2]), 4), round(float(h[1]), 4)]
    P = lambda v: [round(-float(v[0]), 4), round(float(v[2]), 4), round(float(v[1]), 4)]   # vehicle -> page (+x right, +y up, -z forward)
    m = out["meta"]; lo, hi = allV.min(0), allV.max(0); hw = max(abs(lo[0]), abs(hi[0]))
    m["length"] = round(float(hi[1] - lo[1]), 3); wv = allV[allV[:, 2] < ((cam[2] - 0.45) if cam is not None else 1.0)]; m["width"] = round(float(2 * np.abs(wv[:, 0]).max()), 3); m["height"] = round(float(hi[2]), 3)   # width below the mirrors
    m["wb"] = round(float(np.mean([hubs["RL"][1], hubs["RR"][1]]) - np.mean([hubs["FL"][1], hubs["FR"][1]])), 3)
    m["track"] = round(float(hubs["FL"][0] - hubs["FR"][0]), 3)
    def cent(pred):
        pts = [p["V"][np.unique(p["F"])] for p in parts if pred(p)]
        return np.concatenate(pts).mean(0) if pts else None
    hl = cent(lambda p: "led headlight" in p["mat"]["name"].lower() and not CABIN.match(p["node"]))
    if hl is not None:
        pts = np.concatenate([p["V"][np.unique(p["F"])] for p in parts if "led headlight" in p["mat"]["name"].lower() and not CABIN.match(p["node"])])
        pts = pts[(pts[:, 0] < 0) & (pts[:, 1] < 0)]; hl = pts.mean(0) if len(pts) else hl
        m["head"] = P(hl); m["head"][0] = abs(m["head"][0])
    else: m["head"] = [round(hw * 0.68, 3), round(R * 2.3, 3), round(float(lo[1]) + 0.15, 3)]
    tl = cent(lambda p: re.search(r"brake light|red light guide|ruby lens", p["mat"]["name"].lower()) and not CABIN.match(p["node"]))
    m["tail"] = [0, round(float(tl[2]), 4), round(float(tl[1]), 4)] if tl is not None else [0, round(R * 2.4, 3), round(float(hi[1]) - 0.1, 3)]
    eye = np.array([cam[0], steer_c[1] + 0.52, cam[2]]) if cam is not None and steer_c is not None else cam + np.array([0, 0.3, 0]) if cam is not None else np.array([hw * 0.38, lo[1] + m["length"] * 0.52, hi[2] * 0.85])
    m["eye"] = P(eye)
    steer = steer_c if steer_c is not None else eye + np.array([0, -0.52, -0.39])
    m["mirror"] = [round(float(hw + 0.05), 4), round(float(eye[2] - 0.26), 4), round(float(steer[1] - 0.11), 4)]
    # seats: row 1 beside the driver's eye, then every row the cabin has
    sy = round(float(eye[2]) - 0.794, 3); r1 = float(eye[1]) + 0.08; xs = round(float(abs(eye[0])), 3)
    rows = sorted(set(re.findall(r"cabin_seats_row_(\d)", " ".join(p["node"] for p in parts))))
    rowz = []
    for r in rows:
        c = cent(lambda p, r=r: p["node"] == f"cabin_seats_row_{r}"); rowz.append(float(c[1]))
    if not rowz:
        rowz = [r1, r1 + 1.0] + ([r1 + 1.85] if m["length"] > 5.25 and m["height"] > 1.7 else [])
    seats = [[xs, sy, round(rowz[0], 3)], [-xs, sy, round(rowz[0], 3)]]
    for z in rowz[1:]: seats += [[-xs, sy, round(z, 3)], [xs, sy, round(z, 3)], [0.0, round(sy - 0.046, 3), round(z, 3)]]
    m["seats"] = seats   # vehicle Y (-front) is the same as page z (-front)
    if steer_c is not None: m["steer"] = P(steer_c)
    def quad(node, f0=0.0, f1=1.0):
        pts = [p["V"][np.unique(p["F"])] for p in parts if p["node"] == node and SCREEN_M.search(p["mat"]["name"])]
        if not pts: return None
        Q = np.array([P(v) for v in np.concatenate(pts)]); c = Q.mean(0); U, S, Vt = np.linalg.svd(Q - c); n = Vt[2]
        if n[2] < 0: n = -n
        u = np.array([1.0, 0, 0]); u -= n * (u @ n); u /= np.linalg.norm(u); v = np.cross(n, u)
        if v[1] < 0: v = -v
        a = (Q - c) @ u; b = (Q - c) @ v; x0, x1 = a.min(), a.max(); y0, y1 = b.min(), b.max()
        x0, x1 = x0 + (x1 - x0) * f0, x0 + (x1 - x0) * f1
        r = lambda q: [round(float(t), 4) for t in q]
        bl = c + u * x0 + v * y0; br = c + u * x1 + v * y0; tl = c + u * x0 + v * y1; cc = c + u * (x0 + x1) / 2 + v * (y0 + y1) / 2
        return {"bl": r(bl), "br": r(br), "tl": r(tl), "c": r(cc), "n": r(n), "w": round(float(x1 - x0), 4), "h": round(float(y1 - y0), 4)}
    if any(p["node"] == "panoramic_display" for p in parts):   # a dash-wide screen (like the Nautilus): cluster on the left, map and passenger sections
        m["pano"] = quad("panoramic_display"); m["clu"] = quad("panoramic_display", 0, 0.2304)
        m["xs"] = {"nav": quad("panoramic_display", 0.3074, 0.5996), "pas": quad("panoramic_display", 0.6826, 1.0)}
    elif quad("driver_cluster"): m["clu"] = quad("driver_cluster")
    s = quad("center_touchscreen")
    if s: m["scr"] = s
    dst = f"models/{key}.json"
    open(dst, "w").write(json.dumps(out, separators=(",", ":")))
    import base64, os
    tris = sum(len(base64.b64decode(o["i"])) // 6 for o in out["objects"].values())
    print(f"{key}: {m['length']} m, wb {m['wb']}, track {m['track']}, R {R:.3f}, {tris} tris, {os.path.getsize(dst)//1024} KB")
    return out


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
