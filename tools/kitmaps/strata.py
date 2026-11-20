# The road-kit map, version 1: a 5 x 5 downtown grid inside a freeway ring with a diamond interchange on each side.
# World axes: x east, y north. Heading 0 = north, clockwise. Everything snaps at the kit's connectors; straights are clipped to fit.
import math

def dist(a, b): return math.hypot(a["x"] - b["x"], a["y"] - b["y"])

def fill(a, b, base, z_ok=True):
    """straights of `base` (a *_st96 piece) from connector a up to connector b (facing each other on one line)"""
    d = dist(a, b); cur = a
    while d > 96.0005:
        cur = K.add(base, cur)["out"]; d -= 96
    if d > 0.05:
        cur = K.add(f"{base}@{d:.4f}", cur)["out"]
    return cur

def run(a, base, L):
    """L metres of straights from connector a; returns the open end"""
    cur = a
    while L > 96.0005:
        cur = K.add(base, cur)["out"]; L -= 96
    if L > 0.05: cur = K.add(f"{base}@{L:.4f}", cur)["out"]
    return cur

# ---------------------------------------------------------------- downtown: 5 x 5 at a 200 m pitch, the middle row and column are four-lane
P = 200.0; R = range(-2, 3); X = {}
for j in R:
    for i in R:
        x, y = i * P, j * P
        edge = abs(i) == 2 or abs(j) == 2
        if abs(i) == 2 and abs(j) == 2: continue                                  # corners are curves
        if i == 0 and j == 0: X[i, j] = K.start("x_city4_4way", x, y, 0)
        elif j == 0: X[i, j] = K.start("x_city4_city2_4way", x, y, 90)          # main street east-west
        elif i == 0: X[i, j] = K.start("x_city4_city2_4way", x, y, 0)           # main street north-south
        elif edge:
            out = 90 if i == 2 else 270 if i == -2 else 0 if j == 2 else 180       # the missing leg faces outward
            X[i, j] = K.start("x_city2_T", x, y, (out - 270) % 360)
        else: X[i, j] = K.start("x_city2_4way", x, y, 0)

def legs(c):
    return {k: v for k, v in c.items()}

def facing(c, d):
    """the leg of node c whose heading is d (0 N, 90 E, 180 S, 270 W)"""
    for v in c.values():
        if abs(((v["h"] - d + 180) % 360) - 180) < 1: return v
    return None

def base_of(c): return {"CITY2": "city2_st96", "CITY4": "city4_st96", "CITY5": "city5_st96"}[c["prof"]]

for j in R:
    for i in R:
        if (i, j) not in X: continue
        if (i + 1, j) in X: a = facing(X[i, j], 90); fill(a, facing(X[i + 1, j], 270), base_of(a))
        if (i, j + 1) in X: a = facing(X[i, j], 0); fill(a, facing(X[i, j + 1], 180), base_of(a))
# corners, driven clockwise (all right turns): top-right, bottom-right, bottom-left, top-left
for (fi, fj, d_in, ti, tj, d_out) in [(1, 2, 90, 2, 1, 0), (2, -1, 180, 1, -2, 90), (-1, -2, 270, -2, -1, 180), (-2, 1, 0, -1, 2, 270)]:
    a = facing(X[fi, fj], d_in); b = facing(X[ti, tj], d_out)
    cx, cy = (2 if d_in in (90, 0) else -2) * P, 0
    # straight up to 18 m short of the corner point, the curve, then on to the next node
    corner = {90: (2 * P, 2 * P), 180: (2 * P, -2 * P), 270: (-2 * P, -2 * P), 0: (-2 * P, 2 * P)}[d_in]
    L = math.hypot(corner[0] - a["x"], corner[1] - a["y"]) - 18
    c = run(a, "city2_st96", L)
    c = K.add("city2_c90r18", c)["out"]
    fill(c, b, "city2_st96")

# ---------------------------------------------------------------- the freeway ring (median line): sides 3200 m (east, west) and 1800 m (north, south), 400 m corners
RING = 1300.0
SIDES = [  # start point and heading of each side for the counter-clockwise carriageway, its length, and the cross street (main street) at its middle
    ((1300, -1600), 0, 3200), ((900, 2000), 270, 1800), ((-1300, 1600), 180, 3200), ((-900, -2000), 90, 1800)]

def carriageway(ccw):
    """one direction all the way round: straights, an exit and an entrance either side of each diamond, 3 x 30 deg corners"""
    sides = SIDES if ccw else [((p[0], p[1]), h, S) for (p, h, S) in SIDES]
    curve = "fwy3g_c30r400_L" if ccw else "fwy3g_c30r400_R"
    ramps = []
    if ccw:
        (x0, y0), h0, _ = SIDES[0]
        cur = K.start("fwy3g_st96@0.0001", x0, y0, h0)["out"] if False else None
    # build by walking: start piece placed at the first side's start
    order = SIDES if ccw else [SIDES[0], SIDES[3], SIDES[2], SIDES[1]]   # clockwise: east (southbound), south, west, north
    first = True
    for (p, h, S) in order:
        if ccw: start, head = p, h
        else:
            # the clockwise carriageway runs the same side the other way: from the side's far end
            hr = math.radians(h); start = (p[0] + S * math.sin(hr), p[1] + S * math.cos(hr)); head = (h + 180) % 360
        if first:
            cur = K.start("fwy3g_st96@48", start[0], start[1], head)["out"]; done = 48; first = False; first_in = (start, head)
        else: done = 0
        sc = S / 2
        cur = run(cur, "fwy3g_st96", sc - 755.8 - done)
        ex = K.add("fwy3g_exit_336", cur); cur = ex["out"]
        cur = run(cur, "fwy3g_st96", 839.6)
        en = K.add("fwy3g_entrance_432", cur); cur = en["out"]
        cur = run(cur, "fwy3g_st96", S - sc - 419.8 - 432)
        ramps.append((ex["ramp"], en["ramp"]))
        for k in range(3): cur = K.add(curve, cur)["out"]
    return ramps

RA = carriageway(True)
RB = carriageway(False)

def terminal(exit_ramp, entr_ramp):
    """the exit ramp climbs to a signalised ramp terminal on the overpass street; the entrance ramp drops back down from it"""
    c = K.add("ramp1_c30r150_R", exit_ramp)["out"]; c = K.add("ramp1_c30r150_L", c)["out"]
    c = K.add("ramp1_rise7_144", c)["out"]; c = K.add("ramp1_st96@48", c)["out"]
    T = K.add("x_city5_ramps_diamond_terminal", c, via="leg_S")
    c = K.add("ramp1_st96@48", T["leg_N"])["out"]; c = K.add("ramp1_fall7_144", c)["out"]
    c = K.add("ramp1_c30r150_L", c)["out"]; K.add("ramp1_c30r150_R", c)
    return T

def street_legs(T):
    return [T["leg_E"], T["leg_W"]]

# pair each side's two terminals (A's side k with B's matching side)
B_of = {0: 0, 1: 3, 2: 2, 3: 1}
for k in range(4):
    TA = terminal(*RA[k]); TB = terminal(*RB[B_of[k]])
    la, lb = street_legs(TA), street_legs(TB)
    ia, ib = min(((a, b) for a in la for b in lb), key=lambda q: dist(*q))      # the two legs that face each other across the freeway
    d = dist(ia, ib)                                                            # 79 m: 9.5 m of street, the 60 m overpass, 9.5 m
    c = K.add(f"city5_st96@{(d - 60) / 2:.4f}", ia)["out"]; c = K.add("overpass_city5_concrete_60", c)["out"]; K.add(f"city5_st96@{(d - 60) / 2:.4f}", c)
    oa = next(l for l in la if l is not ia); ob = next(l for l in lb if l is not ib)
    for o in (oa, ob):
        ap = K.add("approach_city5_rise7_144", o, via="out")["in"]
        # inner side: on to downtown's main street; outer side: out into the country
        if math.hypot(ap["x"], ap["y"]) < math.hypot(o["x"], o["y"]):
            d_in = {0: 90, 1: 0, 2: 270, 3: 180}[k]                               # the downtown leg facing this side
            node = {0: X[2, 0], 1: X[0, 2], 2: X[-2, 0], 3: X[0, -2]}[k]
            leg = facing(node, d_in)
            L = dist(ap, leg) - 48
            c = run(ap, "city5_st96", L)
            K.add("city4_to_city5_turnlane_48", c, via="out")
        else:
            c = run(ap, "city5_st96", 192)
