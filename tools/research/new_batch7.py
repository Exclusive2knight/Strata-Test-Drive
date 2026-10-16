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
car("cad_lyriq_lux", "cad_lyriq", "Cadillac LYRIQ · 2027", "2027 Cadillac LYRIQ Luxury RWD", "LYRIQ Luxury", "ev", 365, 2550, "rwd", 59000, "Single motor · RWD · 365 hp · 102 kWh · 326 mi", kWh=102, rng=326, cda=0.75)
car("cad_lyriq_v", "cad_lyriqv", "Cadillac LYRIQ · 2027", "2027 Cadillac LYRIQ-V", "LYRIQ-V", "ev", 615, 2700, "awd", 80000, "Dual motor · AWD · 615 hp · 102 kWh · 285 mi", kWh=102, rng=285, cda=0.75)
car("cad_optiq_lux", "cad_optiq", "Cadillac OPTIQ · 2027", "2027 Cadillac OPTIQ Luxury AWD", "OPTIQ Luxury", "ev", 300, 2350, "awd", 54000, "Dual motor · AWD · 300 hp · 85 kWh · 302 mi", kWh=85, rng=302, cda=0.78)
car("cad_optiq_v", "cad_optiqv", "Cadillac OPTIQ · 2027", "2027 Cadillac OPTIQ-V", "OPTIQ-V", "ev", 519, 2450, "awd", 70000, "Dual motor · AWD · 519 hp · 85 kWh · about 280 mi (est.)", kWh=85, rng=280, cda=0.78)
car("cad_vistiq_lux", "cad_vistiq", "Cadillac VISTIQ · 2027", "2027 Cadillac VISTIQ Luxury", "VISTIQ Luxury", "ev", 615, 2800, "awd", 79000, "Dual motor · AWD · 615 hp · 102 kWh · 305 mi", kWh=102, rng=305, cda=0.85)
car("cad_celestiq", "cad_celestiq", "Cadillac CELESTIQ · 2026", "2026 Cadillac CELESTIQ", "CELESTIQ", "ev", 600, 3100, "awd", 340000, "Dual motor · AWD · 600 hp · 111 kWh · 303 mi", kWh=111, rng=303, cda=0.7)


# ---------------- full trim lineups (added in v100). Prices are US starting MSRPs as of mid-2026, approximate where noted in docs/CARS.md
X=car
X("hy_venue_se","hy_venue","Hyundai Venue · 2026","2026 Hyundai Venue SE","Venue SE","ice",121,1220,"fwd",20550,"1.6 L · IVT · FWD · 121 hp",eng="i4h",tq=151,gears=CV,cvt=True,tank=45,mpg=31,cda=0.85)
X("hy_venue_lim","hy_venue","Hyundai Venue · 2026","2026 Hyundai Venue Limited","Venue Limited","ice",121,1240,"fwd",24050,"1.6 L · IVT · FWD · 121 hp",eng="i4h",tq=151,gears=CV,cvt=True,tank=45,mpg=31,cda=0.85)
X("hy_kona_se","hy_kona","Hyundai Kona · 2026","2026 Hyundai Kona SE","Kona SE","ice",147,1380,"fwd",25400,"2.0 L · IVT · FWD · 147 hp",eng="i4h",tq=179,gears=CV,cvt=True,tank=50,mpg=30,cda=0.88)
X("hy_kona_nl","hy_kona","Hyundai Kona · 2026","2026 Hyundai Kona N Line AWD","Kona N Line","ice",190,1500,"awd",32800,"1.6 L turbo · 8-speed · AWD · 190 hp",eng="i4t",tq=264,gears=G8H,tank=47,mpg=26,cda=0.88,modes=["Eco","Normal","Sport","Snow"])
X("hy_kona_lim","hy_kona","Hyundai Kona · 2026","2026 Hyundai Kona Limited AWD","Kona Limited","ice",190,1500,"awd",33300,"1.6 L turbo · 8-speed · AWD · 190 hp",eng="i4t",tq=264,gears=G8H,tank=47,mpg=26,cda=0.88)
X("hy_kona_ev_se","hy_kona_ev","Hyundai Kona Electric · 2025","2025 Hyundai Kona Electric SE","Kona Electric SE","ev",133,1680,"fwd",33550,"Single motor · FWD · 133 hp · 48.6 kWh · 200 mi",kWh=48.6,rng=200,cda=0.8)
X("hy_kona_ev_lim","hy_kona_ev","Hyundai Kona Electric · 2025","2025 Hyundai Kona Electric Limited","Kona Electric Limited","ev",201,1770,"fwd",41550,"Single motor · FWD · 201 hp · 64.8 kWh · 230 mi",kWh=64.8,rng=230,cda=0.8)
X("hy_tucson_se","hy_tucson","Hyundai Tucson · 2026","2026 Hyundai Tucson SE","Tucson SE","ice",187,1580,"fwd",29200,"2.5 L · 8-speed · FWD · 187 hp",eng="i4h",tq=241,gears=G8H,tank=54,mpg=27,cda=0.95)
X("hy_tucson_xrt","hy_tucson","Hyundai Tucson · 2026","2026 Hyundai Tucson XRT AWD","Tucson XRT","ice",187,1660,"awd",36100,"2.5 L · 8-speed · HTRAC AWD · 187 hp",eng="i4h",tq=241,gears=G8H,tank=54,mpg=24,cda=1.0,modes=["Eco","Normal","Sport","Snow","Mud","Sand"])
X("hy_tucson_lim","hy_tucson","Hyundai Tucson · 2026","2026 Hyundai Tucson Limited AWD","Tucson Limited","ice",187,1680,"awd",38650,"2.5 L · 8-speed · HTRAC AWD · 187 hp",eng="i4h",tq=241,gears=G8H,tank=54,mpg=25,cda=0.95)
X("hy_tucson_hev_blue","hy_tucson_hev","Hyundai Tucson · 2026","2026 Hyundai Tucson Hybrid Blue","Tucson Hybrid Blue","hev",231,1720,"awd",33500,"1.6 L turbo hybrid · 6-speed · HTRAC AWD · 231 hp",tank=52,mpg=38,cda=0.95,eng="i4t")
X("hy_tucson_hev_lim","hy_tucson_hev","Hyundai Tucson · 2026","2026 Hyundai Tucson Hybrid Limited","Tucson Hybrid Limited","hev",231,1790,"awd",40600,"1.6 L turbo hybrid · 6-speed · HTRAC AWD · 231 hp",tank=52,mpg=35,cda=0.95,eng="i4t")
X("hy_tucson_phev_lim","hy_tucson_phev","Hyundai Tucson · 2026","2026 Hyundai Tucson Plug-in Hybrid Limited","Tucson PHEV Limited","phev",268,1950,"awd",45500,"1.6 L turbo PHEV · 6-speed · HTRAC AWD · 268 hp · 33 mi EV",tank=42,mpg=35,kWh=13.8,evMi=33,cda=0.95,eng="i4t")
X("hy_santafe_se","hy_santafe","Hyundai Santa Fe · 2026","2026 Hyundai Santa Fe SE","Santa Fe SE","ice",191,1830,"fwd",35000,"2.5 L · 8-speed · FWD · 191 hp",eng="i4h",tq=245,gears=G8H,tank=67,mpg=24,cda=1.0)
X("hy_santafe_xrt","hy_santafe","Hyundai Santa Fe · 2026","2026 Hyundai Santa Fe XRT","Santa Fe XRT","ice",277,1950,"awd",41500,"2.5 L turbo · 8-speed DCT · HTRAC AWD · 277 hp",eng="i4t",tq=422,gears=G8H,tank=67,mpg=21,cda=1.05,modes=["Eco","Normal","Sport","Snow","Mud","Sand"])
X("hy_santafe_cal","hy_santafe","Hyundai Santa Fe · 2026","2026 Hyundai Santa Fe Calligraphy","Santa Fe Calligraphy","ice",277,1960,"awd",49000,"2.5 L turbo · 8-speed DCT · HTRAC AWD · 277 hp",eng="i4t",tq=422,gears=G8H,tank=67,mpg=22,cda=1.0)
X("hy_santafe_hev_lim","hy_santafe_hev","Hyundai Santa Fe · 2026","2026 Hyundai Santa Fe Hybrid Limited","Santa Fe Hybrid Limited","hev",231,2000,"awd",45300,"1.6 L turbo hybrid · 6-speed · HTRAC AWD · 231 hp",tank=67,mpg=34,cda=1.0,eng="i4t")
X("hy_santafe_hev_cal","hy_santafe_hev","Hyundai Santa Fe · 2026","2026 Hyundai Santa Fe Hybrid Calligraphy","Santa Fe Hybrid Calligraphy","hev",231,2030,"awd",49900,"1.6 L turbo hybrid · 6-speed · HTRAC AWD · 231 hp",tank=67,mpg=34,cda=1.0,eng="i4t")
X("hy_palisade_se","hy_palisade","Hyundai Palisade · 2026","2026 Hyundai Palisade SE","Palisade SE","ice",287,2010,"fwd",39400,"3.5 L V6 · 8-speed · FWD · 287 hp",eng="v6",tq=352,gears=G8H,tank=71,mpg=22,cda=1.1)
X("hy_palisade_xrt","hy_palisade","Hyundai Palisade · 2026","2026 Hyundai Palisade XRT PRO","Palisade XRT PRO","ice",287,2150,"awd",50500,"3.5 L V6 · 8-speed · HTRAC AWD · 287 hp",eng="v6",tq=352,gears=G8H,tank=71,mpg=20,cda=1.15,modes=["Eco","Normal","Sport","Snow","Mud","Sand"])
X("hy_palisade_cal","hy_palisade","Hyundai Palisade · 2026","2026 Hyundai Palisade Calligraphy","Palisade Calligraphy","ice",287,2170,"awd",54200,"3.5 L V6 · 8-speed · HTRAC AWD · 287 hp",eng="v6",tq=352,gears=G8H,tank=71,mpg=20,cda=1.1)
X("hy_palisade_hev_lim","hy_palisade_hev","Hyundai Palisade · 2026","2026 Hyundai Palisade Hybrid Limited","Palisade Hybrid Limited","hev",329,2240,"awd",54000,"2.5 L turbo hybrid · 6-speed · HTRAC AWD · 329 hp",tank=71,mpg=31,cda=1.1,eng="i4t")
X("hy_palisade_hev_cal","hy_palisade_hev","Hyundai Palisade · 2026","2026 Hyundai Palisade Hybrid Calligraphy","Palisade Hybrid Calligraphy","hev",329,2260,"awd",57600,"2.5 L turbo hybrid · 6-speed · HTRAC AWD · 329 hp",tank=71,mpg=31,cda=1.1,eng="i4t")
X("hy_santacruz_se","hy_santacruz","Hyundai Santa Cruz · 2026","2026 Hyundai Santa Cruz SE","Santa Cruz SE","ice",191,1700,"fwd",29700,"2.5 L · 8-speed · FWD · 191 hp",eng="i4h",tq=245,gears=G8H,tank=66,mpg=23,cda=1.05)
X("hy_santacruz_xrt","hy_santacruz","Hyundai Santa Cruz · 2026","2026 Hyundai Santa Cruz XRT","Santa Cruz XRT","ice",281,1880,"awd",40600,"2.5 L turbo · 8-speed DCT · HTRAC AWD · 281 hp",eng="i4t",tq=421,gears=G8H,tank=66,mpg=21,cda=1.1,modes=["Eco","Normal","Sport","Snow","Mud","Sand"])
X("hy_santacruz_lim","hy_santacruz","Hyundai Santa Cruz · 2026","2026 Hyundai Santa Cruz Limited","Santa Cruz Limited","ice",281,1880,"awd",42300,"2.5 L turbo · 8-speed DCT · HTRAC AWD · 281 hp",eng="i4t",tq=421,gears=G8H,tank=66,mpg=22,cda=1.05)
X("hy_ioniq5_se_sr","hy_ioniq5","Hyundai IONIQ 5 · 2026","2026 Hyundai IONIQ 5 SE Standard Range","IONIQ 5 SE SR","ev",168,1900,"rwd",42600,"Single motor · RWD · 168 hp · 63 kWh · 245 mi",kWh=63,rng=245,cda=0.7)
X("hy_ioniq5_xrt","hy_ioniq5","Hyundai IONIQ 5 · 2026","2026 Hyundai IONIQ 5 XRT AWD","IONIQ 5 XRT","ev",320,2150,"awd",55500,"Dual motor · AWD · 320 hp · 84 kWh · 259 mi",kWh=84,rng=259,cda=0.75)
X("hy_ioniq5_lim","hy_ioniq5","Hyundai IONIQ 5 · 2026","2026 Hyundai IONIQ 5 Limited AWD","IONIQ 5 Limited","ev",320,2130,"awd",54400,"Dual motor · AWD · 320 hp · 84 kWh · 269 mi",kWh=84,rng=269,cda=0.7)
X("hy_ioniq9_s","hy_ioniq9","Hyundai IONIQ 9 · 2026","2026 Hyundai IONIQ 9 S RWD","IONIQ 9 S","ev",215,2450,"rwd",58950,"Single motor · RWD · 215 hp · 110.3 kWh · 335 mi",kWh=110.3,rng=335,cda=0.85)
X("hy_ioniq9_cal","hy_ioniq9","Hyundai IONIQ 9 · 2026","2026 Hyundai IONIQ 9 Performance Calligraphy","IONIQ 9 Perf. Calligraphy","ev",422,2700,"awd",76500,"Dual motor · AWD · 422 hp · 110.3 kWh · 311 mi",kWh=110.3,rng=311,cda=0.85)
X("bmw_x1_m35i","bmw_x1","BMW X1 · 2026","2026 BMW X1 M35i xDrive","X1 M35i","ice",312,1760,"awd",51900,"2.0 L turbo · 7-speed DCT · xDrive · 312 hp",eng="i4t",tq=400,gears=G7,tank=54,mpg=26,cda=0.82,modes=["Efficient","Personal","Sport","Sport Plus"])
X("bmw_x2_m35i","bmw_x2","BMW X2 · 2026","2026 BMW X2 M35i xDrive","X2 M35i","ice",312,1770,"awd",53100,"2.0 L turbo · 7-speed DCT · xDrive · 312 hp",eng="i4t",tq=400,gears=G7,tank=54,mpg=26,cda=0.78,modes=["Efficient","Personal","Sport","Sport Plus"])
X("bmw_x3_m50","bmw_x3","BMW X3 · 2026","2026 BMW X3 M50 xDrive","X3 M50","ice",393,1990,"awd",66000,"3.0 L turbo I6 mild hybrid · 8-speed · xDrive · 393 hp",eng="v6",tq=580,gears=G8,tank=65,mpg=24,cda=0.88,modes=["Efficient","Personal","Sport","Sport Plus"])
X("bmw_x5_s40i","bmw_x5","BMW X5 · 2025","2025 BMW X5 sDrive40i","X5 sDrive40i","ice",375,2120,"rwd",65700,"3.0 L turbo I6 mild hybrid · 8-speed · RWD · 375 hp",eng="v6",tq=540,gears=G8,tank=83,mpg=24,cda=1.0)
X("bmw_x5_m60i","bmw_x5","BMW X5 · 2025","2025 BMW X5 M60i xDrive","X5 M60i","ice",523,2350,"awd",90600,"4.4 L twin-turbo V8 mild hybrid · 8-speed · xDrive · 523 hp",eng="v8",tq=750,gears=G8,tank=83,mpg=18,cda=1.0,modes=["Efficient","Personal","Sport","Sport Plus"])
X("bmw_x6_m60i","bmw_x6","BMW X6 · 2026","2026 BMW X6 M60i xDrive","X6 M60i","ice",523,2330,"awd",96600,"4.4 L twin-turbo V8 mild hybrid · 8-speed · xDrive · 523 hp",eng="v8",tq=750,gears=G8,tank=83,mpg=18,cda=0.95,modes=["Efficient","Personal","Sport","Sport Plus"])
X("bmw_x7_m60i","bmw_x7","BMW X7 · 2026","2026 BMW X7 M60i xDrive","X7 M60i","ice",523,2600,"awd",109600,"4.4 L twin-turbo V8 mild hybrid · 8-speed · xDrive · 523 hp",eng="v8",tq=750,gears=G8,tank=83,mpg=17,cda=1.1,modes=["Efficient","Personal","Sport","Sport Plus"])
X("bmw_x7_alpina","bmw_x7","BMW X7 · 2026","2026 BMW ALPINA XB7","ALPINA XB7","ice",631,2700,"awd",151000,"4.4 L twin-turbo V8 · 8-speed · xDrive · 631 hp",eng="v8",tq=800,gears=G8,tank=83,mpg=16,cda=1.1,modes=["Comfort Plus","Comfort","Sport","Sport Plus"])
X("mb_gla_amg35","mb_gla","Mercedes-Benz GLA · 2026","2026 Mercedes-AMG GLA 35 4MATIC","AMG GLA 35","ice",302,1720,"awd",58900,"2.0 L turbo · 8-speed DCT · 4MATIC · 302 hp",eng="i4t",tq=400,gears=G7,tank=51,mpg=24,cda=0.82,modes=["Slippery","Comfort","Sport","Sport+","Individual"])
X("mb_glb_amg35","mb_glb","Mercedes-Benz GLB · 2026","2026 Mercedes-AMG GLB 35 4MATIC","AMG GLB 35","ice",302,1810,"awd",60800,"2.0 L turbo · 8-speed DCT · 4MATIC · 302 hp",eng="i4t",tq=400,gears=G7,tank=60,mpg=23,cda=0.9,modes=["Slippery","Comfort","Sport","Sport+","Individual"])
X("mb_glc_amg43","mb_glc","Mercedes-Benz GLC · 2026","2026 Mercedes-AMG GLC 43 4MATIC","AMG GLC 43","ice",416,2000,"awd",70700,"2.0 L turbo mild hybrid · 9-speed · 4MATIC · 416 hp",eng="i4t",tq=500,gears=G9,tank=62,mpg=21,cda=0.88,modes=["Slippery","Comfort","Sport","Sport+","Individual"])
X("mb_glc_coupe_amg43","mb_glc_coupe","Mercedes-Benz GLC Coupe · 2026","2026 Mercedes-AMG GLC 43 4MATIC Coupe","AMG GLC 43 Coupe","ice",416,2020,"awd",76000,"2.0 L turbo mild hybrid · 9-speed · 4MATIC · 416 hp",eng="i4t",tq=500,gears=G9,tank=62,mpg=21,cda=0.84,modes=["Slippery","Comfort","Sport","Sport+","Individual"])
X("mb_gle_350","mb_gle","Mercedes-Benz GLE · 2026","2026 Mercedes-Benz GLE 350 4MATIC","GLE 350 4MATIC","ice",255,2150,"awd",64000,"2.0 L turbo mild hybrid · 9-speed · 4MATIC · 255 hp",eng="i4t",tq=400,gears=G9,tank=85,mpg=23,cda=1.0)
X("mb_gle_580","mb_gle","Mercedes-Benz GLE · 2026","2026 Mercedes-Benz GLE 580 4MATIC","GLE 580 4MATIC","ice",510,2400,"awd",92700,"4.0 L twin-turbo V8 mild hybrid · 9-speed · 4MATIC · 510 hp",eng="v8",tq=700,gears=G9,tank=85,mpg=18,cda=1.0)
X("mb_gle_amg53","mb_gle","Mercedes-Benz GLE · 2026","2026 Mercedes-AMG GLE 53 4MATIC+","AMG GLE 53","ice",429,2350,"awd",89500,"3.0 L turbo I6 mild hybrid · 9-speed · 4MATIC+ · 429 hp",eng="v6",tq=560,gears=G9,tank=85,mpg=19,cda=1.0,modes=["Slippery","Comfort","Sport","Sport+","Individual"])
X("mb_gle_coupe_amg53","mb_gle_coupe","Mercedes-Benz GLE Coupe · 2026","2026 Mercedes-AMG GLE 53 4MATIC+ Coupe","AMG GLE 53 Coupe","ice",429,2380,"awd",92500,"3.0 L turbo I6 mild hybrid · 9-speed · 4MATIC+ · 429 hp",eng="v6",tq=560,gears=G9,tank=85,mpg=19,cda=0.95,modes=["Slippery","Comfort","Sport","Sport+","Individual"])
X("mb_gls_580","mb_gls","Mercedes-Benz GLS · 2026","2026 Mercedes-Benz GLS 580 4MATIC","GLS 580 4MATIC","ice",510,2650,"awd",113800,"4.0 L twin-turbo V8 mild hybrid · 9-speed · 4MATIC · 510 hp",eng="v8",tq=700,gears=G9,tank=90,mpg=17,cda=1.1)
X("mb_g63","mb_g550","Mercedes-Benz G-Class · 2026","2026 Mercedes-AMG G 63","AMG G 63","ice",577,2640,"awd",186000,"4.0 L twin-turbo V8 mild hybrid · 9-speed · 4MATIC · 577 hp",eng="v8",tq=850,gears=G9,tank=100,mpg=14,cda=1.5,modes=["Slippery","Comfort","Sport","Sport+","Individual","Trail","Sand","Rock"])
X("mb_eqb_250","mb_eqb","Mercedes-Benz EQB · 2025","2025 Mercedes-Benz EQB 250+","EQB 250+","ev",188,2050,"fwd",53050,"Single motor · FWD · 188 hp · 70.5 kWh · 251 mi",kWh=70.5,rng=251,cda=0.85)
X("mb_eqb_350","mb_eqb","Mercedes-Benz EQB · 2025","2025 Mercedes-Benz EQB 350 4MATIC","EQB 350 4MATIC","ev",288,2220,"awd",60550,"Dual motor · 4MATIC · 288 hp · 70.5 kWh · 207 mi",kWh=70.5,rng=207,cda=0.85)
X("mb_eqe_suv_500","mb_eqe_suv","Mercedes-Benz EQE SUV · 2026","2026 Mercedes-Benz EQE 500 4MATIC SUV","EQE 500 SUV","ev",402,2650,"awd",91300,"Dual motor · 4MATIC · 402 hp · 90.6 kWh · 253 mi",kWh=90.6,rng=253,cda=0.75)
X("mb_eqs_suv_450p","mb_eqs_suv","Mercedes-Benz EQS SUV · 2026","2026 Mercedes-Benz EQS 450+ SUV","EQS 450+ SUV","ev",355,2700,"rwd",105000,"Single motor · RWD · 355 hp · 108.4 kWh · 305 mi",kWh=108.4,rng=305,cda=0.75)
X("mb_eqs_suv_580","mb_eqs_suv","Mercedes-Benz EQS SUV · 2026","2026 Mercedes-Benz EQS 580 4MATIC SUV","EQS 580 SUV","ev",536,2850,"awd",128900,"Dual motor · 4MATIC · 536 hp · 108.4 kWh · 285 mi",kWh=108.4,rng=285,cda=0.75)
X("cad_lyriq_lux2","cad_lyriq","Cadillac LYRIQ · 2027","2027 Cadillac LYRIQ Luxury AWD","LYRIQ Luxury AWD","ev",528,2650,"awd",65500,"Dual motor · AWD · 528 hp · 102 kWh · 311 mi",kWh=102,rng=311,cda=0.75)
X("cad_lyriq_sport","cad_lyriq","Cadillac LYRIQ · 2027","2027 Cadillac LYRIQ Sport AWD","LYRIQ Sport AWD","ev",528,2650,"awd",68500,"Dual motor · AWD · 528 hp · 102 kWh · 311 mi",kWh=102,rng=311,cda=0.75)
X("cad_optiq_sport","cad_optiq","Cadillac OPTIQ · 2027","2027 Cadillac OPTIQ Sport AWD","OPTIQ Sport","ev",300,2360,"awd",56500,"Dual motor · AWD · 300 hp · 85 kWh · 302 mi",kWh=85,rng=302,cda=0.78)
X("cad_vistiq_sport","cad_vistiq","Cadillac VISTIQ · 2027","2027 Cadillac VISTIQ Sport","VISTIQ Sport","ev",615,2800,"awd",81500,"Dual motor · AWD · 615 hp · 102 kWh · 305 mi",kWh=102,rng=305,cda=0.85)
X("cad_vistiq_plat","cad_vistiq","Cadillac VISTIQ · 2027","2027 Cadillac VISTIQ Platinum","VISTIQ Platinum","ev",615,2820,"awd",90500,"Dual motor · AWD · 615 hp · 102 kWh · 305 mi",kWh=102,rng=305,cda=0.85)

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
