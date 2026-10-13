"""Trims for the Oct 2026 model packs: Hyundai (13), BMW + Mercedes-Benz SUVs (24), Cadillac (12, the XT5 file was cut off in the upload).
One representative trim per model file. Specs are the US models as of mid-2026 (manufacturer sites / press releases);
2027 models not yet rated by the EPA are marked est. Prints the add(...) lines for src/app_template.html."""
import json, sys

# key, model, group, name, short, kind, hp, kg, drive (fwd/rwd/awd), mpg/kWh..., price, extra
# kind: ice / hev / phev / ev
H = "Hyundai SmartSense: Forward Collision-Avoidance Assist, Lane Keeping Assist, Lane Following Assist, Blind-Spot Collision-Avoidance Assist, Rear Cross-Traffic Collision-Avoidance Assist, Smart Cruise Control with Stop & Go, Highway Driving Assist."
BM = "BMW Active Driving Assistant: Frontal Collision Warning with City Collision Mitigation, Lane Departure Warning, Blind Spot Detection, Rear Cross-Traffic Alert, Active Cruise Control with Stop & Go; Driving Assistant Professional optional."
MB = "Mercedes-Benz Driver Assistance: Active Brake Assist, Active Lane Keeping Assist, Blind Spot Assist, Active Distance Assist DISTRONIC, Active Steering Assist (Driver Assistance Package)."
CD = "Cadillac Safety: Automatic Emergency Braking, Front Pedestrian and Cyclist Braking, Lane Keep Assist, Side Blind Zone Alert, Rear Cross Traffic Braking, Adaptive Cruise Control; Super Cruise hands-free driving."
BR = {"Hyundai": (H, "Highway Driving Assist", "HDA", False), "BMW": (BM, "Driving Assistant Professional", "DAP", False),
      "Mercedes-Benz": (MB, "Active Distance Assist DISTRONIC", "DISTRONIC", False), "Cadillac": (CD, "Super Cruise", "SC", True)}
G8 = [4.71, 3.14, 2.10, 1.67, 1.29, 1.00, 0.84, 0.67]          # ZF 8HP (BMW)
G9 = [5.35, 3.24, 2.25, 1.64, 1.21, 1.00, 0.86, 0.72, 0.60]    # 9G-TRONIC
G8H = [4.81, 2.90, 1.86, 1.42, 1.00, 0.77, 0.63, 0.56]          # Hyundai 8-speed
G7 = [3.70, 2.38, 1.43, 1.0, 0.84, 0.65, 0.54]                  # 7/8-speed DCT (approx.)
G10 = [4.70, 2.99, 2.15, 1.80, 1.52, 1.28, 1.00, 0.85, 0.69, 0.64]
CV = [2.6]
C = []
def car(key, model, group, name, short, kind, hp, kg, drv, price, desc, **x):
    C.append(dict(key=key, model=model, group=group, name=name, short=short, kind=kind, hp=hp, kg=kg, drv=drv, price=price, desc=desc, **x))

# ---------------- Hyundai
car("hy_venue_sel", "hy_venue", "Hyundai Venue · 2026", "2026 Hyundai Venue SEL", "Venue SEL", "ice", 121, 1230, "fwd", 22350, "1.6 L · IVT · FWD · 121 hp", eng="i4h", tq=151, gears=CV, cvt=True, tank=45, mpg=31, cda=0.85)
car("hy_kona_sel", "hy_kona", "Hyundai Kona · 2026", "2026 Hyundai Kona SEL", "Kona SEL", "ice", 147, 1390, "fwd", 26550, "2.0 L · IVT · FWD · 147 hp", eng="i4h", tq=179, gears=CV, cvt=True, tank=50, mpg=30, cda=0.88)
car("hy_kona_ev_sel", "hy_kona_ev", "Hyundai Kona Electric · 2025", "2025 Hyundai Kona Electric SEL", "Kona Electric SEL", "ev", 201, 1750, "fwd", 37250, "Single motor · FWD · 201 hp · 64.8 kWh · 261 mi", kWh=64.8, rng=261, cda=0.8)
car("hy_tucson_sel", "hy_tucson", "Hyundai Tucson · 2026", "2026 Hyundai Tucson SEL AWD", "Tucson SEL", "ice", 187, 1640, "awd", 32750, "2.5 L · 8-speed · HTRAC AWD · 187 hp", eng="i4h", tq=241, gears=G8H, tank=54, mpg=25, cda=0.95)
car("hy_tucson_hev_sel", "hy_tucson_hev", "Hyundai Tucson · 2026", "2026 Hyundai Tucson Hybrid SEL Convenience", "Tucson Hybrid SEL", "hev", 231, 1750, "awd", 35350, "1.6 L turbo hybrid · 6-speed · HTRAC AWD · 231 hp", tank=52, mpg=37, cda=0.95, eng="i4t")
car("hy_tucson_phev_sel", "hy_tucson_phev", "Hyundai Tucson · 2026", "2026 Hyundai Tucson Plug-in Hybrid SEL", "Tucson PHEV SEL", "phev", 268, 1925, "awd", 39350, "1.6 L turbo PHEV · 6-speed · HTRAC AWD · 268 hp · 33 mi EV", tank=42, mpg=35, kWh=13.8, evMi=33, cda=0.95, eng="i4t")
car("hy_santafe_sel", "hy_santafe", "Hyundai Santa Fe · 2026", "2026 Hyundai Santa Fe SEL AWD", "Santa Fe SEL", "ice", 277, 1900, "awd", 38200, "2.5 L turbo · 8-speed DCT · HTRAC AWD · 277 hp", eng="i4t", tq=422, gears=G8H, tank=67, mpg=22, cda=1.0)
car("hy_santafe_hev_sel", "hy_santafe_hev", "Hyundai Santa Fe · 2026", "2026 Hyundai Santa Fe Hybrid SEL", "Santa Fe Hybrid SEL", "hev", 231, 1960, "awd", 39900, "1.6 L turbo hybrid · 6-speed · HTRAC AWD · 231 hp", tank=67, mpg=34, cda=1.0, eng="i4t")
car("hy_palisade_sel", "hy_palisade", "Hyundai Palisade · 2026", "2026 Hyundai Palisade SEL AWD", "Palisade SEL", "ice", 287, 2100, "awd", 44400, "3.5 L V6 · 8-speed · HTRAC AWD · 287 hp", eng="v6", tq=352, gears=G8H, tank=71, mpg=21, cda=1.1)
car("hy_palisade_hev_sel", "hy_palisade_hev", "Hyundai Palisade · 2026", "2026 Hyundai Palisade Hybrid SEL Premium", "Palisade Hybrid", "hev", 329, 2210, "awd", 51400, "2.5 L turbo hybrid · 6-speed · HTRAC AWD · 329 hp", tank=71, mpg=34, cda=1.1, eng="i4t")
car("hy_santacruz_sel", "hy_santacruz", "Hyundai Santa Cruz · 2026", "2026 Hyundai Santa Cruz SEL AWD", "Santa Cruz SEL", "ice", 191, 1750, "awd", 34000, "2.5 L · 8-speed · HTRAC AWD · 191 hp", eng="i4h", tq=245, gears=G8H, tank=66, mpg=22, cda=1.05)
car("hy_ioniq5_sel", "hy_ioniq5", "Hyundai IONIQ 5 · 2026", "2026 Hyundai IONIQ 5 SEL RWD", "IONIQ 5 SEL", "ev", 225, 2000, "rwd", 45750, "Single motor · RWD · 225 hp · 84 kWh · 318 mi", kWh=84, rng=318, cda=0.7)
car("hy_ioniq9_sel", "hy_ioniq9", "Hyundai IONIQ 9 · 2026", "2026 Hyundai IONIQ 9 SEL AWD", "IONIQ 9 SEL", "ev", 303, 2600, "awd", 63400, "Dual motor · AWD · 303 hp · 110.3 kWh · 320 mi", kWh=110.3, rng=320, cda=0.85)
# ---------------- BMW
car("bmw_x1_28i", "bmw_x1", "BMW X1 · 2026", "2026 BMW X1 xDrive28i", "X1 xDrive28i", "ice", 241, 1710, "awd", 43200, "2.0 L turbo · 7-speed DCT · xDrive · 241 hp", eng="i4t", tq=400, gears=G7, tank=54, mpg=28, cda=0.82)
car("bmw_x2_28i", "bmw_x2", "BMW X2 · 2026", "2026 BMW X2 xDrive28i", "X2 xDrive28i", "ice", 241, 1720, "awd", 44700, "2.0 L turbo · 7-speed DCT · xDrive · 241 hp", eng="i4t", tq=400, gears=G7, tank=54, mpg=28, cda=0.78)
car("bmw_x3_30", "bmw_x3", "BMW X3 · 2026", "2026 BMW X3 30 xDrive", "X3 30 xDrive", "ice", 255, 1880, "awd", 51200, "2.0 L turbo mild hybrid · 8-speed · xDrive · 255 hp", eng="i4t", tq=400, gears=G8, tank=65, mpg=27, cda=0.88)
car("bmw_x5_40i", "bmw_x5", "BMW X5 · 2025", "2025 BMW X5 xDrive40i", "X5 xDrive40i", "ice", 375, 2200, "awd", 67600, "3.0 L turbo I6 mild hybrid · 8-speed · xDrive · 375 hp", eng="v6", tq=540, gears=G8, tank=83, mpg=23, cda=1.0)
car("bmw_x5_50e", "bmw_x5_50e", "BMW X5 · 2025", "2025 BMW X5 xDrive50e", "X5 xDrive50e", "phev", 483, 2550, "awd", 74100, "3.0 L turbo I6 PHEV · 8-speed · xDrive · 483 hp · 39 mi EV", tank=69, mpg=27, kWh=25.7, evMi=39, cda=1.0, eng="v6")
car("bmw_x6_40i", "bmw_x6", "BMW X6 · 2026", "2026 BMW X6 xDrive40i", "X6 xDrive40i", "ice", 375, 2180, "awd", 76500, "3.0 L turbo I6 mild hybrid · 8-speed · xDrive · 375 hp", eng="v6", tq=540, gears=G8, tank=83, mpg=22, cda=0.95)
car("bmw_x7_40i", "bmw_x7", "BMW X7 · 2026", "2026 BMW X7 xDrive40i", "X7 xDrive40i", "ice", 375, 2450, "awd", 84500, "3.0 L turbo I6 mild hybrid · 8-speed · xDrive · 375 hp", eng="v6", tq=540, gears=G8, tank=83, mpg=21, cda=1.1)
car("bmw_ix3_50", "bmw_ix3", "BMW iX3 · 2027", "2027 BMW iX3 50 xDrive", "iX3 50 xDrive", "ev", 463, 2360, "awd", 60000, "Dual motor · xDrive · 463 hp · 108.7 kWh · about 400 mi (est.)", kWh=108.7, rng=400, cda=0.75)
# ---------------- Mercedes-Benz
car("mb_gla_250", "mb_gla", "Mercedes-Benz GLA · 2026", "2026 Mercedes-Benz GLA 250 4MATIC", "GLA 250 4MATIC", "ice", 221, 1650, "awd", 46200, "2.0 L turbo · 8-speed DCT · 4MATIC · 221 hp", eng="i4t", tq=350, gears=G7, tank=51, mpg=27, cda=0.82)
car("mb_glb_250", "mb_glb", "Mercedes-Benz GLB · 2026", "2026 Mercedes-Benz GLB 250 4MATIC", "GLB 250 4MATIC", "ice", 221, 1750, "awd", 48300, "2.0 L turbo · 8-speed DCT · 4MATIC · 221 hp", eng="i4t", tq=350, gears=G7, tank=60, mpg=25, cda=0.9)
car("mb_glc_300", "mb_glc", "Mercedes-Benz GLC · 2026", "2026 Mercedes-Benz GLC 300 4MATIC", "GLC 300 4MATIC", "ice", 255, 1900, "awd", 53100, "2.0 L turbo mild hybrid · 9-speed · 4MATIC · 255 hp", eng="i4t", tq=400, gears=G9, tank=62, mpg=26, cda=0.88)
car("mb_glc_350e", "mb_glc350e", "Mercedes-Benz GLC · 2026", "2026 Mercedes-Benz GLC 350e 4MATIC", "GLC 350e 4MATIC", "phev", 313, 2250, "awd", 60500, "2.0 L turbo PHEV · 9-speed · 4MATIC · 313 hp · 54 mi EV", tank=50, mpg=26, kWh=23.3, evMi=54, cda=0.88, eng="i4t")
car("mb_glc_coupe_300", "mb_glc_coupe", "Mercedes-Benz GLC Coupe · 2026", "2026 Mercedes-Benz GLC 300 4MATIC Coupe", "GLC 300 Coupe", "ice", 255, 1920, "awd", 61000, "2.0 L turbo mild hybrid · 9-speed · 4MATIC · 255 hp", eng="i4t", tq=400, gears=G9, tank=62, mpg=25, cda=0.84)
car("mb_glc_ev_400", "mb_glc_ev", "Mercedes-Benz GLC with EQ Technology · 2027", "2027 Mercedes-Benz GLC 400 4MATIC with EQ Technology", "GLC 400 4MATIC EQ", "ev", 483, 2450, "awd", 65000, "Dual motor · 4MATIC · 483 hp · 94 kWh · about 300 mi (est.)", kWh=94, rng=300, cda=0.75)
car("mb_gle_450", "mb_gle", "Mercedes-Benz GLE · 2026", "2026 Mercedes-Benz GLE 450 4MATIC", "GLE 450 4MATIC", "ice", 375, 2250, "awd", 72950, "3.0 L turbo I6 mild hybrid · 9-speed · 4MATIC · 375 hp", eng="v6", tq=500, gears=G9, tank=85, mpg=22, cda=1.0)
car("mb_gle_coupe_450", "mb_gle_coupe", "Mercedes-Benz GLE Coupe · 2026", "2026 Mercedes-Benz GLE 450 4MATIC Coupe", "GLE 450 Coupe", "ice", 375, 2300, "awd", 83500, "3.0 L turbo I6 mild hybrid · 9-speed · 4MATIC · 375 hp", eng="v6", tq=500, gears=G9, tank=85, mpg=21, cda=0.95)
car("mb_gls_450", "mb_gls", "Mercedes-Benz GLS · 2026", "2026 Mercedes-Benz GLS 450 4MATIC", "GLS 450 4MATIC", "ice", 375, 2550, "awd", 91100, "3.0 L turbo I6 mild hybrid · 9-speed · 4MATIC · 375 hp", eng="v6", tq=500, gears=G9, tank=90, mpg=20, cda=1.1)
car("mb_g550", "mb_g550", "Mercedes-Benz G-Class · 2026", "2026 Mercedes-Benz G 550", "G 550", "ice", 443, 2560, "awd", 149000, "3.0 L turbo I6 mild hybrid · 9-speed · 4MATIC · 443 hp", eng="v6", tq=560, gears=G9, tank=100, mpg=15, cda=1.5)
car("mb_g580", "mb_g580", "Mercedes-Benz G-Class · 2026", "2026 Mercedes-Benz G 580 with EQ Technology", "G 580 EQ", "ev", 579, 3085, "awd", 163000, "Four motors · 4MATIC · 579 hp · 116 kWh · 239 mi", kWh=116, rng=239, cda=1.5)
car("mb_eqb_300", "mb_eqb", "Mercedes-Benz EQB · 2025", "2025 Mercedes-Benz EQB 300 4MATIC", "EQB 300 4MATIC", "ev", 228, 2200, "awd", 56750, "Dual motor · 4MATIC · 228 hp · 70.5 kWh · 227 mi", kWh=70.5, rng=227, cda=0.85)
car("mb_eqe_suv_350", "mb_eqe_suv", "Mercedes-Benz EQE SUV · 2026", "2026 Mercedes-Benz EQE 350 4MATIC SUV", "EQE 350 SUV", "ev", 288, 2600, "awd", 80000, "Dual motor · 4MATIC · 288 hp · 90.6 kWh · 253 mi", kWh=90.6, rng=253, cda=0.75)
car("mb_eqs_suv_450", "mb_eqs_suv", "Mercedes-Benz EQS SUV · 2026", "2026 Mercedes-Benz EQS 450 4MATIC SUV", "EQS 450 SUV", "ev", 355, 2800, "awd", 106400, "Dual motor · 4MATIC · 355 hp · 108.4 kWh · 285 mi", kWh=108.4, rng=285, cda=0.75)
car("mb_maybach_gls_600", "mb_maybach_gls", "Mercedes-Maybach GLS · 2026", "2026 Mercedes-Maybach GLS 600 4MATIC", "Maybach GLS 600", "ice", 550, 2800, "awd", 180000, "4.0 L twin-turbo V8 mild hybrid · 9-speed · 4MATIC · 550 hp", eng="v8", tq=730, gears=G9, tank=90, mpg=15, cda=1.1)
car("mb_maybach_eqs_680", "mb_maybach_eqs", "Mercedes-Maybach EQS SUV · 2026", "2026 Mercedes-Maybach EQS 680 SUV", "Maybach EQS 680", "ev", 649, 2950, "awd", 182000, "Dual motor · 4MATIC · 649 hp · 108.4 kWh · about 280 mi", kWh=108.4, rng=280, cda=0.78)
# ---------------- Cadillac (XT5 missing: the upload was cut off)
car("cad_ct4_pl", "cad_ct4", "Cadillac CT4 · 2026", "2026 Cadillac CT4 Premium Luxury", "CT4 Premium Lux", "ice", 237, 1600, "rwd", 39000, "2.0 L turbo · 8-speed · RWD · 237 hp", eng="i4t", tq=350, gears=G8, tank=61, mpg=26, cda=0.66)
car("cad_ct4_v", "cad_ct4v", "Cadillac CT4 · 2026", "2026 Cadillac CT4-V", "CT4-V", "ice", 325, 1660, "rwd", 49000, "2.7 L turbo · 10-speed · RWD · 325 hp", eng="i4t", tq=515, gears=G10, tank=61, mpg=24, cda=0.66)
car("cad_ct4_bw", "cad_ct4bw", "Cadillac CT4 · 2026", "2026 Cadillac CT4-V Blackwing", "CT4-V Blackwing", "ice", 472, 1715, "rwd", 64000, "3.6 L twin-turbo V6 · 10-speed · RWD · 472 hp", eng="v6", tq=603, gears=G10, tank=61, mpg=18, cda=0.68, modes=["Tour", "Sport", "Track", "Snow/Ice", "My Mode", "V-Mode"])
car("cad_ct5_pl", "cad_ct5", "Cadillac CT5 · 2026", "2026 Cadillac CT5 Premium Luxury", "CT5 Premium Lux", "ice", 237, 1660, "rwd", 43000, "2.0 L turbo · 10-speed · RWD · 237 hp", eng="i4t", tq=350, gears=G10, tank=66, mpg=26, cda=0.66)
car("cad_ct5_v", "cad_ct5v", "Cadillac CT5 · 2026", "2026 Cadillac CT5-V", "CT5-V", "ice", 360, 1780, "rwd", 52000, "3.0 L twin-turbo V6 · 10-speed · RWD · 360 hp", eng="v6", tq=549, gears=G10, tank=66, mpg=21, cda=0.66)
car("cad_ct5_bw", "cad_ct5bw", "Cadillac CT5 · 2026", "2026 Cadillac CT5-V Blackwing", "CT5-V Blackwing", "ice", 668, 1890, "rwd", 96000, "6.2 L supercharged V8 · 10-speed · RWD · 668 hp", eng="v8", tq=893, gears=G10, tank=66, mpg=15, cda=0.7, modes=["Tour", "Sport", "Track", "Snow/Ice", "My Mode", "V-Mode"])
car("cad_lyriq_lux", "cad_lyriq", "Cadillac LYRIQ · 2027", "2027 Cadillac LYRIQ Luxury RWD", "LYRIQ Luxury", "ev", 365, 2550, "rwd", 59000, "Single motor · RWD · 365 hp · 102 kWh · 326 mi", kWh=102, rng=326, cda=0.75)
car("cad_lyriq_v", "cad_lyriqv", "Cadillac LYRIQ · 2027", "2027 Cadillac LYRIQ-V", "LYRIQ-V", "ev", 615, 2700, "awd", 80000, "Dual motor · AWD · 615 hp · 102 kWh · 285 mi", kWh=102, rng=285, cda=0.75)
car("cad_optiq_lux", "cad_optiq", "Cadillac OPTIQ · 2027", "2027 Cadillac OPTIQ Luxury AWD", "OPTIQ Luxury", "ev", 300, 2350, "awd", 54000, "Dual motor · AWD · 300 hp · 85 kWh · 302 mi", kWh=85, rng=302, cda=0.78)
car("cad_optiq_v", "cad_optiqv", "Cadillac OPTIQ · 2027", "2027 Cadillac OPTIQ-V", "OPTIQ-V", "ev", 519, 2450, "awd", 70000, "Dual motor · AWD · 519 hp · 85 kWh · about 280 mi (est.)", kWh=85, rng=280, cda=0.78)
car("cad_vistiq_lux", "cad_vistiq", "Cadillac VISTIQ · 2027", "2027 Cadillac VISTIQ Luxury", "VISTIQ Luxury", "ev", 615, 2800, "awd", 79000, "Dual motor · AWD · 615 hp · 102 kWh · 305 mi", kWh=102, rng=305, cda=0.85)
car("cad_celestiq", "cad_celestiq", "Cadillac CELESTIQ · 2026", "2026 Cadillac CELESTIQ", "CELESTIQ", "ev", 600, 3100, "awd", 340000, "Dual motor · AWD · 600 hp · 111 kWh · 303 mi", kWh=111, rng=303, cda=0.7)

NO_ICE = ["autoLC", "autopark", "avas", "cornering", "crab", "esa", "leveling", "matrix", "regen", "tech", "ws4"]
NO_EV = ["autoLC", "autoSS", "autopark", "cornering", "crab", "esa", "leveling", "matrix", "tech", "ws4"]
NO_HEV = ["autoLC", "autoSS", "autopark", "cornering", "crab", "esa", "leveling", "matrix", "rAeb", "tech", "ws4"]
PAINT = {"Hyundai": "c:#5b6066", "BMW": "c:#1c2a44", "Mercedes-Benz": "c:#b9bcbf", "Cadillac": "c:#121314"}
out = []
for c in C:
    brand = c["group"].split(" ")[0] if not c["group"].startswith("Mercedes-Maybach") else "Mercedes-Benz"
    std, pn, ps, sc = BR[brand]
    kW = round(c["hp"] * 0.7457); kind = c["kind"]; drv = c["drv"]
    fb = {"fwd": [1, 0], "rwd": [0, 1], "awd": [0.6, 0.4] if brand != "BMW" and brand != "Mercedes-Benz" else [0.4, 0.6]}[drv]
    modes = c.get("modes") or (["Eco", "Normal", "Sport"] if brand == "Hyundai" else ["Eco Pro", "Comfort", "Sport"] if brand == "BMW" else ["Eco", "Comfort", "Sport"] if brand == "Mercedes-Benz" else ["Tour", "Sport", "Snow/Ice"])
    T = {"cda": c["cda"], "ws4": False, "crab": False, "tv": False, "height": False, "modes": len(modes), "real": True, "model": c["model"], "group": c["group"].replace("Mercedes-Maybach", "Mercedes-Benz Maybach") if False else c["group"],
         "name": c["name"], "short": c["short"], "desc": c["desc"], "mass": c["kg"], "kW": kW, "paint": PAINT[brand], "fwd": 0.56 if drv != "rwd" else 0.5, "modeNames": modes,
         "pilotName": pn, "pilotShort": ps, "handsOn": not sc, "odo0": 20, "std": std, "feat": c["desc"].split(" · ")[0] + ", " + str(c["hp"]) + " hp"}
    if sc: T["pilotHwy"] = True
    if kind == "ice":
        T.update(ice=True, tank=c["tank"], mpg=c["mpg"]); no = NO_ICE
        cv = c.get("cvt", False); g = c["gears"]
        D = {"layout": "ice", "eng": c["eng"], "turbo": c["eng"] in ("i4t", "v6", "v8") and "turbo" in c["desc"] or "supercharged" in c["desc"], "Tpk": c["tq"], "Ppk": kW * 1000,
             "red": 6500 if c["eng"] in ("i4h", "i4t") else 6200, "idle": 700, "gears": g, "fd": 3.2 if not cv else 4.0, "rev": 3.4, "bias": fb, "Tna": round(c["tq"] * 0.72)}
        if cv: D.update(cvt=True, rmin=0.4, rmax=2.6)
    else:
        mT = c["kg"] * (3.0 if kind == "ev" else 2.0)
        P = kW * 1000
        D = {"layout": "axle", "T": [round(mT * fb[0]), round(mT * fb[1])], "P": [round(P * fb[0]), round(P * fb[1])]}
        if kind == "ev":
            T.update(kWh=c["kWh"], regenMax=3); T["feat"] = f"about {c['rng']} mi"; no = NO_EV
        else:
            T.update(hybrid=True, sound=c.get("eng", "i4t"), evBtn=True, regenMax=2, tank=c["tank"], mpg=c["mpg"]); no = NO_HEV
            if kind == "phev": T.update(phev=True, kWh=c["kWh"], evMi=c["evMi"]); T["feat"] = f"{c['evMi']} mi EV"
    out.append(f' add({json.dumps(c["key"])},{{...{json.dumps(T, separators=(",", ":"))},no:{json.dumps(no)}}},{json.dumps(D, separators=(", ", ": "))},{c["price"]});')
if __name__ == "__main__":
    open(sys.argv[1], "w").write("\n".join(out) + "\n")
    print(len(out), "trims;", len({c['model'] for c in C}), "models")
