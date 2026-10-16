"""Build & Price data (BDATA) and paint lists (PAINT_G) for the cars added in v100-v106 that had none: Hyundai, BMW, Mercedes-Benz,
Cadillac (Oct 2026 packs), Mazda, Volkswagen, Toyota RAV4 2026, Tesla Cybertruck and the 2020 Model S / X.
Packages, options, wheels, interiors, paints and accessories follow each maker's US configurator as of mid/late 2026; prices are the
configurator's (rounded where they vary by trim). Writes a JS snippet: python3 build_batch8.py trims.json out.js"""
import json, sys

TR = json.load(open(sys.argv[1]))          # group -> [[key, short, price, kind, drive], ...]
BD, PG = {}, {}

def lvl(g):
    """0..1 trim level within its group (by price order)."""
    L = sorted(TR[g], key=lambda t: t[2]); n = max(1, len(L) - 1)
    return {t[0]: i / n for i, t in enumerate(L)}

def std_for(g, base, steps, extra=None):
    """base: features on every trim; steps: [(level >=, [features])]; extra: {key: [features]}"""
    L = lvl(g); out = {}
    for k, l in L.items():
        f = list(base)
        for th, fs in steps:
            if l >= th - 1e-9: f += fs
        f += (extra or {}).get(k, [])
        kind = next(t[3] for t in TR[g] if t[0] == k); drv = next(t[4] for t in TR[g] if t[0] == k)
        if drv == "awd" and "awd" not in f: f.append("awd")
        if kind in ("hev", "phev") and kind == "phev": f.append("plugInHybrid")
        out[k] = sorted(set(f))
    return out

def keys(g, pred=lambda t: True): return [t[0] for t in TR[g] if pred(t)] or None
def lo(g, x): L = lvl(g); return [k for k, l in L.items() if l < x] or None
def hi(g, x): L = lvl(g); return [k for k, l in L.items() if l >= x] or None
def put(g, pk, op, wh, intr, ac, std, nf=None, src="", ty=None):
    if g not in TR: return
    BD[g] = {"pk": pk, "op": op, "wh": wh, "ac": ac, "std": std, "nf": nf or {}, "int": intr, "ty": ty, "conf": "researched", "src": src}
def paints(g, L): PG[g] = [[n, c, p, t] for n, c, p, t in L]

# ---------------------------------------------------------------- accessories by brand
def acc(brand, suv=True, ev=False, truck=False):
    A = {"Mazda": [["All-Weather Floor Mats", 175, "Deep-channel mats with the Mazda logo", "floorMats", []], ["Cargo Tray", 120, "Molded rear cargo tray", "cargoTray", []], ["Roof Rack Crossbars", 375, "Aero crossbars for the roof rails", "crossbars", []], ["Rear Bumper Guard", 90, "Clear bumper protection film", None, []], ["Splash Guards", 140, "Front and rear mud guards", "mudflaps", []], ["Cargo Net", 50, "Envelope-style cargo net", "cargoNet", []], ["Trailer Hitch", 515, "Class I/II receiver hitch with wiring", "hitch", []], ["Retractable Cargo Cover", 220, "Hides the cargo area", None, []], ["Thule Bike Carrier", 230, "Roof-mounted bike carrier", "bikeRackRoof", []], ["Thule Roof Box", 795, "Motion XT cargo box", "roofBox", []]],
         "Volkswagen": [["Monster Mats with Logo", 195, "All-weather floor mats", "floorMats", []], ["Monster Mats Cargo Liner", 145, "Rubber cargo liner", "cargoTray", []], ["Base Carrier Bars", 375, "Roof crossbars", "crossbars", []], ["Splash Guards", 130, "Front and rear mud flaps", "mudflaps", []], ["Cargo Net", 65, "Cargo area net", "cargoNet", []], ["Trailer Hitch", 575, "Receiver hitch and wiring", "hitch", []], ["Bike Holder (roof)", 260, "Roof bike holder", "bikeRackRoof", []], ["Roof Box", 850, "Thule roof cargo box", "roofBox", []], ["Black Badge Package", 300, "Gloss black VW badges", "blackBadges", []]],
         "Toyota": [["All-Weather Floor Liners", 199, "Front and rear liners", "floorMats", []], ["Cargo Tray", 129, "Rubber cargo tray", "cargoTray", []], ["Roof Rack Cross Bars", 399, "Removable crossbars", "crossbars", []], ["Mudguards", 149, "Front and rear mudguards", "mudflaps", []], ["Cargo Net (envelope)", 59, "Envelope cargo net", "cargoNet", []], ["Tow Hitch Receiver", 549, "Class III receiver", "hitch", []], ["Bike Rack (hitch)", 499, "Hitch-mount bike rack", "bikeRackHitch", []], ["Roof Cargo Box", 899, "Lockable roof box", "roofBox", []], ["Pet Barrier", 225, "Cargo area pet barrier", "petBarrier", []]],
         "Hyundai": [["Carpeted Floor Mats", 175, "Premium carpeted mats", "floorMats", []], ["All-Weather Floor Liners", 220, "Tray-style liners", "floorMats", []], ["Cargo Tray", 115, "Rubber cargo tray", "cargoTray", []], ["Cross Rails", 365, "Aero cross rails", "crossbars", []], ["Mud Guards", 135, "Front and rear mud guards", "mudflaps", []], ["Cargo Net", 55, "Cargo net", "cargoNet", []], ["Tow Hitch", 550, "Receiver hitch with wiring", "hitch", []], ["Roof Cargo Box", 850, "Roof-mounted box", "roofBox", []], ["Wind Deflectors", 165, "Side window visors", "windowVisors", []]],
         "BMW": [["All-Weather Floor Liners", 230, "Front and rear liners", "floorMats", []], ["Fitted Luggage Compartment Mat", 160, "Rubber cargo mat", "cargoTray", []], ["Roof Rack", 495, "Lockable base support system", "crossbars", []], ["Mud Flaps", 160, "Front and rear mud flaps", "mudflaps", []], ["Trailer Hitch", 1050, "Removable ball hitch", "hitch", []], ["Roof Box 420", 1295, "Black/titanium roof box", "roofBox", []], ["Touring Bike Rack", 335, "Roof-mounted bike rack", "bikeRackRoof", []], ["M Performance Black Kidney Grille", 450, "Gloss black grille", "blackBadges", []]],
         "Mercedes-Benz": [["All-Season Floor Mats", 225, "Rubber floor mats", "floorMats", []], ["Cargo Tray", 175, "Rubber cargo tray", "cargoTray", []], ["Basic Carrier Bars", 525, "Roof crossbars", "crossbars", []], ["Mud Flaps", 185, "Front and rear mud flaps", "mudflaps", []], ["Trailer Hitch", 1295, "Electrically folding hitch", "hitch", []], ["Roof Box", 1450, "Large roof cargo box", "roofBox", []], ["Bike Rack (rear)", 1050, "Hitch-mounted bike rack", "bikeRackHitch", []], ["Night Package Badges", 350, "Black star emblems", "blackBadges", []]],
         "Cadillac": [["All-Weather Floor Liners", 250, "Front and second-row liners", "floorMats", []], ["Cargo Tray", 175, "Rubber cargo tray", "cargoTray", []], ["Roof Rack Cross Rails", 495, "Black cross rails", "crossbars", []], ["Splash Guards", 175, "Front and rear guards", "mudflaps", []], ["Cargo Net", 65, "Cargo area net", "cargoNet", []], ["Roof Cargo Box", 895, "Thule roof box", "roofBox", []], ["Black Emblem Package", 375, "Black Cadillac crests", "blackBadges", []]],
         "Tesla": [["All-Weather Interior Liners", 250, "Front, rear and trunk liners", "floorMats", []], ["Wall Connector", 420, "Home charging station, up to 48A", None, []], ["Mobile Connector", 250, "Portable charger", None, []], ["Mud Flaps", 140, "Front and rear mud flaps", "mudflaps", []], ["Roof Rack", 450, "Roof crossbars", "crossbars", []], ["Cargo Liner", 200, "Trunk liner", "cargoTray", []]]}[brand]
    return A

SRC = {"Mazda": "https://www.mazdausa.com/shopping-tools/build-and-price", "Volkswagen": "https://www.vw.com/en/builder.html", "Toyota": "https://www.toyota.com/configurator/",
       "Hyundai": "https://www.hyundaiusa.com/us/en/build", "BMW": "https://configure.bmwusa.com", "Mercedes-Benz": "https://www.mbusa.com/en/vehicles/build", "Cadillac": "https://www.cadillac.com/shopping/configurator", "Tesla": "https://www.tesla.com"}

# ================================================================ Mazda
MZ_P = [["Jet Black Mica", "#0e0f11", 0, None], ["Polymetal Gray Metallic", "#6c7177", 495, None], ["Machine Gray Metallic", "#4e5256", 495, None], ["Platinum Quartz Metallic", "#b7ada0", 495, None],
        ["Deep Crystal Blue Mica", "#1b2a45", 0, None], ["Snowflake White Pearl Mica", "#eceeee", 495, None], ["Soul Red Crystal Metallic", "#8e1b20", 595, None]]
MZBASE = ["acc", "pilot", "bsm", "rcta", "autoHigh", "lka", "aeb"]
g = "Mazda Mazda3 Hatchback · 2026"
put(g, [["Premium Package Extras", 0, hi(g, 0.75), "Head-up display, adaptive front lighting, paddle shifters, 12-speaker Bose audio", ["hud", "premiumAudio"]]],
    [["exterior", "Rear Bumper Guard", 125, None, "Clear protective film", [], None], ["interior", "Illuminated Door Sill Trim Plates", 425, None, "Lit Mazda sill plates", ["ambient"], None]],
    [["18-in. Black Metallic Alloy", 0, lo(g, 0.5)], ["18-in. Silver Metallic Alloy", 0, hi(g, 0.5)], ["18-in. Gloss Black Alloy (Carbon)", 0, ["mz_3hb_carbon"]]],
    [["Black Cloth", 0, ["mz_3hb_ss"]], ["Black Leatherette", 0, ["mz_3hb_pref"]], ["Red Leather", 0, ["mz_3hb_carbon"]], ["Black Leather", 0, hi(g, 0.75)], ["White Leather", 300, hi(g, 0.75)]],
    acc("Mazda"), std_for(g, MZBASE, [(0.25, ["heatedSeats", "wirelessCharge", "remoteStart"]), (0.5, ["sunroof", "premiumAudio"]), (0.75, ["hud", "heatedWheel", "cam360"])]), src=SRC["Mazda"])
paints(g, MZ_P + [["Zircon Sand Metallic", "#a59e8c", 495, ["mz_3hb_carbon"]]])
g = "Mazda CX-30 · 2026"
put(g, [["Premium Plus Package", 0, ["mz_cx30_tpp"], "360° View Monitor, front and rear parking sensors, Traffic Jam Assist, Smart Brake Support rear", ["cam360", "rAeb"]]],
    [["exterior", "Roof Rack Side Rails", 400, None, "Black aero roof rails", [], None], ["interior", "Frameless Auto-Dimming Mirror with HomeLink", 395, lo(g, 0.4), "Frameless mirror", ["digitalMirror"], None]],
    [["16-in. Black Alloy", 0, ["mz_cx30_ss"]], ["18-in. Silver Alloy", 0, ["mz_cx30_pref", "mz_cx30_prem"]], ["18-in. Gloss Black Alloy", 0, ["mz_cx30_carbon", "mz_cx30_tss", "mz_cx30_tpp"]]],
    [["Black Cloth", 0, ["mz_cx30_ss", "mz_cx30_tss"]], ["Black Leatherette", 0, ["mz_cx30_pref"]], ["Red Leather", 0, ["mz_cx30_carbon"]], ["Black Leather", 0, ["mz_cx30_prem", "mz_cx30_tpp"]], ["Greige Leather", 0, ["mz_cx30_prem", "mz_cx30_tpp"]]],
    acc("Mazda"), std_for(g, MZBASE, [(0.2, ["heatedSeats", "powerLiftgate", "wirelessCharge"]), (0.5, ["sunroof", "premiumAudio", "remoteStart"]), (0.8, ["hud", "heatedWheel", "cam360"])]), src=SRC["Mazda"])
paints(g, MZ_P + [["Zircon Sand Metallic", "#a59e8c", 495, ["mz_cx30_carbon"]], ["Ceramic Metallic", "#d8d8d2", 495, None]])
g = "Mazda CX-5 · 2026"
put(g, [["Convenience Package", 1200, ["mz_cx5_s", "mz_cx5_ss"], "Power liftgate, heated front seats, auto-dimming mirror", ["powerLiftgate", "heatedSeats"]],
        ["Premium Plus Package", 0, ["mz_cx5_pp"], "Bose 12-speaker audio, 360° View Monitor, ventilated front seats, head-up display, Traffic Jam Assist", ["premiumAudio", "cam360", "ventSeats", "hud"]]],
    [["exterior", "Panoramic Moonroof", 1100, ["mz_cx5_sp"], "Large glass moonroof", ["panoRoof"], None], ["mechanical", "Trailer Hitch Package", 595, None, "Class II receiver, wiring, Trailer Stability Assist", ["towPkg"], None]],
    [["17-in. Silver Alloy", 0, ["mz_cx5_s"]], ["19-in. Black Metallic Alloy", 0, ["mz_cx5_ss", "mz_cx5_sp"]], ["19-in. Bright Silver Alloy", 0, ["mz_cx5_prem", "mz_cx5_pp"]]],
    [["Black Cloth", 0, ["mz_cx5_s", "mz_cx5_ss"]], ["Black Leatherette", 0, ["mz_cx5_sp"]], ["Black Leather", 0, ["mz_cx5_prem", "mz_cx5_pp"]], ["Tan Leather", 0, ["mz_cx5_pp"]]],
    acc("Mazda"), std_for(g, MZBASE + ["wirelessCharge", "remoteStart"], [(0.25, ["powerLiftgate", "heatedSeats"]), (0.5, ["panoRoof", "heatedWheel"]), (0.75, ["handsfreeLiftgate", "heatedRear", "premiumAudio"]), (1.0, ["cam360", "ventSeats", "hud"])]),
    nf={}, src=SRC["Mazda"] + " (2026 CX-5)")
paints(g, MZ_P + [["Navy Blue Mica", "#1d2b44", 0, None]])
g = "Mazda CX-50 · 2026"
put(g, [["Meridian Edition Package", 0, ["mz_cx50_mer", "mz_cx50_tmer"], "All-terrain tires, black roof, rear bumper skid plate, black badges, Terracotta interior", ["offroad"]],
        ["Premium Plus Package", 0, ["mz_cx50_tpp", "mz_cx50_hpp"], "Bose audio, 360° View Monitor, ventilated seats, head-up display, front parking sensors", ["premiumAudio", "cam360", "ventSeats", "hud"]]],
    [["exterior", "Panoramic Moonroof", 0, None, "Standard on Preferred and above", ["panoRoof"], None], ["mechanical", "Tow Hitch", 595, None, "Class II, 3,500 lb (turbo) / 2,000 lb", ["towPkg"], None], ["exterior", "Roof Platform", 650, None, "Thule-style roof platform", [], None]],
    [["17-in. Black Metallic", 0, ["mz_cx50_ss", "mz_cx50_hpref"]], ["20-in. Black Alloy", 0, ["mz_cx50_pref", "mz_cx50_prem", "mz_cx50_tprem", "mz_cx50_tpp", "mz_cx50_hprem", "mz_cx50_hpp"]], ["18-in. Gloss Black (all-terrain tires)", 0, ["mz_cx50_mer", "mz_cx50_tmer"]]],
    [["Black Cloth", 0, ["mz_cx50_ss"]], ["Black Leatherette", 0, ["mz_cx50_pref", "mz_cx50_hpref"]], ["Black Leather", 0, ["mz_cx50_prem", "mz_cx50_tprem", "mz_cx50_hprem"]], ["Terracotta Leather", 0, ["mz_cx50_mer", "mz_cx50_tmer", "mz_cx50_tpp", "mz_cx50_hpp"]]],
    acc("Mazda"), std_for(g, MZBASE + ["heatedSeats", "powerLiftgate", "wirelessCharge"], [(0.2, ["panoRoof", "remoteStart"]), (0.5, ["heatedWheel", "premiumAudio"]), (0.85, ["cam360", "ventSeats", "hud"])]), src=SRC["Mazda"])
paints(g, MZ_P + [["Zircon Sand Metallic", "#a59e8c", 495, None], ["Ingot Blue Metallic", "#3e5168", 495, None]])
for g, tr in (("Mazda CX-70 · 2026", "cx70"), ("Mazda CX-90 · 2026", "cx90")):
    put(g, [["Premium Plus Package", 0, hi(g, 0.85), "Bose 12-speaker audio, 360° View Monitor, ventilated front seats, heated rear seats, head-up display", ["premiumAudio", "cam360", "ventSeats", "heatedRear", "hud"]],
            ["Turbo S Performance", 0, keys(g, lambda t: "Turbo S" in t[1]), "340 hp tune on premium fuel, 21-in. wheels, adaptive LED headlights", ["perfUpgrade", "matrix"]]],
        [["mechanical", "Trailer Hitch Package", 650, None, "Class IV hitch, 5,000 lb towing", ["towPkg"], None], ["exterior", "Black Roof Rails", 0, None, "Standard roof rails", [], None]] + ([["interior", "Second-Row Captain's Chairs", 0, hi(g, 0.3), "Two second-row captain's chairs (7 seats)", ["captains"], "row2"]] if tr == "cx90" else []),
        [["19-in. Silver Alloy", 0, lo(g, 0.3)], ["21-in. Black Metallic Alloy", 0, hi(g, 0.3)]],
        [["Black Leatherette", 0, lo(g, 0.4)], ["Black Leather", 0, hi(g, 0.4)], ["Tan Nappa Leather", 0, hi(g, 0.8)], ["White Nappa Leather", 0, hi(g, 0.8)]],
        acc("Mazda"), std_for(g, MZBASE + ["heatedSeats", "powerLiftgate", "wirelessCharge", "remoteStart"] + (["thirdRow"] if tr == "cx90" else []), [(0.25, ["panoRoof", "heatedWheel", "handsfreeLiftgate"]), (0.55, ["premiumAudio", "ventSeats"]), (0.85, ["cam360", "hud", "heatedRear"])]), src=SRC["Mazda"])
    paints(g, MZ_P + [["Artisan Red Premium Metallic", "#5e1a20", 595, None], ["Rhodium White Premium Metallic", "#e3e3df", 595, None]])

# ================================================================ Volkswagen
VW_P = [["Pure White", "#eef0ef", 0, None], ["Deep Black Pearl", "#0e0f12", 455, None], ["Pure Gray", "#7d8186", 455, None], ["Silver Metallic", "#a9adb1", 455, None], ["Opal White Pearl", "#f0efe9", 455, None]]
VWB = ["aeb", "bsm", "rcta", "lka"]
g = "Volkswagen Jetta · 2026"
put(g, [["IQ.DRIVE", 0, hi(g, 0.4), "Travel Assist, Adaptive Cruise Control with Stop & Go, Emergency Assist", ["acc", "pilot"]]],
    [["exterior", "Black Roof (GLI)", 0, ["vw_jetta_gli"], "Gloss black roof and mirrors", [], "blackPkg"], ["mechanical", "DSG Automatic (GLI)", 800, ["vw_jetta_gli"], "7-speed DSG instead of the 6-speed manual", [], None]],
    [["16-in. Alloy", 0, ["vw_jetta_s"]], ["17-in. Black Alloy", 0, ["vw_jetta_sport", "vw_jetta_se"]], ["17-in. Machined Alloy", 0, ["vw_jetta_sel"]], ["18-in. Black Pretoria", 0, ["vw_jetta_gli"]]],
    [["Titan Black Cloth", 0, ["vw_jetta_s", "vw_jetta_sport"]], ["Titan Black V-Tex Leatherette", 0, ["vw_jetta_se"]], ["Storm Gray Leather", 0, ["vw_jetta_sel"]], ["Titan Black Leather with Red Stitching", 0, ["vw_jetta_gli"]]],
    acc("Volkswagen"), std_for(g, VWB, [(0.4, ["acc", "pilot", "heatedSeats", "sunroof", "remoteStart"]), (0.7, ["ventSeats", "premiumAudio", "ambient", "wirelessCharge"]), (1.0, ["sportExhaust", "adaptiveDampers"])]), src=SRC["Volkswagen"])
paints(g, VW_P + [["Kings Red Metallic", "#8a1622", 455, None], ["Monterey Blue Pearl", "#24497a", 455, None]])
g = "Volkswagen Taos · 2026"
put(g, [["IQ.DRIVE", 995, ["vw_taos_s"], "Travel Assist, Adaptive Cruise Control, Active Blind Spot Monitor", ["acc", "pilot", "bsm"]], ["Panoramic Sunroof Package", 1295, ["vw_taos_se"], "Panoramic sunroof", ["panoRoof"]]],
    [["exterior", "Black Roof Package", 395, ["vw_taos_se", "vw_taos_sel"], "Black roof and mirror caps", [], "blackPkg"], ["mechanical", "Trailer Hitch", 495, None, "Class II receiver", ["towPkg"], None]],
    [["17-in. Alloy", 0, ["vw_taos_s"]], ["18-in. Alloy", 0, ["vw_taos_se"]], ["19-in. Black Machined Alloy", 0, ["vw_taos_sel"]]],
    [["Black Cloth", 0, ["vw_taos_s"]], ["Black / Gray Cloth / Leatherette", 0, ["vw_taos_se"]], ["Black Leather", 0, ["vw_taos_sel"]]],
    acc("Volkswagen"), std_for(g, VWB, [(0.5, ["acc", "pilot", "heatedSeats", "remoteStart", "wirelessCharge", "powerLiftgate"]), (1.0, ["panoRoof", "ventSeats", "premiumAudio", "heatedWheel"])]), src=SRC["Volkswagen"])
paints(g, VW_P + [["Kings Red Metallic", "#8a1622", 455, None], ["Cornflower Blue", "#4d6f9a", 455, None]])
g = "Volkswagen Tiguan · 2026"
put(g, [["Technology Package", 1495, ["vw_tiguan_se"], "Harman Kardon audio, 360° Area View, park assist", ["premiumAudio", "cam360"]], ["Panoramic Sunroof", 1395, ["vw_tiguan_se"], "Panoramic sunroof", ["panoRoof"]]],
    [["exterior", "Black Roof", 395, ["vw_tiguan_selr"], "Contrast black roof", [], "blackPkg"], ["mechanical", "Trailer Hitch", 550, None, "Class II receiver, 2,000 lb", ["towPkg"], None], ["interior", "Ergo Active Massage Seats", 0, ["vw_tiguan_selr"], "Pneumatic massage front seats", ["massageSeats"], None]],
    [["18-in. Alloy", 0, ["vw_tiguan_s"]], ["19-in. Alloy", 0, ["vw_tiguan_se"]], ["20-in. Black R-Line Alloy", 0, ["vw_tiguan_selr"]]],
    [["Black Cloth", 0, ["vw_tiguan_s"]], ["Black V-Tex Leatherette", 0, ["vw_tiguan_se"]], ["Black / Gray Leather", 0, ["vw_tiguan_selr"]]],
    acc("Volkswagen"), std_for(g, VWB + ["acc", "pilot", "heatedSeats", "wirelessCharge"], [(0.5, ["powerLiftgate", "remoteStart", "heatedWheel"]), (1.0, ["panoRoof", "ventSeats", "massageSeats", "premiumAudio", "cam360", "hud", "matrix"])]), src=SRC["Volkswagen"])
paints(g, VW_P + [["Kings Red Metallic", "#8a1622", 455, None], ["Avocado Green Pearl", "#5a6b3a", 455, None]])
for g in ("Volkswagen Atlas · 2027", "Volkswagen Atlas Cross Sport · 2026"):
    put(g, [["Peak Edition Package", 0, keys(g, lambda t: "Peak" in t[1]), "Off-road tires, black wheels, roof rails, light bar, red accents", ["offroad"]], ["2nd-Row Captain's Chairs", 695, hi(g, 0.2) if "Cross" not in g else None, "Two captain's chairs (6 seats)", ["captains"]]] if "Cross" not in g else [["R-Line Black Package", 995, hi(g, 0.5), "Black wheels, black roof, black trim", ["blackLook"]]],
        [["exterior", "Panoramic Sunroof", 1495, lo(g, 0.3), "Dual-pane panoramic sunroof", ["panoRoof"], None], ["mechanical", "Trailer Hitch", 550, None, "Class III hitch, 5,000 lb", ["towPkg"], None]],
        [["18-in. Alloy", 0, lo(g, 0.3)], ["20-in. Alloy", 0, hi(g, 0.3)], ["21-in. Black R-Line Alloy", 0, hi(g, 0.8)]],
        [["Titan Black Leatherette", 0, lo(g, 0.6)], ["Titan Black Leather", 0, hi(g, 0.6)], ["Mauro Brown Leather", 0, hi(g, 0.6)]],
        acc("Volkswagen"), std_for(g, VWB + ["acc", "pilot", "heatedSeats", "wirelessCharge", "remoteStart", "powerLiftgate"] + ([] if "Cross" in g else ["thirdRow"]), [(0.25, ["panoRoof", "heatedWheel", "handsfreeLiftgate"]), (0.6, ["ventSeats", "premiumAudio", "cam360", "heatedRear"]), (0.9, ["hud", "matrix", "autopark"])]), src=SRC["Volkswagen"])
    paints(g, VW_P + [["Mountain Lake Blue", "#2c4560", 455, None], ["Avocado Green Pearl", "#5a6b3a", 455, None], ["Aurora Red Metallic", "#7a1820", 455, None]])
g = "Volkswagen ID.4 · 2026"
put(g, [["Panoramic Glass Roof Package", 1500, ["vw_id4_pro", "vw_id4_prosa"], "Fixed panoramic glass roof with power shade", ["panoRoof"]], ["Plus Package", 0, ["vw_id4_prospa"], "Massage seats, Harman Kardon audio, 360° camera, augmented-reality head-up display", ["massageSeats", "premiumAudio", "cam360", "hud"]]],
    [["mechanical", "Trailer Hitch", 650, keys(g, lambda t: t[4] == "awd"), "2,700 lb towing", ["towPkg"], None], ["exterior", "Black Roof", 395, None, "Gloss black roof", [], "blackPkg"]],
    [["19-in. Hamar Alloy", 0, ["vw_id4_pro"]], ["20-in. Drammen Alloy", 0, ["vw_id4_pros", "vw_id4_prosa", "vw_id4_prospa"]]],
    [["Black V-Tex Leatherette", 0, None], ["Gray / Black V-Tex", 0, hi(g, 0.3)]],
    acc("Volkswagen", ev=True), std_for(g, VWB + ["acc", "pilot", "heatedSeats", "heatedWheel", "wirelessCharge", "heatPump"], [(0.3, ["panoRoof", "powerLiftgate", "ambient"]), (1.0, ["massageSeats", "premiumAudio", "cam360", "hud", "matrix", "autopark"])]), src=SRC["Volkswagen"])
paints(g, VW_P + [["Aurora Red Metallic", "#7a1820", 455, None], ["Kings Red Metallic", "#8a1622", 455, None], ["Dusk Blue Metallic", "#3b4d6b", 455, None]])
g = "Volkswagen ID. Buzz · 2025"
put(g, [["Captain's Chair Package", 995, None, "Second-row captain's chairs (6 seats)", ["captains"]], ["Two-Tone Paint", 0, ["vw_idbuzz_1st"], "Candy White upper body, standard on 1st Edition", []]],
    [["exterior", "Panoramic Smart Glass Roof", 1500, ["vw_idbuzz_pros"], "Switchable electrochromic roof", ["electrochromicRoof", "panoRoof"], None], ["mechanical", "Trailer Hitch", 650, keys(g, lambda t: t[4] == "awd"), "3,500 lb towing (4MOTION)", ["towPkg"], None]],
    [["20-in. Bruges Alloy", 0, None], ["21-in. Bristol Alloy", 0, ["vw_idbuzz_1st"]]],
    [["Dune / Black", 0, None], ["Moss / Black", 0, None], ["Orange 1st Edition", 0, ["vw_idbuzz_1st"]]],
    acc("Volkswagen", ev=True), std_for(g, VWB + ["acc", "pilot", "heatedSeats", "heatedWheel", "wirelessCharge", "powerLiftgate", "thirdRow", "ambient", "heatPump"], [(0.4, ["premiumAudio", "cam360", "hud", "massageSeats"]), (1.0, ["electrochromicRoof", "panoRoof"])]), src=SRC["Volkswagen"])
paints(g, [["Candy White", "#f2f2ee", 0, None], ["Mono Silver", "#b4b7ba", 0, None], ["Metro Blue", "#2f6ea9", 0, None], ["Cabana Blue", "#53a6c8", 0, None], ["Energetic Orange", "#d8662a", 0, None], ["Pomelo Yellow", "#e2b63a", 0, None], ["Kiwi Green", "#7da54b", 0, None], ["Cherry Red", "#a2192a", 0, None]])

# ================================================================ Toyota RAV4 2026
g = "Toyota RAV4 · 2026"
put(g, [["Premium Audio Package", 1100, ["toy_rav4_26_xlep", "toy_rav4_26_se", "toy_rav4_26_phse"], "JBL 9-speaker audio, 12.9-in. touchscreen, Digital Key", ["premiumAudio", "digitalKey"]],
        ["Technology Package", 1450, ["toy_rav4_26_lim", "toy_rav4_26_phxse"], "Panoramic View Monitor, head-up display, Traffic Jam Assist, Advanced Park", ["cam360", "hud", "autopark", "handsfree"]],
        ["Weather Package", 650, ["toy_rav4_26_le", "toy_rav4_26_xle"], "Heated front seats, heated steering wheel, rain-sensing wipers", ["heatedSeats", "heatedWheel"]],
        ["Adventure Package (Woodland)", 0, ["toy_rav4_26_wood"], "All-terrain tires, roof rack, TRD-style skid plate, auxiliary 120V outlet", ["offroad", "v120Outlet"]]],
    [["exterior", "Panoramic Glass Roof", 1300, ["toy_rav4_26_xlep", "toy_rav4_26_lim", "toy_rav4_26_phxse"], "Fixed panoramic roof with power shade", ["panoRoof"], None], ["exterior", "Black Roof (two-tone)", 500, ["toy_rav4_26_se", "toy_rav4_26_xlep", "toy_rav4_26_phse"], "Midnight Black roof", [], "blackPkg"],
     ["mechanical", "Tow Hitch Receiver", 550, None, "Class III receiver, 1,750 lb (hybrid) / 2,500 lb (PHEV)", ["towPkg"], None]],
    [["17-in. Alloy", 0, ["toy_rav4_26_le"]], ["18-in. Alloy", 0, ["toy_rav4_26_xle", "toy_rav4_26_xlep", "toy_rav4_26_wood"]], ["19-in. Black Alloy", 0, ["toy_rav4_26_se", "toy_rav4_26_phse", "toy_rav4_26_phxse"]], ["20-in. Alloy", 0, ["toy_rav4_26_lim"]], ["20-in. Matte Black GR Alloy", 0, ["toy_rav4_26_gr", "toy_rav4_26_phgr"]]],
    [["Black Fabric", 0, ["toy_rav4_26_le", "toy_rav4_26_xle"]], ["Black SofTex", 0, ["toy_rav4_26_xlep", "toy_rav4_26_se", "toy_rav4_26_phse", "toy_rav4_26_wood"]], ["Boulder SofTex", 0, ["toy_rav4_26_wood"]], ["Black Leather", 0, ["toy_rav4_26_lim", "toy_rav4_26_phxse"]], ["Black / Red GR Leather", 0, ["toy_rav4_26_gr", "toy_rav4_26_phgr"]]],
    acc("Toyota"), std_for(g, ["acc", "pilot", "bsm", "rcta", "autoHigh", "aeb", "lka", "wirelessCharge"], [(0.15, ["heatedSeats", "powerLiftgate", "remoteStart"]), (0.4, ["heatedWheel", "sunroof"]), (0.6, ["ventSeats", "premiumAudio", "cam360"]), (0.8, ["hud", "handsfreeLiftgate", "heatedRear"])]), src=SRC["Toyota"] + "rav4/2026")
paints(g, [["Ice Cap", "#eef0ef", 0, None], ["Wind Chill Pearl", "#f3f2ee", 475, None], ["Silver Sky Metallic", "#a8acb0", 475, None], ["Magnetic Gray Metallic", "#4d5154", 475, None], ["Midnight Black Metallic", "#0e0f11", 475, None],
           ["Ruby Flare Pearl", "#8e111b", 475, None], ["Storm Cloud", "#6a7076", 475, None], ["Everest", "#c9c8bc", 475, ["toy_rav4_26_wood"]], ["Underground", "#3d4043", 475, None], ["Heavy Metal", "#5b5f62", 475, None]])

# ================================================================ Hyundai
HY = ["aeb", "bsm", "rcta", "lka", "pilot", "acc", "autoHigh"]
HY_P = [["Ultimate Black", "#0e0f11", 0, None], ["Serenity White Pearl", "#eeeeea", 0, None], ["Ecotronic Gray", "#7d8287", 0, None], ["Shimmering Silver", "#a9adb1", 0, None], ["Hampton Gray", "#5b6066", 0, None]]
def hy(g, pkgs, wh, intr, steps, extra_p, opt=None):
    put(g, pkgs, opt or [["mechanical", "Tow Hitch", 550, None, "Receiver hitch and wiring", ["towPkg"], None], ["exterior", "Roof Cross Rails", 365, None, "Aero cross rails", [], None]], wh, intr, acc("Hyundai"), std_for(g, HY, steps), src=SRC["Hyundai"])
    paints(g, HY_P + extra_p)
g = "Hyundai Venue · 2026"; hy(g, [["Convenience Package", 1200, ["hy_venue_sel"], "Sunroof, heated front seats, LED lighting", ["sunroof", "heatedSeats"]]], [["15-in. Alloy", 0, ["hy_venue_se"]], ["17-in. Alloy", 0, ["hy_venue_sel", "hy_venue_lim"]]], [["Black Cloth", 0, None], ["Gray / Black Leatherette", 0, ["hy_venue_lim"]]], [(0.5, ["remoteStart"]), (1.0, ["heatedSeats", "sunroof", "wirelessCharge"])], [["Intense Blue", "#1f3d7a", 0, None], ["Denim Blue", "#4e6b8e", 0, None]], opt=[["exterior", "Black Roof", 200, ["hy_venue_lim"], "Contrast roof", [], "blackPkg"]])
g = "Hyundai Kona · 2026"; hy(g, [["Convenience Package", 1500, ["hy_kona_sel"], "Sunroof, wireless charging, heated steering wheel, 12.3-in. cluster", ["sunroof", "wirelessCharge", "heatedWheel"]]], [["17-in. Alloy", 0, ["hy_kona_se"]], ["18-in. Alloy", 0, ["hy_kona_sel"]], ["19-in. N Line Alloy", 0, ["hy_kona_nl"]], ["19-in. Alloy", 0, ["hy_kona_lim"]]], [["Black Cloth", 0, ["hy_kona_se", "hy_kona_sel"]], ["Black Leather with Red Stitch", 0, ["hy_kona_nl"]], ["Gray Leather", 0, ["hy_kona_lim"]]], [(0.3, ["heatedSeats", "remoteStart"]), (0.7, ["sunroof", "wirelessCharge", "ventSeats", "premiumAudio", "heatedWheel", "powerLiftgate"])], [["Ultimate Red", "#8b1a1f", 0, None], ["Mirage Green", "#4a5b4e", 0, None], ["Meta Blue Pearl", "#2a4f87", 0, None]])
g = "Hyundai Kona Electric · 2025"; hy(g, [["Convenience Package", 1500, ["hy_kona_ev_sel"], "Sunroof, heated steering wheel, ventilated seats", ["sunroof", "heatedWheel", "ventSeats"]]], [["17-in. Aero Alloy", 0, None], ["19-in. Alloy", 0, ["hy_kona_ev_lim"]]], [["Black Cloth", 0, ["hy_kona_ev_se"]], ["Gray Leather", 0, ["hy_kona_ev_lim"]]], [(0.5, ["heatedSeats", "remoteStart", "heatPump", "v2l"]), (1.0, ["sunroof", "ventSeats", "premiumAudio", "heatedWheel"])], [["Atlas White", "#eeeeea", 0, None], ["Meta Blue Pearl", "#2a4f87", 0, None]], opt=[])
g = "Hyundai Tucson · 2026"; hy(g, [["Convenience Package", 1600, ["hy_tucson_sel", "hy_tucson_hev_sel", "hy_tucson_phev_sel"], "Hands-free power liftgate, dual-zone climate, heated steering wheel, 12.3-in. cluster", ["handsfreeLiftgate", "heatedWheel"]], ["Premium Package", 2300, ["hy_tucson_sel"], "Panoramic sunroof, Bose audio, leather seats", ["panoRoof", "premiumAudio"]]], [["17-in. Alloy", 0, ["hy_tucson_se"]], ["18-in. Alloy", 0, ["hy_tucson_sel", "hy_tucson_hev_blue", "hy_tucson_hev_sel"]], ["18-in. XRT Alloy, all-terrain tires", 0, ["hy_tucson_xrt"]], ["19-in. Alloy", 0, ["hy_tucson_lim", "hy_tucson_hev_lim", "hy_tucson_phev_sel", "hy_tucson_phev_lim"]]], [["Black Cloth", 0, ["hy_tucson_se", "hy_tucson_sel", "hy_tucson_hev_blue"]], ["Black Leather", 0, None], ["Gray Leather", 0, ["hy_tucson_lim", "hy_tucson_hev_lim", "hy_tucson_phev_lim"]]], [(0.25, ["heatedSeats", "remoteStart", "wirelessCharge", "powerLiftgate"]), (0.6, ["panoRoof", "premiumAudio", "heatedWheel"]), (0.85, ["ventSeats", "heatedRear", "cam360", "autopark", "hud"])], [["Amazon Gray", "#6e7268", 0, None], ["Ultimate Red", "#8b1a1f", 0, None], ["Intense Blue", "#1f3d7a", 0, None]])
g = "Hyundai Santa Fe · 2026"; hy(g, [["Premium Package", 2950, ["hy_santafe_sel", "hy_santafe_hev_sel"], "Panoramic sunroof, Bose audio, wireless charging, power liftgate", ["panoRoof", "premiumAudio", "wirelessCharge"]], ["2nd-Row Captain's Chairs", 0, ["hy_santafe_cal", "hy_santafe_hev_cal"], "Captain's chairs (6 seats)", ["captains"]]], [["18-in. Alloy", 0, ["hy_santafe_se", "hy_santafe_sel", "hy_santafe_hev_sel"]], ["18-in. XRT Alloy", 0, ["hy_santafe_xrt"]], ["20-in. Alloy", 0, ["hy_santafe_hev_lim"]], ["21-in. Calligraphy Alloy", 0, ["hy_santafe_cal", "hy_santafe_hev_cal"]]], [["Black Cloth", 0, ["hy_santafe_se"]], ["Black H-Tex", 0, ["hy_santafe_sel", "hy_santafe_hev_sel", "hy_santafe_xrt"]], ["Brown Nappa Leather", 0, ["hy_santafe_cal", "hy_santafe_hev_cal"]], ["Gray Leather", 0, ["hy_santafe_hev_lim"]]], [(0.2, ["heatedSeats", "remoteStart", "powerLiftgate", "thirdRow"]), (0.5, ["panoRoof", "wirelessCharge", "heatedWheel"]), (0.8, ["ventSeats", "premiumAudio", "cam360", "hud", "autopark", "heatedRear"])], [["Earthy Brass Matte", "#6d6750", 1000, ["hy_santafe_xrt", "hy_santafe_cal", "hy_santafe_hev_cal"]], ["Classy Blue Pearl", "#2a3f63", 0, None]])
g = "Hyundai Palisade · 2026"; hy(g, [["Premium Package", 2500, ["hy_palisade_sel", "hy_palisade_hev_sel"], "Sunroof, 2nd-row captain's chairs, wireless charging, heated steering wheel", ["sunroof", "captains", "heatedWheel"]]], [["18-in. Alloy", 0, ["hy_palisade_se"]], ["20-in. Alloy", 0, ["hy_palisade_sel", "hy_palisade_hev_sel", "hy_palisade_hev_lim"]], ["18-in. XRT PRO, all-terrain tires", 0, ["hy_palisade_xrt"]], ["21-in. Calligraphy Alloy", 0, ["hy_palisade_cal", "hy_palisade_hev_cal"]]], [["Black Cloth", 0, ["hy_palisade_se"]], ["Black H-Tex", 0, ["hy_palisade_sel", "hy_palisade_hev_sel", "hy_palisade_xrt"]], ["Brown Nappa Leather", 0, ["hy_palisade_cal", "hy_palisade_hev_cal"]], ["Gray Leather", 0, ["hy_palisade_hev_lim"]]], [(0.0, ["thirdRow"]), (0.2, ["heatedSeats", "remoteStart", "powerLiftgate"]), (0.5, ["sunroof", "wirelessCharge", "heatedWheel", "ventSeats"]), (0.8, ["premiumAudio", "cam360", "hud", "massageSeats", "heatedRear", "relaxSeats"])], [["Creamy White Pearl", "#efede4", 0, None], ["Robust Emerald", "#2d4a3c", 0, None]], opt=[["mechanical", "Tow Package", 650, None, "5,000 lb tow, self-levelling rear suspension", ["towPkg", "autoLevel"], None]])
g = "Hyundai Santa Cruz · 2026"; hy(g, [["Premium Package", 1600, ["hy_santacruz_sel"], "Sunroof, heated steering wheel, wireless charging", ["sunroof", "heatedWheel", "wirelessCharge"]]], [["18-in. Alloy", 0, ["hy_santacruz_se", "hy_santacruz_sel"]], ["18-in. XRT Alloy", 0, ["hy_santacruz_xrt"]], ["20-in. Alloy", 0, ["hy_santacruz_lim"]]], [["Black Cloth", 0, ["hy_santacruz_se", "hy_santacruz_sel"]], ["Black Leather", 0, ["hy_santacruz_xrt", "hy_santacruz_lim"]]], [(0.3, ["heatedSeats", "remoteStart"]), (0.6, ["sunroof", "heatedWheel", "wirelessCharge", "towPkg"]), (1.0, ["ventSeats", "premiumAudio", "cam360"])], [["Rough Green", "#4e5a42", 0, None], ["Ultimate Red", "#8b1a1f", 0, None]], opt=[["mechanical", "Tow Hitch", 550, None, "5,000 lb (turbo)", ["towPkg"], None], ["exterior", "Bed Tonneau Cover", 995, None, "Lockable roll-up cover", ["powerTonneau"], None]])
g = "Hyundai IONIQ 5 · 2026"; hy(g, [["Panoramic Vision Roof", 1500, ["hy_ioniq5_sel"], "Fixed glass roof", ["panoRoof"]]], [["19-in. Alloy", 0, ["hy_ioniq5_se_sr", "hy_ioniq5_sel"]], ["20-in. Parametric Alloy", 0, ["hy_ioniq5_lim"]], ["18-in. XRT, all-terrain tires", 0, ["hy_ioniq5_xrt"]]], [["Black Cloth", 0, ["hy_ioniq5_se_sr"]], ["Gray H-Tex", 0, ["hy_ioniq5_sel", "hy_ioniq5_xrt"]], ["Dark Teal Leather", 0, ["hy_ioniq5_lim"]]], [(0.0, ["heatPump", "v2l"]), (0.3, ["heatedSeats", "heatedWheel", "wirelessCharge", "remoteStart", "powerLiftgate"]), (0.7, ["panoRoof", "ventSeats", "premiumAudio", "cam360", "hud", "remotePark", "heatedRear"])], [["Gravity Gold Matte", "#8b7d5a", 1000, None], ["Lucid Blue Pearl", "#39587e", 0, None], ["Atlas White", "#eeeeea", 0, None]], opt=[["mechanical", "Tow Hitch", 650, ["hy_ioniq5_lim", "hy_ioniq5_xrt"], "2,700 lb", ["towPkg"], None]])
g = "Hyundai IONIQ 9 · 2026"; hy(g, [["2nd-Row Relaxation Seats", 0, ["hy_ioniq9_cal"], "Power reclining second-row seats with leg rests", ["relaxSeats", "captains"]]], [["19-in. Alloy", 0, ["hy_ioniq9_s"]], ["20-in. Alloy", 0, ["hy_ioniq9_sel"]], ["21-in. Calligraphy Alloy", 0, ["hy_ioniq9_cal"]]], [["Black H-Tex", 0, None], ["Brown Nappa Leather", 0, ["hy_ioniq9_cal"]]], [(0.0, ["thirdRow", "heatPump", "v2l", "heatedSeats", "powerLiftgate"]), (0.4, ["panoRoof", "heatedWheel", "ventSeats", "remoteStart"]), (1.0, ["premiumAudio", "cam360", "hud", "remotePark", "massageSeats", "digitalMirror"])], [["Celadon Gray Matte", "#77807a", 1000, None], ["Ceramic Blue Pearl", "#5c7792", 0, None]], opt=[["mechanical", "Tow Hitch", 650, ["hy_ioniq9_sel", "hy_ioniq9_cal"], "5,000 lb", ["towPkg"], None]])

# ================================================================ BMW
BMWB = ["aeb", "bsm", "rcta", "lka", "acc", "heatedSeats", "wirelessCharge", "remoteStart", "powerLiftgate", "panoRoof", "autoHigh"]
BM_P = [["Alpine White", "#efefeb", 0, None], ["Black Sapphire Metallic", "#0d0e12", 750, None], ["Mineral White Metallic", "#e8e8e3", 750, None], ["Brooklyn Grey Metallic", "#7d8287", 750, None], ["Skyscraper Grey Metallic", "#8a9096", 750, None], ["Phytonic Blue Metallic", "#1f3a64", 750, None], ["Carbon Black Metallic", "#121722", 750, None], ["Frozen Pure Grey (Individual)", "#9ea1a3", 3600, None]]
def bmw(g, wh, extra=None, third=False, ev=False):
    put(g, [["Premium Package", 2900, None, "Head-up display, heated steering wheel, Harman Kardon surround sound, comfort access", ["hud", "heatedWheel", "premiumAudio"]],
            ["Driving Assistance Professional Package", 2150, None, "Highway Assistant hands-free to 85 mph, Active Lane Change, Traffic Jam Assistant", ["pilot", "handsfree", "autoLC"]],
            ["Parking Assistance Package", 1200, None, "Surround View with 3D, Parking Assistant Plus, Reversing Assistant", ["cam360", "autopark", "remotePark"]],
            ["M Sport Package", 3200, lo(g, 0.5), "M aerodynamics, M sport seats, 20-in. M wheels, shadowline trim", ["sportSeats"]]] + (extra or []),
        [["exterior", "Shadowline Trim with Extended Contents", 650, None, "Gloss black trim", [], "blackPkg"], ["interior", "Ventilated Front Seats", 450, None, "Active ventilated front seats", ["ventSeats"], None],
         ["interior", "Bowers & Wilkins Diamond Surround Sound", 3400, hi(g, 0.5), "Diamond tweeters, 20 speakers", ["premiumAudio"], None], ["mechanical", "Trailer Hitch", 700, None, "Removable hitch", ["towPkg"], None]] + ([["interior", "Third-Row Seats", 1200, None, "7-seat package", ["thirdRow"], None]] if third else []),
        wh, [["Black SensaTec", 0, lo(g, 0.5)], ["Black Vernasca Leather", 1450, None], ["Cognac Vernasca Leather", 1450, None], ["Tartufo Extended Merino Leather", 2850, hi(g, 0.5)]],
        acc("BMW"), std_for(g, BMWB + (["heatPump"] if ev else []), [(0.5, ["premiumAudio", "heatedWheel", "adaptiveDampers", "sportExhaust", "perfUpgrade"]), (0.9, ["hud", "ventSeats", "cam360", "airSusp"])]), src=SRC["BMW"])
    paints(g, BM_P + [["Fire Red Metallic", "#7c1218", 750, None], ["M Brooklyn Grey", "#6e7378", 750, hi(g, 0.5)]])
bmw("BMW X1 · 2026", [["18-in. V-spoke", 0, ["bmw_x1_28i"]], ["19-in. M Y-spoke", 650, ["bmw_x1_28i"]], ["20-in. M Double-spoke", 0, ["bmw_x1_m35i"]]])
bmw("BMW X2 · 2026", [["19-in. Y-spoke", 0, ["bmw_x2_28i"]], ["20-in. M Star-spoke", 900, ["bmw_x2_28i"]], ["21-in. M Double-spoke", 0, ["bmw_x2_m35i"]]])
bmw("BMW X3 · 2026", [["19-in. V-spoke", 0, ["bmw_x3_30"]], ["20-in. M Y-spoke", 1200, ["bmw_x3_30"]], ["21-in. M Double-spoke Jet Black", 0, ["bmw_x3_m50"]]])
bmw("BMW X5 · 2025", [["20-in. V-spoke", 0, ["bmw_x5_s40i", "bmw_x5_40i", "bmw_x5_50e"]], ["21-in. M Star-spoke", 1200, ["bmw_x5_s40i", "bmw_x5_40i", "bmw_x5_50e"]], ["22-in. M Y-spoke", 0, ["bmw_x5_m60i"]]], third=True,
    extra=[["Executive Package", 2550, None, "Soft-close doors, massage seats, Sky Lounge panoramic roof, heated rear seats", ["softClose", "massageSeats", "heatedRear"]]])
bmw("BMW X6 · 2026", [["20-in. M Star-spoke", 0, ["bmw_x6_40i"]], ["21-in. M Y-spoke", 1200, ["bmw_x6_40i"]], ["22-in. M Double-spoke", 0, ["bmw_x6_m60i"]]])
bmw("BMW X7 · 2026", [["21-in. V-spoke", 0, ["bmw_x7_40i"]], ["22-in. M Double-spoke", 0, ["bmw_x7_m60i"]], ["23-in. ALPINA Classic", 0, ["bmw_x7_alpina"]]], extra=[["Luxury Seating Package", 2300, None, "Massage seats, ventilated rear seats, second-row captain's chairs", ["massageSeats", "captains", "ventRear"]]])
bmw("BMW iX3 · 2027", [["19-in. Aerodynamic", 0, None], ["21-in. M Aerodynamic", 1500, None]], ev=True)

# ================================================================ Mercedes-Benz
MBB = ["aeb", "bsm", "rcta", "lka", "acc", "heatedSeats", "wirelessCharge", "remoteStart", "powerLiftgate", "panoRoof", "autoHigh", "ambient"]
MB_P = [["Polar White", "#efefeb", 0, None], ["Obsidian Black Metallic", "#0e0f12", 750, None], ["Graphite Grey Metallic", "#4b4f54", 750, None], ["High-Tech Silver Metallic", "#aeb2b6", 750, None], ["MANUFAKTUR Patagonia Red", "#6b1018", 1750, None], ["Sodalite Blue Metallic", "#2a3b5a", 750, None], ["MANUFAKTUR Opalite White Bright", "#f2f1ec", 1750, None]]
def mb(g, wh, third=False, ev=False, amg=False, extra=None):
    put(g, [["Premium Package", 2200, lo(g, 0.6), "Burmester surround sound, KEYLESS-GO, heated steering wheel, augmented-reality navigation", ["premiumAudio", "heatedWheel"]],
            ["Driver Assistance Package", 1950, None, "Active Distance Assist DISTRONIC, Active Steering Assist, Active Lane Change Assist, Evasive Steering Assist", ["pilot", "autoLC", "autoEmergencySteer"]],
            ["Parking Assistance Package", 1050, None, "Surround View System, Active Parking Assist, Parktronic", ["cam360", "autopark"]],
            ["AMG Line Exterior", 2500, lo(g, 0.6) if not amg else None, "AMG body styling, sport brakes, AMG wheels", ["sportSeats"]]] + (extra or []),
        [["exterior", "Night Package", 650, None, "Gloss black trim and mirrors", [], "blackPkg"], ["interior", "Heated & Ventilated Front Seats", 450, None, "Active ventilated front seats", ["ventSeats"], None],
         ["interior", "Burmester 3D Surround Sound", 1950, hi(g, 0.5), "High-end 3D audio", ["premiumAudio"], None], ["mechanical", "Trailer Hitch", 550, None, "Electrically folding hitch", ["towPkg"], None], ["interior", "MBUX Head-Up Display", 1100, None, "Full-colour head-up display", ["hud"], None]] + ([["interior", "Third-Row Seating", 1050, None, "7-passenger seating", ["thirdRow"], None]] if third else []),
        wh, [["Black MB-Tex", 0, lo(g, 0.5)], ["Black Leather", 1620, None], ["Macchiato Beige Leather", 1620, None], ["Black Nappa Leather (AMG)", 0, hi(g, 0.6)]],
        acc("Mercedes-Benz"), std_for(g, MBB + (["heatPump"] if ev else []), [(0.5, ["premiumAudio", "heatedWheel", "adaptiveDampers", "perfUpgrade"]), (0.9, ["hud", "ventSeats", "cam360", "airSusp", "massageSeats"])]), src=SRC["Mercedes-Benz"])
    paints(g, MB_P + [["Spectral Blue Metallic", "#273e66", 750, None]])
mb("Mercedes-Benz GLA · 2026", [["19-in. AMG Twin 5-spoke", 0, ["mb_gla_250"]], ["20-in. AMG Multispoke", 0, ["mb_gla_amg35"]]], amg=True)
mb("Mercedes-Benz GLB · 2026", [["19-in. 5-twin-spoke", 0, ["mb_glb_250"]], ["20-in. AMG Multispoke", 0, ["mb_glb_amg35"]]], third=True)
mb("Mercedes-Benz GLC · 2026", [["19-in. 5-spoke", 0, ["mb_glc_300", "mb_glc_350e"]], ["20-in. AMG 5-twin-spoke", 750, ["mb_glc_300", "mb_glc_350e"]], ["21-in. AMG Multispoke", 0, ["mb_glc_amg43"]]])
mb("Mercedes-Benz GLC Coupe · 2026", [["20-in. AMG 5-twin-spoke", 0, ["mb_glc_coupe_300"]], ["21-in. AMG Cross-spoke", 0, ["mb_glc_coupe_amg43"]]])
mb("Mercedes-Benz GLC with EQ Technology · 2027", [["20-in. Aero", 0, None], ["21-in. AMG Aero", 1100, None]], ev=True)
mb("Mercedes-Benz GLE · 2026", [["19-in. 5-twin-spoke", 0, ["mb_gle_350"]], ["20-in. AMG 5-twin-spoke", 0, ["mb_gle_450"]], ["21-in. AMG Multispoke", 0, ["mb_gle_amg53", "mb_gle_580"]]], third=True, extra=[["E-ACTIVE BODY CONTROL", 8350, ["mb_gle_450", "mb_gle_580"], "Active hydraulic suspension that leans into curves", ["airSusp", "adaptiveDampers"]]])
mb("Mercedes-Benz GLE Coupe · 2026", [["21-in. AMG Multispoke", 0, None], ["22-in. AMG Cross-spoke", 1200, None]])
mb("Mercedes-Benz GLS · 2026", [["21-in. 5-twin-spoke", 0, ["mb_gls_450"]], ["23-in. AMG Multispoke", 0, ["mb_gls_580"]]], extra=[["Executive Rear Seat Package", 2900, None, "Second-row captain's chairs with massage and tablet", ["captains", "massageSeats", "rearEntertainment"]]])
mb("Mercedes-Benz EQB · 2025", [["18-in. Aero", 0, None], ["19-in. AMG Multispoke", 650, None]], third=True, ev=True)
mb("Mercedes-Benz EQE SUV · 2026", [["20-in. Aero", 0, None], ["21-in. AMG Multispoke", 1200, None]], ev=True)
mb("Mercedes-Benz EQS SUV · 2026", [["20-in. Aero", 0, None], ["22-in. AMG Multispoke", 1400, None]], third=True, ev=True, extra=[["Pinnacle Trim", 4800, None, "MBUX Hyperscreen, rear-axle steering 10°, Burmester 4D", ["passengerScreen", "ws4"]]])
mb("Mercedes-Benz G-Class · 2026", [["20-in. 5-twin-spoke", 0, ["mb_g550", "mb_g580"]], ["22-in. AMG Cross-spoke", 0, ["mb_g63"]]], extra=[["Off-Road Package", 0, None, "Three locking differentials, low range, G-Turn on the G 580", ["offroad", "lockers"]]])
mb("Mercedes-Maybach GLS · 2026", [["23-in. Maybach Forged Multispoke", 0, None]], extra=[["Executive Rear Seat Package PLUS", 0, None, "Reclining rear seats, rear table, refrigerator, champagne flutes", ["captains", "massageSeats", "coolBox"]]])
mb("Mercedes-Maybach EQS SUV · 2026", [["22-in. Maybach Forged", 0, None]], ev=True, extra=[["Executive Rear Seat Package PLUS", 0, None, "Reclining rear seats, rear MBUX tablets, refrigerator", ["captains", "massageSeats", "coolBox", "rearEntertainment"]]])

# ================================================================ Cadillac
CDB = ["aeb", "bsm", "rcta", "lka", "acc", "heatedSeats", "wirelessCharge", "remoteStart", "powerLiftgate", "panoRoof", "autoHigh", "ambient", "heatPump", "heatedWheel"]
CD_P = [["Crystal White Tricoat", "#f0efe9", 1325, None], ["Stellar Black Metallic", "#0d0e11", 0, None], ["Argent Silver Metallic", "#a9adb1", 0, None], ["Opulent Blue Metallic", "#1f3156", 0, None], ["Radiant Red Tintcoat", "#7a121a", 1325, None], ["Emerald Lake Metallic", "#2c4a42", 0, None], ["Celestial Metallic", "#8c8f8f", 0, None]]
def cad(g, wh, extra=None, third=False):
    put(g, [["Super Cruise", 2500, lo(g, 0.6), "Hands-free driving on 750,000 miles of roads, with automatic lane change", ["pilot", "handsfree", "autoLC"]],
            ["Technology Package", 1650, lo(g, 0.6), "Head-up display, 360° HD surround vision, rear camera mirror, enhanced automatic parking assist", ["hud", "cam360", "digitalMirror", "autopark"]],
            ["Comfort & Convenience Package", 1300, None, "Ventilated front seats, massage seats, heated rear seats", ["ventSeats", "massageSeats", "heatedRear"]]] + (extra or []),
        [["interior", "AKG Studio Reference Audio", 1295, None, "AKG 23-speaker sound", ["premiumAudio"], None], ["mechanical", "Trailer Hitch", 650, None, "Class III hitch", ["towPkg"], None], ["exterior", "Black Package", 1095, None, "Black wheels, crest and trim", ["blackLook"], "blackPkg"]],
        wh, [["Jet Black Inteluxe", 0, lo(g, 0.4)], ["Jet Black Leather", 0, None], ["Sky Cool Gray Leather", 0, None], ["Medium Dark Mocha", 0, hi(g, 0.4)]],
        acc("Cadillac"), std_for(g, CDB + (["thirdRow"] if third else []), [(0.4, ["premiumAudio", "adaptiveDampers"]), (0.8, ["pilot", "handsfree", "autoLC", "hud", "cam360", "ventSeats", "massageSeats", "airSusp"])]), src=SRC["Cadillac"])
    paints(g, CD_P)
cad("Cadillac LYRIQ · 2027", [["20-in. Bright Silver", 0, lo(g := "Cadillac LYRIQ · 2027", 0.6)], ["22-in. Diamond-cut", 1000, lo(g, 0.9)], ["22-in. V-Series Gloss Black", 0, ["cad_lyriq_v"]]])
cad("Cadillac OPTIQ · 2027", [["20-in. Machined", 0, ["cad_optiq_lux", "cad_optiq_sport"]], ["21-in. Gloss Black", 750, ["cad_optiq_lux", "cad_optiq_sport"]], ["22-in. V-Series", 0, ["cad_optiq_v"]]])
cad("Cadillac VISTIQ · 2027", [["21-in. Bright Machined", 0, None], ["22-in. Gloss Black", 1000, None]], third=True)
cad("Cadillac CELESTIQ · 2026", [["23-in. Bespoke Forged", 0, None]], extra=[["Commission Personalisation", 0, None, "Bespoke paint, leather, embroidery and 3D-printed trim", ["electrochromicRoof", "massageSeats", "passengerScreen"]]])

# ================================================================ Tesla
TSA = ["aeb", "bsm", "rcta", "lka", "acc", "pilot", "heatedSeats", "heatedRear", "heatedWheel", "panoRoof", "wirelessCharge", "premiumAudio", "remoteStart", "dashcam", "powerLiftgate", "airSusp", "heatPump"]
g = "Tesla Cybertruck · 2026"
put(g, [["Full Self-Driving (Supervised)", 8000, None, "Navigate on Autopilot, Auto Lane Change, Autopark, Actually Smart Summon, city-street steering", ["fsd", "autoLC", "autopark", "remotePark"]], ["Off-Road Light Bar", 1600, None, "Roof-mounted LED light bar", ["offroadLights"]]],
    [["exterior", "Powered Tonneau Cover", 0, None, "Standard armored vault cover", ["powerTonneau"], None], ["mechanical", "Tow Package", 0, None, "Standard, 11,000 lb", ["towPkg"], None], ["exterior", "Satin Black Wrap", 6000, None, "Full satin black wrap", ["blackLook"], "blackPkg"]],
    [["20-in. Cybertruck Wheels with Aero Covers", 0, None], ["20-in. Cybertruck Wheels (all-terrain)", 0, None]],
    [["Black and White Vegan Leather", 0, None], ["All Black", 0, ["ct_beast"]]],
    acc("Tesla") + [["Basecamp Tent", 2975, "Bed-mounted tent", None, []], ["Bed Rails", 350, "Accessory bed rails", "bedRack", []]],
    std_for(g, TSA + ["v120Outlet", "steerByWire", "ws4", "frontCam", "powerTonneau", "towPkg"], [(1.0, ["perfUpgrade"])]), nf={"fsd": ["Full Self-Driving (Supervised)", "Supervised point-to-point driver assistance that steers, brakes and navigates on highways and city streets."]}, src=SRC["Tesla"] + "/cybertruck")
paints(g, [["Stainless Steel", "#b8bcbf", 0, None], ["Satin Black Wrap", "#1c1d1f", 6000, None], ["Satin Gray Wrap", "#5a5e62", 6000, None]])
for g, X in (("Tesla Model S · 2020", False), ("Tesla Model X · 2020", True)):
    put(g, [["Full Self-Driving Capability", 7000, None, "Navigate on Autopilot, Auto Lane Change, Autopark, Summon, Smart Summon", ["fsd", "autoLC", "autopark", "remotePark"]]] + ([["Six-Seat Interior", 6500, None, "Second-row captain's chairs", ["captains", "thirdRow"]], ["Seven-Seat Interior", 3500, None, "Third-row seats", ["thirdRow"]]] if X else []),
        [["mechanical", "Tow Package", 1000, None, "5,000 lb", ["towPkg"], None]] if X else [],
        [["19-in. Silver Wheels", 0, keys(g, lambda t: "Long" in t[1])], ["21-in. Sonic Carbon Twin Turbine Wheels", 4500, keys(g, lambda t: "Long" in t[1])], ["21-in. Arachnid / 22-in. Turbine Wheels", 0, keys(g, lambda t: "Perf" in t[1])]],
        [["All Black Premium Interior", 0, None], ["Black and White Premium Interior", 1500, None], ["Cream Premium Interior", 1500, None]],
        acc("Tesla"), std_for(g, TSA + (["falconDoors"] if X else []), [(1.0, ["perfUpgrade", "launchCtrl"])]), nf={"fsd": ["Full Self-Driving Capability", "Navigate on Autopilot with automatic lane changes, Autopark and Smart Summon (2020)."], "falconDoors": ["Falcon Wing Doors", "Rear doors that open upward, sensing the space around them."]}, src="https://www.tesla.com (2020 configurator, archived)")
    paints(g, [["Solid Black", "#0d0e10", 0, None], ["Midnight Silver Metallic", "#4a4e53", 1000, None], ["Deep Blue Metallic", "#1d3a72", 1000, None], ["Pearl White Multi-Coat", "#eceeee", 1000, None], ["Red Multi-Coat", "#a3121c", 2000, None]])

out = "Object.assign(BDATA," + json.dumps(BD, separators=(",", ":"), ensure_ascii=False) + ");   // v107: build & price for the Hyundai, BMW, Mercedes-Benz, Cadillac, Mazda, VW, RAV4 2026, Cybertruck and 2020 Model S / X\n"
out += "Object.assign(PAINT_G," + json.dumps(PG, separators=(",", ":"), ensure_ascii=False) + ");\n"
open(sys.argv[2], "w").write(out)
print(len(BD), "groups;", len(PG), "paint lists;", sorted(set(TR) - set(BD)))
