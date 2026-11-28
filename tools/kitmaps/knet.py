# Road network -> snapped road kit pieces (and the game's road graph to match).
#
# A region of the map is described as junctions and the roads between them, each road with its kit profile (CITY2, CITY4, BLVD6D...).
# For every junction the planner picks the kit intersection piece whose legs fit the roads (fewest lane-change pieces), turns it to
# line up, then fills every road from one junction's leg to the next with the kit's own transition pieces (5 -> 4 lanes, 4 -> 2 lanes...),
# any fixed pieces asked for (a Michigan-left turnaround) and straights cut to length, all snapped connector to connector.
# The same plan gives the game its road graph: nodes at the junction centres, edges with the kit profile's lanes and widths, the
# turnaround as a crossover node, and where each junction's own surface ends on each leg.
import math, json

# the kit's lane-change pieces: (from profile, to profile) -> piece, its length
TRANS = {("CITY5", "CITY4"): ("city5_to_city4_48", 48.0), ("CITY4", "CITY5"): ("city4_to_city5_turnlane_48", 48.0),
         ("CITY4", "CITY2"): ("city4_to_city2_narrow_48", 48.0), ("CITY2", "CITY4"): ("city2_to_city4_widen_48", 48.0)}
SAME = [{"CITY2", "RES2"}, {"CITY2", "RURAL2"}, {"RES2", "RURAL2"}]   # butt straight onto each other
STRAIGHT = {"CITY2": "city2_st96", "CITY4": "city4_st96", "CITY5": "city5_st96", "CITY6D": "city6d_st96", "CITY8D": "city8d_st96",
            "BLVD6D": "blvd6d_st96", "RES2": "res2_st96", "RES2P": "res2p_st96", "RURAL2": "rural2_st96", "ONEWAY3": "oneway3_st96"}
# junction pieces the planner may use
JUNC = ["x_city2_4way", "x_city2_T", "x_city4_4way", "x_city4_city2_4way", "x_city4_res2_T", "x_city5_4way", "x_city5_city2_T",
        "x_city6d_4way", "x_city6d_city5_4way", "x_blvd6d_city5_4way", "x_res2_4way", "x_res2_T", "x_rural2_4way", "x_rural2_T"]
# kit profile -> the game's road: type and the overrides that put its lanes, kerbs and median where the kit paints them
GAME = {"CITY2": ("col", {"n": 1, "m": 0, "side": 0.6}), "CITY4": ("art", {"n": 2, "m": 0, "side": 0.15}),
        "CITY5": ("art", {"n": 2, "m": 3.6, "side": 0.3}), "BLVD6D": ("blvd", {"n": 3, "m": 14.4, "shL": 0.45, "side": 0.3}),
        "CITY6D": ("blvd", {"n": 3, "m": 4.8, "shL": 0.3, "side": 0.45}), "RES2": ("res", {}), "RURAL2": ("road", {})}
KERB = {"CITY2": 4.2, "RES2": 4.2, "RURAL2": 4.35, "CITY4": 7.35, "CITY5": 9.3, "BLVD6D": 18.3, "CITY6D": 13.2}
LANES = {"CITY2": 1, "RES2": 1, "RURAL2": 1, "CITY4": 2, "CITY5": 2, "CITY6D": 3, "BLVD6D": 3}


def same(a, b): return a == b or {a, b} in SAME


def chain(a, b):
    """lane-change pieces from profile a to b (shortest), or None"""
    if same(a, b): return []
    seen = {a: []}; q = [a]
    while q:
        p = q.pop(0)
        for (x, y), v in TRANS.items():
            if x == p and y not in seen:
                seen[y] = seen[p] + [(v[0], x, y, v[1])]
                if same(y, b): return seen[y]
                q.append(y)
    return None


def hd(dx, dy): return math.degrees(math.atan2(dx, dy)) % 360       # heading clockwise from north
def adiff(a, b): return abs(((a - b + 180) % 360) - 180)


class Net:
    def __init__(self, K):
        self.K = K; self.nodes = {}; self.roads = []; self.fail = []

    def node(self, nid, x, y, ctrl=None, piece=None, z=0.0):
        self.nodes[nid] = dict(id=nid, x=x, y=y, z=z, ctrl=ctrl, piece=piece, roads=[]); return nid

    def road(self, a, b, prof, name, lim=None, fixed=(), outside=False, toward=None):
        """fixed: [(piece, s from a's centre to the piece's middle, reversed?, crossover offset from the piece's 'in' end)]"""
        r = dict(a=a, b=b, prof=prof, name=name, lim=lim, fixed=list(fixed), outside=outside, toward=toward, i=len(self.roads))
        self.roads.append(r); self.nodes[a]["roads"].append((r, 0))
        if b in self.nodes: self.nodes[b]["roads"].append((r, 1))
        return r

    # ---- junctions
    def _dirs(self, n):
        out = []
        for r, end in n["roads"]:
            o = r["toward"] if r["outside"] else self.nodes[r["b"] if end == 0 else r["a"]]
            ox, oy = (o[0], o[1]) if r["outside"] else (o["x"], o["y"])
            out.append((r, end, hd(ox - n["x"], oy - n["y"])))
        return out

    CURVE = {"CITY2": ("city2_c90r18", 18.0), "CITY4": ("city4_c90r18", 18.0), "CITY5": ("city5_c90r19", 19.0), "RES2": ("res2_c90r18", 18.0),
             "CITY6D": ("city6d_c90r23", 23.0), "BLVD6D": ("blvd6d_c90r29", 29.0), "RURAL2": ("rural2_c90r18", 18.0)}

    def corner(self, n, D):
        """a right-angle bend: the kit's 90-degree curve, its ends on both roads R from the corner"""
        K = self.K; (r1, e1, h1), (r2, e2, h2) = D
        if r1["prof"] != r2["prof"] and not same(r1["prof"], r2["prof"]): self.fail.append(("corner profiles", n["id"])); return None
        pc, R = self.CURVE[r1["prof"]]
        for (ra, ea, ha), (rb, eb, hb) in (((r1, e1, h1), (r2, e2, h2)), ((r2, e2, h2), (r1, e1, h1))):
            tx, ty = n["x"] + R * math.sin(math.radians(ha)), n["y"] + R * math.cos(math.radians(ha))
            ux, uy = n["x"] + R * math.sin(math.radians(hb)), n["y"] + R * math.cos(math.radians(hb))
            v = K.piece(pc); cin = next(c for c in v["connectors"] if c["name"] == "in"); cout = next(c for c in v["connectors"] if c["name"] == "out")
            h = (ha + 180) % 360                      # travelling in from road a toward the corner
            ox, oy = K.tw(cout["pos"][0], cout["pos"][2], tx, ty, h)
            if math.hypot(ox - ux, oy - uy) < 0.3:
                out = K.start(pc, tx, ty, h, n["z"]); n["pc"] = pc
                n["legs"] = {(ra["i"], ea): (out["in"], ra["prof"], R), (rb["i"], eb): (out["out"], rb["prof"], R)}; return pc
        self.fail.append(("corner fit", n["id"], pc)); return None

    def pick(self, n):
        K = self.K; D = self._dirs(n); best = None
        if len(D) == 2 and abs(adiff(D[0][2], D[1][2]) - 90) < 3: return self.corner(n, D)
        cands = [n["piece"]] if n["piece"] else JUNC
        for pc in cands:
            v = K.piece(pc); legs = [c for c in v["connectors"] if c["name"].startswith("leg_")]
            if len(legs) != len(D): continue
            for rot in (0, 90, 180, 270):
                used = set(); cost = 0; M = {}
                for r, end, h in D:
                    m = [c for c in legs if c["name"] not in used and adiff((c["heading"] + rot) % 360, h) < 6]
                    if not m: break
                    c = m[0]; ch = chain(c["profile"], r["prof"])
                    if ch is None: break
                    used.add(c["name"]); M[(r["i"], end)] = c; cost += len(ch) + (0.5 if c["profile"] != r["prof"] and not ch else 0)   # (a near match, e.g. RES2 for CITY2, only when nothing exact fits)
                    # the road to a junction already placed: its legs and lane changes must fit between the two
                    o = None if r["outside"] else self.nodes.get(r["b"] if end == 0 else r["a"])
                    if o and o.get("legs") and (r["i"], 1 - end) in o["legs"]:
                        _, po, lo = o["legs"][(r["i"], 1 - end)]; ch2 = chain(c["profile"], po)
                        D_ = math.hypot(o["x"] - n["x"], o["y"] - n["y"]) - lo - math.hypot(c["pos"][0], c["pos"][2]) - sum(f[1] * 0 + K.piece(f[0])["size"][2] for f in r["fixed"])
                        if ch2 is None or sum(q[3] for q in ch2) > D_ + 0.01: cost += 100
                else:
                    size = max(math.hypot(c["pos"][0], c["pos"][2]) for c in legs)
                    key = (cost, size)
                    if best is None or key < best[0]: best = (key, pc, rot, M)
        if not best: self.fail.append(("no piece", n["id"], [(r["name"], r["prof"], round(h)) for r, _, h in D])); return None
        _, pc, rot, M = best
        out = K.start(pc, n["x"], n["y"], rot, n["z"])
        n["pc"] = pc; n["rot"] = rot; n["legs"] = {}
        for k, c in M.items(): n["legs"][k] = (out[c["name"]], c["profile"], math.hypot(c["pos"][0], c["pos"][2]))
        return pc

    # ---- roads
    def fill(self, r):
        K = self.K; A = self.nodes[r["a"]]; B = self.nodes.get(r["b"])
        hasA = (r["i"], 0) in A.get("legs", {}); hasB = bool(B) and (r["i"], 1) in B.get("legs", {})
        if not r["outside"] and not (hasA and hasB):
            # one end's junction got no kit piece: the road stays the old map's, with the lane changes off the kit junction at the other end
            r["fallback"] = True; r["fbEnd"] = 0 if hasA else 1 if hasB else None
            if not hasA and hasB:
                cb, pb, lb = B["legs"][(r["i"], 1)]; cur = cb; ch = chain(pb, r["prof"]) or []
                for nm, x, y, L in ch: cur = K.add(nm, cur)["out"]
                r["trimB"] = lb + sum(c[3] for c in ch); return
            if not hasA: return
        if not hasA: return
        ca, pa, la = A["legs"][(r["i"], 0)]
        if r["outside"] or r.get("fallback"):
            # leaves the region: only the lane change back to the road's own profile, the rest is the old map's straights
            cur = ca; ch = chain(pa, r["prof"]) or []
            for nm, x, y, L in ch: cur = K.add(nm, cur)["out"]
            r["trimA"] = la + sum(c[3] for c in ch); r["openA"] = cur; return
        cb, pb, lb = B["legs"][(r["i"], 1)]
        D = math.hypot(cb["x"] - ca["x"], cb["y"] - ca["y"])
        fixedL = sum(K.piece(f[0])["size"][2] for f in r["fixed"])
        offA = chain(pa, r["prof"]) or []; offB = chain(r["prof"], pb) or []
        if sum(c[3] for c in offA + offB) + fixedL > D - 0.5:
            offA = chain(pa, pb) or []; offB = []          # no room for the road's own lanes: straight from one junction's lanes to the other's
        if sum(c[3] for c in offA + offB) + fixedL > D + 0.01:
            self.fail.append(("too short", r["name"], A["id"], B["id"], round(D, 1), [c[0] for c in offA + offB], fixedL)); return
        free = D - sum(c[3] for c in offA + offB) - fixedL
        def straight(L, cur, prof):
            while L > 0.05:
                l = min(L, 96.0); cur = K.add(f"{STRAIGHT[prof]}@{l:.3f}", cur)["out"]; L -= l
            return cur
        cur = ca; prof = pa
        PP = [(0.0, pa), (la, pa)]; s_ = la
        for nm, x, y, L in offA: cur = K.add(nm, cur)["out"]; prof = y; s_ += L; PP.append((s_, y))
        mid = prof; sA = la + sum(c[3] for c in offA)          # distance from A's centre
        for pc, smid, rev, xo in sorted(r["fixed"], key=lambda f: f[1]):
            Lp = K.piece(pc)["size"][2]; gap = max(0.0, min(free, smid - Lp / 2 - sA))
            cur = straight(gap, cur, prof); free -= gap; sA += gap
            o = K.add(pc, cur, via="out" if rev else "in"); cur = o["in" if rev else "out"]
            r.setdefault("xo", []).append(sA + (Lp - xo if rev else xo)); sA += Lp
        cur = straight(free, cur, prof)
        Dc = math.hypot(B["x"] - A["x"], B["y"] - A["y"]); s_ = Dc - lb - sum(c[3] for c in offB); PP.append((s_, prof))
        for nm, x, y, L in offB: cur = K.add(nm, cur)["out"]; prof = y; s_ += L; PP.append((s_, y))
        PP += [(Dc - lb, pb), (Dc, pb)]; r["pp"] = PP
        miss = math.hypot(cur["x"] - cb["x"], cur["y"] - cb["y"])
        if miss > 0.05: self.fail.append(("miss", r["name"], A["id"], B["id"], round(miss, 3)))
        cur["used"] = cb["used"] = True
        r["trimA"] = la; r["trimB"] = lb; r["mid"] = mid

    def build(self):
        # the most constrained junctions first (a piece asked for, then the most roads), then outward from them, so each one is picked
        # knowing the junctions already placed at the other end of its roads
        todo = sorted(self.nodes.values(), key=lambda n: (not n["piece"], -len(n["roads"])))
        done = set(); order = []
        while todo:
            n = todo.pop(0)
            if n["id"] in done: continue
            q = [n]
            while q:
                m = q.pop(0)
                if m["id"] in done: continue
                done.add(m["id"]); order.append(m)
                for r, end in m["roads"]:
                    if r["outside"]: continue
                    o = self.nodes.get(r["b"] if end == 0 else r["a"])
                    if o and o["id"] not in done: q.append(o)
        for n in order:
            if len(n["roads"]) >= 2 or n["piece"]: self.pick(n)
        for r in self.roads: self.fill(r)
        return self.fail

    # ---- the game's road graph for this region: nodes [x, y, ctrl, kind], edges [type, name, pts, opts], and every kit junction leg's
    # stop bar [x, y, heading out, distance from the centre] (the game waits there and keeps its own junction surface inside it)
    def game(self, stops):
        N = []; E = []; LEGS = []
        corner = lambda n: n.get("pc", "").find("_c90") > 0
        for n in self.nodes.values():
            if corner(n): continue
            N.append([n["x"], n["y"], n["ctrl"], None])
            for (ri, end), (c, prof, reach) in (n.get("legs") or {}).items():
                st = (stops.get(n.get("pc"), {}) or {}).get(c["name"])
                leg = [n["x"], n["y"], round((c["h"]) % 360, 1), round(st if st else reach - 1.2, 2)]
                pr = next((q for q in self.K.piece(n["pc"])["connectors"] if q["name"] == "prop_signal_" + c["name"][4:]), None)
                if pr and "rot" in n:     # the kit's signal pole for traffic coming in on this leg (far right corner)
                    px, py = self.K.tw(pr["pos"][0], pr["pos"][2], n["x"], n["y"], n["rot"]); leg += [round(px, 2), round(py, 2)]
                LEGS.append(leg)
        done = set()
        for r in self.roads:
            if r["outside"] or r.get("fallback") or r["i"] in done: continue
            # a road round a kit corner piece is one edge with a rounded corner ([x, y, R])
            chainR = [r]; a = self.nodes[r["a"]]; b = self.nodes[r["b"]]
            pts = [[a["x"], a["y"]]]
            cur, end_n = r, b
            while corner(end_n):
                nxt = next((q for q, e_ in end_n["roads"] if q is not cur), None)
                if not nxt or nxt["outside"]: break
                pts.append([end_n["x"], end_n["y"], self.CURVE[cur["prof"]][1]]); done.add(nxt["i"])
                end_n = self.nodes[nxt["b"] if nxt["a"] == end_n["id"] else nxt["a"]]; cur = nxt
            typ, o = GAME.get(r.get("mid") or r["prof"], GAME.get(r["prof"], ("col", {})))
            o = dict(o); o["kit"] = 1
            PP = r.get("pp"); rev = False
            if PP and len(pts) == 1:
                profs = {p for _, p in PP}
                if profs <= {"CITY4", "CITY5"} and "CITY5" in profs and "CITY4" in profs:
                    # four lanes that open a centre turn lane: the game's median grows over the lane-change piece (narrow end first)
                    typ, o = "art", {"n": 2, "m": 3.6, "side": 0.3, "kit": 1}
                    if PP[0][1] == "CITY5": rev = True; PP = [(PP[-1][0] - s_, p_) for s_, p_ in PP[::-1]]
                    a5 = next(s_ for s_, p_ in PP if p_ == "CITY5"); a4 = max(s_ for s_, p_ in PP if p_ == "CITY4" and s_ <= a5)
                    o["tp"] = [round(a4, 2), round(a5, 2), 0]
                elif any(LANES.get(p, 1) == 1 for p in profs) and any(LANES.get(p, 1) == 2 for p in profs):
                    # two lanes that widen to four (or five) near a junction: the game keeps one lane each way and adds the kit's
                    # extra width as kerb-to-kerb room each side (auxW), ramping over the lane-change piece
                    typ, o = "col", {"n": 1, "m": 0, "side": 0.6, "kit": 1}
                    S_ = [[round(s_, 2), round(KERB[p_] - KERB["CITY2"], 2)] for s_, p_ in PP]
                    o["aux"] = [{"u0": S_[0][0], "u1": S_[-1][0], "sg": sg, "S": S_, "kit": 1} for sg in (1, -1)]
            if rev: pts = [[b["x"], b["y"]]]; a, b = b, a; end_n = b
            if r["lim"]: o["lim"] = r["lim"]
            L = math.hypot(b["x"] - a["x"], b["y"] - a["y"]); xs = []
            for s in r.get("xo", []):
                f = s / L; xs.append([round(a["x"] + (b["x"] - a["x"]) * f, 2), round(a["y"] + (b["y"] - a["y"]) * f, 2)])
                N.append([xs[-1][0], xs[-1][1], None, "xo"])
            full = [pts[0]] + xs + pts[1:] + [[end_n["x"], end_n["y"]]]
            # split at the crossovers (each is a node of its own)
            seg = [full[0]]
            for p in full[1:]:
                seg.append(p)
                if len(p) == 2: E.append([typ, r["name"], seg, o]); seg = [p]
        return {"nodes": N, "edges": E, "legs": LEGS}
