# A region of the old map rebuilt from the kit as it stands (same junctions, same roads): exec'd by oldmap.py after dt.py, with K, NET,
# TRIM, Net (knet.py) and the downtown plan in scope. Every junction in the box whose roads meet near right angles becomes the kit
# piece those roads need; straight roads between two of them are planned piece by piece; curved roads and roads leaving the box get
# their lane changes at the junction and keep the old map's bent straights beyond.
KP = {"blvd": "BLVD6D", "art": "CITY4", "ave": "CITY4", "st": "CITY2", "col": "CITY2", "road": "RURAL2", "res": "RES2"}
REG_SKIP = set(DT_SKIP); KNETS = [K.knet]; PLANNED = {(n["x"], n["y"]) for n in DT.nodes.values()}

def auto_region(name, box, ctrl_over=None, prof_over=None):
    x0, x1, y0, y1 = box; inB = lambda x, y: x0 <= x <= x1 and y0 <= y <= y1
    R = Net(K); NN = NET["N"]; deg = {}
    for e in NET["E"]:
        for i in (e["a"], e["b"]): deg.setdefault(i, []).append(e)
    nid = lambda i: f"{name}:{i}"
    # junctions: inside the box, three or more roads, all of a kind the kit has, meeting near right angles
    J = {}
    for i, L in deg.items():
        n = NN[i]
        if not inB(n["x"], n["y"]) or len(L) < 3 or n["k"] != "x" or n["c"] in ("merge",) or (round(n["x"]), round(n["y"])) in PLANNED: continue
        if any(e["t"] not in KP for e in L): continue
        hs = []
        for e in L:
            P = e["P"] if e["a"] == i else e["P"][::-1]
            q = next((p for p in P[1:] if math.hypot(p[0] - n["x"], p[1] - n["y"]) > 12), P[-1])
            hs.append(hd(q[0] - n["x"], q[1] - n["y"]))
        if any(min(abs(((a - b) % 90 + 45) % 90 - 45) for b in hs) > 6 for a in hs): continue      # not square-on
        J[i] = n; PLANNED.add((round(n["x"]), round(n["y"]))); R.node(nid(i), n["x"], n["y"], (ctrl_over or {}).get((round(n["x"]), round(n["y"])), n["c"] or None))
    out = []; planned = []
    for e in NET["E"]:
        if e.get("kit") or e["t"] not in KP: continue
        a, b = e["a"] in J, e["b"] in J
        if not (a or b): continue
        P = e["P"]; prof = (prof_over or {}).get(e["nm"], KP[e["t"]])
        straight = max(abs((p[0] - P[0][0]) * (P[-1][1] - P[0][1]) - (p[1] - P[0][1]) * (P[-1][0] - P[0][0])) / max(1e-6, math.hypot(P[-1][0] - P[0][0], P[-1][1] - P[0][1])) for p in P) < 0.3
        if a and b and straight:
            r = R.road(nid(e["a"]), nid(e["b"]), prof, e["nm"], lim=None); REG_SKIP.add(e["i"]); planned.append((e["i"], r)); continue
        for end, inj in ((0, a), (1, b)):
            if not inj: continue
            n = NN[e["a"] if end == 0 else e["b"]]; Q = P if end == 0 else P[::-1]
            q = next((p for p in Q[1:] if math.hypot(p[0] - n["x"], p[1] - n["y"]) > 12), Q[-1])
            r = R.road(nid(e["a"] if end == 0 else e["b"]), None, prof, e["nm"], outside=True, toward=(q[0], q[1])); out.append((e["i"], end, r))
    fails = R.build()
    for n in R.nodes.values():
        if not n.get("legs"): PLANNED.discard((round(n["x"]), round(n["y"])))     # no kit piece fits: the old map's junction stays
    for f in fails: print(f"  {name}", f)
    for ei, end, r in out: TRIM[(ei, end)] = r.get("trimA", 0)
    for ei, r in planned:
        if r.get("fallback"):           # a junction at one end got no piece: the old road stays, trimmed where the kit junction's lanes end
            REG_SKIP.discard(ei)
            if "trimA" in r: TRIM[(ei, 0)] = r["trimA"]
            if "trimB" in r: TRIM[(ei, 1)] = r["trimB"]
    g = R.game(json.load(open("tools/kitmaps/stops.json")))
    KNETS.append(g)
    for n in R.nodes.values():
        if n.get("legs"): K.kj = getattr(K, "kj", []) + [[n["x"], n["y"], min(l[2] for l in n["legs"].values())]]
    print(f"{name}: {len(J)} junctions, {len(R.roads)} roads, {len(out)} open, {len(fails)} problems")
    return R

auto_region("Harbor Point", [3090, 4310, -1110, -190])
auto_region("Fairhaven", [2290, 2910, -310, 310])
auto_region("Map", [-1e6, 1e6, -1e6, 1e6])       # everything else: suburbs, towns, county crossroads

# every region's graph in one: nodes, edges, legs, and the boxes whose old roads the game drops
# drop: the old roads these replace (by their end points; downtown's are never built)
DROP = []
for e in NET["E"]:
    if e["i"] in REG_SKIP and e["i"] not in DT_SKIP and not e.get("kit"):
        A, B = NET["N"][e["a"]], NET["N"][e["b"]]; DROP.append([A["x"], A["y"], B["x"], B["y"]])
K.knet = {"nodes": [n for g in KNETS for n in g["nodes"]], "edges": [e for g in KNETS for e in g["edges"]], "legs": [l for g in KNETS for l in g["legs"]], "drop": DROP}
