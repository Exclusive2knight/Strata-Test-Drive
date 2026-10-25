"""2025 Audi Q5 / SQ5 SUV (third generation, PPC platform) — every US trim on the uploaded q5_25 model, then applies it to the template.
Q5: 2.0 TFSI 268 hp / 295 lb-ft, 7-speed S tronic, quattro, 0-60 5.8 s, 25 mpg combined, ~4,244 lb (KBB, Autoblog).
SQ5: 3.0 TFSI V6 with 48 V mild hybrid, 362 hp / 406 lb-ft, 7-speed S tronic, quattro, 0-60 about 4.4 s, ~4,464 lb.
Q5 prices from Autoblog ($52,200 / $56,700 / $60,600); SQ5 prices are estimates. Sportback body is not included (the model is the SUV body).
    python3 tools/research/q5_25.py      (rewrites the q5_25 / sq5_25 lines, DMODES, SUSR, BDATA, LAZY)"""
import json, os, re
G7 = [3.19, 2.19, 1.52, 1.06, 0.80, 0.63, 0.52]
PS = "Audi pre sense basic, front and rear (automatic emergency braking with pedestrian and cyclist detection), Audi side assist with exit warning, rear cross traffic assist, lane departure warning, park distance control front and rear, rear view camera."
ACA = " Adaptive cruise assist with lane guidance (stop and go, keeps you centred in the lane, hands on), top view camera."
PRE = " Park assist plus (steers itself into and out of spaces), Audi active lane assist, traffic sign recognition."
S = ["crab", "ws4", "cornering"]
TR = [  # key, name, kg, price, paint, mpg, extras
    ("q5_25_pr", "Q5 Premium", 1925, 52200, "c:#d9dadb", 25, dict(std=PS, feats=["bsm", "rcta", "rAeb", "heatedSeats", "remoteStart", "powerLiftgate", "panoRoof", "wirelessCharge", "awd"])),
    ("q5_25_pp", "Q5 Premium Plus", 1935, 56700, "c:#1b2a44", 25, dict(std=PS + ACA + " Head-up display, Bang & Olufsen 3D sound.", feats=["acc", "pilot", "bsm", "rcta", "rAeb", "cam360", "hud", "heatedSeats", "heatedWheel", "remoteStart", "powerLiftgate", "panoRoof", "wirelessCharge", "premiumAudio", "ambient", "awd"])),
    ("q5_25_prest", "Q5 Prestige", 1950, 60600, "c:#7d1a22", 25, dict(std=PS + ACA + PRE + " Digital Matrix LED headlights, digital OLED taillights, ventilated front seats, 10.9-in. passenger display.", feats=["acc", "pilot", "lka", "bsm", "rcta", "rAeb", "cam360", "autopark", "hud", "matrix", "oledTail", "autoHigh", "heatedSeats", "ventSeats", "heatedWheel", "remoteStart", "powerLiftgate", "panoRoof", "wirelessCharge", "premiumAudio", "ambient", "passengerDisplay", "awd"])),
    ("sq5_25_pr", "SQ5 Premium", 2025, 63800, "c:#2f6b3a", 21, dict(std=PS + ACA + " S sport suspension with damper control, red S brake calipers, sport seats.", feats=["acc", "pilot", "bsm", "rcta", "rAeb", "cam360", "heatedSeats", "remoteStart", "powerLiftgate", "panoRoof", "wirelessCharge", "adaptiveDampers", "sportSeats", "awd"])),
    ("sq5_25_pp", "SQ5 Premium Plus", 2035, 67600, "c:#b7bcc1", 21, dict(std=PS + ACA + " S sport suspension with damper control, head-up display, Bang & Olufsen 3D sound, sport seats.", feats=["acc", "pilot", "bsm", "rcta", "rAeb", "cam360", "hud", "heatedSeats", "heatedWheel", "remoteStart", "powerLiftgate", "panoRoof", "wirelessCharge", "premiumAudio", "ambient", "adaptiveDampers", "sportSeats", "awd"])),
    ("sq5_25_prest", "SQ5 Prestige", 2050, 72500, "c:#c4351c", 21, dict(std=PS + ACA + PRE + " S sport suspension with damper control, Digital Matrix LED headlights, digital OLED taillights, ventilated and massaging sport seats, 10.9-in. passenger display.", feats=["acc", "pilot", "lka", "bsm", "rcta", "rAeb", "cam360", "autopark", "hud", "matrix", "oledTail", "autoHigh", "heatedSeats", "ventSeats", "massageSeats", "heatedWheel", "remoteStart", "powerLiftgate", "panoRoof", "wirelessCharge", "premiumAudio", "ambient", "passengerDisplay", "adaptiveDampers", "sportSeats", "awd"])),
]
MODES = [["comfort", "comfort", "Soft damping and light steering for relaxed cruising."], ["balanced", "normal", "Default balance of comfort and agility."],
         ["dynamic", "sport", "Sharper throttle and S tronic shifts, firmer damping and heavier steering."], ["efficiency", "eco", "Economy throttle and shifts; coasts with the engine idling when you lift off."],
         ["offroad", "offroad", "Adapts quattro and ESC for loose surfaces; with air suspension the car rises 45 mm."], ["individual", "custom", "Driver combines engine, steering, suspension and quattro settings."]]


def build():
    adds, dm, su = [], {}, {}
    for key, nm, kg, price, paint, mpg, x in TR:
        sq = key.startswith("sq5"); feats = x["feats"]; hp, tq = (362, 550) if sq else (268, 400); kW = round(hp * 0.7457)
        T = {"cda": 0.92, "ws4": False, "crab": False, "tv": False, "height": False, "modes": 2, "real": True, "model": "q5_25", "group": "Audi Q5 · 2025",
             "name": f"2025 Audi {nm}", "short": nm, "desc": ("3.0 TFSI V6 mild hybrid" if sq else "2.0 TFSI") + f" · 7-speed S tronic · quattro · {hp} hp", "mass": kg, "kW": kW, "paint": paint, "fwd": 0.57 if sq else 0.56,
             "Ff": 6200, "Fr": 5800, "modeNames": ["Comfort", "Dynamic"], "noSigLC": True, "pilotName": "adaptive cruise assist", "pilotShort": "ACA", "handsOn": True, "odo0": 20, "std": x["std"],
             "feat": f"{'3.0 V6 mild hybrid' if sq else '2.0 TFSI'}, {hp} hp, 0-60 in {'4.4' if sq else '5.8'} s", "ice": True, "tank": 65 if not sq else 70, "mpg": mpg}
        no = S + ["avas", "regen", "tech", "autoLC", "esa"] + ([] if "autopark" in feats else ["autopark"]) + ([] if "acc" in feats else ["acc", "pilot"]) + ([] if "matrix" in feats else ["matrix", "leveling"])
        D = {"layout": "ice", "eng": "v6" if sq else "i4t", "turbo": True, "Tna": 470 if sq else 340, "Tpk": tq, "Ppk": kW * 1000, "red": 6500 if sq else 6400, "idle": 700, "gears": G7, "fd": 5.3, "rev": 4.0, "bias": [0.45, 0.55] if sq else [0.6, 0.4], "dct": True}
        adds.append(f' add({json.dumps(key)},{{...{json.dumps(T, separators=(",", ":"))},no:{json.dumps(no)}}},{json.dumps(D, separators=(", ", ": "))},{price});')
        dm[key] = {"m": [list(m) for m in MODES], "t": ["quattro all-wheel drive" + (" with sport differential feel (rear-biased)" if sq else " with ultra technology (disconnects the rear axle when cruising)"), "Hill Descent Control"],
                   "s": ["adaptive", "S sport suspension with damper control", True] if sq else ["passive", "Steel-spring suspension with conventional dampers", False]}
        su[key] = ["multilink", "multilink", "coil", "adaptive" if sq else "passive", "S sport suspension with damper control" if sq else "Steel springs, conventional dampers", "front_rear", None, 200 if sq else 205, [190, 210] if sq else [170, 190], "sport" if sq else "comfort"]
    keys = [t[0] for t in TR]; Q = keys[:3]; SQ = keys[3:]
    bd = {"pk": [["Convenience Package", 1500, ["q5_25_pr"], "adaptive cruise assist with lane guidance, top view camera, heated steering wheel", ["acc", "pilot", "cam360", "heatedWheel"]],
                 ["S line Exterior Package", 900, Q, "S line bumpers, sport steering wheel, 20-in. wheels", ["sportSeats"]],
                 ["Black Optic Package", 1300, keys[1:], "gloss-black trim, black roof rails, 20-in. (21-in. on SQ5) black wheels", ["blackLook"]],
                 ["Driver Assistance Package", 1750, ["q5_25_pp", "sq5_25_pp"], "park assist plus, Audi active lane assist, traffic sign recognition", ["autopark", "lka"]],
                 ["Adaptive Air Suspension", 2100, ["q5_25_prest", "sq5_25_pp", "sq5_25_prest"], "adaptive air suspension with damper control; lowers 30 mm at speed, rises 45 mm in offroad mode", ["airSusp", "adaptiveDampers"]],
                 ["Sport Package", 1200, ["q5_25_pp", "q5_25_prest"], "sport suspension with damper control, sport seats", ["adaptiveDampers", "sportSeats"]]],
          "op": [["exterior", "Digital Matrix LED headlights and OLED taillights", 1500, ["q5_25_pp", "sq5_25_pp"], "headlights that dim around other cars, selectable taillight signatures", ["matrix", "oledTail"], None],
                 ["interior", "10.9-in. passenger display", 1000, ["q5_25_pp", "sq5_25_pp"], "screen for the front passenger with its own apps", ["passengerDisplay"], None],
                 ["exterior", "Tow hitch", 550, None, "detachable tow hitch, 4,400 lb rating", ["towPkg"], None]],
          "wh": [["19-in. 5-arm alloy", 0, ["q5_25_pr", "q5_25_pp"]], ["20-in. 10-spoke alloy", 0, ["q5_25_prest"]], ["20-in. S alloy", 0, ["sq5_25_pr", "sq5_25_pp"]], ["21-in. S 5-V-spoke alloy", 0, ["sq5_25_prest"]], ["21-in. black S alloy", 1500, SQ]],
          "ac": [["All-weather floor mats", 240, "front and rear rubber mats", "floorMats", []]],
          "std": {t[0]: t[6]["feats"] for t in TR},
          "nf": {"oledTail": ["Digital OLED taillights", "OLED rear lights with selectable signatures and a warning symbol for cars that get too close behind you."], "passengerDisplay": ["Passenger display", "A 10.9-in. screen for the front passenger."]},
          "int": [["Black leather", 0, Q], ["Okapi Brown leather", 0, ["q5_25_pp", "q5_25_prest"]], ["Black Valcona leather with S embossing", 0, SQ], ["Arras Red Valcona leather", 0, ["sq5_25_pp", "sq5_25_prest"]]],
          "ty": [["All-Season (std)", 0, Q, "allseason"], ["Summer performance (std)", 0, SQ, "summer"], ["All-Season (no cost)", 0, SQ, "allseason"]],
          "conf": "estimate", "src": "https://www.autoblog.com/cars/audi/q5/2025"}
    return adds, dm, su, {"Audi Q5 · 2025": bd}, keys


if __name__ == "__main__":
    ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); p = os.path.join(ROOT, "src", "app_template.html"); s = open(p).read()
    adds, dm, su, bd, keys = build()
    lines = s.split("\n"); pat = re.compile(r'^ add\("s?q5_25_'); idx = {i for i, l in enumerate(lines) if pat.match(l)}
    anchor = next(i for i, l in enumerate(lines) if l.startswith(' add("f150_22_'))
    lines = [l for i, l in enumerate(lines) if i not in idx]; anchor = next(i for i, l in enumerate(lines) if l.startswith(' add("f150_22_'))
    lines[anchor:anchor] = adds; s = "\n".join(lines)
    def merge(prefix, upd):
        global s
        i = s.index(prefix); j = s.index("\n", i); D = json.loads(s[i + len(prefix):j].rstrip().rstrip(";")); D.update(upd); s = s[:i] + prefix + json.dumps(D, separators=(",", ":")) + ";" + s[j:]
    merge("const DMODES=", dm); merge("const SUSR=", su); merge("var BDATA=", bd)
    if 'const LAZY=new Set(["q5_25",' not in s: s = s.replace('const LAZY=new Set(["f150_22",', 'const LAZY=new Set(["q5_25","f150_22",', 1)
    open(p, "w").write(s); print("applied", len(adds), "trims")
