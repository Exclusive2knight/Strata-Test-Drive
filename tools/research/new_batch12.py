"""Batch 12 (Nov 1 2026): new models from the Chevrolet / Navigator / Range Rover pack
   - Land Rover Range Rover · 2026 (rr_rangerover), Range Rover Sport · 2026 (rr_sport), Range Rover Velar · 2026 (rr_velar), Range Rover Evoque · 2026 (rr_evoque)
   - Lincoln Navigator · 2026 (lin_navigator)
Sources: cars.com "How Much Is the 2026 Land Rover Range Rover?" (prices incl. destination), cars.com 2026 Velar trims, TrueCar 2026 Evoque and
2027 Range Rover Sport trims, Ford Authority 2026 Navigator lineup (prices excl. $2,595 destination). Weights, tanks and mpg are estimates.
The P550e plug-in hybrids are modelled as their combined output (no plug-in battery modes yet). Writes JSON for apply_batch12.py."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import new_batch7 as B
import new_batch11 as NB   # reuses its trims() builder (it fills B.C on import: cleared below)

LR = "Land Rover safety: Emergency Braking, Lane Keep Assist, Driver Condition Monitor, Traffic Sign Recognition with Adaptive Speed Limiter, Blind Spot Assist, Rear Traffic Monitor, Adaptive Cruise Control with Steering Assist, 3D Surround Camera, Park Assist, ClearSight Ground View."
LRB = "Land Rover safety: Emergency Braking, Lane Keep Assist, Driver Condition Monitor, Traffic Sign Recognition with Adaptive Speed Limiter, Blind Spot Assist, Rear Traffic Monitor, Adaptive Cruise Control, 3D Surround Camera."
LN = "Lincoln Co-Pilot360 2.0: Pre-Collision Assist with Automatic Emergency Braking, Blind Spot Information System with Cross-Traffic Alert, Lane-Keeping System, Rear Brake Assist, Auto High Beams. Co-Pilot360 Plus: Intelligent Adaptive Cruise with Stop-and-Go, Lane Centering and Speed Sign Recognition, Evasive Steering Assist, Reverse Brake Assist, Active Park Assist 2.0, 360° camera. BlueCruise hands-free highway driving."
B.BR.update({"Land": (LR, "Adaptive Cruise Control with Steering Assist", "ACC", False), "Lincoln": (LN, "BlueCruise", "BlueCruise", True)})
B.PAINT.update({"Land": "c:#2c3a36", "Lincoln": "c:#1d2430"})
B.C.clear(); X = B.car
G8 = B.G8; G10 = B.G10
TR = ["Comfort", "Eco", "Dynamic", "Grass Gravel Snow", "Mud & Ruts", "Sand", "Rock Crawl"]          # Terrain Response 2 (+ Auto)
TRV = ["Comfort", "Eco", "Dynamic", "Grass Gravel Snow", "Mud & Ruts", "Sand"]                     # Velar / Evoque (no low range)
TRE = ["Comfort", "Eco", "Grass Gravel Snow", "Mud & Ruts", "Sand"]
LIN = ["Normal", "Conserve", "Excite", "Slippery", "Deep Conditions"]
TOP = ["acc", "pilot", "bsm", "rcta", "rAeb", "autoHigh", "cam360", "autopark", "hud", "matrix", "heatedSeats", "ventSeats", "heatedWheel", "heatedRear", "massageSeats", "remoteStart", "wirelessCharge", "panoRoof", "powerLiftgate", "handsfreeLiftgate", "airSusp", "adaptiveDampers", "premiumAudio", "ambient", "digitalMirror", "awd", "offroad", "towPkg"]
MID = ["acc", "pilot", "bsm", "rcta", "rAeb", "autoHigh", "cam360", "heatedSeats", "heatedWheel", "remoteStart", "wirelessCharge", "panoRoof", "powerLiftgate", "airSusp", "adaptiveDampers", "ambient", "awd", "offroad"]
BASE = ["acc", "bsm", "rcta", "autoHigh", "cam360", "heatedSeats", "remoteStart", "wirelessCharge", "powerLiftgate", "awd"]

# ---------------- Range Rover · 2026 (cars.com, prices incl. destination)
G = "Land Rover Range Rover · 2026"
X("rr_p400se", "rr_rangerover", G, "2026 Range Rover P400 SE", "Range Rover P400 SE", "ice", 395, 2510, "awd", 115450, "3.0 L turbo I6 mild hybrid · 8-speed · AWD · 395 hp", eng="v6", tq=550, gears=G8, tank=90, mpg=21, cda=1.05, modes=TR, std=LR, feats=MID + ["hud", "matrix", "ws4"])
X("rr_p550e_se", "rr_rangerover", G, "2026 Range Rover P550e SE", "Range Rover P550e", "ice", 543, 2735, "awd", 128050, "3.0 L turbo I6 plug-in hybrid · 8-speed · AWD · 543 hp combined", eng="v6", tq=800, gears=G8, tank=71, mpg=24, cda=1.05, modes=TR, std=LR, feats=MID + ["hud", "matrix", "ws4"])
X("rr_p530se", "rr_rangerover", G, "2026 Range Rover P530 SE", "Range Rover P530 SE", "ice", 523, 2585, "awd", 140150, "4.4 L twin-turbo V8 · 8-speed · AWD · 523 hp", eng="v8", tq=750, gears=G8, tank=90, mpg=18, cda=1.05, modes=TR, std=LR, feats=MID + ["hud", "matrix", "ws4", "massageSeats", "premiumAudio"])
X("rr_p530ab", "rr_rangerover", G, "2026 Range Rover P530 Autobiography", "Range Rover Autobiography", "ice", 523, 2610, "awd", 176950, "4.4 L twin-turbo V8 · 8-speed · AWD · 523 hp", eng="v8", tq=750, gears=G8, tank=90, mpg=18, cda=1.05, modes=TR, std=LR, feats=TOP + ["ws4"])
X("rr_p615sv", "rr_rangerover", G, "2026 Range Rover P615 SV", "Range Rover SV", "ice", 607, 2640, "awd", 221650, "High-output 4.4 L twin-turbo V8 · 8-speed · AWD · 607 hp", eng="v8", tq=750, gears=G8, tank=90, mpg=17, cda=1.05, modes=TR, std=LR, feats=TOP + ["ws4"])
# ---------------- Range Rover Sport · 2026 (TrueCar lineup)
G = "Land Rover Range Rover Sport · 2026"
X("rrs_se", "rr_sport", G, "2026 Range Rover Sport P360 SE", "RR Sport SE", "ice", 355, 2350, "awd", 85550, "3.0 L turbo I6 mild hybrid · 8-speed · AWD · 355 hp", eng="v6", tq=500, gears=G8, tank=80, mpg=21, cda=0.98, modes=TR, std=LR, feats=MID)
X("rrs_dse", "rr_sport", G, "2026 Range Rover Sport P400 Dynamic SE", "RR Sport Dynamic SE", "ice", 395, 2370, "awd", 92650, "3.0 L turbo I6 mild hybrid · 8-speed · AWD · 395 hp", eng="v6", tq=550, gears=G8, tank=80, mpg=21, cda=0.98, modes=TR, std=LR, feats=MID + ["matrix", "hud"])
X("rrs_p550e", "rr_sport", G, "2026 Range Rover Sport P550e Autobiography", "RR Sport P550e", "ice", 542, 2650, "awd", 113850, "3.0 L turbo I6 plug-in hybrid · 8-speed · AWD · 542 hp combined", eng="v6", tq=800, gears=G8, tank=71, mpg=24, cda=0.98, modes=TR, std=LR, feats=TOP + ["ws4"])
X("rrs_ab", "rr_sport", G, "2026 Range Rover Sport P530 Autobiography", "RR Sport Autobiography", "ice", 523, 2450, "awd", 122750, "4.4 L twin-turbo V8 · 8-speed · AWD · 523 hp", eng="v8", tq=750, gears=G8, tank=80, mpg=18, cda=0.98, modes=TR, std=LR, feats=TOP + ["ws4"])
X("rrs_sv", "rr_sport", G, "2026 Range Rover Sport SV", "RR Sport SV", "ice", 626, 2410, "awd", 153850, "4.4 L twin-turbo V8 mild hybrid · 8-speed · AWD · 626 hp · 6D Dynamics", eng="v8", tq=800, gears=G8, tank=80, mpg=17, cda=0.98, modes=TR[:3] + ["SV Mode"] + TR[3:], std=LR, feats=TOP + ["ws4", "sportExhaust"])
# ---------------- Range Rover Velar · 2026 (cars.com)
G = "Land Rover Range Rover Velar · 2026"
X("rrv_s", "rr_velar", G, "2026 Range Rover Velar P250 S", "Velar P250 S", "ice", 247, 1950, "awd", 61600, "2.0 L turbo I4 · 8-speed · AWD · 247 hp", eng="i4t", tq=365, gears=G8, tank=63, mpg=23, cda=0.9, modes=TRV, std=LRB, feats=BASE)
X("rrv_dse", "rr_velar", G, "2026 Range Rover Velar P250 Dynamic SE", "Velar P250 Dynamic SE", "ice", 247, 1960, "awd", 63800, "2.0 L turbo I4 · 8-speed · AWD · 247 hp", eng="i4t", tq=365, gears=G8, tank=63, mpg=23, cda=0.9, modes=TRV, std=LR, feats=BASE + ["pilot", "matrix", "heatedWheel", "ambient"])
X("rrv_p400dse", "rr_velar", G, "2026 Range Rover Velar P400 Dynamic SE", "Velar P400 Dynamic SE", "ice", 395, 2060, "awd", 70800, "3.0 L turbo I6 mild hybrid · 8-speed · AWD · 395 hp", eng="v6", tq=550, gears=G8, tank=63, mpg=21, cda=0.9, modes=TRV, std=LR, feats=BASE + ["pilot", "matrix", "heatedWheel", "ambient", "airSusp", "adaptiveDampers"])
X("rrv_ab", "rr_velar", G, "2026 Range Rover Velar P400 Autobiography", "Velar Autobiography", "ice", 395, 2080, "awd", 78900, "3.0 L turbo I6 mild hybrid · 8-speed · AWD · 395 hp", eng="v6", tq=550, gears=G8, tank=63, mpg=21, cda=0.9, modes=TRV, std=LR, feats=BASE + ["pilot", "rAeb", "matrix", "hud", "heatedWheel", "ventSeats", "massageSeats", "ambient", "airSusp", "adaptiveDampers", "premiumAudio", "panoRoof"])
# ---------------- Range Rover Evoque · 2026 (TrueCar)
G = "Land Rover Range Rover Evoque · 2026"
X("rre_s", "rr_evoque", G, "2026 Range Rover Evoque S", "Evoque S", "ice", 246, 1850, "awd", 51375, "2.0 L turbo I4 mild hybrid · 9-speed · AWD · 246 hp", eng="i4t", tq=365, gears=[4.7, 2.84, 1.91, 1.38, 1.0, 0.81, 0.7, 0.58, 0.48], tank=65, mpg=24, cda=0.85, modes=TRE, std=LRB, feats=BASE)
X("rre_dse", "rr_evoque", G, "2026 Range Rover Evoque Dynamic SE", "Evoque Dynamic SE", "ice", 246, 1860, "awd", 56475, "2.0 L turbo I4 mild hybrid · 9-speed · AWD · 246 hp", eng="i4t", tq=365, gears=[4.7, 2.84, 1.91, 1.38, 1.0, 0.81, 0.7, 0.58, 0.48], tank=65, mpg=24, cda=0.85, modes=TRE, std=LR, feats=BASE + ["pilot", "matrix", "heatedWheel", "ambient", "premiumAudio", "panoRoof", "adaptiveDampers"])
# ---------------- Lincoln Navigator · 2026 (Ford Authority, MSRP excl. destination)
G = "Lincoln Navigator · 2026"
NAV = ["acc", "pilot", "handsfree", "autoLC", "bsm", "rcta", "rAeb", "autoHigh", "cam360", "autopark", "hud", "heatedSeats", "ventSeats", "heatedWheel", "heatedRear", "remoteStart", "wirelessCharge", "panoRoof", "powerLiftgate", "handsfreeLiftgate", "adaptiveDampers", "premiumAudio", "ambient", "towPkg", "thirdRow", "awd"]
X("nav_prem", "lin_navigator", G, "2026 Lincoln Navigator Premiere 4x4", "Navigator Premiere", "ice", 440, 2700, "awd", 91995, "3.5 L twin-turbo V6 · 10-speed · 4x4 · 440 hp", eng="v6", tq=690, gears=G10, tank=106, mpg=18, cda=1.25, modes=LIN, std=LN, feats=NAV)
X("nav_res", "lin_navigator", G, "2026 Lincoln Navigator Reserve 4x4", "Navigator Reserve", "ice", 440, 2720, "awd", 101995, "3.5 L twin-turbo V6 · 10-speed · 4x4 · 440 hp", eng="v6", tq=690, gears=G10, tank=106, mpg=18, cda=1.25, modes=LIN, std=LN, feats=NAV + ["massageSeats", "airSusp"])
X("nav_bl", "lin_navigator", G, "2026 Lincoln Black Label Navigator 4x4", "Black Label Navigator", "ice", 440, 2740, "awd", 118995, "3.5 L twin-turbo V6 · 10-speed · 4x4 · 440 hp", eng="v6", tq=690, gears=G10, tank=106, mpg=18, cda=1.25, modes=LIN, std=LN, feats=NAV + ["massageSeats", "airSusp", "captains"])

MD = {"Comfort": ("comfort", "Terrain Response: General Driving. Smooth throttle, relaxed shifts and soft air suspension."),
      "Eco": ("eco", "Gentler throttle, earlier upshifts and reduced climate load to save fuel."),
      "Dynamic": ("sport", "Sharper throttle, later shifts, firmer dampers and weightier steering; the car sits lower on the air suspension."),
      "SV Mode": ("sportplus", "SV's most focused setting: 6D Dynamics hydraulic suspension at its firmest, loudest exhaust, sharpest response."),
      "Grass Gravel Snow": ("snow", "Terrain Response: gentle throttle, early upshifts and tight traction control for slippery firm surfaces."),
      "Mud & Ruts": ("mud", "Terrain Response: raised ride height, more wheel slip allowed and locked differentials to keep moving in mud."),
      "Sand": ("sand", "Terrain Response: aggressive throttle and late upshifts to keep momentum, traction control lets the wheels spin."),
      "Rock Crawl": ("rock", "Terrain Response: low range, maximum ride height, very fine throttle and locked differentials for rocks."),
      "Normal": ("normal", "Default Lincoln Drive Mode balancing comfort and response."),
      "Conserve": ("eco", "Softens throttle and climate draw to maximize efficiency."),
      "Excite": ("sport", "Sharpens throttle, holds gears longer and firms steering and dampers."),
      "Slippery": ("snow", "Gentler throttle and adjusted traction for wet, icy or snowy roads."),
      "Deep Conditions": ("deepsnow", "Maximizes traction in deep snow, mud or sand by allowing more wheel slip.")}


def dmodes(c):
    m = [[n, MD[n][0], MD[n][1]] for n in c["modes"]]; f = c.get("feats", [])
    if c["group"].startswith("Land"):
        t = ["Terrain Response 2 with Auto", "Intelligent All-Wheel Drive"]
        if "Rock Crawl" in c["modes"]: t += ["Two-speed transfer box (low range)", "Configurable Terrain Response", "Wade Sensing (up to 900 mm)", "All-Terrain Progress Control", "Hill Descent Control"]
        else: t += ["All-Terrain Progress Control", "Hill Descent Control"]
        if "ws4" in f: t.append("All-Wheel Steering")
        s = ["airadaptive", "Electronic Air Suspension with Adaptive Dynamics" + (" and 6D Dynamics" if c["key"] == "rrs_sv" else ""), True] if "airSusp" in f else ["adaptive" if "adaptiveDampers" in f else "passive", "Adaptive Dynamics" if "adaptiveDampers" in f else "Passive dampers", True]
    else:
        t = ["4x4 with two-speed transfer case", "Lincoln Drive Modes", "Trailer Backup Assist", "Pro Trailer Hitch Assist"]
        s = ["airadaptive", "Adaptive Suspension with Road Preview and air springs", True] if "airSusp" in f else ["adaptive", "Adaptive Suspension with Road Preview", True]
    return {"m": m, "t": t, "s": s}


def susr(c):
    f = c.get("feats", []); mdl = c["model"]
    gc = {"rr_rangerover": 219, "rr_sport": 216, "rr_velar": 213, "rr_evoque": 212, "lin_navigator": 230}[mdl]
    if mdl == "lin_navigator":
        return ["double_wishbone", "multilink", "air" if "airSusp" in f else "coil", "adaptive", "Adaptive Suspension with Road Preview" + (", air springs" if "airSusp" in f else ""), "front_rear", [-50, 50] if "airSusp" in f else None, gc, [200, 220], "comfort"]
    if "airSusp" in f:
        return ["double_wishbone", "multilink", "air", "adaptive", "Electronic Air Suspension with Adaptive Dynamics", "front_rear", [-50, 75] if mdl in ("rr_rangerover", "rr_sport") else [-40, 45], gc + (75 if mdl in ("rr_rangerover", "rr_sport") else 45), [230, 260], "comfort"]
    return ["macpherson" if mdl == "rr_evoque" else "double_wishbone", "multilink", "coil", "adaptive" if "adaptiveDampers" in f else "passive", "Adaptive Dynamics" if "adaptiveDampers" in f else "Passive dampers", "front_rear", None, gc, [180, 200], "balanced"]


def bdata():
    out = {}
    for name in sorted(set(c["group"] for c in B.C)):
        ks = [c["key"] for c in B.C if c["group"] == name]
        e = {"pk": [], "op": [], "wh": [], "ac": [], "std": {c["key"]: list(c.get("feats", [])) for c in B.C if c["group"] == name}, "nf": {}, "int": [], "ty": [["All-Season (std)", 0, None, "allseason"]], "conf": "estimate", "src": ""}
        if name.startswith("Land"):
            e["pk"] = [["Off-Road Pack", 1150, ks, "All-Terrain Progress Control, Configurable Terrain Response, 20-in. all-terrain tyres", ["offroad"]],
                       ["Towing Pack", 950, ks, "electrically deployable tow hitch, Advanced Tow Assist", ["towPkg"]]]
            e["wh"] = [["20-in. alloy", 0, ks[:1]], ["21-in. alloy", 0, ks[1:] or None], ["22-in. Gloss Black", 0, ks[1:] or None]]
            e["int"] = [["Ebony Windsor leather", 0, None], ["Light Cloud / Ebony semi-aniline", 0, ks[1:] or None]]
            e["src"] = "https://www.landroverusa.com"
        else:
            e["pk"] = [["Rear Seat Entertainment", 2995, ks, "two rear-seat screens", ["rearEntertainment"]]]
            e["wh"] = [["22-in. machined alloy", 0, None], ["24-in. Black Label alloy", 0, ks[-1:]]]
            e["int"] = [["Ebony leather", 0, None], ["Black Label Chalet theme", 0, ks[-1:]]]
            e["src"] = "https://fordauthority.com/2025/12/2026-lincoln-navigator-lineup-features-new-trim-higher-prices/"
        out[name] = e
    return out


if __name__ == "__main__":
    T = NB.trims()
    adds = []
    for c, t, d, no in T:
        f = set(c.get("feats", []))
        t["modeNames"] = c["modes"]; t["modes"] = len(c["modes"])
        if c["group"].startswith("Land"):
            t["pilotName"] = "Adaptive Cruise Control with Steering Assist" if "pilot" in f else "Adaptive Cruise Control"; t["pilotShort"] = "ACC"; t["handsOn"] = True
            if "ws4" in f: t["ws4"] = True; no = [x for x in no if x != "ws4"]
        else:
            t["pilotName"] = "BlueCruise"; t["pilotShort"] = "BlueCruise"; t["handsOn"] = False
            no = [x for x in no if x not in ("autoLC", "autopark")]
        if "autopark" in f: no = [x for x in no if x != "autopark"]
        if "matrix" in f: no = [x for x in no if x != "matrix"]
        if "pilot" not in f and "pilot" not in no: no.append("pilot")
        adds.append(f' add({json.dumps(c["key"])},{{...{json.dumps(t, separators=(",", ":"))},no:{json.dumps(no)}}},{json.dumps(d, separators=(", ", ": "))},{c["price"]});')
    res = {"adds": adds, "dmodes": {c["key"]: dmodes(c) for c in B.C}, "susr": {c["key"]: susr(c) for c in B.C}, "bdata": bdata(), "keys": [c["key"] for c in B.C]}
    json.dump(res, open(sys.argv[1], "w"), indent=0)
    print(len(adds), "trims")
