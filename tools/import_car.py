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

WHEEL = {"wheel_front_left": "FL", "wheel_front_right": "FR", "wheel_rear_left": "RL", "wheel_rear_right": "RR",
         "wheel_0_1": "FL", "wheel_0_-1": "FR", "wheel_1_1": "RL", "wheel_1_-1": "RR"}   # the heavy work-truck chassis names them by axle
# work equipment that moves (plows, salt spreader, rollback deck, wheel-lift): each its own object, centred on its box
EQUIP = re.compile(r"^(plow_A_frame|blade_left|blade_right|hopper|spinner_chute|rollback_deck|underlift|boom|warning_bar|tipping_body|gutter_brush_-?1|stop_arm|crossing_arm|(red|amber)_(left|right)_(front|rear)|mq_door_(FL|FR|RL|RR)|mq_tailgate|mq_mirror_[LR])$")
CABIN = re.compile(r"^(interior|headliner|driver_cab|passenger_seats|cabin_.*|driver_cluster|cluster_information_display|panoramic_display|center_touchscreen|flush_center_screen|period_dashboard|dash|dashboard|dashboard_trim|center_display|steering_wheel|steering_yoke)$")
SCREEN_M = re.compile(r"cluster_blank|infotainment_blank|blank screen|blank display surface|blank custom ui surface|blank custom display|blank center display|display glass|display graphics|navigation", re.I)


def srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


def hexcol(c, pre="col_"):
    return pre + "".join(f"{int(round(v * 255)):02x}" for v in np.clip(c, 0, 1))   # linear, like the earlier imports


def main(src, key, budget=60000, cab_budget=42000, wheels_only=False):
    M.NODES = {}
    parts, _ = M.load_gltf(src)
    # GLB (X left, Y up, Z forward)  ->  vehicle space for pack(): +X left, -Y front, Z up
    extra = []
    for p in parts:   # wheel nodes sometimes carry a stray far-away piece in the same mesh: give those triangles to the body
        hub = M.NODES.get(p["node"]) if p["node"].startswith("wheel") else None
        if hub is None: continue
        far = np.linalg.norm(p["V"][p["F"]].mean(1) - np.array(hub), axis=1) > 0.9
        if far.any() and not far.all():
            extra.append({**p, "node": "body", "F": p["F"][far]}); p["F"] = p["F"][~far]
        elif far.all(): p["node"] = "body"
    parts += extra
    for p in parts:
        V = p["V"]; p["V"] = np.stack([V[:, 0], -V[:, 2], V[:, 1]], 1)
    cam = M.NODES.get("driver_camera"); cam = np.array([cam[0], -cam[2], cam[1]]) if cam is not None else None
    for p in parts:   # buses: wheel_<1|-1>_<z> nodes, shell / driver_cab / passenger_seats
        m_ = re.match(r"^wheel_(-?1)_(-?[\d.]+)$", p["node"])
        if m_: WHEEL[p["node"]] = ("F" if float(m_.group(2)) > 0 else "R") + ("L" if m_.group(1) == "1" else "R")
    for p in parts:   # a stray part filed under a wheel node (high up: a mirror) belongs to the body
        if p["node"] in WHEEL and p["V"][:, 2].mean() > 1.4: p["node"] = "body"
    wheels = {WHEEL[p["node"]]: [] for p in parts if p["node"] in WHEEL}
    for p in parts:
        if p["node"] in WHEEL: wheels[WHEEL[p["node"]]].append(p)
    if len(wheels) != 4: sys.exit("needs the four wheel_* nodes")
    hubs, R = {}, []
    for w, L in wheels.items():
        P = np.concatenate([q["V"][np.unique(q["F"])] for q in L]); lo, hi = P.min(0), P.max(0); hubs[w] = (lo + hi) / 2; R.append((hi[2] - lo[2]) / 2)
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
        if node in WHEEL: return "strata_tire" if "rubber" in nl else "strata_rim" if max(p["mat"]["color"]) > 0.25 else hexcol(p["mat"]["color"])   # dark wheel faces stay dark (not silver)
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
    if wheels_only:   # rebuild only the wheels of an already imported model, keep everything else
        cur = json.load(open(f"models/{key}.json"))
        for w in ("FL", "RL", "FR", "RR"):
            h = hubs[w]
            tire = collect(lambda p, w=w: p["node"] in WHEEL and WHEEL[p["node"]] == w and "rubber" in p["mat"]["name"].lower())
            rim = collect(lambda p, w=w: p["node"] in WHEEL and WHEEL[p["node"]] == w and "rubber" not in p["mat"]["name"].lower())
            cur["objects"]["tire_" + w] = build(tire, 2500, h); cur["objects"]["rim_" + w] = build(rim if rim else tire, 3000, h)
        open(f"models/{key}.json", "w").write(json.dumps(cur, separators=(",", ":"))); print(key, "wheels rebuilt"); return cur
    out["objects"]["body"] = build(collect(lambda p: p["node"] not in WHEEL and not CABIN.match(p["node"]) and not EQUIP.match(p["node"]) and p["node"] != "driver_camera"), budget)
    eq = {}
    for nd in sorted({p["node"] for p in parts if EQUIP.match(p["node"])}):
        d = collect(lambda p, nd=nd: p["node"] == nd); Vu = d[0][np.unique(d[1])]; lo_, hi_ = Vu.min(0), Vu.max(0); c_ = (lo_ + hi_) / 2
        out["objects"]["eq_" + nd] = build(d, 9000, c_); eq[nd] = (c_, lo_, hi_)
    cab = collect(lambda p: CABIN.match(p["node"]) and p["node"] not in ("steering_wheel", "steering_yoke"))
    if cab: out["objects"]["cabin"] = build(cab, cab_budget)
    sw = collect(lambda p: p["node"] in ("steering_wheel", "steering_yoke")); steer_c = None
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
    def quad(node, f0=0.0, f1=1.0, pts=None):
        if pts is None: pts = [p["V"][np.unique(p["F"])] for p in parts if p["node"] == node and SCREEN_M.search(p["mat"]["name"])]
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
    elif quad("cabin_cluster_blank"): m["clu"] = quad("cabin_cluster_blank")   # Fusion set 2: blank screen nodes for our own UI
    elif quad("cluster_information_display"): m["clu"] = quad("cluster_information_display")
    elif steer_c is not None and any(p["node"] == "period_dashboard" for p in parts):
        # older dashboards: the gauge bezels (bright trim) sit in the dash right behind the steering wheel; the cluster screen covers them
        pts = [p["V"][np.unique(p["F"])] for p in parts if p["node"] == "period_dashboard" and re.search(r"machined alloy|led headlight", p["mat"]["name"].lower())]
        pts = np.concatenate(pts) if pts else np.zeros((0, 3))
        pts = pts[(np.abs(pts[:, 0] - steer_c[0]) < 0.25) & (pts[:, 2] > steer_c[2]) & (pts[:, 2] < steer_c[2] + 0.35)] if len(pts) else pts
        if len(pts) > 8:
            lo_, hi_ = pts.min(0), pts.max(0); yf = hi_[1] + 0.004   # vehicle space: -Y is forward, so this is just in front of the bezels, on the driver side
            r = lambda q: [round(float(t), 4) for t in q]
            bl = P([hi_[0], yf, lo_[2]]); br = P([lo_[0], yf, lo_[2]]); tl = P([hi_[0], yf, hi_[2]]); cc = P([(lo_[0] + hi_[0]) / 2, yf, (lo_[2] + hi_[2]) / 2])
            m["clu"] = {"bl": r(bl), "br": r(br), "tl": r(tl), "c": r(cc), "n": [0.0, 0.0, 1.0], "w": round(float(hi_[0] - lo_[0]), 4), "h": round(float(hi_[2] - lo_[2]), 4)}
    s = quad("center_touchscreen") or quad("flush_center_screen") or quad("center_display") or quad("cabin_infotainment_blank")
    if s: m["scr"] = s
    ps = quad("cabin_passenger_blank")
    if ps and "xs" not in m: m["xs"] = {"pas": ps}   # Monarch Q6: a third, passenger-side screen
    if ("clu" not in m or "scr" not in m) and cam is not None:
        # no named screen nodes (a refreshed cabin): the display glass in the dashboard, split into separate panels side by side;
        # the one in front of the driver is the cluster, the one nearest the middle is the centre screen
        F_ = [(p["V"], p["F"]) for p in parts if CABIN.match(p["node"]) and SCREEN_M.search(p["mat"]["name"])]
        if F_:
            tri = np.concatenate([V[F] for V, F in F_]); x0_ = tri[:, :, 0].min(1); x1_ = tri[:, :, 0].max(1); o_ = np.argsort(x0_); groups = []; cur = [o_[0]]; hi_x = x1_[o_[0]]
            for b_ in o_[1:]:   # panels: runs of triangles whose x spans overlap (a big panel's two triangles stay together)
                if x0_[b_] > hi_x + 0.03: groups.append(cur); cur = []; hi_x = x1_[b_]
                cur.append(b_); hi_x = max(hi_x, x1_[b_])
            groups.append(cur)
            area = lambda g: float(np.linalg.norm(np.cross(tri[g, 1] - tri[g, 0], tri[g, 2] - tri[g, 0]), axis=1).sum() / 2)
            G_ = [(tri[g].reshape(-1, 3), float((x0_[g].min() + x1_[g].max()) / 2), area(g)) for g in groups if len(g) >= 2]
            if "clu" not in m:
                d_ = [g for g in G_ if abs(g[1] - cam[0]) < 0.25]
                if d_: g = min(d_, key=lambda g: abs(g[1] - cam[0])); m["clu"] = quad(None, pts=[g[0]]); G_ = [x for x in G_ if x is not g]
            if "scr" not in m and G_:
                g = max(G_, key=lambda g: g[2] / (1 + 3 * abs(g[1]))); m["scr"] = quad(None, pts=[g[0]])   # the biggest panel, near the middle
    if eq:   # page coords: centre and box of each equipment piece
        def box(lo_, hi_):
            a, b = np.array(P(lo_)), np.array(P(hi_)); return [round(float(v), 4) for v in np.minimum(a, b)], [round(float(v), 4) for v in np.maximum(a, b)]
        m["equip"] = {k: {"c": P(c_), "lo": box(lo_, hi_)[0], "hi": box(lo_, hi_)[1]} for k, (c_, lo_, hi_) in eq.items()}
        mv = {k: v for k, v in m["equip"].items() if k.startswith("mq_")}   # opening doors / tailgate / folding mirrors: not work equipment
        if mv: m["parts"] = mv; m["equip"] = {k: v for k, v in m["equip"].items() if k not in mv} or None
        if not m["equip"]: del m["equip"]
    dst = f"models/{key}.json"
    if KEEP_SCREENS:   # a refreshed body on the same cabin with its screen graphics taken out: keep the screen spots from the model it replaces
        import os
        if os.path.exists(dst):
            old = json.load(open(dst)).get("meta", {})
            for k_ in ("scr", "clu", "pano", "xs"):
                if k_ not in m and k_ in old: m[k_] = old[k_]
    open(dst, "w").write(json.dumps(out, separators=(",", ":")))
    import base64, os
    tris = sum(len(base64.b64decode(o["i"])) // 6 for o in out["objects"].values())
    print(f"{key}: {m['length']} m, wb {m['wb']}, track {m['track']}, R {R:.3f}, {tris} tris, {os.path.getsize(dst)//1024} KB")
    return out


KEEP_SCREENS = "--keep-screens" in sys.argv
if __name__ == "__main__":
    sys.argv = [a for a in sys.argv if a != "--keep-screens"]
    if "--wheels" in sys.argv:
        main(sys.argv[1], sys.argv[2], wheels_only=True); sys.exit()
    nums = [int(a) for a in sys.argv[3:] if a.isdigit()]   # optional triangle budgets: body [cabin] (lighter for traffic-only vehicles)
    main(sys.argv[1], sys.argv[2], *nums)
    # these zips seat the driver under the steering wheel: move the seats back, then fit the eye height to the cabin
    import subprocess
    subprocess.run([sys.executable, "tools/fix_normals.py", "--write", sys.argv[2]])   # panels facing inward look grey
    subprocess.run([sys.executable, "tools/fix_seats.py", "--write", sys.argv[2]])
    subprocess.run([sys.executable, "tools/fix_eye.py", "--write", sys.argv[2]])
