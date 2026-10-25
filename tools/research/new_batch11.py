"""Batch 11 (Oct 25 2026): every US trim, drive modes, suspension and packages for
   - Ford F-150 · 2022 (new model f150_22, the uploaded XLT SuperCrew 5.5 ft)
   - the Genesis / Chevrolet Bolt / Malibu / Nissan Altima pack (batch 10 had one trim per model and no modes / suspension / packages).
Sources: Genesis US trim lists (KBB / cars.com 2026-27), GM Authority (2027 Bolt), AutoGuide (2027 Altima), Edmunds (2022 F-150 trims).
Prices are base MSRP where found; the rest are estimates. Writes dist/batch11.json for apply_batch11.py."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import new_batch7 as B

GE = "Genesis Active Safety Control: Forward Collision-Avoidance Assist with junction turning, Lane Keeping Assist, Lane Following Assist, Blind-Spot Collision-Avoidance Assist, Rear Cross-Traffic Collision-Avoidance Assist, Smart Cruise Control with Stop & Go, Highway Driving Assist, Safe Exit Assist, Driver Attention Warning."
GE2 = GE.replace("Highway Driving Assist,", "Highway Driving Assist II (assisted lane change),") + " Remote Smart Parking Assist, Surround View Monitor, Blind-Spot View Monitor, head-up display."
CH = "Chevy Safety Assist: Automatic Emergency Braking, Front Pedestrian Braking, Lane Keep Assist with Lane Departure Warning, Following Distance Indicator, Forward Collision Alert, IntelliBeam."
CHB = CH + " Adaptive Cruise Control, Side Blind Zone Alert, Rear Cross Traffic Alert, HD Rear Vision Camera. Available Super Cruise hands-free driving."
NI = "Nissan Safety Shield 360: automatic emergency braking with pedestrian detection, rear automatic braking, blind spot warning, rear cross traffic alert, lane departure warning, high beam assist."
NIP = NI + " ProPILOT Assist (adaptive cruise with Stop & Go and steering assist), Intelligent Around View Monitor."
B.BR.update({"Genesis": (GE, "Highway Driving Assist", "HDA", False), "Chevrolet": (CH, "Adaptive Cruise Control", "ACC", False), "Nissan": (NI, "ProPILOT Assist", "ProPILOT", False)})
B.PAINT.update({"Genesis": "c:#2f3a33", "Chevrolet": "c:#a8acb0", "Nissan": "c:#7a1f24"})
B.C.clear(); X = B.car; G8 = B.G8H; CV = B.CV
GI = ["Eco", "Comfort", "Sport", "Snow"]; GS = ["Eco", "Comfort", "Sport", "Sport+", "Snow"]

# key, model, group, name, short, kind, hp, kg, drv, price, desc, extras (std = safety text override, feats = BDATA standard features)
# ---------------- Genesis G70 · 2027
X("gen_g70_25t", "gen_g70", "Genesis G70 · 2027", "2027 Genesis G70 2.5T AWD", "G70 2.5T", "ice", 300, 1720, "awd", 45550, "2.5 L turbo · 8-speed · AWD · 300 hp", eng="i4t", tq=422, gears=G8, tank=60, mpg=24, cda=0.68, modes=GI, feats=["acc", "pilot", "bsm", "rcta", "autoHigh", "heatedSeats", "remoteStart", "wirelessCharge", "awd"])
X("gen_g70_25tp", "gen_g70", "Genesis G70 · 2027", "2027 Genesis G70 2.5T Prestige AWD", "G70 2.5T Prestige", "ice", 300, 1735, "awd", 50450, "2.5 L turbo · 8-speed · AWD · 300 hp", eng="i4t", tq=422, gears=G8, tank=60, mpg=24, cda=0.68, modes=GI, std=GE2, feats=["acc", "pilot", "autoLC", "bsm", "rcta", "rAeb", "autoHigh", "cam360", "hud", "heatedSeats", "ventSeats", "heatedWheel", "heatedRear", "remoteStart", "wirelessCharge", "premiumAudio", "sunroof", "awd"])
X("gen_g70_33t", "gen_g70", "Genesis G70 · 2027", "2027 Genesis G70 3.3T Sport Prestige AWD", "G70 3.3T Sport Prestige", "ice", 368, 1800, "awd", 55600, "3.3 L twin-turbo V6 · 8-speed · AWD · 368 hp", eng="v6", tq=510, gears=G8, tank=60, mpg=20, cda=0.68, modes=GS, std=GE2, feats=["acc", "pilot", "autoLC", "bsm", "rcta", "rAeb", "autoHigh", "cam360", "hud", "heatedSeats", "ventSeats", "heatedWheel", "remoteStart", "wirelessCharge", "premiumAudio", "sunroof", "adaptiveDampers", "lsd", "sportExhaust", "sportSeats", "awd", "perfUpgrade"])
# ---------------- G80 · 2027
X("gen_g80_25t", "gen_g80", "Genesis G80 · 2027", "2027 Genesis G80 2.5T AWD", "G80 2.5T", "ice", 300, 1900, "awd", 60945, "2.5 L turbo · 8-speed · AWD · 300 hp", eng="i4t", tq=422, gears=G8, tank=73, mpg=23, cda=0.7, modes=GI, feats=["acc", "pilot", "bsm", "rcta", "autoHigh", "heatedSeats", "ventSeats", "heatedWheel", "remoteStart", "wirelessCharge", "panoRoof", "awd"])
X("gen_g80_25ta", "gen_g80", "Genesis G80 · 2027", "2027 Genesis G80 2.5T Advanced AWD", "G80 2.5T Advanced", "ice", 300, 1920, "awd", 66045, "2.5 L turbo · 8-speed · AWD · 300 hp", eng="i4t", tq=422, gears=G8, tank=73, mpg=23, cda=0.7, modes=GI, std=GE2, feats=["acc", "pilot", "autoLC", "bsm", "rcta", "rAeb", "autoHigh", "cam360", "hud", "heatedSeats", "ventSeats", "heatedWheel", "heatedRear", "remoteStart", "wirelessCharge", "premiumAudio", "panoRoof", "ambient", "awd"])
X("gen_g80_25tsp", "gen_g80", "Genesis G80 · 2027", "2027 Genesis G80 2.5T Sport Prestige AWD", "G80 2.5T Sport Prestige", "ice", 300, 1940, "awd", 71945, "2.5 L turbo · 8-speed · AWD · 300 hp", eng="i4t", tq=422, gears=G8, tank=73, mpg=23, cda=0.7, modes=GS, std=GE2, feats=["acc", "pilot", "autoLC", "bsm", "rcta", "rAeb", "autoHigh", "cam360", "hud", "heatedSeats", "ventSeats", "heatedWheel", "heatedRear", "massageSeats", "remoteStart", "wirelessCharge", "premiumAudio", "panoRoof", "ambient", "adaptiveDampers", "remotePark", "awd"])
X("gen_g80_35tsp", "gen_g80", "Genesis G80 · 2027", "2027 Genesis G80 3.5T Sport Prestige AWD", "G80 3.5T Sport Prestige", "ice", 375, 2010, "awd", 80645, "3.5 L twin-turbo V6 · 8-speed · AWD · 375 hp", eng="v6", tq=530, gears=G8, tank=73, mpg=20, cda=0.7, modes=GS, std=GE2, feats=["acc", "pilot", "autoLC", "bsm", "rcta", "rAeb", "autoHigh", "cam360", "hud", "heatedSeats", "ventSeats", "heatedWheel", "heatedRear", "massageSeats", "remoteStart", "wirelessCharge", "premiumAudio", "panoRoof", "ambient", "adaptiveDampers", "remotePark", "ws4", "lsd", "awd", "perfUpgrade"])
# ---------------- G90 · 2026
X("gen_g90_35t", "gen_g90", "Genesis G90 · 2026", "2026 Genesis G90 3.5T AWD", "G90 3.5T", "ice", 375, 2230, "awd", 90000, "3.5 L twin-turbo V6 · 8-speed · AWD · 375 hp", eng="v6", tq=530, gears=G8, tank=83, mpg=20, cda=0.75, modes=GI, std=GE2, feats=["acc", "pilot", "autoLC", "bsm", "rcta", "rAeb", "autoHigh", "cam360", "hud", "heatedSeats", "ventSeats", "heatedWheel", "heatedRear", "massageSeats", "remoteStart", "wirelessCharge", "premiumAudio", "panoRoof", "ambient", "airSusp", "adaptiveDampers", "ws4", "softClose", "remotePark", "awd"])
X("gen_g90_35t_esc", "gen_g90", "Genesis G90 · 2026", "2026 Genesis G90 3.5T e-SC AWD", "G90 3.5T e-SC", "ice", 409, 2300, "awd", 100000, "3.5 L twin-turbo V6 + electric supercharger · 8-speed · AWD · 409 hp", eng="v6", tq=549, gears=G8, tank=83, mpg=20, cda=0.75, modes=GI, std=GE2, feats=["acc", "pilot", "autoLC", "bsm", "rcta", "rAeb", "autoHigh", "cam360", "hud", "heatedSeats", "ventSeats", "heatedWheel", "heatedRear", "massageSeats", "remoteStart", "wirelessCharge", "premiumAudio", "panoRoof", "ambient", "airSusp", "adaptiveDampers", "ws4", "softClose", "remotePark", "rearEntertainment", "awd", "perfUpgrade"])
# ---------------- GV60 · 2027
X("gen_gv60_std", "gen_gv60", "Genesis GV60 · 2027", "2027 Genesis GV60 Standard RWD", "GV60 Standard", "ev", 225, 2000, "rwd", 48000, "Single motor · RWD · 225 hp · 84 kWh · about 294 mi", kWh=84, rng=294, cda=0.72, modes=["Eco", "Comfort", "Sport", "Snow"], feats=["acc", "pilot", "bsm", "rcta", "autoHigh", "heatedSeats", "wirelessCharge", "v2l", "heatPump"])
X("gen_gv60_adv", "gen_gv60", "Genesis GV60 · 2027", "2027 Genesis GV60 Advanced AWD", "GV60 Advanced", "ev", 314, 2150, "awd", 54000, "Dual motor · AWD · 314 hp · 84 kWh · about 264 mi", kWh=84, rng=264, cda=0.72, modes=["Eco", "Comfort", "Sport", "Snow"], std=GE2, feats=["acc", "pilot", "autoLC", "bsm", "rcta", "rAeb", "autoHigh", "cam360", "hud", "heatedSeats", "ventSeats", "heatedWheel", "wirelessCharge", "premiumAudio", "panoRoof", "v2l", "heatPump", "awd"])
X("gen_gv60_perf", "gen_gv60", "Genesis GV60 · 2027", "2027 Genesis GV60 Performance AWD", "GV60 Performance", "ev", 429, 2200, "awd", 60000, "Dual motor · AWD · 429 hp (483 with Boost) · 84 kWh · about 249 mi", kWh=84, rng=249, cda=0.72, modes=["Eco", "Comfort", "Sport", "Snow"], std=GE2, feats=["acc", "pilot", "autoLC", "bsm", "rcta", "rAeb", "autoHigh", "cam360", "hud", "heatedSeats", "ventSeats", "heatedWheel", "heatedRear", "wirelessCharge", "premiumAudio", "panoRoof", "v2l", "heatPump", "adaptiveDampers", "digitalMirror", "awd", "perfUpgrade"])
# ---------------- GV70 · 2027 (KBB 2027 trim list)
X("gen_gv70_25t", "gen_gv70", "Genesis GV70 · 2027", "2027 Genesis GV70 2.5T AWD", "GV70 2.5T", "ice", 300, 1950, "awd", 50895, "2.5 L turbo · 8-speed · AWD · 300 hp", eng="i4t", tq=422, gears=G8, tank=66, mpg=22, cda=0.88, modes=GI, feats=["acc", "pilot", "bsm", "rcta", "autoHigh", "heatedSeats", "remoteStart", "wirelessCharge", "powerLiftgate", "awd"])
X("gen_gv70_25ts", "gen_gv70", "Genesis GV70 · 2027", "2027 Genesis GV70 2.5T Select AWD", "GV70 2.5T Select", "ice", 300, 1960, "awd", 54095, "2.5 L turbo · 8-speed · AWD · 300 hp", eng="i4t", tq=422, gears=G8, tank=66, mpg=22, cda=0.88, modes=GI, feats=["acc", "pilot", "bsm", "rcta", "autoHigh", "heatedSeats", "ventSeats", "heatedWheel", "remoteStart", "wirelessCharge", "panoRoof", "powerLiftgate", "awd"])
X("gen_gv70_25ta", "gen_gv70", "Genesis GV70 · 2027", "2027 Genesis GV70 2.5T Advanced AWD", "GV70 2.5T Advanced", "ice", 300, 1975, "awd", 58595, "2.5 L turbo · 8-speed · AWD · 300 hp", eng="i4t", tq=422, gears=G8, tank=66, mpg=22, cda=0.88, modes=GI, std=GE2, feats=["acc", "pilot", "autoLC", "bsm", "rcta", "rAeb", "autoHigh", "cam360", "heatedSeats", "ventSeats", "heatedWheel", "heatedRear", "remoteStart", "wirelessCharge", "premiumAudio", "panoRoof", "powerLiftgate", "awd"])
X("gen_gv70_25tsp", "gen_gv70", "Genesis GV70 · 2027", "2027 Genesis GV70 2.5T Sport Prestige AWD", "GV70 2.5T Sport Prestige", "ice", 300, 1990, "awd", 63095, "2.5 L turbo · 8-speed · AWD · 300 hp", eng="i4t", tq=422, gears=G8, tank=66, mpg=22, cda=0.88, modes=GS, std=GE2, feats=["acc", "pilot", "autoLC", "bsm", "rcta", "rAeb", "autoHigh", "cam360", "hud", "heatedSeats", "ventSeats", "heatedWheel", "heatedRear", "remoteStart", "wirelessCharge", "premiumAudio", "panoRoof", "powerLiftgate", "adaptiveDampers", "remotePark", "awd"])
X("gen_gv70_35tsp", "gen_gv70", "Genesis GV70 · 2027", "2027 Genesis GV70 3.5T Sport Prestige AWD", "GV70 3.5T Sport Prestige", "ice", 375, 2050, "awd", 72045, "3.5 L twin-turbo V6 · 8-speed · AWD · 375 hp", eng="v6", tq=530, gears=G8, tank=66, mpg=19, cda=0.88, modes=GS, std=GE2, feats=["acc", "pilot", "autoLC", "bsm", "rcta", "rAeb", "autoHigh", "cam360", "hud", "heatedSeats", "ventSeats", "heatedWheel", "heatedRear", "remoteStart", "wirelessCharge", "premiumAudio", "panoRoof", "powerLiftgate", "adaptiveDampers", "remotePark", "lsd", "sportExhaust", "awd", "perfUpgrade"])
# ---------------- Electrified GV70 · 2027
X("gen_egv70", "gen_egv70", "Genesis Electrified GV70 · 2027", "2027 Genesis Electrified GV70 Advanced AWD", "Electrified GV70 Advanced", "ev", 429, 2300, "awd", 67000, "Dual motor · AWD · 429 hp (483 with Boost) · 84 kWh · about 263 mi", kWh=84, rng=263, cda=0.82, modes=["Eco", "Comfort", "Sport", "Snow"], std=GE2, feats=["acc", "pilot", "autoLC", "bsm", "rcta", "rAeb", "autoHigh", "cam360", "heatedSeats", "ventSeats", "heatedWheel", "heatedRear", "wirelessCharge", "premiumAudio", "panoRoof", "powerLiftgate", "v2l", "heatPump", "awd"])
X("gen_egv70_prest", "gen_egv70", "Genesis Electrified GV70 · 2027", "2027 Genesis Electrified GV70 Prestige AWD", "Electrified GV70 Prestige", "ev", 429, 2320, "awd", 75000, "Dual motor · AWD · 429 hp (483 with Boost) · 84 kWh · about 263 mi", kWh=84, rng=263, cda=0.82, modes=["Eco", "Comfort", "Sport", "Snow"], std=GE2, feats=["acc", "pilot", "autoLC", "bsm", "rcta", "rAeb", "autoHigh", "cam360", "hud", "heatedSeats", "ventSeats", "heatedWheel", "heatedRear", "massageSeats", "wirelessCharge", "premiumAudio", "panoRoof", "powerLiftgate", "v2l", "heatPump", "remotePark", "adaptiveDampers", "awd"])
# ---------------- GV80 · 2027
X("gen_gv80_25t", "gen_gv80", "Genesis GV80 · 2027", "2027 Genesis GV80 2.5T AWD", "GV80 2.5T", "ice", 300, 2200, "awd", 60850, "2.5 L turbo · 8-speed · AWD · 300 hp", eng="i4t", tq=422, gears=G8, tank=80, mpg=21, cda=1.0, modes=GI, feats=["acc", "pilot", "bsm", "rcta", "autoHigh", "heatedSeats", "ventSeats", "heatedWheel", "remoteStart", "wirelessCharge", "panoRoof", "powerLiftgate", "awd"])
X("gen_gv80_25ta", "gen_gv80", "Genesis GV80 · 2027", "2027 Genesis GV80 2.5T Advanced AWD", "GV80 2.5T Advanced", "ice", 300, 2220, "awd", 68000, "2.5 L turbo · 8-speed · AWD · 300 hp", eng="i4t", tq=422, gears=G8, tank=80, mpg=21, cda=1.0, modes=GI, std=GE2, feats=["acc", "pilot", "autoLC", "bsm", "rcta", "rAeb", "autoHigh", "cam360", "hud", "heatedSeats", "ventSeats", "heatedWheel", "heatedRear", "remoteStart", "wirelessCharge", "premiumAudio", "panoRoof", "powerLiftgate", "thirdRow", "awd"])
X("gen_gv80_35ta", "gen_gv80", "Genesis GV80 · 2027", "2027 Genesis GV80 3.5T Advanced AWD", "GV80 3.5T Advanced", "ice", 375, 2290, "awd", 76000, "3.5 L twin-turbo V6 · 8-speed · AWD · 375 hp", eng="v6", tq=530, gears=G8, tank=80, mpg=19, cda=1.0, modes=GI, std=GE2, feats=["acc", "pilot", "autoLC", "bsm", "rcta", "rAeb", "autoHigh", "cam360", "hud", "heatedSeats", "ventSeats", "heatedWheel", "heatedRear", "remoteStart", "wirelessCharge", "premiumAudio", "panoRoof", "powerLiftgate", "thirdRow", "adaptiveDampers", "awd"])
X("gen_gv80_35tp", "gen_gv80", "Genesis GV80 · 2027", "2027 Genesis GV80 3.5T Prestige AWD", "GV80 3.5T Prestige", "ice", 375, 2310, "awd", 84500, "3.5 L twin-turbo V6 · 8-speed · AWD · 375 hp", eng="v6", tq=530, gears=G8, tank=80, mpg=19, cda=1.0, modes=GI, std=GE2, feats=["acc", "pilot", "autoLC", "bsm", "rcta", "rAeb", "autoHigh", "cam360", "hud", "heatedSeats", "ventSeats", "heatedWheel", "heatedRear", "massageSeats", "remoteStart", "wirelessCharge", "premiumAudio", "panoRoof", "powerLiftgate", "thirdRow", "adaptiveDampers", "softClose", "remotePark", "awd"])
# ---------------- GV80 Coupe · 2027
X("gen_gv80c_35t", "gen_gv80c", "Genesis GV80 Coupe · 2027", "2027 Genesis GV80 Coupe 3.5T Advanced", "GV80 Coupe 3.5T", "ice", 375, 2250, "awd", 75000, "3.5 L twin-turbo V6 · 8-speed · AWD · 375 hp", eng="v6", tq=530, gears=G8, tank=80, mpg=19, cda=0.98, modes=GS, std=GE2, feats=["acc", "pilot", "autoLC", "bsm", "rcta", "rAeb", "autoHigh", "cam360", "hud", "heatedSeats", "ventSeats", "heatedWheel", "heatedRear", "remoteStart", "wirelessCharge", "premiumAudio", "panoRoof", "powerLiftgate", "adaptiveDampers", "sportSeats", "awd", "perfUpgrade"])
# (key kept from batch 10 for the e-SC coupe so saves and lineups don't break)
B.C[-1]["key"] = "gen_gv80c_35ta"
X("gen_gv80c_35t", "gen_gv80c", "Genesis GV80 Coupe · 2027", "2027 Genesis GV80 Coupe 3.5T e-SC Prestige", "GV80 Coupe 3.5T e-SC", "ice", 409, 2300, "awd", 86000, "3.5 L twin-turbo V6 + electric supercharger · 8-speed · AWD · 409 hp", eng="v6", tq=549, gears=G8, tank=80, mpg=19, cda=0.98, modes=GS, std=GE2, feats=["acc", "pilot", "autoLC", "bsm", "rcta", "rAeb", "autoHigh", "cam360", "hud", "heatedSeats", "ventSeats", "heatedWheel", "heatedRear", "massageSeats", "remoteStart", "wirelessCharge", "premiumAudio", "panoRoof", "powerLiftgate", "adaptiveDampers", "sportSeats", "remotePark", "softClose", "lsd", "awd", "perfUpgrade"])
# ---------------- Chevrolet Bolt · 2027 (GM Authority: 1LT $28,995, RS $32,995; 210 hp, 65 kWh LFP, 255 mi)
X("chv_bolt_lt", "chv_bolt", "Chevrolet Bolt · 2027", "2027 Chevrolet Bolt LT", "Bolt LT", "ev", 210, 1750, "fwd", 28995, "Single motor · FWD · 210 hp · 65 kWh LFP · about 255 mi", kWh=65, rng=255, cda=0.72, modes=["Normal", "Sport", "Snow/Ice"], std=CHB, feats=["acc", "bsm", "rcta", "autoHigh", "heatedSeats", "wirelessCharge", "heatPump"])
X("chv_bolt_rs", "chv_bolt", "Chevrolet Bolt · 2027", "2027 Chevrolet Bolt RS", "Bolt RS", "ev", 210, 1760, "fwd", 32995, "Single motor · FWD · 210 hp · 65 kWh LFP · about 255 mi", kWh=65, rng=255, cda=0.72, modes=["Normal", "Sport", "Snow/Ice"], std=CHB, feats=["acc", "bsm", "rcta", "autoHigh", "heatedSeats", "heatedWheel", "ventSeats", "wirelessCharge", "heatPump", "cam360", "digitalMirror"])
# ---------------- Chevrolet Malibu · 2025 (final model year: LS, RS, LT, 2LT)
X("chv_malibu_ls", "chv_malibu", "Chevrolet Malibu · 2025", "2025 Chevrolet Malibu LS", "Malibu LS", "ice", 163, 1430, "fwd", 25100, "1.5 L turbo · CVT · FWD · 163 hp", eng="i4t", tq=250, gears=CV, cvt=True, tank=59, mpg=32, cda=0.66, modes=["Normal", "Sport", "Snow/Ice"], feats=["autoHigh"])
X("chv_malibu_rs", "chv_malibu", "Chevrolet Malibu · 2025", "2025 Chevrolet Malibu RS", "Malibu RS", "ice", 163, 1440, "fwd", 26700, "1.5 L turbo · CVT · FWD · 163 hp", eng="i4t", tq=250, gears=CV, cvt=True, tank=59, mpg=32, cda=0.66, modes=["Normal", "Sport", "Snow/Ice"], feats=["autoHigh", "remoteStart"])
X("chv_malibu_lt", "chv_malibu", "Chevrolet Malibu · 2025", "2025 Chevrolet Malibu LT", "Malibu LT", "ice", 163, 1440, "fwd", 28000, "1.5 L turbo · CVT · FWD · 163 hp", eng="i4t", tq=250, gears=CV, cvt=True, tank=59, mpg=32, cda=0.66, modes=["Normal", "Sport", "Snow/Ice"], feats=["autoHigh", "remoteStart", "heatedSeats", "bsm", "rcta"])
X("chv_malibu_2lt", "chv_malibu", "Chevrolet Malibu · 2025", "2025 Chevrolet Malibu 2LT", "Malibu 2LT", "ice", 163, 1460, "fwd", 31200, "1.5 L turbo · CVT · FWD · 163 hp", eng="i4t", tq=250, gears=CV, cvt=True, tank=59, mpg=32, cda=0.66, modes=["Normal", "Sport", "Snow/Ice"], std=CHB.replace(" Available Super Cruise hands-free driving.", ""), feats=["acc", "autoHigh", "remoteStart", "heatedSeats", "ventSeats", "heatedWheel", "bsm", "rcta", "wirelessCharge", "premiumAudio"])
# ---------------- Nissan Altima · 2027 (AutoGuide: SV $27,790, SR $29,190, SR AWD $30,690 — the final Altima)
X("nissan_altima27_sv", "nissan_altima", "Nissan Altima · 2027", "2027 Nissan Altima SV", "Altima SV", "ice", 188, 1460, "fwd", 27790, "2.5 L · Xtronic CVT · FWD · 188 hp", eng="i4h", tq=244, gears=CV, cvt=True, tank=61, mpg=32, cda=0.66, modes=["Normal", "Sport"], std=NIP, feats=["acc", "pilot", "bsm", "rcta", "rAeb", "autoHigh", "remoteStart", "heatedSeats"])
X("nissan_altima27_sr", "nissan_altima", "Nissan Altima · 2027", "2027 Nissan Altima SR", "Altima SR", "ice", 188, 1470, "fwd", 29190, "2.5 L · Xtronic CVT · FWD · 188 hp", eng="i4h", tq=244, gears=CV, cvt=True, tank=61, mpg=31, cda=0.66, modes=["Normal", "Sport"], std=NIP, feats=["acc", "pilot", "bsm", "rcta", "rAeb", "autoHigh", "remoteStart", "heatedSeats", "sportSeats"])
X("nissan_altima27_sra", "nissan_altima", "Nissan Altima · 2027", "2027 Nissan Altima SR Intelligent AWD", "Altima SR AWD", "ice", 182, 1550, "awd", 30690, "2.5 L · Xtronic CVT · Intelligent AWD · 182 hp", eng="i4h", tq=244, gears=CV, cvt=True, tank=61, mpg=29, cda=0.66, modes=["Normal", "Sport"], std=NIP, feats=["acc", "pilot", "bsm", "rcta", "rAeb", "autoHigh", "remoteStart", "heatedSeats", "sportSeats", "awd"])

B.C[:] = [c for c in B.C if c.get("name")]
OLD = {"gen_g70_25t", "gen_g80_25t", "gen_g90_35t", "gen_gv60_adv", "gen_gv70_25t", "gen_egv70", "gen_gv80_25t", "gen_gv80c_35t", "chv_bolt_lt", "chv_malibu_lt", "nissan_altima27_sv"}
# the batch-10 key gen_g90_35t was the 409 hp e-SC; keep that key on the e-SC so saved garages keep the same car
for c in B.C:
    if c["key"] == "gen_g90_35t": c["key"] = "gen_g90_35t_std"
    elif c["key"] == "gen_g90_35t_esc": c["key"] = "gen_g90_35t"
    elif c["key"] == "gen_gv80c_35ta": pass

def trims():
    out = []
    for c in B.C:
        brand = c["group"].split(" ")[0]
        std, pn, ps, sc = B.BR[brand]
        if c.get("std"): std = c["std"]
        kW = round(c["hp"] * 0.7457); kind = c["kind"]; drv = c["drv"]
        fb = {"fwd": [1, 0], "rwd": [0, 1], "awd": [0.4, 0.6] if brand == "Genesis" and kind == "ice" else [0.6, 0.4]}[drv]
        modes = c["modes"]
        hda2 = "Highway Driving Assist II" in std
        T = {"cda": c["cda"], "ws4": "ws4" in c.get("feats", []), "crab": False, "tv": False, "height": False, "modes": len(modes), "real": True, "model": c["model"], "group": c["group"],
             "name": c["name"], "short": c["short"], "desc": c["desc"], "mass": c["kg"], "kW": kW, "paint": B.PAINT[brand], "fwd": 0.56 if drv != "rwd" else 0.5, "modeNames": modes,
             "pilotName": "Highway Driving Assist II" if hda2 else ("ProPILOT Assist" if brand == "Nissan" and "ProPILOT" in std else pn), "pilotShort": "HDA2" if hda2 else ps, "handsOn": True, "odo0": 20, "std": std,
             "feat": c["desc"].split(" · ")[0] + ", " + str(c["hp"]) + " hp"}
        feats = set(c.get("feats", []))
        if kind == "ice":
            T.update(ice=True, tank=c["tank"], mpg=c["mpg"]); no = list(B.NO_ICE)
            cv = c.get("cvt", False); g = c["gears"]
            D = {"layout": "ice", "eng": c["eng"], "turbo": "turbo" in c["desc"] or "supercharger" in c["desc"], "Tpk": c["tq"], "Ppk": kW * 1000,
                 "red": 6500 if c["eng"] in ("i4h", "i4t") else 6300, "idle": 700, "gears": g, "fd": 3.2 if not cv else 4.0, "rev": 3.4, "bias": fb, "Tna": round(c["tq"] * 0.72)}
            if cv: D.update(cvt=True, rmin=0.4, rmax=2.6)
        else:
            mT = c["kg"] * 3.0; P = kW * 1000
            D = {"layout": "axle", "T": [round(mT * fb[0]), round(mT * fb[1])], "P": [round(P * fb[0]), round(P * fb[1])]}
            T.update(kWh=c["kWh"], regenMax=3); T["feat"] = f"{c['hp']} hp, about {c['rng']} mi"; no = list(B.NO_EV)
        # what this trim can't have at all
        if "acc" not in feats and "acc" not in str(c.get("opt", "")): pass
        if "autoLC" in feats and "autoLC" in no: no.remove("autoLC")
        if "remotePark" in feats or "autopark" in feats:
            if "autopark" in no: no.remove("autopark")
        if "ws4" in feats and "ws4" in no: no.remove("ws4")
        if brand == "Genesis" and "matrix" in no: no.remove("matrix")
        if brand == "Nissan" and not ("ProPILOT" in std): no += ["pilot"]
        out.append((c, T, D, no))
    return out

# ---------------- drive modes (DMODES)
MD = {"Eco": ("eco", "Softer throttle, early upshifts and lighter climate load to save fuel."),
      "Comfort": ("comfort", "Balanced default: smooth throttle and shifts, comfort steering and dampers."),
      "Normal": ("normal", "Default balanced everyday setting."),
      "Sport": ("sport", "Sharper throttle, later shifts, heavier steering and firmer adaptive dampers where fitted."),
      "Sport+": ("sportplus", "Most aggressive throttle and shift map, loosest stability control and stiffest damping."),
      "Snow": ("snow", "Gentle throttle and early upshifts to limit wheelspin on snow and ice."),
      "Snow/Ice": ("snow", "Reduces throttle sensitivity and adjusts traction control on slippery roads.")}
def dmodes(c):
    m = [[n, MD[n][0], MD[n][1]] for n in c["modes"]]
    brand = c["group"].split(" ")[0]; t = []
    if c["drv"] == "awd":
        t.append({"Genesis": "AWD with Multi-Plate Clutch and Dynamic Torque Vectoring", "Nissan": "Intelligent AWD"}.get(brand, "AWD"))
    if c["model"] in ("gen_gv70", "gen_gv80", "gen_gv80c") and c["drv"] == "awd": t.append("Terrain Mode: Snow, Mud, Sand")
    if c["kind"] == "ev": t.append("Regenerative braking paddles, i-Pedal one-pedal driving" if brand == "Genesis" else "Regen on Demand paddle, One Pedal Driving")
    f = c.get("feats", [])
    if "airSusp" in f: s = ["airadaptive", "Electronic air suspension with road preview (Electronic Control Suspension)", True]
    elif "adaptiveDampers" in f: s = ["adaptive", "Electronic Control Suspension with road preview" if brand == "Genesis" else "Adaptive dampers", True]
    else: s = ["passive", {"gen_g70": "Passive dampers, MacPherson front / multi-link rear", "chv_bolt": "MacPherson strut front, compound-link torsion beam rear", "chv_malibu": "MacPherson strut front, four-link rear", "nissan_altima": "Independent strut front, multi-link rear"}.get(c["model"], "Passive dampers, multi-link front and rear"), False]
    D = {"m": m, "t": t, "s": s}
    return D

# ---------------- suspension (SUSR): [front, rear, spring, damper, damper name, anti-roll bars, ride-height range, ground clearance mm, wheel travel mm, tune]
def susr(c):
    f = c.get("feats", []); mdl = c["model"]
    if mdl == "chv_bolt": return ["macpherson", "torsion_beam", "coil", "passive", "Passive twin-tube dampers", "front_only", None, 150, [150, 170], "comfort"]
    if mdl == "chv_malibu": return ["macpherson", "multilink", "coil", "passive", "Passive twin-tube dampers", "front_rear", None, 140, [160, 175], "comfort"]
    if mdl == "nissan_altima": return ["macpherson", "multilink", "coil", "passive", "Passive twin-tube dampers" + (", SR sport-tuned springs and stabilizers" if "SR" in c["short"] else ""), "front_rear", None, 135, [155, 170], "sport" if "SR" in c["short"] else "comfort"]
    front = "macpherson" if mdl in ("gen_gv60", "gen_egv70") else "multilink"
    gc = {"gen_g70": 130, "gen_g80": 135, "gen_g90": 150, "gen_gv60": 160, "gen_gv70": 200, "gen_egv70": 175, "gen_gv80": 220, "gen_gv80c": 210}[mdl]
    if "airSusp" in f: return [front, "multilink", "air", "adaptive", "Electronic air suspension with road preview camera", "front_rear", [-20, 20], gc, [160, 180], "comfort"]
    if "adaptiveDampers" in f: return [front, "multilink", "coil", "adaptive", "Electronic Control Suspension (adaptive dampers with road preview)", "front_rear", None, gc, [160, 180], "sport" if ("Sport" in c["short"] or "Perf" in c["short"] or "Coupe" in c["short"] or "3.3T" in c["short"]) else "balanced"]
    return [front, "multilink", "coil", "passive", "Passive dampers", "front_rear", None, gc, [160, 180], "balanced"]

# ---------------- packages, wheels, interiors, tyres (BDATA)
def bdata():
    out = {}
    def G(name, keys): return [c["key"] for c in B.C if c["group"] == name and c["key"] in keys] or None
    for name in sorted(set(c["group"] for c in B.C)):
        ks = [c["key"] for c in B.C if c["group"] == name]; base = ks[0]; top = ks[-1]
        brand = name.split(" ")[0]; e = {"pk": [], "op": [], "wh": [], "ac": [], "std": {}, "nf": {}, "int": [], "ty": [], "conf": "estimate", "src": ""}
        for c in B.C:
            if c["group"] == name: e["std"][c["key"]] = list(c.get("feats", []))
        if brand == "Genesis":
            ice = any(c["kind"] == "ice" for c in B.C if c["group"] == name)
            e["pk"] = [["Advanced Package (in Advanced trims)", 0, None, "Highway Driving Assist II, Surround View Monitor, Blind-Spot View Monitor, Lexicon audio, heated rear seats", ["autoLC", "cam360", "premiumAudio", "heatedRear"]],
                       ["Sport Package", 0, [k for k in ks if "sp" in k or "33t" in k or "perf" in k or "gv80c" in k] or None, "Electronic Control Suspension with road preview, sport seats, Sport+ mode, sport brakes", ["adaptiveDampers", "sportSeats"]],
                       ["Prestige Package (in Prestige trims)", 0, None, "Nappa leather, head-up display, ventilated seats, Remote Smart Parking Assist, soft-close doors", ["hud", "ventSeats", "remotePark", "softClose"]]]
            e["op"] = [["exterior", "Matte paint", 1500, None, "matte finish (Prestige trims)", [], None], ["interior", "Rear-seat comfort package", 1450, [top], "heated and ventilated rear seats, rear sunshades", ["heatedRear"], None]]
            e["wh"] = [["19-in. alloy", 0, [base]], ["20-in. alloy", 0, [k for k in ks if k != base] or None], ["21-in. Sport alloy", 0, [k for k in ks if "sp" in k or "33t" in k or "perf" in k] or None]]
            e["int"] = [["Black leatherette", 0, [base]], ["Obsidian Black Nappa", 0, [k for k in ks if k != base] or None], ["Vanilla Beige / Brown Nappa", 0, [k for k in ks if k != base] or None]]
            e["ty"] = [["All-Season (std)", 0, None, "allseason"], ["Summer performance (Sport)", 0, [k for k in ks if "sp" in k or "33t" in k or "perf" in k] or None, "summer"]]
            e["nf"] = {"lsd": ["Electronic limited-slip differential", "Shifts torque between the rear wheels when powering out of corners."], "remotePark": ["Remote Smart Parking Assist", "Moves the car in and out of tight spaces from the key fob."]}
            e["conf"] = "estimate"; e["src"] = "https://www.genesis.com/us/en/models"
        elif name.startswith("Chevrolet Bolt"):
            e["pk"] = [["LT Comfort Package", 995, ["chv_bolt_lt"], "heated front seats and wheel, power driver seat", ["heatedSeats", "heatedWheel"]],
                       ["Tech Package", 1495, ["chv_bolt_rs"], "HD Surround Vision, rear camera mirror, wireless charging, 11-in. display upgrades", ["cam360", "digitalMirror", "wirelessCharge"]],
                       ["Super Cruise Package (WK7)", 1195, ["chv_bolt_lt", "chv_bolt_rs"], "Super Cruise hands-free driving on compatible roads (3 years included)", ["handsfree", "pilot", "autoLC"]],
                       ["Dual Panel Sunroof Package", 1195, ["chv_bolt_rs"], "power sunroof", ["panoRoof"]]]
            e["wh"] = [["17-in. aluminum", 0, ["chv_bolt_lt"]], ["19-in. RS black aluminum", 0, ["chv_bolt_rs"]]]
            e["int"] = [["Jet Black cloth/leatherette", 0, ["chv_bolt_lt"]], ["Jet Black leatherette with red accents", 0, ["chv_bolt_rs"]]]
            e["ty"] = [["All-Season (std)", 0, None, "allseason"]]
            e["conf"] = "confirmed"; e["src"] = "https://gmauthority.com/blog/2025/12/2027-chevy-bolt-configurator-live/"
        elif name.startswith("Chevrolet Malibu"):
            e["pk"] = [["Driver Confidence Package", 545, ["chv_malibu_lt"], "Side Blind Zone Alert, Rear Cross Traffic Alert, Rear Park Assist", ["bsm", "rcta"]],
                       ["Sun and Wheels Package", 1395, ["chv_malibu_rs", "chv_malibu_lt"], "power sunroof, 19-in. wheels", ["sunroof"]]]
            e["wh"] = [["16-in. steel", 0, ["chv_malibu_ls"]], ["18-in. black aluminum", 0, ["chv_malibu_rs"]], ["17-in. aluminum", 0, ["chv_malibu_lt"]], ["18-in. machined aluminum", 0, ["chv_malibu_2lt"]]]
            e["int"] = [["Jet Black cloth", 0, ["chv_malibu_ls", "chv_malibu_rs", "chv_malibu_lt"]], ["Jet Black leather", 0, ["chv_malibu_2lt"]]]
            e["ty"] = [["All-Season (std)", 0, None, "allseason"]]
            e["conf"] = "estimate"; e["src"] = "https://www.chevrolet.com/cars/malibu"
        elif name.startswith("Nissan Altima"):
            e["pk"] = [["Premium Package", 1990, ["nissan_altima27_sr", "nissan_altima27_sra"], "power moonroof, Bose audio, Intelligent Around View Monitor, ProPILOT Assist with Navi-link", ["sunroof", "premiumAudio", "cam360"]],
                       ["Splash Guard and Floor Mat Package", 345, None, "splash guards, carpeted floor mats", ["floorMats"]]]
            e["wh"] = [["17-in. aluminum", 0, ["nissan_altima27_sv"]], ["19-in. gloss black aluminum", 0, ["nissan_altima27_sr", "nissan_altima27_sra"]]]
            e["int"] = [["Charcoal cloth", 0, ["nissan_altima27_sv"]], ["Charcoal sport cloth with orange stitching", 0, ["nissan_altima27_sr", "nissan_altima27_sra"]]]
            e["ty"] = [["All-Season (std)", 0, None, "allseason"]]
            e["conf"] = "confirmed"; e["src"] = "https://www.autoguide.com/auto/manufacturers/nissan/2027-nissan-altima-starts-at-27-790-drops-base-awd-trim-44640250"
        out[name] = e
    return out

if __name__ == "__main__":
    T = trims()
    adds = [f' add({json.dumps(c["key"])},{{...{json.dumps(t, separators=(",", ":"))},no:{json.dumps(no)}}},{json.dumps(d, separators=(", ", ": "))},{c["price"]});' for c, t, d, no in T]
    res = {"adds": adds, "dmodes": {c["key"]: dmodes(c) for c in B.C}, "susr": {c["key"]: susr(c) for c in B.C}, "bdata": bdata(), "keys": [c["key"] for c in B.C]}
    json.dump(res, open(sys.argv[1], "w"), indent=0)
    print(len(adds), "trims")
