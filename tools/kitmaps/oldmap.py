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

def follow(P, base, side=0.0, flat=(0, 0), dw=0.0, tag=""):
    """kit pieces along polyline P (x, y, z), each placed on its own sample point and tangent and bent to reach the next one
    (no chaining, so nothing drifts); side shifts the pieces right of the line (the freeway carriageways)"""
    if len(P) < 2: return
    D = [0.0]
    for i in range(1, len(P)): D.append(D[-1] + math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]))
    L = D[-1]
    if L < 1: return
    hilly = max(p[2] for p in P) - min(p[2] for p in P) > 0.5
    n = max(1, round(L / (SEG if hilly else 32.0))); pts = []      # short pieces only where the road climbs (fewer pieces, faster frames)
    for k in range(n + 1):
        d = L * k / n; i = 0
        while i < len(D) - 2 and D[i + 1] < d: i += 1
        f = (d - D[i]) / max(1e-9, D[i + 1] - D[i])
        pts.append([P[i][j] + (P[i + 1][j] - P[i][j]) * min(1, max(0, f)) for j in range(3)])
    tan = []
    for k in range(len(pts)):
        a_, b_ = pts[max(0, k - 1)], pts[min(len(pts) - 1, k + 1)]
        tan.append(head(a_, b_))
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
nj = 0
for ni, L in legs_at.items():
    nd = NET["N"][ni]
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

for e in NET["E"]:
    base = BASE.get(e["t"])
    if not base: continue
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
            for sub in mcut(P, "c"): follow(sub, base, side=1.85, flat=fl(sub, FL))
            R_ = P[::-1]
            for sub in mcut(R_, "c"): follow(sub, base, side=1.85, flat=(FL[1] if sub[0] == R_[0] else 0, FL[0] if sub[-1] == R_[-1] else 0))
        elif e.get("fly") and e.get("G"):
            # a flyover: where it is up in the air (over 2.5 m above the ground) it is the kit's flyover deck, no grass verges
            EP, G = e["P"], e["G"]
            gz = lambda q: G[min(range(len(EP)), key=lambda i: (EP[i][0] - q[0]) ** 2 + (EP[i][1] - q[1]) ** 2)]
            for sub in mcut(P, "r"):
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
            subs = mcut(P, "r")
            cut = len(subs) != 1 or len(subs[0]) != len(P)
            for sub in subs: follow(sub, base, flat=(0, 0) if cut else FL)
    elif e["t"] == "xway":
        follow(P, base, side=1.85, flat=FL)              # this direction: lanes from 11 m right of the centre line
        follow(P[::-1], base, side=1.85, flat=FL[::-1])  # and the other way
    else:
        follow(P, base, flat=FL, dw=(e["hw"] - EDGE[base]) if base in EDGE else 0.0)
