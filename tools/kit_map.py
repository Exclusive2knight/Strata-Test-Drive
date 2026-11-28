"""Build a map from road kit pieces snapped together at their connectors, check every joint, and draw a top-down preview.

    python3 tools/kit_map.py <roadkit folder> <layout script.py> <out props/kitmap.json> [preview.png]

The layout script gets a `K` (a Kit) and places pieces with it:

    a = K.start("x_city4_4way", x=0, y=0, h=0)          # first piece: its origin at world (x, y), turned h degrees (0 = kit -Z = world north)
    s = K.add("city4_st96", a["leg_N"])                   # snap the piece's "in" connector onto an open connector (returns its connectors)
    b = K.add("x_city4_4way", s["out"], via="leg_S")      # or pick which of its connectors goes on the joint

World axes: x east, y north (the game's road-graph axes). Kit -Z is world north when h = 0, kit +X is east.
A connector pose is (x, y, heading): heading in degrees clockwise from north, pointing OUT of its piece.
Two connectors mate when their positions coincide, they face opposite ways and their profiles match; K.check() reports every
open end and every joint that is off by more than 2 cm / 0.5 deg or has a profile mismatch.

Output: {"place": [[piece, x, y, heading], ...], "joints": [...], "open": [...]}
"""
import sys, json, math, os

D2R = math.pi / 180


# profiles with the same lanes and nearly the same kerb line: allowed to butt straight onto each other (no kit transition piece exists)
COMPAT = [{"CITY2", "RES2"}, {"CITY2", "RURAL2"}, {"RES2", "RURAL2"}]


def near_pairs(C, r):
    """every pair of connectors within r of each other (grid buckets, so big maps stay fast)"""
    G = {}
    for i, c in enumerate(C): G.setdefault((math.floor(c["x"] / 2), math.floor(c["y"] / 2)), []).append(i)
    for (gx, gy), L in G.items():
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                M = G.get((gx + dx, gy + dy))
                if not M: continue
                for i in L:
                    for j in M:
                        if j <= i: continue
                        a, b = C[i], C[j]
                        if abs(a["x"] - b["x"]) <= r and abs(a["y"] - b["y"]) <= r: yield i, a, b


def flow_ok(a, b):
    fa, fb = a.get("flow", "both"), b.get("flow", "both")
    return fa == "both" or fb == "both" or fa != fb


class Kit:
    def __init__(self, root):
        self.man = {v["name"]: v for v in json.load(open(os.path.join(root, "manifest.json")))["pieces"]}
        self.place = []        # [name, x, y, h, z]        # [name, x, y, h]
        self.conns = []        # every placed connector: dict(x, y, h, prof, flow, piece index, name, used)

    # kit local (X right, -Z forward) -> world, for a piece at (x, y) turned h degrees clockwise
    @staticmethod
    def tw(px, pz, x, y, h):
        c, s = math.cos(h * D2R), math.sin(h * D2R)
        ex, ny = px, -pz                      # kit X -> east, kit -Z -> north
        return x + ex * c + ny * s, y - ex * s + ny * c

    def piece(self, name):
        """a kit piece, or a straight clipped to any length: "city4_st96@37.5" (the 96 m straight cut to 37.5 m)"""
        if name in self.man: return self.man[name]
        if "%" in name:                       # kerb moved sideways: same joints
            i = name.index("%"); rest = name[i + 1:]; tail = "!f" if rest.endswith("!f") else ""
            v = dict(self.piece(name[:i] + tail)); v["name"] = name; self.man[name] = v; return v
        if name.endswith("!l"):            # v38.1: no sidewalk on its left (a boulevard carriageway beside a narrow median): same joints
            v = dict(self.piece(name[:-2])); v["name"] = name; self.man[name] = v; return v
        if name.endswith("!p"):            # flyover deck without its pier: same joints
            v = dict(self.piece(name[:-2])); v["name"] = name; self.man[name] = v; return v
        if name.endswith("!f"):            # no kerb / sidewalk: same joints as the full piece
            v = dict(self.piece(name[:-2])); v["name"] = name; v["flat"] = True; self.man[name] = v; return v
        base, L = name.split("@"); R = 0.0; dz = 0.0
        if "^" in L: L, dz = L.split("^"); dz = float(dz.split(",")[0])
        if "~" in L: L, R = L.split("~"); R = float(R)
        L = float(L); v = json.loads(json.dumps(self.man[base]))
        for c in v["connectors"]:
            if c["name"] == "out":
                if R:                                   # bent: the end sits round the arc and turns by L / R
                    th = L / R; c["pos"][0] = R - R * math.cos(th); c["pos"][2] = -R * math.sin(th); c["heading"] = (math.degrees(th)) % 360
                else: c["pos"][2] = -L
                c["pos"][1] = dz
        v["name"] = name; v["clip"] = [base, L]; v["bend"] = R; v["dz"] = dz; self.man[name] = v
        return v

    def _put(self, name, x, y, h, z=0.0):
        v = self.piece(name); i = len(self.place)
        self.place.append([name, round(x, 4), round(y, 4), round(h % 360, 4), round(z, 4)])
        out = {}
        for c in v["connectors"]:
            if c["profile"] == "PROP": continue
            wx, wy = self.tw(c["pos"][0], c["pos"][2], x, y, h)
            rec = {"x": wx, "y": wy, "h": (c["heading"] + h) % 360, "prof": c["profile"], "flow": c.get("flow", "both"), "pi": i, "name": c["name"], "used": False, "z": z + c["pos"][1]}
            self.conns.append(rec); out[c["name"]] = rec
        return out

    def start(self, name, x=0.0, y=0.0, h=0.0, z=0.0):
        return self._put(name, x, y, h, z)

    def add(self, name, at, via="in", mirror_ok=False):
        """snap `name` so its connector `via` sits on the open connector `at` (facing it)"""
        v = self.piece(name)
        c = next(c for c in v["connectors"] if c["name"] == via)
        if c["profile"] != at["prof"] and not mirror_ok and {c["profile"], at["prof"]} not in COMPAT:
            raise ValueError(f"{name}.{via} is {c['profile']}, the joint is {at['prof']}")
        # the new connector must face the opposite way: c.heading + h = at.h + 180
        h = (at["h"] + 180 - c["heading"]) % 360
        ox, oy = self.tw(c["pos"][0], c["pos"][2], 0, 0, h)
        out = self._put(name, at["x"] - ox, at["y"] - oy, h, at["z"] - c["pos"][1])
        at["used"] = True; out[via]["used"] = True
        return out

    def check(self, tol=0.12):
        """pair up connectors that coincide; report mismatches and open ends"""
        joints, bad = [], []
        C = self.conns
        for i, a, b in near_pairs(C, 0.5):
            if True:
                if a["pi"] == b["pi"]: continue
                d = math.hypot(a["x"] - b["x"], a["y"] - b["y"])
                if d > 0.5: continue
                dh = abs(((a["h"] - b["h"]) % 360) - 180)
                if dh > 90: continue          # same way round: the two carriageways of a freeway share the median line, they don't join
                if not flow_ok(a, b): continue   # an "out" only joins an "in": the other carriageway's joints sit on the same spot
                ok = d <= tol and dh <= 0.5 and (a["prof"] == b["prof"] or {a["prof"], b["prof"]} in COMPAT) and abs(a["z"] - b["z"]) < 0.05
                (joints if ok else bad).append([a["pi"], a["name"], b["pi"], b["name"], round(d, 3), round(dh, 2), a["prof"], b["prof"]])
                a["used"] = b["used"] = True
        opn = [[c["pi"], self.place[c["pi"]][0], c["name"], round(c["x"], 2), round(c["y"], 2), round(c["h"], 1), c["prof"]] for c in C if not c["used"]]
        return joints, bad, opn


# kit profile -> the game's road type (+ overrides so its lanes sit where the kit paints them)
PROF = {"CITY2": ("col", {}), "CITY4": ("art", {}), "CITY5": ("art", {"m": 3.6}), "CITY6D": ("blvd", {"m": 5.1, "shL": 0.2}),
        "CITY8D": ("blvd", {"n": 4, "m": 5.1, "shL": 0.2}), "BLVD6D": ("blvd", {"m": 14.0}), "RES2": ("res", {}), "RES2P": ("st", {}),
        "RURAL2": ("road", {}), "RURAL2P": ("road", {}), "FOREST2": ("road", {}), "RAMP1": ("ramp", {}), "RAMP2": ("ramp", {"n": 2, "m": -7.2}),
        "ONEWAY3": ("sd", {"n": 3, "m": -10.8}), "SVC3": ("sd", {"n": 3, "m": -10.8}), "SVC2": ("sd", {}), "FWY3G": ("fwyc", {}), "FWY3B": ("fwyc", {"m": 0.6})}
LANES = {"CITY2": 1, "RES2": 1, "RES2P": 1, "RURAL2": 1, "CITY4": 2, "CITY5": 2, "CITY6D": 3, "CITY8D": 4, "BLVD6D": 3, "RAMP1": 1, "RAMP2": 2}
ONEWAY = {"RAMP1", "RAMP2", "ONEWAY3", "SVC3", "SVC2", "FWY2G", "FWY3G", "FWY4G", "FWY5G", "FWY2B", "FWY3B", "FWY4B", "FWY5B"}


def centreline(K, i):
    """world points along a linear piece from its first road connector to its second (an arc when the headings differ)"""
    name, x, y, h, z = K.place[i]
    cs = [c for c in K.piece(name)["connectors"] if c["profile"] != "PROP"]
    a, b = cs[0], cs[1]
    A = K.tw(a["pos"][0], a["pos"][2], x, y, h) + (z + a["pos"][1],); B = K.tw(b["pos"][0], b["pos"][2], x, y, h) + (z + b["pos"][1],)
    ha = (a["heading"] + h + 180) % 360; hb = (b["heading"] + h) % 360       # travel direction leaving A, arriving at B
    turn = ((hb - ha + 540) % 360) - 180
    if abs(turn) < 0.5: return [A, B], a["name"], b["name"]
    # circle through A tangent to ha: centre on the side the road turns to
    R = math.hypot(B[0] - A[0], B[1] - A[1]) / (2 * math.sin(abs(turn) * D2R / 2))
    sgn = 1 if turn > 0 else -1                      # +: turning right (clockwise)
    hr = (ha + 90 * sgn) * D2R
    cx, cy = A[0] + R * math.sin(hr), A[1] + R * math.cos(hr)
    a0 = math.atan2(A[0] - cx, A[1] - cy)
    n = max(2, int(abs(turn) / 6) + 1); pts = []
    for k in range(n + 1):
        t = a0 + sgn * abs(turn) * D2R * k / n
        pts.append((cx + R * math.sin(t), cy + R * math.cos(t), A[2] + (B[2] - A[2]) * k / n))
    return pts, a["name"], b["name"]


def graph(K, names=None):
    """chains of linear pieces between junctions -> edges [type, name, pts, opts]; junctions -> nodes [x, y, ctrl]"""
    C = K.conns; key = lambda c: (c["pi"], c["name"])
    mate = {}
    for i, a, b in near_pairs(C, 0.15):
            if a["pi"] != b["pi"] and math.hypot(a["x"] - b["x"], a["y"] - b["y"]) < 0.15 and abs(((a["h"] - b["h"]) % 360) - 180) < 5 and flow_ok(a, b): mate[key(a)] = b; mate[key(b)] = a
    byp = {}
    for c in C: byp.setdefault(c["pi"], []).append(c)
    # two-ended pieces are part of the road even when the profile changes (city5 -> city4 transitions): a node there would make the
    # lanes jump sideways and the traffic stop. The edge takes the lane layout of the end it starts from.
    linear = {i for i, cs in byp.items() if len(cs) == 2}
    nodes, edges, done = [], [], set()
    jpos = {}; jin = {}        # jin[(piece, connector)]: points from the junction's node out to that connector (the ramp's own path)
    # freeway exits and entrances: the node sits on the median line where the ramp leaves / joins, the ramp curves away along the
    # deceleration / acceleration lane to its connector (kit local X right, Z back; exits leave near the start, entrances join near the end)
    RAMPJ = {"fwy3g_exit_336": (-140, [(21.6, -200), (25.0, -290)]), "fwy3g_entrance_432": (-310, [(21.6, -230), (24.0, -80)]),
             "fwy3g_exit_2lane_480": (-200, [(23.4, -270), (27.0, -400)]), "fwy3g_entrance_2lane_528": (-400, [(23.4, -300), (26.0, -100)])}
    for i, cs in byp.items():
        if i in linear: continue
        nm, px, py, ph, pz = K.place[i]
        if nm in RAMPJ:
            zn, via = RAMPJ[nm]; jx, jy = K.tw(0, zn, px, py, ph); jz = pz
            for c in cs:
                if c["prof"].startswith("RAMP"): jin[(i, c["name"])] = [K.tw(vx, vz, px, py, ph) + (pz,) for vx, vz in via] + [(c["x"], c["y"], c["z"])]
            jpos[i] = (jx, jy, jz); nodes.append([round(jx, 3), round(jy, 3), "merge", round(jz, 3)]); continue
        jx = sum(c["x"] for c in cs) / len(cs); jy = sum(c["y"] for c in cs) / len(cs); jz = sum(c["z"] for c in cs) / len(cs)
        ctrl = "signal" if nm.startswith("x_city") or nm.startswith("x_blvd") or nm.startswith("x_oneway") or nm.startswith("x_svc") else None
        jpos[i] = (jx, jy, jz); nodes.append([round(jx, 3), round(jy, 3), ctrl, round(jz, 3)])
    starts = [c for c in C if c["pi"] not in linear] + [c for c in C if c["pi"] in linear and key(c) not in mate]
    for s in starts:
        if key(s) in done: continue
        pts = []
        if s["pi"] in jpos: pts.append(jpos[s["pi"]])
        if key(s) in jin: pts += jin[key(s)][:-1]
        pts.append((s["x"], s["y"], s["z"])); done.add(key(s))
        cur = mate.get(key(s)) if s["pi"] not in linear else s
        prof = s["prof"]; end = None; profs_seen = {prof}
        while cur is not None and cur["pi"] in linear:
            done.add(key(cur))
            profs_seen |= {c["prof"] for c in byp[cur["pi"]]}
            cl, n0, n1 = centreline(K, cur["pi"])
            if cur["name"] != n0: cl = cl[::-1]
            pts += [p for p in cl[1:]]
            other = next(c for c in byp[cur["pi"]] if c is not cur); done.add(key(other))
            nxt = mate.get(key(other))
            if nxt is None: end = None; cur = None; break
            if nxt["pi"] not in linear: end = nxt; done.add(key(nxt)); break
            if key(nxt) in done: break          # a closed loop of road with no junction on it
            cur = nxt
        if end is not None:
            pts.append((end["x"], end["y"], end["z"]))
            if key(end) in jin: pts += jin[key(end)][:-1][::-1]
            pts.append(jpos[end["pi"]])
        if len(pts) < 2: continue
        # drop repeated points
        P = [pts[0]]
        for p in pts[1:]:
            if math.hypot(p[0] - P[-1][0], p[1] - P[-1][1]) > 0.05: P.append(p)
        if len(P) < 2: continue
        # the lane layout of the narrowest profile the road runs through (a four-lane street that narrows to two is modelled as two)
        if profs_seen:
            prof = min(profs_seen, key=lambda q: (LANES.get(q, 9), 0 if q == "CITY4" else 1))
        typ, o = PROF.get(prof, ("road", {}))
        # one-way roads run the way the traffic flows: a junction's "in" connector takes traffic into the junction, an open end's "out" lets it leave
        if prof in ONEWAY and ((s["pi"] not in linear and s.get("flow") == "in") or (s["pi"] in linear and s.get("flow") == "out")): P = P[::-1]
        o = dict(o)
        if any(abs(p[2]) > 0.01 for p in P): o["kz"] = [round(p[2], 3) for p in P]   # heights at each point (bridges, ramps)
        edges.append([typ, (names or {}).get(len(edges), ""), [[round(p[0], 3), round(p[1], 3)] for p in P], o])
    return nodes, edges


def preview(K, root, path):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.dirname(__file__))
    from kit_pack import piece, clip, bend, slope
    cache = {}
    f, ax = plt.subplots(figsize=(14, 14))
    for name, x, y, h, z in K.place:
        if name not in cache:
            v = K.piece(name); d = piece(os.path.join(root, K.man[v["clip"][0] if "clip" in v else name]["file"]))
            if "clip" in v: d = bend(slope(clip(d, 96.0 if "_st96" in v["clip"][0] else 48.0 if "_st48" in v["clip"][0] else 24.0, v["clip"][1]), v["clip"][1], v.get("dz", 0.0)), v.get("bend", 0.0))
            cache[name] = d
        d = cache[name]; P = d["p"]; I = d["i"]
        pts = [K.tw(P[k] / 100, P[k + 2] / 100, x, y, h) for k in range(0, len(P), 3)]
        for t in range(0, len(I), 3):
            tri = [pts[I[t]], pts[I[t + 1]], pts[I[t + 2]]]
            ax.fill([q[0] for q in tri], [q[1] for q in tri], color="#555", lw=0)
    for c in K.conns:
        if not c["used"]: ax.plot(c["x"], c["y"], "ro", ms=4)
    ax.set_aspect("equal"); plt.savefig(path, dpi=110)


if __name__ == "__main__":
    root, script, out = sys.argv[1:4]
    K = Kit(root)
    exec(open(script).read(), {"K": K, "math": math})
    joints, bad, opn = K.check()
    # a layout that only dresses an existing road graph (the old map rebuilt in kit pieces) sets K.nograph
    nodes, edges = ([], []) if getattr(K, "nograph", False) else graph(K, getattr(K, "names", None))
    json.dump({"place": K.place, "kj": getattr(K, "kj", []), "nodes": nodes, "edges": edges, "joints": joints, "bad": bad, "open": opn}, open(out, "w"), separators=(",", ":"))
    print(f"graph: {len(nodes)} junctions, {len(edges)} edges")
    print(f"{len(K.place)} pieces, {len(joints)} joints, {len(bad)} BAD joints, {len(opn)} open ends")
    for b in bad[:20]: print("  BAD", b)
    for o in opn[:30]: print("  open", o)
    if len(sys.argv) > 4: preview(K, root, sys.argv[4])
