"""2022 Ford F-150 SuperCrew 4x4 (14th gen, pre-2024 facelift) — every US trim on the uploaded f150_22 model.
Engines per Edmunds 2022 trim list (standard engine shown; Lariat/King Ranch/Platinum list their popular engines). Prices are 2022 SuperCrew 4x4 estimates."""
import json
G10 = [4.70, 2.99, 2.15, 1.80, 1.52, 1.28, 1.00, 0.85, 0.69, 0.64]
FCP = "Ford Co-Pilot360 2.0: Pre-Collision Assist with Automatic Emergency Braking, BLIS with trailer coverage and Cross-Traffic Alert, Lane-Keeping System, Auto High Beams, Post-Collision Braking, rear view camera."
FCPA = FCP + " Co-Pilot360 Assist 2.0: Intelligent Adaptive Cruise with Stop-and-Go and Lane Centering, Speed Sign Recognition, Evasive Steering Assist."
BLUE = FCPA + " BlueCruise hands-free driving on mapped highways, Active Park Assist 2.0, 360° camera."
S = ["cornering", "leveling", "crab", "matrix", "ws4"]
ENG = {"33": ("v6", False, 359, 290, 6500, "3.3 L Ti-VCT V6"), "27": ("v6", True, 542, 325, 6000, "2.7 L EcoBoost V6"), "50": ("v8", False, 556, 400, 7000, "5.0 L Coyote V8"),
       "35": ("v6", True, 678, 400, 6000, "3.5 L EcoBoost V6"), "pb": ("v6", True, 773, 430, 6000, "3.5 L PowerBoost hybrid V6"), "hor": ("v6", True, 691, 450, 6000, "3.5 L High-Output EcoBoost V6")}
TR = [  # key, trim, engine, kg, price, paint, mpg, tank L, extras
    ("f150_22_xl", "XL", "33", 2050, 41500, "c:#eeeeec", 20, 87, dict(std=FCP, feats=["bsm", "rcta", "autoHigh", "towPkg", "awd"])),
    ("f150_22_stx", "STX", "27", 2120, 45000, "c:#1c1d20", 20, 87, dict(std=FCP, feats=["bsm", "rcta", "autoHigh", "towPkg", "awd"])),
    ("f150_22_xlt", "XLT", "27", 2180, 49500, "c:#2c5a7a", 20, 87, dict(std=FCP, feats=["bsm", "rcta", "autoHigh", "remoteStart", "towPkg", "awd"])),
    ("f150_22_lariat", "Lariat", "50", 2300, 58500, "c:#7a1f24", 19, 98, dict(std=FCPA, feats=["acc", "pilot", "bsm", "rcta", "autoHigh", "heatedSeats", "ventSeats", "heatedWheel", "remoteStart", "wirelessCharge", "towPkg", "awd"])),
    ("f150_22_kr", "King Ranch", "35", 2380, 64500, "c:#5a3a22", 18, 98, dict(std=FCPA + " 360° camera.", feats=["acc", "pilot", "bsm", "rcta", "autoHigh", "cam360", "heatedSeats", "ventSeats", "heatedWheel", "heatedRear", "remoteStart", "wirelessCharge", "premiumAudio", "towPkg", "awd"])),
    ("f150_22_plat", "Platinum", "35", 2400, 67000, "c:#3a3d42", 18, 98, dict(std=FCPA + " 360° camera, Active Park Assist 2.0.", feats=["acc", "pilot", "bsm", "rcta", "rAeb", "autoHigh", "cam360", "autopark", "heatedSeats", "ventSeats", "heatedWheel", "heatedRear", "massageSeats", "remoteStart", "wirelessCharge", "premiumAudio", "panoRoof", "ambient", "towPkg", "trailerAssist", "awd"])),
    ("f150_22_ltd", "Limited", "pb", 2560, 79000, "c:#d8d6d0", 23, 114, dict(std=BLUE + " PowerBoost full hybrid: 35 kW motor in the 10-speed, 1.5 kWh battery, Pro Power Onboard 7.2 kW.", hybrid=True, feats=["acc", "pilot", "handsfree", "autoLC", "bsm", "rcta", "rAeb", "autoHigh", "cam360", "autopark", "heatedSeats", "ventSeats", "heatedWheel", "heatedRear", "massageSeats", "remoteStart", "wirelessCharge", "premiumAudio", "panoRoof", "ambient", "towPkg", "trailerAssist", "proPower", "awd"])),
    ("f150_22_tremor", "Tremor", "35", 2450, 58500, "c:#c45a1a", 17, 98, dict(std=FCPA + " Electronic locking rear differential, Trail Control, Trail Turn Assist, 33-in. all-terrain tyres.", offGrip=1.3, feats=["acc", "pilot", "bsm", "rcta", "autoHigh", "offroad", "towPkg", "heatedSeats", "remoteStart", "proPower", "awd", "perfUpgrade"])),
    ("f150_22_raptor", "Raptor", "hor", 2600, 66000, "c:#2f6fb0", 15, 136, dict(std=FCP + " Trail Control, Trail Turn Assist, front and rear e-lockers, 360° camera with off-road spotter view.", offGrip=1.45, feats=["bsm", "rcta", "autoHigh", "cam360", "offroad", "heatedSeats", "heatedWheel", "remoteStart", "premiumAudio", "awd", "perfUpgrade", "sportExhaust"])),
]
MODES = [["Normal", "normal", "Default on-road calibration for throttle, shifting, steering and 4x4."], ["Eco", "eco", "Softer throttle and early upshifts to save fuel."],
         ["Sport", "sport", "Quicker throttle response, holds gears longer and firmer steering."], ["Tow/Haul", "tow", "Adjusts shift points and grade braking for trailers and heavy loads."],
         ["Slippery", "snow", "Reduces throttle and adjusts traction control for snow, ice or wet roads."], ["Deep Snow/Sand", "sand", "Allows more wheelspin and holds gears for deep snow or sand."],
         ["Mud/Rut", "mud", "Permits wheelspin and keeps momentum in mud and deep ruts."]]
ROCK = ["Rock Crawl", "rock", "4x4 Low only: slow, precise throttle and locked rear differential for rocks."]
BAJA = ["Baja", "offroad", "High-speed desert running: quickest throttle and shifts, Fox Live Valve dampers firm up, traction control eased off."]
OFFRD = ["Off-Road", "offroad", "General off-road: softer throttle, more wheelspin allowed, dampers tuned for rough trails."]


def build():
    adds, dm, su = [], {}, {}
    for key, trim, e, kg, price, paint, mpg, tank, x in TR:
        eng, turbo, tq, hp, red, en = ENG[e]; kW = round(hp * 0.7457); hyb = x.get("hybrid")
        feats = x["feats"]; std = x["std"]
        pilot = ("BlueCruise", "BLUE", False) if "handsfree" in feats else ("Lane Centering", "LC", True)
        T = {"cda": 1.6 if trim == "Raptor" else 1.55, "ws4": False, "crab": False, "tv": False, "height": False, "modes": 7, "real": True, "model": "f150_22", "group": "Ford F-150 · 2022",
             "name": f"2022 Ford F-150 {trim} SuperCrew 4x4", "short": f"F-150 {trim}", "desc": f"{en} · 10-speed · 4x4 · {hp} hp", "mass": kg, "kW": kW, "paint": paint, "fwd": 0.56, "Ff": 6800, "Fr": 6400,
             "modeNames": [m[0] for m in MODES], "noSigLC": True, "pilotName": pilot[0], "pilotShort": pilot[1], "handsOn": pilot[2], "odo0": 31000, "std": std, "ice": True, "tank": tank, "mpg": mpg,
             "feat": f"{en}, {hp} hp"}
        if not pilot[2]: T["pilotHwy"] = True
        if "offGrip" in x: T["offGrip"] = x["offGrip"]
        if hyb: T["par"] = True
        no = S + ["avas", "regen", "tech"] + ([] if "autopark" in feats else ["autopark"]) + ([] if "autoLC" in feats else ["autoLC"]) + ([] if "acc" in feats else ["acc", "pilot"])
        D = {"layout": "ice", "eng": eng, "turbo": turbo, "Tna": round(tq * (0.6 if turbo else 0.9)), "Tpk": tq, "Ppk": kW * 1000, "red": red, "idle": 650 if eng == "v6" else 600, "gears": G10,
             "fd": 3.73 if trim in ("Tremor", "Raptor") else 3.55 if e != "50" else 3.31, "rev": 4.87, "bias": [0.3, 0.7]}
        if e == "50": D["pkRpm"] = 4250
        if hyb: D["par"] = {"T": 240, "P": 35000, "kWh": 1.5}
        adds.append(f' add({json.dumps(key)},{{...{json.dumps(T, separators=(",", ":"))},no:{json.dumps(no)}}},{json.dumps(D, separators=(", ", ": "))},{price});')
        m = [list(a) for a in MODES]
        if trim == "Raptor": m = [m[0], m[2], m[4], m[3], OFFRD, BAJA, list(ROCK), m[6]]
        elif trim == "Tremor": m.append(list(ROCK))
        t = ["Two-speed transfer case with 4WD Low" + (" and 4A automatic 4WD" if trim not in ("XL", "STX") else ""), "Hill Descent Control" + ("" if trim in ("Tremor", "Raptor") else " (with FX4)")]
        if trim in ("Tremor",): t += ["Electronic locking rear differential", "Trail Control (low-speed off-road cruise)", "Trail Turn Assist"]
        if trim == "Raptor": t += ["Front Torsen and rear electronic locking differentials", "Trail Control", "Trail Turn Assist", "Fox Live Valve dampers with end-stop control"]
        if hyb: m_ev = None
        s = ["adaptive", "Fox Live Valve 3.0 internal-bypass dampers, five-link coil rear", True] if trim == "Raptor" else ["passive", "FOX 2.0 monotube off-road shocks" if trim == "Tremor" else "Independent front / leaf-spring rear passive suspension", False]
        dm[key] = {"m": m, "t": t, "s": s}
        if trim == "Raptor": su[key] = ["double_wishbone", "solid_axle_coil", "coil", "bypass", "Fox 3.0 Live Valve internal-bypass shocks, 5-link coil rear", "front_rear", None, 307, [356, 381], "offroad"]
        elif trim == "Tremor": su[key] = ["double_wishbone", "solid_axle_leaf", "leaf_rear", "reservoir", "FOX 2.0 monotube off-road shocks", "front_only", None, 239, [230, 260], "offroad"]
        else: su[key] = ["double_wishbone", "solid_axle_leaf", "leaf_rear", "passive", "Twin-tube passive shocks" + (" (PowerBoost hybrid)" if hyb else ""), "front_only", None, 239 if trim != "XL" else 236, [210, 240], "comfort"]
    keys = [t[0] for t in TR]
    std = {t[0]: t[8]["feats"] for t in TR}
    bd = {"pk": [["XL Mid Equipment Group 101A", 1795, ["f150_22_xl"], "power windows/locks, cruise control, SYNC 4, remote keyless entry", []],
                 ["XLT Mid Equipment Group 301A", 2195, ["f150_22_xlt"], "power-adjustable pedals, dual-zone climate, 8-way power driver seat, LED box lighting, remote start", ["remoteStart"]],
                 ["XLT High Equipment Group 302A", 6445, ["f150_22_xlt"], "301A plus heated front seats and wheel, 12-in. touchscreen, Co-Pilot360 Assist 2.0, B&O audio, power tailgate", ["heatedSeats", "heatedWheel", "acc", "pilot", "premiumAudio"]],
                 ["Lariat High Equipment Group 502A", 6880, ["f150_22_lariat"], "ambient lighting, heated 2nd row, B&O Unleashed 18-speaker audio, 360° camera, Active Park Assist 2.0", ["ambient", "heatedRear", "premiumAudio", "cam360", "autopark"]],
                 ["King Ranch High Equipment Group 701A", 3950, ["f150_22_kr"], "Max Recline seats, Active Park Assist 2.0, twin-panel moonroof", ["panoRoof", "autopark"]],
                 ["Platinum Plus Package", 3995, ["f150_22_plat"], "twin-panel moonroof, Max Recline seats, 22-in. wheels", ["panoRoof"]],
                 ["FX4 Off-Road Package", 1145, ["f150_22_xl", "f150_22_stx", "f150_22_xlt", "f150_22_lariat", "f150_22_kr", "f150_22_plat"], "electronic locking rear axle, skid plates, off-road shocks, Hill Descent Control", ["offroad"]],
                 ["Max Trailer Tow Package", 1610, ["f150_22_xlt", "f150_22_lariat", "f150_22_kr", "f150_22_plat"], "integrated trailer brake controller, e-locking rear axle, Pro Trailer Backup Assist", ["towPkg", "trailerAssist"]],
                 ["Ford Co-Pilot360 Active 2.0 Prep (BlueCruise)", 1595, ["f150_22_lariat", "f150_22_kr", "f150_22_plat"], "BlueCruise hands-free highway driving hardware and 3-year service", ["handsfree", "autoLC"]],
                 ["Raptor 37 Performance Package", 7500, ["f150_22_raptor"], "37-in. BFGoodrich KO2 tyres, 17-in. beadlock-capable wheels, Fox Live Valve recalibration", ["perfUpgrade"]],
                 ["Tremor High Equipment Group 401A", 5200, ["f150_22_tremor"], "12-in. touchscreen, B&O audio, 360° camera, heated/ventilated seats, twin-panel moonroof", ["cam360", "premiumAudio", "ventSeats", "panoRoof"]]],
          "op": [["exterior", "Twin-Panel Moonroof", 1495, ["f150_22_xlt", "f150_22_lariat", "f150_22_tremor"], "power twin-panel moonroof", ["panoRoof"], None],
                 ["exterior", "Factory Spray-In Bedliner", 595, None, "black spray-in bedliner", ["bedLinerFeat"], "bedLiner"],
                 ["mechanical", "Pro Power Onboard 2.0 kW", 995, ["f150_22_xlt", "f150_22_lariat", "f150_22_kr", "f150_22_plat"], "2.0 kW 120V outlets in the bed", ["proPower"], None],
                 ["mechanical", "Pro Power Onboard 7.2 kW", 750, ["f150_22_ltd"], "7.2 kW generator with 240V outlet", ["proPower"], None],
                 ["mechanical", "3.5 L PowerBoost Full Hybrid V6", 3300, ["f150_22_xlt", "f150_22_lariat", "f150_22_kr", "f150_22_plat"], "430 hp hybrid V6 (engine upgrade)", ["perfUpgrade"], None],
                 ["exterior", "Power Deployable Running Boards", 1095, ["f150_22_lariat", "f150_22_kr", "f150_22_plat"], "automatic power-deploying running boards", [], "runningBoards"],
                 ["exterior", "Tailgate Work Surface", 225, ["f150_22_xl", "f150_22_stx", "f150_22_xlt", "f150_22_lariat"], "tailgate work surface with clamp pockets", [], None]],
          "wh": [["17-in. Silver Steel", 0, ["f150_22_xl"]], ["18-in. Dark Painted Aluminum", 0, ["f150_22_stx"]], ["18-in. Chrome-Like PVD Aluminum", 0, ["f150_22_xlt"]], ["20-in. Machined Aluminum", 995, ["f150_22_xlt", "f150_22_lariat"]],
                 ["20-in. King Ranch Painted Aluminum", 0, ["f150_22_kr"]], ["20-in. Polished Aluminum", 0, ["f150_22_plat"]], ["22-in. Polished Aluminum", 0, ["f150_22_ltd"]], ["18-in. Carbonized Gray w/ 33-in. A/T", 0, ["f150_22_tremor"]], ["17-in. Raptor Aluminum w/ 35-in. BFGoodrich KO2", 0, ["f150_22_raptor"]]],
          "ac": [["Ford Soft Roll-Up Tonneau Cover", 549, "vinyl roll-up cover", "bedCover", []], ["Bed Extender", 385, "folding tubular bed extender", "bedExtender", []], ["All-Weather Floor Liners", 225, "front and rear molded liners", "floorMats", []]],
          "std": std, "nf": {}, "int": [["Medium Earth Gray Vinyl", 0, ["f150_22_xl"]], ["Medium Dark Slate Cloth", 0, ["f150_22_stx", "f150_22_xlt"]], ["Black Onyx Leather", 0, ["f150_22_lariat", "f150_22_plat"]], ["Java King Ranch Leather", 0, ["f150_22_kr"]], ["Black Onyx/Light Slate Leather", 0, ["f150_22_ltd"]], ["Black Onyx ActiveX", 0, ["f150_22_tremor"]], ["Black Onyx Cloth w/ Blue Accents", 0, ["f150_22_raptor"]]],
          "ty": [["All-Season (std)", 0, ["f150_22_xl", "f150_22_stx", "f150_22_xlt", "f150_22_lariat", "f150_22_kr", "f150_22_plat", "f150_22_ltd"], "allseason"], ["275/65R18 All-Terrain", 195, ["f150_22_stx", "f150_22_xlt", "f150_22_lariat"], "allterrain"], ["33-in. All-Terrain (std)", 0, ["f150_22_tremor"], "allterrain"], ["35-in. BFGoodrich KO2 (std)", 0, ["f150_22_raptor"], "allterrain"]],
          "conf": "estimate", "src": "https://edmunds.com/ford/f-150/2022/trims"}
    return adds, dm, su, {"Ford F-150 · 2022": bd}, keys
