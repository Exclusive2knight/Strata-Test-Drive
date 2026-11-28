# The old map rebuilt from road kit pieces: every old road is followed by kit straights cut to length, bent to its curve and graded
K.nograph = True   # the game keeps the old road graph; these pieces only replace how the roads look
# to its heights; the freeway's two carriageways are separate kit pieces either side of its centre line. Junction areas are left for
# kit junction pieces (next step). Reads tools/kitmaps/oldnet.json (exported from the game's own road graph).
import json, math, os
NET = json.load(open("tools/kitmaps/oldnet.json"))
BASE = {"st": "res2p_st96", "ave": "city4_st96", "road": "rural2_st96", "res": "res2_st96", "art": "city4_st96", "col": "city2_st96",
        "blvd": "blvd6d_st96", "ramp": "ramp1_st96", "rbt": "ramp1_st96", "sd": "svc2_st96", "aw": "svc3_st96", "curb": "svc3_st96",
        "lane": "forest2_st96", "dirt": "rural2_st96", "xway": "fwy3g_st96"}
EDGE = {"res2p_st96": 6.05, "city4_st96": 7.35, "city2_st96": 4.2, "res2_st96": 4.2, "rural2_st96": 4.35, "blvd6d_st96": 18.3, "forest2_st96": 3.6}   # x of the kerb / road edge
SEG = 16.0          # metres per piece: short enough that a bent straight follows any of the old curves within a few cm

def head(a, b): return math.degrees(math.atan2(b[0] - a[0], b[1] - a[1])) % 360

def follow(P, base, side=0.0, flat=(0, 0), dw=0.0, tag="", one=False):
    """kit pieces along polyline P (x, y, z), each placed on its own sample point and tangent and bent to reach the next one
    (no chaining, so nothing drifts); side shifts the pieces right of the line (the freeway carriageways)"""
    if len(P) < 2: return
    D = [0.0]
    for i in range(1, len(P)): D.append(D[-1] + math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]))
    L = D[-1]
    if L < 1: return
    hilly = max(p[2] for p in P) - min(p[2] for p in P) > 0.5
    def at(d):
        d = min(L, max(0.0, d)); i = 0
        while i < len(D) - 2 and D[i + 1] < d: i += 1
        f = (d - D[i]) / max(1e-9, D[i + 1] - D[i])
        return [P[i][j] + (P[i + 1][j] - P[i][j]) * min(1, max(0, f)) for j in range(3)]
    # v37.5: on curves the pieces get shorter (at most 4 degrees of turn each) and every piece starts on the road's own tangent there,
    # so a bent piece ends nearly on the next one's heading (32 m pieces on a 60 m ramp loop met at 20-40 degree kinks: the choppy ramps)
    turn = 0.0
    for i in range(1, len(P) - 1):
        if D[i] - D[i - 1] < 0.05 or D[i + 1] - D[i] < 0.05: continue
        turn += abs((head(P[i], P[i + 1]) - head(P[i - 1], P[i]) + 540) % 360 - 180)
    curvy = base.startswith(("ramp", "svc"))   # v38: ramps and service drives: shorter pieces, at most 1.5 degrees of turn each (the 4-degree joints showed as kinks and a stepped verge)
    n = 1 if one else max(1, round(L / (SEG if hilly or curvy else 32.0)), min(int(L / 2.5), math.ceil(turn / (1.5 if curvy else 2.5)))); pts = [at(L * k / n) for k in range(n + 1)]      # short pieces only where the road climbs or turns
    tan = [head(at(L * k / n - 2.0), at(L * k / n + 2.0)) if 0 < k < n else head(at(0), at(min(L, 3.0))) if k == 0 else head(at(max(0, L - 3.0)), at(L)) for k in range(n + 1)]
    sh = lambda p, h: (p[0] + side * math.cos(math.radians(h)), p[1] - side * math.sin(math.radians(h)), p[2])
    for k in range(1, len(pts)):
        A = sh(pts[k - 1], tan[k - 1]); B = sh(pts[k], tan[k]); hc = tan[k - 1]
        dx, dy = B[0] - A[0], B[1] - A[1]
        fwd = dx * math.sin(math.radians(hc)) + dy * math.cos(math.radians(hc)); lat = dx * math.cos(math.radians(hc)) - dy * math.sin(math.radians(hc))
        if fwd <= 0.2: continue
        d2 = dx * dx + dy * dy
        if abs(lat) < 0.01: R = 0.0; Lp = fwd
        else:
            R = d2 / (2 * lat); th = 2 * math.asin(min(1.0, math.sqrt(d2) / (2 * abs(R)))); Lp = abs(R) * th
        if not (0.2 < Lp < 200): continue
        dz = B[2] - A[2]
        nm = f"{base}@{Lp:.3f}" + (f"~{R:.2f}" if R and abs(R) < 20000 else "") + (f"^{dz:.3f}" if abs(dz) > 0.005 else "")
        dd = L * (k - 1) / n
        if abs(dw) > 0.05: nm += f"%{dw:.2f}"                   # kerb moved out (or in) to the road's own kerb line
        if tag: nm += tag                                         # e.g. "!p": a flyover deck without the kit's own pier (the game builds the piers)
        elif dd < flat[0] or dd > L - flat[1] - SEG: nm += "!f"
        K.start(nm, A[0], A[1], hc, A[2])

def part(e):
    """the visible stretch of a road: inside a junction (or where a ramp still lies on the freeway it leaves) the junction's own surface shows"""
    P = e["P"]; u0, u1 = e.get("u0", 0), e.get("u1", e["L"])
    if u1 - u0 < 3: return []
    D = [0.0]
    for i in range(1, len(P)): D.append(D[-1] + math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]))
    k = D[-1] / max(1e-9, e["L"])
    def at(u):
        d = u * k; i = 0
        while i < len(D) - 2 and D[i + 1] < d: i += 1
        f = (d - D[i]) / max(1e-9, D[i + 1] - D[i]); return [P[i][j] + (P[i + 1][j] - P[i][j]) * min(1, max(0, f)) for j in range(3)]
    return [at(u0)] + [P[i] for i in range(len(P)) if u0 * k < D[i] < u1 * k] + [at(u1)]

# ---- junctions: a kit intersection wherever the old one is a plain 4-way or T with roads meeting near right angles
CLS = {"st": "c2", "col": "c2", "res": "r2", "road": "u2", "lane": "u2", "dirt": "u2", "ave": "c4", "art": "c4"}
JP = {  # piece: (leg names and their class in the piece, with the class each accepts)
    "x_city2_4way": {"leg_N": "c2", "leg_E": "c2", "leg_S": "c2", "leg_W": "c2"},
    "x_res2_4way": {"leg_N": "r2", "leg_E": "r2", "leg_S": "r2", "leg_W": "r2"},
    "x_rural2_4way": {"leg_N": "u2", "leg_E": "u2", "leg_S": "u2", "leg_W": "u2"},
    "x_city4_4way": {"leg_N": "c4", "leg_E": "c4", "leg_S": "c4", "leg_W": "c4"},
    "x_city4_city2_4way": {"leg_N": "c4", "leg_E": "c2", "leg_S": "c4", "leg_W": "c2"},
    "x_city2_T": {"leg_N": "c2", "leg_E": "c2", "leg_S": "c2"},
    "x_res2_T": {"leg_N": "r2", "leg_E": "r2", "leg_S": "r2"},
    "x_rural2_T": {"leg_N": "u2", "leg_E": "u2", "leg_S": "u2"},
    "x_city4_res2_T": {"leg_N": "c4", "leg_E": "r2", "leg_S": "c4"}}
ACC = {"c2": {"c2", "r2", "u2"}, "r2": {"r2", "c2"}, "u2": {"u2", "c2"}, "c4": {"c4"}}   # two-lane kinds stand in for each other
LEGH = {"leg_N": 0, "leg_E": 90, "leg_S": 180, "leg_W": 270}
TRIM = {}        # (edge index, end) -> distance from the node where the kit junction's leg ends
legs_at = {}
for e in NET["E"]:
    P = e["P"]
    if len(P) < 3: continue
    legs_at.setdefault(e["a"], []).append((e, 0, head(P[0], P[2])))
    legs_at.setdefault(e["b"], []).append((e, 1, head(P[-1], P[-3])))
exec(open("tools/kitmaps/dt.py").read())   # v40: downtown is planned piece by piece from the kit (its junctions, lane changes and turnarounds)
exec(open("tools/kitmaps/auto.py").read())   # v40: Harbor Point, Fairhaven... as they stand, junctions and straight roads from the kit
nj = 0
for ni, L in legs_at.items():
    nd = NET["N"][ni]
    if inR(nd["x"], nd["y"]) or (round(nd["x"]), round(nd["y"])) in PLANNED: continue
    if nd["k"] != "x" or len(L) not in (3, 4) or any(e["t"] not in CLS for e, _, _ in L): continue
    best = None
    for exact in (True, False):
     if best: break
     for pc, legs in JP.items():
        if len(legs) != len(L): continue
        for e0, _, h0 in L:
            for base_leg in legs:
                h = (h0 - LEGH[base_leg]) % 360; used = {}; ok = True
                for ln, cl in legs.items():
                    want = (LEGH[ln] + h) % 360
                    m = [q for q in L if abs(((q[2] - want + 180) % 360) - 180) < 9 and id(q) not in used.values() and (CLS[q[0]["t"]] == cl if exact else CLS[q[0]["t"]] in ACC[cl])]
                    if not m: ok = False; break
                    used[ln] = id(m[0]); used[ln + "_q"] = m[0]
                if ok: best = (pc, h, {ln: used[ln + "_q"] for ln in legs}); break
            if best: break
        if best: break
    if not best: continue
    pc, h, M = best
    out = K.start(pc, nd["x"], nd["y"], h, nd["z"])
    K.kj = getattr(K, "kj", []); K.kj.append([nd["x"], nd["y"], min(math.hypot(out[ln]["x"] - nd["x"], out[ln]["y"] - nd["y"]) for ln in M)])
    for ln, (e, end, _) in M.items():
        c = out[ln]; d = math.hypot(c["x"] - nd["x"], c["y"] - nd["y"])
        TRIM[(e["i"], end)] = d
    nj += 1
print(f"kit junctions: {nj}")

# ---- freeway exits and entrances: the kit's merge pieces (placed and checked by the game, kitMerges / kitMrgOut: the ramps there were
# reshaped to the piece). The carriageway straights and the ramp's own pieces stop where a merge piece takes over.
MP = []
for nm, x, y, h, z, nx, ny in NET.get("M", []):
    K.start(nm, x, y, h, z)
    Lp = float(nm.split("@")[1].split("^")[0])
    MP.append((x, y, math.sin(math.radians(h)), math.cos(math.radians(h)), Lp, nx, ny, h))
print(f"kit merge pieces: {len(MP)}")

def mcov(p, hd, kind):
    """is this point under a merge piece? kind "c": a carriageway centre line travelling at heading hd; "r": a ramp"""
    for x, y, fx, fy, Lp, _, _, h in MP:
        dx, dy = p[0] - x, p[1] - y
        a = dx * fx + dy * fy
        if a < -0.01 or a > Lp + 0.01: continue
        t = dx * fy - dy * fx
        if kind == "c":
            if abs(t + 1.85) < 2.5 and abs(((hd - h + 180) % 360) - 180) < 25: return True
        elif 12 < t < 46: return True
    return False

def mcut(P, kind):
    """P with the stretches under merge pieces cut out (cut exactly at the piece's ends): a list of polylines"""
    out, cur = [], []
    hd = lambda i: head(P[max(0, i - 1)], P[min(len(P) - 1, i + 1)])
    cov = [mcov(P[i], hd(i), kind) for i in range(len(P))]
    for i in range(len(P)):
        if i and cov[i] != cov[i - 1]:
            a, b = P[i - 1], P[i]; lo, hi = 0.0, 1.0; h_ = hd(i)
            for _ in range(24):
                m = (lo + hi) / 2; q = [a[j] + (b[j] - a[j]) * m for j in range(3)]
                if mcov(q, h_, kind) == cov[i - 1]: lo = m
                else: hi = m
            q = [a[j] + (b[j] - a[j]) * (lo + hi) / 2 for j in range(3)]
            if cov[i - 1]: cur = [q]
            else: cur.append(q); out.append(cur); cur = []
        if not cov[i]: cur.append(P[i])
    if len(cur) > 1: out.append(cur)
    return [c for c in out if len(c) > 1]

def mfull(i):
    """every ramp at this node got a merge piece"""
    n = NET["N"][i]; m = sum(1 for q in MP if abs(n["x"] - q[5]) < 1 and abs(n["y"] - q[6]) < 1)
    return m > 0 and m >= sum(1 for f in NET["E"] if f["t"] == "ramp" and i in (f["a"], f["b"]))

# ---- ramps that run alongside the freeway as an extra lane (the stack's back-to-back exits, weaving stretches) where no merge piece went:
# that stretch of carriageway is the kit's 4-lane one (its 4th lane sits where the ramp runs, 23.65 m out), reached through the kit's own
# lane-add / lane-end tapers over the hidden stretch where the ramp leaves or joins the centre line, and the ramp's own pieces stop there.
import bisect
XWE = [e for e in NET["E"] if e["t"] == "xway"]
def cumd(P):
    D = [0.0]
    for i in range(1, len(P)): D.append(D[-1] + math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]))
    return D
XD = {e["i"]: cumd(e["P"]) for e in XWE}
GR = {}
for e in XWE:
    P = e["P"]
    for i in range(len(P) - 1): GR.setdefault((int(P[i][0] // 60), int(P[i][1] // 60)), []).append((e, i))
def xproj(q):
    """the nearest freeway centre line: (edge, u, signed offset left of the edge's direction, its height there)"""
    best = None
    for cx in (-1, 0, 1):
        for cy in (-1, 0, 1):
            for e, i in GR.get((int(q[0] // 60) + cx, int(q[1] // 60) + cy), ()):
                a, b = e["P"][i], e["P"][i + 1]; dx, dy = b[0] - a[0], b[1] - a[1]; l2 = dx * dx + dy * dy or 1e-9
                f = max(0.0, min(1.0, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / l2)); px, py = a[0] + dx * f, a[1] + dy * f
                d = math.hypot(q[0] - px, q[1] - py)
                if best is None or d < best[0]:
                    l = math.sqrt(l2); t = (dx * (q[1] - a[1]) - dy * (q[0] - a[0])) / l
                    best = (d, e, XD[e["i"]][i] + l * f, t, a[2] + (b[2] - a[2]) * f, math.degrees(math.atan2(dx, dy)) % 360)
    return best
AUX = {}   # (edge, dir) -> sorted [(u, kind)]
for r in NET["E"]:
    if r["t"] != "ramp": continue
    ends = [NET["N"][r["a"]], NET["N"][r["b"]]]
    for sub in mcut(r["P"], "r"):
        D = cumd(sub); Ltot = D[-1]
        for k, q in enumerate(sub):
            b = xproj(q)
            if not b or b[0] > 27: continue
            _, e, u, t, zf, hf = b
            if abs(q[2] - zf) > 1.2: continue                                   # a flyover passing over, not alongside
            hr = head(sub[max(0, k - 1)], sub[min(len(sub) - 1, k + 1)])
            if abs(((hr - hf + 90) % 180) - 90) > 20: continue                  # crossing, not running alongside
            nearend = min(math.hypot(q[0] - n["x"], q[1] - n["y"]) for n in ends) < 140
            kind = "aux" if 20 <= abs(t) <= 26.5 else ("taper" if abs(t) < 20 and nearend else None)
            if kind: AUX.setdefault((e["i"], 1 if t < 0 else -1), []).append((u, kind))
for v in AUX.values(): v.sort()
def aux_at(ei, dr, u):
    v = AUX.get((ei, dr))
    if not v: return None
    i = bisect.bisect_left(v, (u, "")); c = [v[j] for j in (i - 1, i) if 0 <= j < len(v)]
    c = [x for x in c if abs(x[0] - u) < 6]
    if not c: return None
    return "aux" if any(x[1] == "aux" for x in c) else "taper"
def carriage(sub, e, dr, flat):
    """one carriageway (travel along sub) in 3-lane, 4-lane and taper runs"""
    if not AUX.get((e["i"], dr)): follow(sub, "fwy3g_st96", side=1.85, flat=flat); return
    D = XD[e["i"]]; L = D[-1]; P = e["P"]; j = 0; cls = []
    for q in sub:   # u along the edge for each point (points are in order, so a moving search)
        best = None
        for i in range(len(P)):
            d = (P[i][0] - q[0]) ** 2 + (P[i][1] - q[1]) ** 2
            if best is None or d < best[0]: best = (d, i)
        u = D[best[1]]; cls.append(aux_at(e["i"], dr, u))
    runs = []
    for q, c in zip(sub, cls):
        if runs and runs[-1][0] == c: runs[-1][1].append(q)
        else:
            if runs: runs[-1][1].append(q)
            runs.append([c, [q]])
    for k, (c, R) in enumerate(runs):
        if len(R) < 2: continue
        prv = runs[k - 1][0] if k else None; nxt = runs[k + 1][0] if k + 1 < len(runs) else None
        if c == "aux": follow(R, "fwy4g_st96", side=1.85)
        elif c == "taper" and nxt == "aux": follow(R, "fwy3g_lane_add_180", side=1.85, one=True)
        elif c == "taper" and prv == "aux": follow(R, "fwy3g_lane_end_merge_180", side=1.85, one=True)
        else: follow(R, "fwy3g_st96", side=1.85, flat=flat if k in (0, len(runs) - 1) else (0, 0))
def ramp_off(P):
    """a ramp without its stretches alongside (or merging across) the freeway: those are carriageway lanes now"""
    out, cur = [], []
    for q in P:
        b = xproj(q); on = False
        if b and b[0] <= 26.5 and abs(q[2] - b[4]) <= 1.2:
            on = aux_at(b[1]["i"], 1 if b[3] < 0 else -1, b[2]) is not None
        if on:
            if len(cur) > 1: out.append(cur)
            cur = []
        else: cur.append(q)
    if len(cur) > 1: out.append(cur)
    return out
print(f"ramp lanes alongside the freeway: {sum(len(v) for v in AUX.values())} samples on {len(AUX)} carriageways")

# ---- two one-lane ramps that meet and run on side by side (the stack's ramps joining before the freeway, the C-D road): that stretch
# is the kit's two-lane ramp along the line between them, then its 2-to-1 taper (or 1-to-2 where one road splits in two), and the
# single ramps' own pieces stop where it takes over
def outward(e, end):
    P = e["P"] if end == 0 else e["P"][::-1]
    return P
def at_dist(P, d):
    D = cumd(P)
    if d >= D[-1]: return None
    i = bisect.bisect_right(D, d) - 1; f = (d - D[i]) / max(1e-9, D[i + 1] - D[i])
    return [P[i][j] + (P[i + 1][j] - P[i][j]) * f for j in range(3)]
LEGS = {}
for e in NET["E"]:
    for end, ni in ((0, e["a"]), (1, e["b"])): LEGS.setdefault(ni, []).append((e, end))
RRCUT = {}   # (edge i, end) -> metres from that end the single-lane pieces leave out
nrr = 0
for ni, L in LEGS.items():
    rl = [(e, end) for e, end in L if e["t"] == "ramp"]
    if len(rl) != 3 or any(e["t"] == "xway" for e, _ in L): continue
    ins = [(e, end) for e, end in rl if end == 1]; outs = [(e, end) for e, end in rl if end == 0]
    if len(ins) == 2 and len(outs) == 1: pair, one, merge = ins, outs[0], True
    elif len(outs) == 2 and len(ins) == 1: pair, one, merge = outs, ins[0], False
    else: continue
    A, B = outward(*pair[0]), outward(*pair[1]); C = outward(*one)
    s1 = s2 = None; d = 2.0
    while d < 180:
        a, b = at_dist(A, d), at_dist(B, d)
        if not a or not b: break
        g = math.hypot(a[0] - b[0], a[1] - b[1])
        if s1 is None and g >= 3.3: s1 = d
        if s1 is not None:
            if 3.0 <= g <= 5.4: s2 = d
            else: break
        d += 2.0
    if s1 is None or s2 is None or s2 - s1 < 12: continue
    M = []; d = s1
    while d <= s2 + 0.01:
        a, b = at_dist(A, d), at_dist(B, d); M.append([(a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2]); d += 4.0
    cl = max(8.0, 72.0 - s1); c = at_dist(C, cl)
    if not c: continue
    if merge:
        follow(M[::-1], "ramp2_st48"); follow([M[0], c], "ramp_narrow_2to1_72", one=True)
    else:
        follow([c, M[0]], "ramp_widen_1to2_72", one=True); follow(M, "ramp2_st48")
    for (e, end) in pair: RRCUT[(e["i"], end)] = s2
    RRCUT[(one[0]["i"], one[1])] = cl
    nrr += 1
print(f"ramp pairs on a two-lane ramp: {nrr}")
for e in NET["E"]:
    for end in (0, 1):
        if (e["i"], end) in RRCUT:
            if end == 0: e["u0"] = max(e.get("u0", 0), RRCUT[(e["i"], 0)])
            else: e["u1"] = min(e.get("u1", e["L"]), e["L"] - RRCUT[(e["i"], 1)])

# v38.1: a boulevard whose median opens or closes (tp): the kit has no taper piece, so where the median is wider than 5.5 m each carriageway
# is a one-way three-lane piece following its own lanes out from the median, and where it is narrower the six-lane divided road with the
# narrow planted median (city6d). The game keeps a median of tp[2] x the full width at the narrow end, so the two meet without a jog
def taper_blvd(e, P, FL):
    tp = e["tp"]; mn = tp[2] if len(tp) > 2 else 0.0; L = e["L"]
    sm = lambda a, b, x: (lambda t: t * t * (3 - 2 * t))(min(1, max(0, (x - a) / (b - a))))
    mAt = lambda u: e["m"] * (mn + (1 - mn) * sm(tp[0], tp[1], u))
    D = [0.0]
    for i in range(1, len(P)): D.append(D[-1] + math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]))
    k = (e["P"] and sum(math.hypot(e["P"][i][0] - e["P"][i - 1][0], e["P"][i][1] - e["P"][i - 1][1]) for i in range(1, len(e["P"])))) / max(1e-9, L)
    full = e["P"][0]; d0 = math.hypot(P[0][0] - full[0], P[0][1] - full[1])   # how far along the edge the visible stretch starts
    U = [(d0 + d) / max(1e-9, k) for d in D]
    def off(i, t):
        a = P[max(0, i - 1)]; b = P[min(len(P) - 1, i + 1)]; h = math.atan2(b[1] - a[1], b[0] - a[0])
        return [P[i][0] - math.sin(h) * t, P[i][1] + math.cos(h) * t, P[i][2]]
    runs, cur, w0 = [], [], None
    for i in range(len(P)):
        wide = mAt(U[i]) > 5.5
        if w0 is not None and wide != w0: runs.append((w0, cur)); cur = [cur[-1]]
        cur.append(i); w0 = wide
    if len(cur) > 1: runs.append((w0, cur))
    for wide, I in runs:
        if not wide: follow([P[i] for i in I], "city6d_st96"); continue
        R = [off(i, -(mAt(U[i]) / 2 + 5.4)) for i in I]           # this way: right of the centre line, beyond the median
        Lf = [off(i, mAt(U[i]) / 2 + 5.4) for i in I][::-1]       # and the other way, followed in its own direction
        follow(R, "svc3_st96", tag="!l"); follow(Lf, "svc3_st96", tag="!l")   # the median side keeps its kerb, not the service drive's sidewalk

for e in NET["E"]:
    base = BASE.get(e["t"])
    if not base or e["i"] in REG_SKIP or e.get("kit"): continue
    if (e["i"], 0) in TRIM: e["u0"] = TRIM[(e["i"], 0)]
    if (e["i"], 1) in TRIM: e["u1"] = e["L"] - TRIM[(e["i"], 1)]
    # where a ramp joins or leaves (a merge), the pieces nearest it lose their kerb and sidewalk ("!f") so the ramp's mouth is open
    FL = (80 if NET["N"][e["a"]]["c"] == "merge" else 0, 80 if NET["N"][e["b"]]["c"] == "merge" else 0)
    P = part(e)
    if len(P) < 2: continue
    if MP and e["t"] in ("xway", "ramp"):
        # an open (kerbless) stretch stays only by a node where some ramp got no merge piece, and only on the pieces that still reach it
        if e["t"] == "xway": FL = tuple(0 if mfull(i) else f for f, i in zip(FL, (e["a"], e["b"])))
        fl = lambda sub, F: (F[0] if sub[0] is P[0] or sub[0] == P[0] else 0, F[1] if sub[-1] is P[-1] or sub[-1] == P[-1] else 0)
        if e["t"] == "xway":
            for sub in mcut(P, "c"): carriage(sub, e, 1, fl(sub, FL))
            R_ = P[::-1]
            for sub in mcut(R_, "c"): carriage(sub, e, -1, (FL[1] if sub[0] == R_[0] else 0, FL[0] if sub[-1] == R_[-1] else 0))
        elif e.get("fly") and e.get("G"):
            # a flyover: where it is up in the air (over 2.5 m above the ground) it is the kit's flyover deck, no grass verges
            EP, G = e["P"], e["G"]
            gz = lambda q: G[min(range(len(EP)), key=lambda i: (EP[i][0] - q[0]) ** 2 + (EP[i][1] - q[1]) ** 2)]
            for sub in [r_ for s_ in mcut(P, "r") for r_ in ramp_off(s_)]:
                runs, cur, up0 = [], [], None
                for q in sub:
                    up = q[2] - gz(q) > 2.5
                    if up0 is not None and up != up0: runs.append((up0, cur)); cur = [cur[-1]]
                    cur.append(q); up0 = up
                if len(cur) > 1: runs.append((up0, cur))
                for up, r in runs:
                    if up: follow(r, "ramp1_flyover_st48", tag="!p")
                    else: follow(r, base)
        else:
            subs = [r for sub in mcut(P, "r") for r in ramp_off(sub)]
            cut = len(subs) != 1 or len(subs[0]) != len(P)
            for sub in subs: follow(sub, base, flat=(0, 0) if cut else FL)
    elif e["t"] == "xway":
        follow(P, base, side=1.85, flat=FL)              # this direction: lanes from 11 m right of the centre line
        follow(P[::-1], base, side=1.85, flat=FL[::-1])  # and the other way
    elif e["t"] == "blvd" and e.get("tp"):
        taper_blvd(e, P, FL)
    else:
        follow(P, base, flat=FL, dw=(e["hw"] - EDGE[base]) if base in EDGE else 0.0)
