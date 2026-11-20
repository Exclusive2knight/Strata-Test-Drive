# The old map rebuilt from road kit pieces: every old road is followed by kit straights cut to length, bent to its curve and graded
K.nograph = True   # the game keeps the old road graph; these pieces only replace how the roads look
# to its heights; the freeway's two carriageways are separate kit pieces either side of its centre line. Junction areas are left for
# kit junction pieces (next step). Reads tools/kitmaps/oldnet.json (exported from the game's own road graph).
import json, math, os
NET = json.load(open("tools/kitmaps/oldnet.json"))
BASE = {"st": "res2p_st96", "ave": "city4_st96", "road": "rural2_st96", "res": "res2_st96", "art": "city4_st96", "col": "city2_st96",
        "blvd": "blvd6d_st96", "ramp": "ramp1_st96", "rbt": "ramp1_st96", "sd": "svc2_st96", "aw": "svc3_st96", "curb": "svc3_st96",
        "lane": "forest2_st96", "dirt": "rural2_st96", "xway": "fwy3g_st96"}
SEG = 24.0          # metres per piece: short enough that a bent straight follows any of the old curves within a few cm

def head(a, b): return math.degrees(math.atan2(b[0] - a[0], b[1] - a[1])) % 360

def follow(P, base, side=0.0):
    """kit pieces along polyline P (x, y, z), each placed on its own sample point and tangent and bent to reach the next one
    (no chaining, so nothing drifts); side shifts the pieces right of the line (the freeway carriageways)"""
    if len(P) < 2: return
    D = [0.0]
    for i in range(1, len(P)): D.append(D[-1] + math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]))
    L = D[-1]
    if L < 1: return
    n = max(1, round(L / SEG)); pts = []
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
    for ln, (e, end, _) in M.items():
        c = out[ln]; d = math.hypot(c["x"] - nd["x"], c["y"] - nd["y"])
        TRIM[(e["i"], end)] = d
    nj += 1
print(f"kit junctions: {nj}")

for e in NET["E"]:
    base = BASE.get(e["t"])
    if not base: continue
    if (e["i"], 0) in TRIM: e["u0"] = TRIM[(e["i"], 0)]
    if (e["i"], 1) in TRIM: e["u1"] = e["L"] - TRIM[(e["i"], 1)]
    P = part(e)
    if len(P) < 2: continue
    if e["t"] == "xway":
        follow(P, base, side=1.85)                      # this direction: lanes from 11 m right of the centre line
        follow(P[::-1], base, side=1.85)                # and the other way
    else:
        follow(P, base)
