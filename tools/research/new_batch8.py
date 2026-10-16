"""Trims for the Oct 2026 packs: Mazda (6 models), Volkswagen (7), Toyota RAV4 2026, Tesla Cybertruck and the 2020 Model S / X.
US lineups and starting MSRPs as of mid-2026 (manufacturer sites and press releases); 2027 models not yet EPA-rated are est.
Drive modes are each car's real selector (Mazda Mi-Drive, VW Driving Mode Selection / 4MOTION Active Control, Toyota Drive Mode, Tesla).
Prints the add(...) lines and a DMODES object for src/app_template.html:  python3 new_batch8.py adds.js dmodes.js"""
import json, sys

MZ = "Mazda i-Activsense: Smart Brake Support with pedestrian and cyclist detection, Mazda Radar Cruise Control with Stop & Go, Lane-Keep Assist, Lane Departure Warning, Blind Spot Monitoring with Rear Cross Traffic Alert, Driver Attention Alert, Cruising & Traffic Support."
VW = "Volkswagen IQ.DRIVE: Front Assist with pedestrian and cyclist monitoring, Active Blind Spot Monitor, Rear Traffic Alert, Lane Assist, Adaptive Cruise Control with Stop & Go, Travel Assist (semi-automated driving assistance, hands on), Emergency Assist."
TY = "Toyota Safety Sense 4.0: Pre-Collision System with pedestrian, cyclist and motorcycle detection, Full-Speed Dynamic Radar Cruise Control, Lane Departure Alert with Steering Assist, Lane Tracing Assist, Road Sign Assist, Automatic High Beams, Proactive Driving Assist, Blind Spot Monitor with Rear Cross-Traffic Alert."
BR = {"Mazda": (MZ, "Cruising & Traffic Support", "CTS"), "Volkswagen": (VW, "Travel Assist", "TA"), "Toyota": (TY, "Lane Tracing Assist", "LTA")}
PAINT = {"Mazda": "c:#8e1b20", "Volkswagen": "c:#2a3b52", "Toyota": "c:#5b6066"}
G6 = [3.55, 2.02, 1.45, 1.00, 0.71, 0.60]          # Skyactiv-Drive 6-speed
G8M = [5.25, 3.03, 1.95, 1.46, 1.22, 1.00, 0.81, 0.64]   # Mazda 8-speed (CX-70 / CX-90)
G8 = [5.52, 3.31, 2.22, 1.72, 1.31, 1.00, 0.82, 0.64]    # Aisin 8-speed (VW)
G7D = [3.40, 2.75, 1.65, 1.06, 0.79, 0.78, 0.64]        # 7-speed DSG
C = []
def car(key, model, group, name, short, kind, hp, kg, drv, price, desc, modes, **x):
    C.append(dict(key=key, model=model, group=group, name=name, short=short, kind=kind, hp=hp, kg=kg, drv=drv, price=price, desc=desc, modes=modes, **x))

N, S, O, TW, E, CM, SP, IN, SN, OR, TR, EVM = ("Normal", "normal"), ("Sport", "sport"), ("Off-Road", "offroad"), ("Towing", "tow"), ("Eco", "eco"), ("Comfort", "comfort"), ("Sport", "sport"), ("Individual", "custom"), ("Snow", "snow"), ("Offroad", "offroad"), ("Trail", "trail"), ("EV", "ev")
MI2 = [N, S]; MI3 = [N, S, O]; MI4 = [N, S, O, TW]
# ---------------- Mazda (Mi-Drive)
m3 = ("mz_3hb", "Mazda Mazda3 Hatchback · 2026")
car("mz_3hb_ss", *m3, "2026 Mazda3 2.5 S Select Sport Hatchback", "Mazda3 2.5 S Select Sport", "ice", 191, 1390, "fwd", 26150, "2.5 L · 6-speed · FWD · 191 hp", MI2, eng="i4h", tq=186, gears=G6, tank=51, mpg=31, cda=0.66)
car("mz_3hb_pref", *m3, "2026 Mazda3 2.5 S Preferred Hatchback", "Mazda3 2.5 S Preferred", "ice", 191, 1400, "fwd", 28150, "2.5 L · 6-speed · FWD · 191 hp", MI2, eng="i4h", tq=186, gears=G6, tank=51, mpg=31, cda=0.66)
car("mz_3hb_carbon", *m3, "2026 Mazda3 2.5 S Carbon Edition Hatchback", "Mazda3 Carbon Edition", "ice", 191, 1410, "fwd", 29650, "2.5 L · 6-speed · FWD · 191 hp", MI2, eng="i4h", tq=186, gears=G6, tank=51, mpg=31, cda=0.66)
car("mz_3hb_prem", *m3, "2026 Mazda3 2.5 S Premium AWD Hatchback", "Mazda3 2.5 S Premium AWD", "ice", 191, 1500, "awd", 32150, "2.5 L · 6-speed · i-Activ AWD · 191 hp", MI2, eng="i4h", tq=186, gears=G6, tank=51, mpg=28, cda=0.66)
car("mz_3hb_turbo", *m3, "2026 Mazda3 2.5 Turbo Premium Plus AWD Hatchback", "Mazda3 2.5 Turbo Premium Plus", "ice", 250, 1560, "awd", 37150, "2.5 L turbo · 6-speed · i-Activ AWD · 250 hp (premium fuel)", MI2, eng="i4t", tq=320, gears=G6, tank=51, mpg=27, cda=0.66)
c30 = ("mz_cx30", "Mazda CX-30 · 2026")
car("mz_cx30_ss", *c30, "2026 Mazda CX-30 2.5 S Select Sport", "CX-30 2.5 S Select Sport", "ice", 191, 1530, "awd", 26900, "2.5 L · 6-speed · i-Activ AWD · 191 hp", MI3, eng="i4h", tq=186, gears=G6, tank=48, mpg=29, cda=0.78)
car("mz_cx30_pref", *c30, "2026 Mazda CX-30 2.5 S Preferred", "CX-30 2.5 S Preferred", "ice", 191, 1540, "awd", 29150, "2.5 L · 6-speed · i-Activ AWD · 191 hp", MI3, eng="i4h", tq=186, gears=G6, tank=48, mpg=29, cda=0.78)
car("mz_cx30_carbon", *c30, "2026 Mazda CX-30 2.5 S Carbon Edition", "CX-30 Carbon Edition", "ice", 191, 1545, "awd", 30500, "2.5 L · 6-speed · i-Activ AWD · 191 hp", MI3, eng="i4h", tq=186, gears=G6, tank=48, mpg=29, cda=0.78)
car("mz_cx30_prem", *c30, "2026 Mazda CX-30 2.5 S Premium", "CX-30 2.5 S Premium", "ice", 191, 1550, "awd", 32750, "2.5 L · 6-speed · i-Activ AWD · 191 hp", MI3, eng="i4h", tq=186, gears=G6, tank=48, mpg=29, cda=0.78)
car("mz_cx30_tss", *c30, "2026 Mazda CX-30 2.5 Turbo Select Sport", "CX-30 2.5 Turbo Select Sport", "ice", 250, 1600, "awd", 31400, "2.5 L turbo · 6-speed · i-Activ AWD · 250 hp (premium fuel)", MI3, eng="i4t", tq=320, gears=G6, tank=48, mpg=26, cda=0.78)
car("mz_cx30_tpp", *c30, "2026 Mazda CX-30 2.5 Turbo Premium Plus", "CX-30 2.5 Turbo Premium Plus", "ice", 250, 1620, "awd", 37900, "2.5 L turbo · 6-speed · i-Activ AWD · 250 hp (premium fuel)", MI3, eng="i4t", tq=320, gears=G6, tank=48, mpg=26, cda=0.78)
c5 = ("mz_cx5", "Mazda CX-5 · 2026")
for k, t, p in (("s", "S", 29990), ("ss", "S Select", 31990), ("sp", "S Preferred", 33990), ("prem", "S Premium", 36990), ("pp", "S Premium Plus", 39990)):
    car("mz_cx5_" + k, *c5, f"2026 Mazda CX-5 2.5 {t} AWD", f"CX-5 2.5 {t}", "ice", 187, 1690, "awd", p, "2.5 L · 6-speed · i-Activ AWD · 187 hp · 15.6-inch touchscreen", MI3, eng="i4h", tq=185, gears=G6, tank=56, mpg=28, cda=0.86)
c50 = ("mz_cx50", "Mazda CX-50 · 2026")
for k, t, p in (("ss", "2.5 S Select", 30500), ("pref", "2.5 S Preferred", 32850), ("prem", "2.5 S Premium", 36100), ("mer", "2.5 S Meridian Edition", 37400)):
    car("mz_cx50_" + k, *c50, f"2026 Mazda CX-50 {t}", f"CX-50 {t}", "ice", 187, 1650, "awd", p, "2.5 L · 6-speed · i-Activ AWD · 187 hp", MI4, eng="i4h", tq=185, gears=G6, tank=58, mpg=27, cda=0.88)
for k, t, p in (("tprem", "2.5 Turbo Premium", 40850), ("tmer", "2.5 Turbo Meridian Edition", 42000), ("tpp", "2.5 Turbo Premium Plus", 44100)):
    car("mz_cx50_" + k, *c50, f"2026 Mazda CX-50 {t}", f"CX-50 {t}", "ice", 256, 1730, "awd", p, "2.5 L turbo · 6-speed · i-Activ AWD · 256 hp (premium fuel)", MI4, eng="i4t", tq=320, gears=G6, tank=58, mpg=25, cda=0.88)
for k, t, p in (("hpref", "Hybrid Preferred", 34450), ("hprem", "Hybrid Premium", 37650), ("hpp", "Hybrid Premium Plus", 40600)):
    car("mz_cx50_" + k, *c50, f"2026 Mazda CX-50 {t}", f"CX-50 {t}", "hev", 219, 1760, "awd", p, "2.5 L hybrid · eCVT · AWD · 219 hp", [N, S, ("Off-Road", "offroad"), EVM], tank=55, mpg=38, cda=0.88, eng="i4h")
c70 = ("mz_cx70", "Mazda CX-70 · 2026")
for k, t, p, hp, tq in (("tpref", "3.3 Turbo Preferred", 41200, 280, 332), ("tprem", "3.3 Turbo Premium", 45150, 280, 332), ("tsprem", "3.3 Turbo S Premium", 53450, 340, 369), ("tspp", "3.3 Turbo S Premium Plus", 56800, 340, 369)):
    car("mz_cx70_" + k, *c70, f"2026 Mazda CX-70 {t}", f"CX-70 {t}", "ice", hp, 2010, "awd", p, f"3.3 L turbo inline-6 mild hybrid · 8-speed · i-Activ AWD · {hp} hp", MI4, eng="v6", tq=tq, gears=G8M, tank=74, mpg=25, cda=0.98, rwdBias=True)
for k, t, p in (("phpref", "PHEV Preferred", 51500), ("phpp", "PHEV Premium Plus", 57600)):
    car("mz_cx70_" + k, *c70, f"2026 Mazda CX-70 {t}", f"CX-70 {t}", "phev", 323, 2270, "awd", p, "2.5 L PHEV · 8-speed · i-Activ AWD · 323 hp · 26 mi EV", [N, S, O, TW, EVM], tank=57, mpg=25, kWh=17.8, evMi=26, cda=0.98, eng="i4h")
c90 = ("mz_cx90", "Mazda CX-90 · 2026")
for k, t, p, hp, tq in (("tsel", "3.3 Turbo Select", 39500, 280, 332), ("tpref", "3.3 Turbo Preferred", 42600, 280, 332), ("tpp", "3.3 Turbo Preferred Plus", 45600, 280, 332), ("tprem", "3.3 Turbo Premium", 48100, 280, 332),
                            ("tsprem", "3.3 Turbo S Premium", 54600, 340, 369), ("tspp", "3.3 Turbo S Premium Plus", 59100, 340, 369)):
    car("mz_cx90_" + k, *c90, f"2026 Mazda CX-90 {t}", f"CX-90 {t}", "ice", hp, 2080, "awd", p, f"3.3 L turbo inline-6 mild hybrid · 8-speed · i-Activ AWD · {hp} hp · 3 rows", MI4, eng="v6", tq=tq, gears=G8M, tank=74, mpg=25, cda=1.02, rwdBias=True)
for k, t, p in (("phpref", "PHEV Preferred", 50850), ("phpp", "PHEV Premium Plus", 58300)):
    car("mz_cx90_" + k, *c90, f"2026 Mazda CX-90 {t}", f"CX-90 {t}", "phev", 323, 2330, "awd", p, "2.5 L PHEV · 8-speed · i-Activ AWD · 323 hp · 26 mi EV · 3 rows", [N, S, O, TW, EVM], tank=57, mpg=25, kWh=17.8, evMi=26, cda=1.02, eng="i4h")
# ---------------- Volkswagen
DM = [E, N, CM, SP, IN]
AWDM = [E, N, CM, SP, IN, SN, OR]
jt = ("vw_jetta", "Volkswagen Jetta · 2026")
car("vw_jetta_s", *jt, "2026 Volkswagen Jetta S", "Jetta S", "ice", 158, 1340, "fwd", 23395, "1.5 L turbo · 8-speed · FWD · 158 hp", [E, N, SP], eng="i4t", tq=184, gears=G8, tank=50, mpg=34, cda=0.64)
car("vw_jetta_sport", *jt, "2026 Volkswagen Jetta Sport", "Jetta Sport", "ice", 158, 1350, "fwd", 24995, "1.5 L turbo · 8-speed · FWD · 158 hp", [E, N, SP], eng="i4t", tq=184, gears=G8, tank=50, mpg=34, cda=0.64)
car("vw_jetta_se", *jt, "2026 Volkswagen Jetta SE", "Jetta SE", "ice", 158, 1355, "fwd", 26595, "1.5 L turbo · 8-speed · FWD · 158 hp", [E, N, SP, IN], eng="i4t", tq=184, gears=G8, tank=50, mpg=34, cda=0.64)
car("vw_jetta_sel", *jt, "2026 Volkswagen Jetta SEL", "Jetta SEL", "ice", 158, 1370, "fwd", 30995, "1.5 L turbo · 8-speed · FWD · 158 hp", DM, eng="i4t", tq=184, gears=G8, tank=50, mpg=33, cda=0.64)
car("vw_jetta_gli", *jt, "2026 Volkswagen Jetta GLI Autobahn", "Jetta GLI Autobahn", "ice", 228, 1450, "fwd", 33995, "2.0 L turbo · 7-speed DSG · FWD · 228 hp", DM, eng="i4t", tq=258, gears=G7D, tank=50, mpg=29, cda=0.64)
ta = ("vw_taos", "Volkswagen Taos · 2026")
car("vw_taos_s", *ta, "2026 Volkswagen Taos S", "Taos S", "ice", 174, 1440, "fwd", 25995, "1.5 L turbo · 8-speed · FWD · 174 hp", [E, N, SP], eng="i4t", tq=184, gears=G8, tank=50, mpg=31, cda=0.82)
car("vw_taos_se", *ta, "2026 Volkswagen Taos SE 4MOTION", "Taos SE 4MOTION", "ice", 174, 1530, "awd", 31495, "1.5 L turbo · 7-speed DSG · 4MOTION AWD · 174 hp", AWDM, eng="i4t", tq=184, gears=G7D, tank=50, mpg=28, cda=0.82)
car("vw_taos_sel", *ta, "2026 Volkswagen Taos SEL 4MOTION", "Taos SEL 4MOTION", "ice", 174, 1550, "awd", 36495, "1.5 L turbo · 7-speed DSG · 4MOTION AWD · 174 hp", AWDM, eng="i4t", tq=184, gears=G7D, tank=50, mpg=28, cda=0.82)
tg = ("vw_tiguan", "Volkswagen Tiguan · 2026")
car("vw_tiguan_s", *tg, "2026 Volkswagen Tiguan S", "Tiguan S", "ice", 201, 1640, "fwd", 30995, "2.0 L turbo · 8-speed · FWD · 201 hp", [E, CM, SP, IN], eng="i4t", tq=221, gears=G8, tank=58, mpg=28, cda=0.84)
car("vw_tiguan_se", *tg, "2026 Volkswagen Tiguan SE 4MOTION", "Tiguan SE 4MOTION", "ice", 201, 1720, "awd", 34995, "2.0 L turbo · 8-speed · 4MOTION AWD · 201 hp", AWDM, eng="i4t", tq=221, gears=G8, tank=58, mpg=26, cda=0.84)
car("vw_tiguan_selr", *tg, "2026 Volkswagen Tiguan SEL R-Line Turbo 4MOTION", "Tiguan SEL R-Line Turbo", "ice", 268, 1760, "awd", 42995, "2.0 L turbo · 8-speed · 4MOTION AWD · 268 hp", AWDM, eng="i4t", tq=258, gears=G8, tank=58, mpg=24, cda=0.84)
at = ("vw_atlas", "Volkswagen Atlas · 2027")
for k, t, p in (("se", "SE 4MOTION", 39995), ("set", "SE with Technology 4MOTION", 44995), ("peak", "Peak Edition SE with Technology", 48495), ("sel", "SEL 4MOTION", 50495), ("selp", "SEL Premium R-Line 4MOTION", 55495)):
    car("vw_atlas_" + k, *at, f"2027 Volkswagen Atlas {t}", f"Atlas {t.replace(' 4MOTION', '')}", "ice", 269, 2050, "awd", p, "2.0 L turbo · 8-speed · 4MOTION AWD · 269 hp · 3 rows (est.)", AWDM, eng="i4t", tq=273, gears=G8, tank=70, mpg=22, cda=1.02)
acs = ("vw_atlas_cs", "Volkswagen Atlas Cross Sport · 2026")
for k, t, p in (("se", "SE 4MOTION", 38995), ("set", "SE with Technology 4MOTION", 43495), ("sel", "SEL 4MOTION", 48495), ("selr", "SEL R-Line 4MOTION", 50995), ("selp", "SEL Premium R-Line 4MOTION", 53995)):
    car("vw_atlas_cs_" + k, *acs, f"2026 Volkswagen Atlas Cross Sport {t}", f"Atlas Cross Sport {t.replace(' 4MOTION', '')}", "ice", 269, 1980, "awd", p, "2.0 L turbo · 8-speed · 4MOTION AWD · 269 hp", AWDM, eng="i4t", tq=273, gears=G8, tank=70, mpg=23, cda=0.98)
ID = [E, CM, SP, ("Custom", "custom")]
IDA = ID + [("Traction", "snow")]
i4 = ("vw_id4", "Volkswagen ID.4 · 2026")
car("vw_id4_pro", *i4, "2026 Volkswagen ID.4 Pro", "ID.4 Pro", "ev", 282, 2140, "rwd", 45095, "Single motor · RWD · 282 hp · 82 kWh · 291 mi", ID, kWh=82, rng=291, cda=0.62)
car("vw_id4_pros", *i4, "2026 Volkswagen ID.4 Pro S", "ID.4 Pro S", "ev", 282, 2160, "rwd", 48995, "Single motor · RWD · 282 hp · 82 kWh · 291 mi", ID, kWh=82, rng=291, cda=0.62)
car("vw_id4_prosa", *i4, "2026 Volkswagen ID.4 Pro S AWD", "ID.4 Pro S AWD", "ev", 335, 2250, "awd", 52995, "Dual motor · AWD · 335 hp · 82 kWh · 263 mi", IDA, kWh=82, rng=263, cda=0.62)
car("vw_id4_prospa", *i4, "2026 Volkswagen ID.4 Pro S Plus AWD", "ID.4 Pro S Plus AWD", "ev", 335, 2270, "awd", 56595, "Dual motor · AWD · 335 hp · 82 kWh · 263 mi", IDA, kWh=82, rng=263, cda=0.62)
ib = ("vw_idbuzz", "Volkswagen ID. Buzz · 2025")
car("vw_idbuzz_pros", *ib, "2025 Volkswagen ID. Buzz Pro S", "ID. Buzz Pro S", "ev", 282, 2690, "rwd", 59995, "Single motor · RWD · 282 hp · 86 kWh · 234 mi · 3 rows", ID, kWh=86, rng=234, cda=0.95)
car("vw_idbuzz_prospa", *ib, "2025 Volkswagen ID. Buzz Pro S Plus 4MOTION", "ID. Buzz Pro S Plus 4MOTION", "ev", 335, 2790, "awd", 67995, "Dual motor · 4MOTION AWD · 335 hp · 86 kWh · 231 mi · 3 rows", IDA, kWh=86, rng=231, cda=0.95)
car("vw_idbuzz_1st", *ib, "2025 Volkswagen ID. Buzz 1st Edition 4MOTION", "ID. Buzz 1st Edition", "ev", 335, 2790, "awd", 69995, "Dual motor · 4MOTION AWD · 335 hp · 86 kWh · 231 mi · two-tone paint", IDA, kWh=86, rng=231, cda=0.95)
# ---------------- Toyota RAV4 2026 (all hybrid)
rv = ("toy_rav4_26", "Toyota RAV4 · 2026")
RH = [E, N, SP]; RHA = [E, N, SP, TR, SN]
for k, t, p, d, hp in (("le", "LE", 31900, "fwd", 226), ("xle", "XLE AWD", 34900, "awd", 236), ("xlep", "XLE Premium AWD", 37400, "awd", 236), ("wood", "Woodland AWD", 39400, "awd", 236), ("se", "SE AWD", 38400, "awd", 236), ("lim", "Limited AWD", 43500, "awd", 236), ("gr", "GR Sport AWD", 45500, "awd", 236)):
    car("toy_rav4_26_" + k, *rv, f"2026 Toyota RAV4 Hybrid {t}", f"RAV4 {t.replace(' AWD', '')}", "hev", hp, 1680 if d == "fwd" else 1750, d, p, f"2.5 L hybrid · eCVT · {'AWD' if d == 'awd' else 'FWD'} · {hp} hp", (RHA if d == "awd" else RH) + [EVM], tank=55, mpg=44 if d == "fwd" else 43, cda=0.86, eng="i4h")
for k, t, p in (("phse", "SE Plug-in Hybrid", 43400), ("phxse", "XSE Plug-in Hybrid", 47900), ("phgr", "GR Sport Plug-in Hybrid", 50400)):
    car("toy_rav4_26_" + k, *rv, f"2026 Toyota RAV4 {t}", f"RAV4 {t.replace('Plug-in Hybrid', 'PHEV')}", "phev", 320, 1950, "awd", p, "2.5 L PHEV · eCVT · AWD · 320 hp · about 50 mi EV", RHA + [EVM], tank=55, mpg=40, kWh=22.7, evMi=50, cda=0.86, eng="i4h")

NO_ICE = ["autoLC", "autopark", "avas", "cornering", "crab", "esa", "leveling", "matrix", "regen", "tech", "ws4"]
NO_EV = ["autoLC", "autoSS", "autopark", "cornering", "crab", "esa", "leveling", "matrix", "tech", "ws4"]
NO_HEV = ["autoLC", "autoSS", "autopark", "cornering", "crab", "esa", "leveling", "matrix", "rAeb", "tech", "ws4"]
DESC = {"normal": "Default balance of response, comfort and efficiency.", "sport": "Sharper throttle, firmer steering and later shifts.", "eco": "Softer throttle and earlier shifts or gentler motor response to save energy.",
        "comfort": "Softer steering and a relaxed throttle for a smooth ride.", "custom": "Your own mix of engine, steering and suspension settings.", "snow": "Gentle starts and early upshifts for slippery roads.",
        "offroad": "Lets the wheels spin a little and sends power to the wheels with grip for dirt, mud and snow.", "tow": "Holds gears longer and steadies the car with a trailer behind.",
        "trail": "Brakes a spinning wheel so the others pull you out of ruts and over rocks.", "ev": "Drives on the battery alone at low speed."}
out = []; dm = {}
for c in C:
    brand = c["group"].split(" ")[0]
    std, pn, ps = BR[brand]
    kW = round(c["hp"] * 0.7457); kind = c["kind"]; drv = c["drv"]
    fb = {"fwd": [1, 0], "rwd": [0, 1], "awd": [0.35, 0.65] if c.get("rwdBias") else [0.6, 0.4]}[drv]
    names = [m[0] for m in c["modes"] if m[1] != "ev"]
    T = {"cda": c["cda"], "ws4": False, "crab": False, "tv": False, "height": False, "modes": len(names), "real": True, "model": c["model"], "group": c["group"],
         "name": c["name"], "short": c["short"], "desc": c["desc"], "mass": c["kg"], "kW": kW, "paint": PAINT[brand], "fwd": 0.56 if drv != "rwd" else 0.5, "modeNames": names,
         "pilotName": pn, "pilotShort": ps, "handsOn": True, "odo0": 20, "std": std, "feat": c["desc"].split(" · ")[0] + ", " + str(c["hp"]) + " hp"}
    if kind == "ice":
        T.update(ice=True, tank=c["tank"], mpg=c["mpg"]); no = NO_ICE
        g = c["gears"]
        D = {"layout": "ice", "eng": c["eng"], "turbo": "turbo" in c["desc"], "Tpk": round(c["tq"] * 1.356), "Ppk": kW * 1000,
             "red": 6500 if c["eng"] in ("i4h", "i4t") else 6200, "idle": 700, "gears": g, "fd": 3.6 if len(g) <= 6 else 3.2, "rev": 3.4, "bias": fb, "Tna": round(c["tq"] * 1.356 * 0.72)}
    else:
        mT = c["kg"] * (3.0 if kind == "ev" else 2.0)
        P = kW * 1000
        D = {"layout": "axle", "T": [round(mT * fb[0]), round(mT * fb[1])], "P": [round(P * fb[0]), round(P * fb[1])]}
        if kind == "ev":
            T.update(kWh=c["kWh"], regenMax=3); T["feat"] = f"about {c['rng']} mi"; no = NO_EV
        else:
            T.update(hybrid=True, sound=c.get("eng", "i4h"), evBtn=True, regenMax=2, tank=c["tank"], mpg=c["mpg"]); no = NO_HEV
            if kind == "phev": T.update(phev=True, kWh=c["kWh"], evMi=c["evMi"]); T["feat"] = f"{c['evMi']} mi EV"
    out.append(f' add({json.dumps(c["key"])},{{...{json.dumps(T, separators=(",", ":"))},no:{json.dumps(no)}}},{json.dumps(D, separators=(", ", ": "))},{c["price"]});')
    e = {"m": [[n, k, DESC[k]] for n, k in c["modes"] if k != "ev"]}
    if any(k == "ev" for n, k in c["modes"]): e["ev"] = {"btn": "EV", "modes": [["hyb", "Auto EV/HV"], ["ev", "EV Mode"], ["save", "HV Mode"]] if kind == "phev" else [["ev", "EV Mode"]]}
    dm[c["key"]] = e
if __name__ == "__main__":
    open(sys.argv[1], "w").write("\n".join(out) + "\n")
    open(sys.argv[2], "w").write("Object.assign(DMODES," + json.dumps(dm, separators=(",", ":")) + ");   // v106: Mazda Mi-Drive, VW Driving Mode Selection / 4MOTION Active Control, RAV4 Drive Mode, real lists\n")
    print(len(out), "trims;", len({c['model'] for c in C}), "models")
