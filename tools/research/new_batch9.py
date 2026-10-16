"""2010 Acura MDX, 2017 Ford Fusion, 2007 Ford Mustang, 2007 Kia Sportage: trims, drivetrains, drive modes, suspension, paints.
US specs and original MSRPs from the makers' model-year press kits. Older cars get only the driver aids they really had.
Prints a JS snippet: python3 new_batch9.py out.js"""
import json, sys
G6A = [3.36, 2.10, 1.56, 1.15, 0.86, 0.69]     # Acura 6AT
G6F = [4.48, 2.87, 1.84, 1.41, 1.00, 0.74]     # Ford 6F
G5M = [3.38, 2.00, 1.32, 1.00, 0.68]           # Tremec TR-3650
G5A = [3.22, 2.29, 1.55, 1.00, 0.71]           # 5R55S
G4K = [2.84, 1.55, 1.00, 0.70]                  # Kia 4AT
OLD = ["aeb", "lka", "elk", "esa", "acc", "pilot", "bsm", "rcta", "rAeb", "isa", "autoHold", "autoHigh", "autopark", "autoLC", "cam360", "hud", "matrix", "cornering", "leveling", "crab", "ws4", "tech", "avas", "regen", "autoSS"]
C = []
def car(k, model, group, name, short, kind, hp, tq_lbft, kg, drv, price, desc, gears, eng, tank, mpg, modes, has=(), cda=0.9, **x):
    C.append(dict(k=k, model=model, group=group, name=name, short=short, kind=kind, hp=hp, tq=tq_lbft, kg=kg, drv=drv, price=price, desc=desc, gears=gears, eng=eng, tank=tank, mpg=mpg, modes=modes, has=list(has), cda=cda, **x))
# 2010 Acura MDX: 3.7 L V6 300 hp / 270 lb-ft, 6AT, SH-AWD. Advance: Adaptive Cruise, Collision Mitigation Braking, Blind Spot Information
M = ("acura_mdx10", "Acura MDX · 2010")
car("mdx10_base", *M, "2010 Acura MDX SH-AWD", "MDX", "ice", 300, 270, 2050, "awd", 42230, "3.7 L V6 · 6-speed · SH-AWD · 300 hp · 3 rows", G6A, "v6", 79, 17, ["Normal", "Sport"], cda=1.0)
car("mdx10_tech", *M, "2010 Acura MDX SH-AWD Technology", "MDX Technology", "ice", 300, 270, 2060, "awd", 46030, "3.7 L V6 · 6-speed · SH-AWD · 300 hp · navigation, ELS surround", G6A, "v6", 79, 17, ["Normal", "Sport"], cda=1.0)
car("mdx10_adv", *M, "2010 Acura MDX SH-AWD Advance", "MDX Advance", "ice", 300, 270, 2090, "awd", 50830, "3.7 L V6 · 6-speed · SH-AWD · 300 hp · Active Damper System", G6A, "v6", 79, 17, ["Comfort", "Sport"], has=["acc", "aeb", "bsm"], cda=1.0, sus="adaptive")
car("mdx10_ent", *M, "2010 Acura MDX SH-AWD Entertainment", "MDX Entertainment", "ice", 300, 270, 2080, "awd", 48530, "3.7 L V6 · 6-speed · SH-AWD · 300 hp · rear DVD", G6A, "v6", 79, 17, ["Normal", "Sport"], cda=1.0)
# 2017 Ford Fusion
F = ("fusion17", "Ford Fusion · 2017")
car("fus17_s", *F, "2017 Ford Fusion S", "Fusion S", "ice", 175, 175, 1560, "fwd", 22610, "2.5 L · 6-speed · FWD · 175 hp", G6F, "i4h", 62, 25, ["Normal", "Sport"], cda=0.65)
car("fus17_se", *F, "2017 Ford Fusion SE 1.5 EcoBoost", "Fusion SE", "ice", 181, 185, 1580, "fwd", 24840, "1.5 L EcoBoost · 6-speed · FWD · 181 hp · SYNC 3", G6F, "i4t", 62, 27, ["Normal", "Sport"], cda=0.65)
car("fus17_ti", *F, "2017 Ford Fusion Titanium 2.0 EcoBoost AWD", "Fusion Titanium", "ice", 245, 275, 1690, "awd", 32895, "2.0 L EcoBoost · 6-speed · AWD · 245 hp", G6F, "i4t", 62, 24, ["Normal", "Sport"], has=["acc", "aeb", "bsm", "rcta", "lka", "autoHigh", "autopark"], cda=0.65)
car("fus17_sport", *F, "2017 Ford Fusion Sport 2.7 EcoBoost AWD", "Fusion Sport", "ice", 325, 380, 1750, "awd", 33590, "2.7 L twin-turbo V6 · 6-speed · AWD · 325 hp · Continuously Controlled Damping", G6F, "v6", 62, 20, ["Normal", "Sport"], has=["bsm", "rcta"], cda=0.66, sus="adaptive")
car("fus17_plat", *F, "2017 Ford Fusion Platinum 2.0 EcoBoost AWD", "Fusion Platinum", "ice", 245, 275, 1720, "awd", 37650, "2.0 L EcoBoost · 6-speed · AWD · 245 hp", G6F, "i4t", 62, 24, ["Normal", "Sport"], has=["acc", "aeb", "bsm", "rcta", "lka", "autoHigh", "autopark"], cda=0.65)
car("fus17_hyb", *F, "2017 Ford Fusion Hybrid SE", "Fusion Hybrid SE", "hev", 188, 0, 1650, "fwd", 25675, "2.0 L hybrid · eCVT · FWD · 188 hp · 42 mpg", None, "i4h", 51, 42, ["Normal", "Sport"], has=["bsm"], cda=0.62)
car("fus17_energi", *F, "2017 Ford Fusion Energi Titanium", "Fusion Energi", "phev", 188, 0, 1780, "fwd", 33120, "2.0 L plug-in hybrid · eCVT · FWD · 188 hp · 22 mi EV", None, "i4h", 53, 42, ["Normal", "Sport"], has=["acc", "aeb", "bsm", "rcta", "lka", "autoHigh"], cda=0.62, kWh=7.6, evMi=22)
# 2007 Ford Mustang
S = ("mustang07", "Ford Mustang · 2007")
car("must07_v6", *S, "2007 Ford Mustang V6 Deluxe Coupe", "Mustang V6", "ice", 210, 240, 1520, "rwd", 19995, "4.0 L V6 · 5-speed manual · RWD · 210 hp", G5M, "v6", 61, 19, ["Normal"], cda=0.72, manual=True)
car("must07_v6p", *S, "2007 Ford Mustang V6 Premium Coupe", "Mustang V6 Premium", "ice", 210, 240, 1530, "rwd", 21470, "4.0 L V6 · 5-speed auto · RWD · 210 hp · Shaker 500", G5A, "v6", 61, 18, ["Normal"], cda=0.72)
car("must07_gt", *S, "2007 Ford Mustang GT Deluxe Coupe", "Mustang GT", "ice", 300, 320, 1585, "rwd", 25995, "4.6 L V8 · 5-speed manual · RWD · 300 hp", G5M, "v8", 61, 17, ["Normal"], cda=0.74, manual=True)
car("must07_gtp", *S, "2007 Ford Mustang GT Premium Coupe", "Mustang GT Premium", "ice", 300, 320, 1595, "rwd", 29995, "4.6 L V8 · 5-speed manual · RWD · 300 hp · leather", G5M, "v8", 61, 17, ["Normal"], cda=0.74, manual=True)
car("must07_gt500", *S, "2007 Ford Shelby GT500 Coupe", "Shelby GT500", "ice", 500, 480, 1750, "rwd", 42975, "5.4 L supercharged V8 · 6-speed manual · RWD · 500 hp", [2.66, 1.78, 1.30, 1.00, 0.80, 0.63], "v8", 61, 14, ["Normal"], cda=0.76, manual=True)
# 2007 Kia Sportage
K = ("sportage07", "Kia Sportage · 2007")
car("sport07_lx", *K, "2007 Kia Sportage LX 2.0", "Sportage LX", "ice", 140, 136, 1500, "fwd", 16995, "2.0 L · 4-speed · FWD · 140 hp", G4K, "i4h", 58, 21, ["Normal"], cda=0.95)
car("sport07_lxv6", *K, "2007 Kia Sportage LX V6 4WD", "Sportage LX V6", "ice", 173, 178, 1640, "awd", 20595, "2.7 L V6 · 4-speed · 4WD with lock · 173 hp", G4K, "v6", 58, 18, ["Normal"], cda=0.95)
car("sport07_ex", *K, "2007 Kia Sportage EX V6 4WD", "Sportage EX V6", "ice", 173, 178, 1660, "awd", 23295, "2.7 L V6 · 4-speed · 4WD with lock · 173 hp · leather, sunroof", G4K, "v6", 58, 18, ["Normal"], cda=0.95)
STD = {"Acura": "2010 AcuraLink, Vehicle Stability Assist, side-curtain airbags. Advance: Adaptive Cruise Control, Collision Mitigation Braking System, Blind Spot Information System.",
       "Ford": "AdvanceTrac with Roll Stability Control (Fusion), MyKey, SYNC (2017 SE and up: SYNC 3). Driver Assist and Adaptive Cruise packages on Titanium / Platinum.",
       "Kia": "Electronic Stability Control, 4-wheel disc ABS, six airbags.", "Mustang": "4-wheel disc ABS, traction control (2007), side airbags on Premium."}
out = []; susr = {}; dm = {}
for c in C:
    brand = "Mustang" if "Mustang" in c["group"] else c["group"].split(" ")[0]
    kind = c["kind"]; kW = round(c["hp"] * 0.7457); drv = c["drv"]; fb = {"fwd": [1, 0], "rwd": [0, 1], "awd": [0.6, 0.4] if "MDX" not in c["group"] else [0.7, 0.3]}[drv]
    no = [f for f in OLD if f not in c["has"]]
    T = {"cda": c["cda"], "ws4": False, "crab": False, "tv": drv == "awd" and "MDX" in c["group"], "height": False, "modes": len(c["modes"]), "real": True, "model": c["model"], "group": c["group"], "name": c["name"], "short": c["short"], "desc": c["desc"],
         "mass": c["kg"], "kW": kW, "paint": "c:#2b2e33", "fwd": 0.58 if drv != "rwd" else 0.52, "modeNames": c["modes"], "pilotName": "Lane Keeping System" if "Fusion" in c["group"] else "Cruise Control", "pilotShort": "LKS", "handsOn": True,
         "odo0": {"2010": 98000, "2017": 64000, "2007": 121000}[c["group"][-4:]], "std": STD[brand], "feat": c["desc"].split(" · ")[0] + ", " + str(c["hp"]) + " hp", "noSigLC": True}
    if kind == "ice":
        T.update(ice=True, tank=c["tank"], mpg=c["mpg"])
        g = c["gears"]; D = {"layout": "ice", "eng": c["eng"], "turbo": "EcoBoost" in c["desc"] or "supercharged" in c["desc"] or "turbo" in c["desc"], "Tpk": round(c["tq"] * 1.356), "Ppk": kW * 1000,
                            "red": 6500 if c["eng"] in ("i4h", "i4t") else 6250, "idle": 700, "gears": g, "fd": 3.73 if "Mustang" in c["group"] else 4.07 if "Kia" in c["group"] else 3.4, "rev": 3.4, "bias": fb, "Tna": round(c["tq"] * 1.356 * 0.72)}
        if c.get("manual"): T["manual"] = True
    else:
        mT = c["kg"] * 2.0; P = kW * 1000; D = {"layout": "axle", "T": [round(mT), 0], "P": [P, 0]}
        T.update(hybrid=True, sound="i4h", evBtn=True, regenMax=2, tank=c["tank"], mpg=c["mpg"])
        if kind == "phev": T.update(phev=True, kWh=c["kWh"], evMi=c["evMi"]); T["feat"] = f"{c['evMi']} mi EV"
    out.append(f' add({json.dumps(c["k"])},{{...{json.dumps(T, separators=(",", ":"))},no:{json.dumps(no)}}},{json.dumps(D, separators=(", ", ": "))},{c["price"]});')
    sus = c.get("sus", "passive")
    if "MDX" in c["group"]: susr[c["k"]] = ["macpherson", "multilink", "coil", sus, "Active Damper System (Advance)" if sus == "adaptive" else "Passive dampers, multilink rear", "front_rear", None, 203, [170, 190], "sport" if sus == "adaptive" else "balanced"]
    elif "Fusion" in c["group"]: susr[c["k"]] = ["macpherson", "multilink", "coil", sus, "Continuously Controlled Damping" if sus == "adaptive" else "Passive dampers, multilink rear", "front_rear", None, 140, [150, 170], "sport" if sus == "adaptive" else "comfort"]
    elif "Mustang" in c["group"]: susr[c["k"]] = ["macpherson", "solid_axle_coil", "coil", "passive", "Three-link solid rear axle with Panhard rod" + (", Shelby-tuned Bilstein dampers" if "gt500" in c["k"] else ""), "front_rear", None, 130, [140, 150], "sport" if "gt" in c["k"] else "balanced"]
    else: susr[c["k"]] = ["macpherson", "multilink", "coil", "passive", "Passive dampers, multilink rear", "front_rear", None, 195, [165, 185], "comfort"]
    dm[c["k"]] = {"m": [[n, n.lower() if n.lower() in ("normal", "sport", "comfort") else "normal", {"Normal": "Default balance of response, comfort and efficiency.", "Sport": "Sharper throttle and later shifts.", "Comfort": "Softer Active Damper setting for a smoother ride."}[n]] for n in c["modes"]]}
    if kind != "ice": dm[c["k"]]["ev"] = {"btn": "EV", "modes": [["hyb", "EV Auto"], ["ev", "EV Now"], ["save", "EV Later"], ["charge", "EV Charge"]] if kind == "phev" else [["ev", "EV Now"]]}
PG = {"Acura MDX · 2010": [["Aspen White Pearl", "#ecebe5", 0, None], ["Crystal Black Pearl", "#0e0f12", 0, None], ["Palladium Metallic", "#9fa2a3", 0, None], ["Grigio Metallic", "#5d6064", 0, None], ["Dark Cherry Pearl", "#4a1418", 0, None], ["Bali Blue Pearl", "#24395c", 0, None]],
      "Ford Fusion · 2017": [["Oxford White", "#eef0ef", 0, None], ["Shadow Black", "#0e0f11", 0, None], ["Ingot Silver", "#a6aaae", 0, None], ["Magnetic", "#4a4d50", 0, None], ["Ruby Red", "#7d0f16", 395, None], ["Lightning Blue", "#2a5a9a", 0, None], ["White Platinum", "#f1f0ea", 595, None]],
      "Ford Mustang · 2007": [["Performance White", "#f0f0ee", 0, None], ["Black", "#0d0e10", 0, None], ["Torch Red", "#b10e16", 0, None], ["Grabber Orange", "#e0601a", 0, None], ["Vista Blue Metallic", "#2c62a8", 0, None], ["Satin Silver Metallic", "#a8acaf", 0, None], ["Windveil Blue", "#4f6f8f", 0, None]],
      "Kia Sportage · 2007": [["Clear White", "#efefec", 0, None], ["Black Cherry", "#2b0c12", 0, None], ["Smokey Blue", "#3b4a5c", 0, None], ["Steel Silver", "#a4a8ac", 0, None], ["Ebony Black", "#0e0f11", 0, None], ["Sunset Orange", "#c55a1c", 0, None]]}
js = "\n".join(out) + "\n"
open(sys.argv[1], "w").write(json.dumps({"adds": js, "susr": susr, "dm": dm, "pg": PG, "keys": [c["k"] for c in C]}))
print(len(C), "trims")
