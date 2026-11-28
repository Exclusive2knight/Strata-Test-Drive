# Downtown Westport built from the road kit (v40). Exec'd by oldmap.py with K and NET (the game's current road graph) in scope.
# Main St (a Michigan-left boulevard, BLVD6D) crosses every other street: 1st, 3rd, Woodward, Park and River St, each with the kit's
# boulevard crossing (x_blvd6d_city5_4way). Between crossings is one Michigan-left turnaround (blvd6d_michigan_left_180), alternately
# facing each way. 2nd St, Griswold St, Cass Ave and Brush St stop at Fort St and Congress St. The cross streets have the kit's five-lane
# approach at Main St and taper to their own lanes after it; every other junction is the kit piece its roads call for.
exec(open("tools/kitmaps/knet.py").read())
DT = Net(K)
DX = [-1600, -1450, -1300, -1150, -1000, -850, -700, -550, -400]; DY = [-450, -300, -150, 0, 150, 300, 450]
DXN = ["1st St", "2nd St", "3rd St", "Griswold St", "Woodward Ave", "Cass Ave", "Park Ave", "Brush St", "River St"]
DYN = ["Grand Ave", "Jefferson Ave", "Fort St", "Main St", "Congress St", "Lafayette Ave", "Michigan Ave"]
MX = [-1600, -1300, -1000, -700, -400]
inR = lambda x, y: -1601 <= x <= -399 and -451 <= y <= 451
nid = lambda x, y: f"{x},{y}"
for x in DX:
    for y in DY:
        if y == 0 and x not in MX: continue
        sig = y == 0 or x in (-850, -1000) or (abs(y) <= 150 and -1600 < x < -400) or (abs(y) == 300 and x in (-1600, -1300, -700, -400))
        DT.node(nid(x, y), x, y, "signal" if sig else "allstop", piece="x_blvd6d_city5_4way" if y == 0 else None)
# east-west streets
for j, y in enumerate(DY):
    if y == 0:
        for k in range(len(MX) - 1):
            a, b = MX[k], MX[k + 1]
            # the turnaround in the middle of the 300 m block: eastbound U-turns in the even blocks, westbound in the odd ones
            DT.road(nid(a, 0), nid(b, 0), "BLVD6D", "Main St", 35, fixed=[("blvd6d_michigan_left_180", 150.0, k % 2 == 1, 129.0)])
        continue
    for k in range(len(DX) - 1):
        DT.road(nid(DX[k], y), nid(DX[k + 1], y), "CITY4" if j % 2 == 1 else "CITY2", DYN[j], 30 if j % 2 == 1 else 25)
# north-south streets
for i, x in enumerate(DX):
    ys = [y for y in DY if y != 0 or x in MX]
    for k in range(len(ys) - 1):
        if ys[k] == -150 and ys[k + 1] == 150: continue         # stops at Fort St and Congress St
        DT.road(nid(x, ys[k]), nid(x, ys[k + 1]), "CITY4" if x in (-1000, -850) else "CITY2", DXN[i], 30 if x in (-1000, -850) else 25)
# roads leaving downtown: their first stretch off the junction is planned here (lane changes), the rest stays the old map's
KP = {"blvd": "BLVD6D", "art": "CITY4", "ave": "CITY4", "st": "CITY2", "col": "CITY2", "road": "RURAL2", "res": "RES2"}
DT_SKIP = set(); DT_OUT = []
for e in NET["E"]:
    A, B = NET["N"][e["a"]], NET["N"][e["b"]]
    ia, ib = inR(A["x"], A["y"]), inR(B["x"], B["y"])
    if ia and ib: DT_SKIP.add(e["i"]); continue
    if ia == ib: continue
    end = 0 if ia else 1; n = A if ia else B; P = e["P"] if ia else e["P"][::-1]
    key = nid(round(n["x"]), round(n["y"]))
    if key not in DT.nodes: continue
    q = next((p for p in P[1:] if math.hypot(p[0] - n["x"], p[1] - n["y"]) > 5), P[-1])
    r = DT.road(key, None, KP.get(e["t"], "CITY2"), e["nm"], outside=True, toward=(q[0], q[1]))
    DT_OUT.append((e["i"], end, r))
fails = DT.build()
for f in fails: print("  DT", f)
for ei, end, r in DT_OUT: TRIM[(ei, end)] = r.get("trimA", 0)
K.knet = DT.game(json.load(open("tools/kitmaps/stops.json")))
K.kj = getattr(K, "kj", []) + [[n["x"], n["y"], min(l[2] for l in n["legs"].values())] for n in DT.nodes.values() if n.get("legs")]
print(f"downtown: {len(DT.nodes)} junctions, {len(DT.roads)} roads, {len(DT_SKIP)} old edges replaced, {len(DT_OUT)} roads leave it, {len(fails)} problems")
