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


class Kit:
    def __init__(self, root):
        self.man = {v["name"]: v for v in json.load(open(os.path.join(root, "manifest.json")))["pieces"]}
        self.place = []        # [name, x, y, h]
        self.conns = []        # every placed connector: dict(x, y, h, prof, flow, piece index, name, used)

    # kit local (X right, -Z forward) -> world, for a piece at (x, y) turned h degrees clockwise
    @staticmethod
    def tw(px, pz, x, y, h):
        c, s = math.cos(h * D2R), math.sin(h * D2R)
        ex, ny = px, -pz                      # kit X -> east, kit -Z -> north
        return x + ex * c + ny * s, y - ex * s + ny * c

    def _put(self, name, x, y, h):
        v = self.man[name]; i = len(self.place)
        self.place.append([name, round(x, 4), round(y, 4), round(h % 360, 4)])
        out = {}
        for c in v["connectors"]:
            if c["profile"] == "PROP": continue
            wx, wy = self.tw(c["pos"][0], c["pos"][2], x, y, h)
            rec = {"x": wx, "y": wy, "h": (c["heading"] + h) % 360, "prof": c["profile"], "flow": c.get("flow", "both"), "pi": i, "name": c["name"], "used": False, "z": c["pos"][1]}
            self.conns.append(rec); out[c["name"]] = rec
        return out

    def start(self, name, x=0.0, y=0.0, h=0.0):
        return self._put(name, x, y, h)

    def add(self, name, at, via="in", mirror_ok=False):
        """snap `name` so its connector `via` sits on the open connector `at` (facing it)"""
        v = self.man[name]
        c = next(c for c in v["connectors"] if c["name"] == via)
        if c["profile"] != at["prof"] and not mirror_ok:
            raise ValueError(f"{name}.{via} is {c['profile']}, the joint is {at['prof']}")
        # the new connector must face the opposite way: c.heading + h = at.h + 180
        h = (at["h"] + 180 - c["heading"]) % 360
        ox, oy = self.tw(c["pos"][0], c["pos"][2], 0, 0, h)
        out = self._put(name, at["x"] - ox, at["y"] - oy, h)
        at["used"] = True; out[via]["used"] = True
        return out

    def check(self, tol=0.02):
        """pair up connectors that coincide; report mismatches and open ends"""
        joints, bad = [], []
        C = self.conns
        for i, a in enumerate(C):
            for b in C[i + 1:]:
                if a["pi"] == b["pi"]: continue
                d = math.hypot(a["x"] - b["x"], a["y"] - b["y"])
                if d > 0.5: continue
                dh = abs(((a["h"] - b["h"]) % 360) - 180)
                ok = d <= tol and dh <= 0.5 and a["prof"] == b["prof"] and abs(a["z"] - b["z"]) < 0.05
                (joints if ok else bad).append([a["pi"], a["name"], b["pi"], b["name"], round(d, 3), round(dh, 2), a["prof"], b["prof"]])
                a["used"] = b["used"] = True
        opn = [[c["pi"], self.place[c["pi"]][0], c["name"], round(c["x"], 2), round(c["y"], 2), round(c["h"], 1), c["prof"]] for c in C if not c["used"]]
        return joints, bad, opn


def preview(K, root, path):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.dirname(__file__))
    from kit_pack import piece
    cache = {}
    f, ax = plt.subplots(figsize=(14, 14))
    for name, x, y, h in K.place:
        if name not in cache:
            d = piece(os.path.join(root, K.man[name]["file"])); cache[name] = d
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
    json.dump({"place": K.place, "joints": joints, "bad": bad, "open": opn}, open(out, "w"), separators=(",", ":"))
    print(f"{len(K.place)} pieces, {len(joints)} joints, {len(bad)} BAD joints, {len(opn)} open ends")
    for b in bad[:20]: print("  BAD", b)
    for o in opn[:30]: print("  open", o)
    if len(sys.argv) > 4: preview(K, root, sys.argv[4])
