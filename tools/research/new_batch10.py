"""Trims for the Genesis / Chevrolet / Nissan pack (Oct 23 2026): one representative trim per model file.
US specs as of mid-2026 (manufacturer sites / press); 2027 figures not yet rated are estimates. Writes the add(...) lines."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import new_batch7 as B
GE = "Genesis Active Safety Control: Forward Collision-Avoidance Assist, Lane Keeping Assist, Lane Following Assist, Blind-Spot Collision-Avoidance Assist, Rear Cross-Traffic Collision-Avoidance Assist, Smart Cruise Control with Stop & Go, Highway Driving Assist II."
CH = "Chevy Safety Assist: Automatic Emergency Braking, Front Pedestrian Braking, Lane Keep Assist with Lane Departure Warning, Following Distance Indicator, Forward Collision Alert, IntelliBeam."
NI = "Nissan Safety Shield 360: automatic emergency braking with pedestrian detection, rear automatic braking, blind spot warning, rear cross traffic alert, lane departure warning, high beam assist."
B.BR.update({"Genesis": (GE, "Highway Driving Assist II", "HDA II", False), "Chevrolet": (CH, "Adaptive Cruise Control", "ACC", False), "Nissan": (NI, "ProPILOT Assist", "ProPILOT", False)})
B.PAINT.update({"Genesis": "c:#2f3a33", "Chevrolet": "c:#a8acb0", "Nissan": "c:#7a1f24"})
B.C.clear(); X = B.car; G8 = B.G8H; CV = B.CV
X("gen_g70_25t", "gen_g70", "Genesis G70 · 2027", "2027 Genesis G70 2.5T AWD", "G70 2.5T", "ice", 300, 1720, "awd", 44000, "2.5 L turbo · 8-speed · AWD · 300 hp", eng="i4t", tq=422, gears=G8, tank=60, mpg=24, cda=0.68, modes=["Eco","Comfort","Sport","Snow"])
X("gen_g80_25t", "gen_g80", "Genesis G80 · 2027", "2027 Genesis G80 2.5T AWD", "G80 2.5T", "ice", 300, 1900, "awd", 57000, "2.5 L turbo · 8-speed · AWD · 300 hp", eng="i4t", tq=422, gears=G8, tank=73, mpg=23, cda=0.7, modes=["Eco","Comfort","Sport","Snow"])
X("gen_g90_35t", "gen_g90", "Genesis G90 · 2026", "2026 Genesis G90 3.5T e-SC AWD", "G90 3.5T e-SC", "ice", 409, 2300, "awd", 100000, "3.5 L twin-turbo V6 + electric supercharger · 8-speed · AWD · 409 hp", eng="v6", tq=549, gears=G8, tank=83, mpg=20, cda=0.75, modes=["Eco","Comfort","Sport","Snow"])
X("gen_gv60_adv", "gen_gv60", "Genesis GV60 · 2027", "2027 Genesis GV60 Advanced AWD", "GV60 Advanced", "ev", 314, 2150, "awd", 54000, "Dual motor · AWD · 314 hp · 84 kWh · about 264 mi", kWh=84, rng=264, cda=0.72, modes=["Eco","Comfort","Sport","Snow"])
X("gen_gv70_25t", "gen_gv70", "Genesis GV70 · 2027", "2027 Genesis GV70 2.5T AWD", "GV70 2.5T", "ice", 300, 1950, "awd", 48000, "2.5 L turbo · 8-speed · AWD · 300 hp", eng="i4t", tq=422, gears=G8, tank=66, mpg=22, cda=0.88, modes=["Eco","Comfort","Sport","Snow"])
X("gen_egv70", "gen_egv70", "Genesis Electrified GV70 · 2027", "2027 Genesis Electrified GV70 AWD", "Electrified GV70", "ev", 429, 2300, "awd", 67000, "Dual motor · AWD · 429 hp (483 with Boost) · 84 kWh · about 263 mi", kWh=84, rng=263, cda=0.82, modes=["Eco","Comfort","Sport","Snow"])
X("gen_gv80_25t", "gen_gv80", "Genesis GV80 · 2027", "2027 Genesis GV80 2.5T AWD", "GV80 2.5T", "ice", 300, 2200, "awd", 60000, "2.5 L turbo · 8-speed · AWD · 300 hp", eng="i4t", tq=422, gears=G8, tank=80, mpg=21, cda=1.0, modes=["Eco","Comfort","Sport","Snow"])
X("gen_gv80c_35t", "gen_gv80c", "Genesis GV80 Coupe · 2027", "2027 Genesis GV80 Coupe 3.5T e-SC", "GV80 Coupe 3.5T", "ice", 409, 2300, "awd", 82000, "3.5 L twin-turbo V6 + electric supercharger · 8-speed · AWD · 409 hp", eng="v6", tq=549, gears=G8, tank=80, mpg=19, cda=0.98, modes=["Eco","Comfort","Sport","Snow"])
X("chv_bolt_lt", "chv_bolt", "Chevrolet Bolt · 2027", "2027 Chevrolet Bolt LT", "Bolt LT", "ev", 210, 1750, "fwd", 28995, "Single motor · FWD · 210 hp · 65 kWh LFP · about 262 mi", kWh=65, rng=262, cda=0.72, modes=["Normal","Sport","Snow/Ice"])
X("chv_malibu_lt", "chv_malibu", "Chevrolet Malibu · 2025", "2025 Chevrolet Malibu LT", "Malibu LT", "ice", 163, 1440, "fwd", 28000, "1.5 L turbo · CVT · FWD · 163 hp", eng="i4t", tq=250, gears=CV, cvt=True, tank=59, mpg=32, cda=0.66, modes=["Normal","Sport","Snow/Ice"])
X("nissan_altima27_sv", "nissan_altima", "Nissan Altima · 2027", "2027 Nissan Altima SV", "Altima SV", "ice", 188, 1460, "fwd", 29000, "2.5 L · Xtronic CVT · FWD · 188 hp", eng="i4h", tq=244, gears=CV, cvt=True, tank=61, mpg=32, cda=0.66, modes=["Normal","Sport"])

out = []
for c in B.C:
    brand = c["group"].split(" ")[0] if not c["group"].startswith("Mercedes-Maybach") else "Mercedes-Benz"
    std, pn, ps, sc = B.BR[brand]
    kW = round(c["hp"] * 0.7457); kind = c["kind"]; drv = c["drv"]
    fb = {"fwd": [1, 0], "rwd": [0, 1], "awd": [0.6, 0.4] if brand != "BMW" and brand != "Mercedes-Benz" else [0.4, 0.6]}[drv]
    modes = c.get("modes") or (["Eco", "Normal", "Sport"] if brand == "Hyundai" else ["Eco Pro", "Comfort", "Sport"] if brand == "BMW" else ["Eco", "Comfort", "Sport"] if brand == "Mercedes-Benz" else ["Tour", "Sport", "Snow/Ice"])
    T = {"cda": c["cda"], "ws4": False, "crab": False, "tv": False, "height": False, "modes": len(modes), "real": True, "model": c["model"], "group": c["group"].replace("Mercedes-Maybach", "Mercedes-Benz Maybach") if False else c["group"],
         "name": c["name"], "short": c["short"], "desc": c["desc"], "mass": c["kg"], "kW": kW, "paint": B.PAINT[brand], "fwd": 0.56 if drv != "rwd" else 0.5, "modeNames": modes,
         "pilotName": pn, "pilotShort": ps, "handsOn": not sc, "odo0": 20, "std": std, "feat": c["desc"].split(" · ")[0] + ", " + str(c["hp"]) + " hp"}
    if sc: T["pilotHwy"] = True
    if kind == "ice":
        T.update(ice=True, tank=c["tank"], mpg=c["mpg"]); no = B.NO_ICE
        cv = c.get("cvt", False); g = c["gears"]
        D = {"layout": "ice", "eng": c["eng"], "turbo": c["eng"] in ("i4t", "v6", "v8") and "turbo" in c["desc"] or "supercharged" in c["desc"], "Tpk": c["tq"], "Ppk": kW * 1000,
             "red": 6500 if c["eng"] in ("i4h", "i4t") else 6200, "idle": 700, "gears": g, "fd": 3.2 if not cv else 4.0, "rev": 3.4, "bias": fb, "Tna": round(c["tq"] * 0.72)}
        if cv: D.update(cvt=True, rmin=0.4, rmax=2.6)
    else:
        mT = c["kg"] * (3.0 if kind == "ev" else 2.0)
        P = kW * 1000
        D = {"layout": "axle", "T": [round(mT * fb[0]), round(mT * fb[1])], "P": [round(P * fb[0]), round(P * fb[1])]}
        if kind == "ev":
            T.update(kWh=c["kWh"], regenMax=3); T["feat"] = f"about {c['rng']} mi"; no = B.NO_EV
        else:
            T.update(hybrid=True, sound=c.get("eng", "i4t"), evBtn=True, regenMax=2, tank=c["tank"], mpg=c["mpg"]); no = B.NO_HEV
            if kind == "phev": T.update(phev=True, kWh=c["kWh"], evMi=c["evMi"]); T["feat"] = f"{c['evMi']} mi EV"
    out.append(f' add({json.dumps(c["key"])},{{...{json.dumps(T, separators=(",", ":"))},no:{json.dumps(no)}}},{json.dumps(D, separators=(", ", ": "))},{c["price"]});')
if __name__ == "__main__":
    open(sys.argv[1], "w").write("\n".join(out) + "\n")
    print(len(out), "trims")
